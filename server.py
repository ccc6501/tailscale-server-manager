"""
Tailscale Server Manager - Enhanced Web Version
FastAPI backend with comprehensive settings, port management, and monitoring
"""

import asyncio
import json
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Encoding helper
DEFAULT_ENCODING = "utf-8"

# ------------------------------------------------------------
# Configuration Models
# ------------------------------------------------------------

@dataclass
class ServiceConfig:
    name: str
    kind: str  # "backend" or "frontend" or "other"
    start_cmd: str
    working_dir: Optional[str] = None
    match_keywords: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    api_url: Optional[str] = None
    tailscale_url: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ServerSettings:
    storage_paths: Dict[str, str] = field(default_factory=dict)
    scheduled_tasks: List[Dict[str, Any]] = field(default_factory=list)
    stats_retention_days: int = 30
    auto_restart_on_failure: bool = False
    check_port_conflicts: bool = True
    default_tailscale_domain: str = ""
    update_interval_seconds: int = 5
    api_base_url: str = "http://localhost:8765"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Pydantic models for API requests
class SettingsUpdate(BaseModel):
    storage_paths: Optional[Dict[str, str]] = None
    scheduled_tasks: Optional[List[Dict[str, Any]]] = None
    stats_retention_days: Optional[int] = None
    auto_restart_on_failure: Optional[bool] = None
    check_port_conflicts: Optional[bool] = None
    default_tailscale_domain: Optional[str] = None
    update_interval_seconds: Optional[int] = None
    api_base_url: Optional[str] = None


class ServiceAdd(BaseModel):
    name: str
    kind: str
    start_cmd: str
    working_dir: Optional[str] = None
    match_keywords: List[str] = []
    ports: List[int] = []
    api_url: Optional[str] = None
    tailscale_url: Optional[str] = None
    description: Optional[str] = None


class ScheduledTaskModel(BaseModel):
    name: str
    cron_expression: str
    action: str  # "start", "stop", "restart"
    service_name: str
    enabled: bool = True


# ------------------------------------------------------------
# Runtime Tracking
# ------------------------------------------------------------

class ServiceRuntime:
    """Track runtime information for services"""
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time: Optional[datetime] = None
        self.errors: List[Dict[str, Any]] = []
        self.restart_count: int = 0
        self.last_error: Optional[str] = None
        
    def mark_started(self):
        self.start_time = datetime.now()
        
    def mark_stopped(self):
        self.start_time = None
        
    def add_error(self, error_msg: str):
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "message": error_msg
        })
        self.last_error = error_msg
        if len(self.errors) > 10:
            self.errors = self.errors[-10:]
    
    def get_uptime(self) -> Optional[str]:
        if not self.start_time:
            return None
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uptime": self.get_uptime(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "errors": self.errors[-3:],  # Last 3 errors for display
            "restart_count": self.restart_count,
            "last_error": self.last_error
        }


# Global runtime tracker
runtime_tracker: Dict[str, ServiceRuntime] = {}

# ------------------------------------------------------------
# Configuration Loading & Management
# ------------------------------------------------------------

def load_services() -> List[ServiceConfig]:
    """Load services from config file"""
    config_file = Path("services_config.json")
    
    if not config_file.exists():
        default_services = [
            {
                "name": "FastAPI Backend",
                "kind": "backend",
                "start_cmd": "uvicorn main:app --host 0.0.0.0 --port 8000",
                "working_dir": None,
                "match_keywords": ["uvicorn", "main:app"],
                "ports": [8000],
                "api_url": "http://localhost:8000",
                "tailscale_url": None,
                "description": "Main backend API service"
            }
        ]
        
        config_file.write_text(json.dumps(default_services, indent=2), encoding=DEFAULT_ENCODING)
        services = [ServiceConfig(**s) for s in default_services]
    else:
        services_data = json.loads(config_file.read_text(encoding=DEFAULT_ENCODING))
        services = [ServiceConfig(**s) for s in services_data]
    
    for svc in services:
        if svc.name not in runtime_tracker:
            runtime_tracker[svc.name] = ServiceRuntime(svc.name)
    
    return services


def save_services(services: List[ServiceConfig]):
    """Save services to config file"""
    config_file = Path("services_config.json")
    config_file.write_text(json.dumps([s.to_dict() for s in services], indent=2), encoding=DEFAULT_ENCODING)


def load_settings() -> ServerSettings:
    """Load server settings from file"""
    settings_file = Path("settings.json")
    
    if not settings_file.exists():
        settings = ServerSettings(
            storage_paths={
                "logs": "./logs",
                "data": "./data",
                "backups": "./backups"
            },
            scheduled_tasks=[],
            stats_retention_days=30,
            auto_restart_on_failure=False,
            check_port_conflicts=True,
            default_tailscale_domain="",
            update_interval_seconds=5,
            api_base_url="http://localhost:8765"
        )
        settings_file.write_text(json.dumps(settings.to_dict(), indent=2), encoding=DEFAULT_ENCODING)
        return settings
    
    settings_data = json.loads(settings_file.read_text(encoding=DEFAULT_ENCODING))
    return ServerSettings(**settings_data)


def save_settings(settings: ServerSettings):
    """Save settings to file"""
    settings_file = Path("settings.json")
    settings_file.write_text(json.dumps(settings.to_dict(), indent=2), encoding=DEFAULT_ENCODING)


SERVICES = load_services()
SETTINGS = load_settings()

# ------------------------------------------------------------
# Port Management & Validation
# ------------------------------------------------------------

def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False


def get_port_conflicts(services: List[ServiceConfig]) -> Dict[int, List[str]]:
    """Find port conflicts between services"""
    port_usage = {}
    for svc in services:
        for port in svc.ports:
            if port not in port_usage:
                port_usage[port] = []
            port_usage[port].append(svc.name)
    
    return {port: svcs for port, svcs in port_usage.items() if len(svcs) > 1}


def scan_service_for_ports(svc: ServiceConfig) -> List[int]:
    """Scan running service processes to detect ports they're using"""
    detected_ports = []
    procs = find_matching_procs(svc)
    
    for proc_info in procs:
        try:
            proc = psutil.Process(proc_info['pid'])
            connections = proc.connections()
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr:
                    port = conn.laddr.port
                    if port not in detected_ports:
                        detected_ports.append(port)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return detected_ports


def validate_new_service(new_service: ServiceConfig, existing_services: List[ServiceConfig]) -> Dict[str, Any]:
    """Validate a new service before adding it"""
    issues = []
    warnings = []
    
    if any(s.name == new_service.name for s in existing_services):
        issues.append(f"Service name '{new_service.name}' already exists")
    
    if SETTINGS.check_port_conflicts and new_service.ports:
        for port in new_service.ports:
            conflicting = [s.name for s in existing_services if port in s.ports]
            if conflicting:
                issues.append(f"Port {port} conflicts with: {', '.join(conflicting)}")
            
            if is_port_in_use(port):
                warnings.append(f"Port {port} is currently in use")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }

# ------------------------------------------------------------
# Process Management
# ------------------------------------------------------------

def _matches_keywords(proc: psutil.Process, keywords: List[str]) -> bool:
    if not keywords:
        return False
    try:
        cmdline = " ".join(proc.cmdline()).lower()
        return all(k.lower() in cmdline for k in keywords)
    except:
        return False


def find_matching_procs(svc: ServiceConfig) -> List[Dict[str, Any]]:
    """Find processes matching service keywords"""
    if not svc.match_keywords:
        return []
    
    matches = []
    try:
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                name = p.info.get('name', '').lower()
                if any(k.lower() in name for k in svc.match_keywords):
                    if _matches_keywords(p, svc.match_keywords):
                        matches.append({
                            'pid': p.info['pid'],
                            'name': p.info['name'],
                            'cpu': round(p.info.get('cpu_percent', 0), 1),
                            'memory': p.info.get('memory_info', {}).get('rss', 0) if p.info.get('memory_info') else 0,
                            'create_time': p.info.get('create_time', 0)
                        })
                else:
                    if _matches_keywords(p, svc.match_keywords):
                        matches.append({
                            'pid': p.info['pid'],
                            'name': p.info['name'],
                            'cpu': round(p.info.get('cpu_percent', 0), 1),
                            'memory': p.info.get('memory_info', {}).get('rss', 0) if p.info.get('memory_info') else 0,
                            'create_time': p.info.get('create_time', 0)
                        })
            except:
                continue
    except:
        pass
    return matches


def start_service(svc: ServiceConfig) -> Dict[str, Any]:
    """Start a service"""
    try:
        creationflags = 0
        if sys.platform.startswith("win"):
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        
        subprocess.Popen(
            svc.start_cmd,
            cwd=svc.working_dir or None,
            shell=True,
            creationflags=creationflags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        
        time.sleep(0.5)
        runtime_tracker[svc.name].mark_started()
        return {"success": True, "message": f"Started {svc.name}"}
    except Exception as e:
        error_msg = str(e)
        runtime_tracker[svc.name].add_error(error_msg)
        return {"success": False, "message": error_msg}


def stop_service(svc: ServiceConfig, timeout: float = 5.0) -> Dict[str, Any]:
    """Stop a service"""
    try:
        procs = find_matching_procs(svc)
        if not procs:
            runtime_tracker[svc.name].mark_stopped()
            return {"success": True, "message": "No processes found", "count": 0}
        
        proc_objects = []
        for p_info in procs:
            try:
                p = psutil.Process(p_info['pid'])
                proc_objects.append(p)
                p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if proc_objects:
            gone, alive = psutil.wait_procs(proc_objects, timeout=timeout)
            for p in alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        runtime_tracker[svc.name].mark_stopped()
        return {"success": True, "message": f"Stopped {len(procs)} process(es)", "count": len(procs)}
    except Exception as e:
        error_msg = str(e)
        runtime_tracker[svc.name].add_error(error_msg)
        return {"success": False, "message": error_msg, "count": 0}


def get_service_status(svc: ServiceConfig) -> Dict[str, Any]:
    """Get comprehensive status of a service"""
    procs = find_matching_procs(svc)
    is_running = len(procs) > 0
    
    # Update runtime tracker
    if is_running and not runtime_tracker[svc.name].start_time:
        runtime_tracker[svc.name].mark_started()
    elif not is_running and runtime_tracker[svc.name].start_time:
        runtime_tracker[svc.name].mark_stopped()
    
    # Scan for actual ports if service is running
    actual_ports = scan_service_for_ports(svc) if is_running else []
    
    # Port status
    port_status = []
    for port in svc.ports:
        in_use = is_port_in_use(port)
        port_status.append({
            "port": port,
            "in_use": in_use,
            "accessible": in_use and is_running
        })
    
    return {
        "name": svc.name,
        "kind": svc.kind,
        "running": is_running,
        "processes": procs,
        "pid_count": len(procs),
        "ports": svc.ports,
        "port_status": port_status,
        "detected_ports": actual_ports,
        "api_url": svc.api_url,
        "tailscale_url": svc.tailscale_url,
        "description": svc.description,
        "runtime": runtime_tracker[svc.name].to_dict()
    }


def get_all_statuses() -> List[Dict[str, Any]]:
    """Get status of all services"""
    return [get_service_status(svc) for svc in SERVICES]


def get_system_stats() -> Dict[str, Any]:
    """Get overall system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_percent": round(disk.percent, 1),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2)
        }
    except:
        return {}

# ------------------------------------------------------------
# FastAPI Application
# ------------------------------------------------------------

app = FastAPI(title="Tailscale Server Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/")
async def get_index():
    """Serve the main HTML page"""
    try:
        html_file = Path(__file__).parent / "index.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text(encoding=DEFAULT_ENCODING, errors="replace"))
        else:
            return HTMLResponse(content="""
                <html>
                <body>
                    <h1>Tailscale Server Manager</h1>
                    <p>Error: index.html not found in the server directory.</p>
                    <p>Please ensure index.html is in the same directory as server.py</p>
                    <p>API is running at: <a href="/docs">/docs</a></p>
                </body>
                </html>
            """, status_code=500)
    except Exception as e:
        return HTMLResponse(content=f"""
            <html>
            <body>
                <h1>Error loading interface</h1>
                <p>{str(e)}</p>
                <p>API is running at: <a href="/docs">/docs</a></p>
            </body>
            </html>
        """, status_code=500)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services_count": len(SERVICES)
    }


@app.get("/api/services")
async def get_services():
    """Get list of all services with their configurations"""
    return [svc.to_dict() for svc in SERVICES]


@app.get("/api/status")
async def get_status():
    """Get status of all services"""
    return get_all_statuses()


@app.get("/api/settings")
async def get_settings():
    """Get current server settings"""
    return SETTINGS.to_dict()


@app.post("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update server settings"""
    global SETTINGS
    
    if settings_update.storage_paths is not None:
        SETTINGS.storage_paths = settings_update.storage_paths
    if settings_update.scheduled_tasks is not None:
        SETTINGS.scheduled_tasks = settings_update.scheduled_tasks
    if settings_update.stats_retention_days is not None:
        SETTINGS.stats_retention_days = settings_update.stats_retention_days
    if settings_update.auto_restart_on_failure is not None:
        SETTINGS.auto_restart_on_failure = settings_update.auto_restart_on_failure
    if settings_update.check_port_conflicts is not None:
        SETTINGS.check_port_conflicts = settings_update.check_port_conflicts
    if settings_update.default_tailscale_domain is not None:
        SETTINGS.default_tailscale_domain = settings_update.default_tailscale_domain
    if settings_update.update_interval_seconds is not None:
        SETTINGS.update_interval_seconds = settings_update.update_interval_seconds
    if settings_update.api_base_url is not None:
        SETTINGS.api_base_url = settings_update.api_base_url
    
    save_settings(SETTINGS)
    
    await manager.broadcast({"type": "settings_updated", "data": SETTINGS.to_dict()})
    
    return {"success": True, "message": "Settings updated"}


@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return get_system_stats()


@app.get("/api/port-conflicts")
async def get_conflicts():
    """Get port conflict information"""
    conflicts = get_port_conflicts(SERVICES)
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }


@app.post("/api/service/add")
async def add_service(service: ServiceAdd):
    """Add a new service"""
    global SERVICES
    
    new_svc = ServiceConfig(**service.dict())
    
    validation = validate_new_service(new_svc, SERVICES)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={
            "message": "Service validation failed",
            "issues": validation["issues"],
            "warnings": validation["warnings"]
        })
    
    SERVICES.append(new_svc)
    runtime_tracker[new_svc.name] = ServiceRuntime(new_svc.name)
    save_services(SERVICES)
    
    await manager.broadcast({"type": "service_added", "data": new_svc.to_dict()})
    
    return {
        "success": True,
        "message": "Service added successfully",
        "warnings": validation["warnings"]
    }


@app.delete("/api/service/{service_name}")
async def delete_service(service_name: str):
    """Delete a service"""
    global SERVICES
    
    SERVICES = [s for s in SERVICES if s.name != service_name]
    if service_name in runtime_tracker:
        del runtime_tracker[service_name]
    
    save_services(SERVICES)
    
    await manager.broadcast({"type": "service_deleted", "service_name": service_name})
    
    return {"success": True, "message": f"Service '{service_name}' deleted"}


@app.post("/api/service/{service_name}/start")
async def start_service_endpoint(service_name: str):
    """Start a service"""
    svc = next((s for s in SERVICES if s.name == service_name), None)
    if not svc:
        return {"success": False, "message": "Service not found"}
    
    result = start_service(svc)
    
    await manager.broadcast({"type": "status_update", "data": get_all_statuses()})
    
    return result


@app.post("/api/service/{service_name}/stop")
async def stop_service_endpoint(service_name: str):
    """Stop a service"""
    svc = next((s for s in SERVICES if s.name == service_name), None)
    if not svc:
        return {"success": False, "message": "Service not found"}
    
    result = stop_service(svc)
    
    await manager.broadcast({"type": "status_update", "data": get_all_statuses()})
    
    return result


@app.post("/api/service/{service_name}/restart")
async def restart_service_endpoint(service_name: str):
    """Restart a service"""
    svc = next((s for s in SERVICES if s.name == service_name), None)
    if not svc:
        return {"success": False, "message": "Service not found"}
    
    stop_result = stop_service(svc)
    time.sleep(0.5)
    start_result = start_service(svc)
    
    runtime_tracker[svc.name].restart_count += 1
    
    await manager.broadcast({"type": "status_update", "data": get_all_statuses()})
    
    return {
        "success": start_result["success"],
        "message": f"Stopped: {stop_result.get('count', 0)} process(es), Started service"
    }


@app.post("/api/service/{service_name}/scan-ports")
async def scan_ports_endpoint(service_name: str):
    """Scan and update ports for a running service"""
    svc = next((s for s in SERVICES if s.name == service_name), None)
    if not svc:
        return {"success": False, "message": "Service not found"}
    
    detected_ports = scan_service_for_ports(svc)
    
    return {
        "success": True,
        "detected_ports": detected_ports,
        "configured_ports": svc.ports
    }


@app.post("/api/bulk/stop/{kind}")
async def stop_by_kind(kind: str):
    """Stop all services of a specific kind"""
    total = 0
    for svc in SERVICES:
        if svc.kind.lower() == kind.lower():
            result = stop_service(svc)
            total += result.get("count", 0)
    
    await manager.broadcast({"type": "status_update", "data": get_all_statuses()})
    
    return {"success": True, "message": f"Stopped {total} process(es)", "count": total}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time status updates"""
    await manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "status_update",
            "data": get_all_statuses()
        })
        
        await websocket.send_json({
            "type": "system_stats",
            "data": get_system_stats()
        })
        
        while True:
            update_interval = SETTINGS.update_interval_seconds
            await asyncio.sleep(update_interval)
            try:
                await websocket.send_json({
                    "type": "status_update",
                    "data": get_all_statuses()
                })
                
                await websocket.send_json({
                    "type": "system_stats",
                    "data": get_system_stats()
                })
            except:
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import sys
    
    # Determine host and port from command line or use defaults
    host = "0.0.0.0"
    port = 8765
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default: {port}")
    
    print("=" * 60)
    print("Tailscale Server Manager - Starting")
    print("=" * 60)
    print(f"Version: 2.0.0")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Services Loaded: {len(SERVICES)}")
    print(f"Local Access: http://localhost:{port}")
    print(f"Remote Access: http://[your-tailscale-ip]:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run with proper headless configuration
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        # Headless-friendly settings
        reload=False,
        workers=1
    )
