# System Architecture

```
### Current Design
_Original single-node process orchestration, now extended with enrollment tracking._

### Implemented Enhancements
- Multi-server enrollment (remote nodes register & send heartbeats)
- Aggregated fleet metrics (CPU / Memory / Disk averages)
- Scheduled tasks CRUD UI (service start/stop/restart definitions)

### Future Expansion Ideas
- Service health checks
- Resource monitoring graphs
- Log aggregation
- Alert system
- Service dependencies

## Multi-Server Enrollment & Metrics
Remote nodes register once via `POST /api/servers/register` receiving a UUID. They periodically send heartbeats (`POST /api/servers/{id}/heartbeat`) containing lightweight metrics (cpu_percent, memory_percent, disk_percent, etc.). The manager stores a bounded rolling history per node (max 200 samples) and exposes:

- `GET /api/metrics/summary` – fleet averages (CPU / Memory / Disk)
- `GET /api/metrics/{server_id}` – per-node time series

`ServerNode` fields: id, name, host, ip, tags[], services[], metadata{}, last_seen (ISO8601), last_metrics{}.

Persistence: static node fields in `servers.json`; metrics snapshots history kept in memory (eviction after 200 samples).

## Scheduled Tasks (Cron-like)
CRUD storage of desired service actions using standard 5-field cron syntax. Stored inline in `settings.json` (`scheduled_tasks`). Execution loop not implemented yet.

Endpoints: `GET /api/tasks`, `POST /api/tasks`, `PUT /api/tasks/{name}`, `DELETE /api/tasks/{name}`.

Model: name, cron_expression, action(start|stop|restart), service_name, enabled.

UI: Form for creation + list with enable/disable + delete actions.

Planned Executor (future): minute loop parses enabled tasks, matches current time → dispatch service action → log result & retries.

## Aggregation Function Fix
`aggregate_server_metrics()` moved to top-level (it was previously nested inside `get_system_stats()` causing NameError for `/api/metrics/summary`).

## Next Enhancements
1. WebSocket broadcast on task changes
2. Auth tokens for server enrollment & task mutations
3. Historical charts (CPU / Memory / Disk trends)
4. Remote command execution (orchestrate services on other nodes)
5. Service dependency graph & rolling restarts
6. Structured logging + tail endpoint

---

**Built for: Tailscale-powered server management**  
**Optimized for: Remote access and ease of use**  
**Designed with: Modern web best practices**
                          All Connected Clients
```

### 3. Status Monitoring

```
Server → psutil → Process List → Match Keywords → Service Status
   ↓
WebSocket Broadcast (every 5s)
   ↓
Update UI
```

## File Structure

```
tailscale_web_manager/
├── server.py              # Backend server
├── index.html             # Frontend interface
├── services_config.json   # Service definitions
├── requirements.txt       # Python dependencies
├── start_server.bat       # Windows startup
├── start_server.sh        # Linux/Mac startup
├── README.md              # Full documentation
├── QUICKSTART.md          # Fast setup guide
├── START_HERE.md          # Getting started
└── PREVIEW.html           # Visual demo
```

## Technology Stack

### Backend

- **FastAPI**: Modern Python web framework
- **uvicorn**: ASGI server
- **psutil**: Process management
- **WebSockets**: Real-time communication

### Frontend

- **Vanilla JavaScript**: No frameworks needed
- **CSS3**: Modern styling with gradients
- **WebSocket API**: Real-time updates
- **Fetch API**: REST calls

### Design

- **Dark theme**: ChatOps Neon inspired
- **Responsive**: Works on all devices
- **Animations**: Smooth transitions
- **Toast notifications**: User feedback

## Security Model

```
┌─────────────────────────────────────┐
│  Tailscale Network (encrypted)      │
│  ├─ Device Authentication           │
│  ├─ End-to-end encryption           │
│  └─ ACL-based access control        │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Server (runs as your user)         │
│  ├─ Inherits user permissions       │
│  ├─ Process control via psutil      │
│  └─ Config file validation          │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Managed Services                   │
│  └─ Run with server's privileges    │
└─────────────────────────────────────┘
```

## Deployment Options

### Option 1: Development

```bash
python server.py
# Access: http://localhost:8765
```

### Option 2: Tailscale Access

```bash
python server.py
# Access: http://[tailscale-ip]:8765
```

### Option 3: System Service

```bash
# Linux systemd or Windows NSSM
# Starts automatically on boot
# Access: http://[tailscale-ip]:8765
```

### Option 4: HTTPS via Tailscale

```bash
tailscale serve https / http://localhost:8765
# Access: https://[machine-name].[tailnet].ts.net
```

## Performance Characteristics

- **Startup time**: < 1 second
- **Memory usage**: ~50MB (Python + FastAPI)
- **CPU usage**: < 1% idle, < 5% during operations
- **WebSocket latency**: < 10ms on local network
- **Update frequency**: 5 seconds (configurable)
- **Concurrent connections**: Unlimited (practical: 100+)

## Scalability Notes

### Current Design

- Single server instance
- Manages processes on same machine
- Good for: 10-50 services

### Future Expansion Ideas

### Future Expansion Ideas

- Service health checks
- Resource monitoring graphs
- Log aggregation
- Alert system
- Service dependencies

## Multi-Server Enrollment & Metrics

Remote nodes register once via `POST /api/servers/register` receiving a UUID. They periodically send heartbeats (`POST /api/servers/{id}/heartbeat`) containing lightweight metrics (cpu_percent, memory_percent, disk_percent, etc.). The manager stores a bounded rolling history per node (max 200 samples) and exposes:

- `GET /api/metrics/summary` for fleet averages (CPU / Memory / Disk)
- `GET /api/metrics/{server_id}` for per-node time series

Data structure (`ServerNode`): id, name, host, ip, tags[], services[], metadata{}, last_seen (ISO8601), last_metrics{}.

Persistence: static node fields in `servers.json`; metrics history kept in memory for fast access and eviction.

Future: add authentication tokens, Prometheus exporter, remote command execution, and long-term metrics storage.

## Scheduled Tasks (Cron-like)

CRUD-only scheduling layer allowing operators to define desired service actions using standard 5-field cron syntax. Stored inline in `settings.json` under `scheduled_tasks`.

Endpoints: `GET /api/tasks`, `POST /api/tasks`, `PUT /api/tasks/{name}`, `DELETE /api/tasks/{name}`

Model: name, cron_expression, action(start|stop|restart), service_name, enabled.

Frontend Tasks Tab: Form (create), list (cards), enable/disable toggle (PUT), delete (DELETE). Validation currently minimal; add robust parser (e.g. croniter) + timezone awareness later.

Planned Executor (future): minute loop parses enabled tasks, matching current time → dispatch service action → log result & retries.

## Aggregation Function Fix

`aggregate_server_metrics()` moved to top-level (was accidentally indented inside `get_system_stats()`) preventing runtime NameError during `/api/metrics/summary` calls.

## Next Enhancements

1. WebSocket broadcast on task changes
2. Auth tokens for server enrollment + task mutations
3. Historical charts (CPU / Memory / Disk trends)
4. Remote command execution (start/stop services on other nodes)
5. Service dependency graph & orchestrated rolling restarts
6. Structured logging + log tail endpoint

---

**Built for: Tailscale-powered server management**  
**Optimized for: Remote access and ease of use**  
**Designed with: Modern web best practices**
\n+## Multi-Server Enrollment & Metrics
\n+Remote nodes register once via `POST /api/servers/register` receiving a UUID. They periodically send heartbeats (`POST /api/servers/{id}/heartbeat`) containing lightweight metrics (cpu_percent, memory_percent, disk_percent, etc.). The manager stores a bounded rolling history per node (max 200 samples) and exposes:\n\n- `GET /api/metrics/summary` for fleet averages (CPU / Memory / Disk).\n- `GET /api/metrics/{server_id}` for per-node time series.\n\nData structure (`ServerNode`): id, name, host, ip, tags[], services[], metadata{}, last_seen (ISO8601), last_metrics{}.
\n+Persistence: static node fields in `servers.json`; metrics history kept in memory for fast access and eviction.\n\nFuture: add authentication tokens, Prometheus exporter, remote command execution, and long-term metrics storage.
\n+## Scheduled Tasks (Cron-like)
\n+CRUD-only scheduling layer allowing operators to define desired service actions using standard 5-field cron syntax. Stored inline in `settings.json` under `scheduled_tasks`.
\n+Endpoints: `GET /api/tasks`, `POST /api/tasks`, `PUT /api/tasks/{name}`, `DELETE /api/tasks/{name}`.\n\nModel: name, cron_expression, action(start|stop|restart), service_name, enabled.
\n+Frontend Tasks Tab: Form (create), list (cards), enable/disable toggle (PUT), delete (DELETE).\nValidation currently minimal; add robust parser (e.g. croniter) + timezone awareness later.
\n+Planned Executor: minute loop parses enabled tasks, matching current time → dispatch service action → log result & retries.
\n+## Aggregation Function Fix
\n+`aggregate_server_metrics()` moved to top-level (was accidentally indented inside `get_system_stats()`) preventing runtime NameError during `/api/metrics/summary` calls.
\n+## Next Enhancements

1. WebSocket broadcast on task changes.\n2. Auth tokens for server enrollment + task mutations.\n3. Historical charts (CPU / Memory / Disk trends).\n4. Remote command execution (start/stop services on other nodes).\n5. Service dependency graph & orchestrated rolling restarts.\n6. Structured logging + log tail endpoint.
