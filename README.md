# 🛡️ Tailscale Server Manager (Enhanced Edition)

A beautiful, powerful web interface for managing your Tailscale-powered services. Built with Python FastAPI backend and a sleek dark-themed HTML frontend inspired by modern design systems.

## ✨ Enhanced Features

- **🎨 Settings Menu**: Configure storage paths, monitoring intervals, port checks, and more
- **📊 System Stats**: Real-time CPU, memory, and disk usage monitoring
- **🔍 Detailed Service Cards**: Shows name, status, ports, uptime, errors, and connection details
- **➕ Add Service Wizard**: Easy interface to add new services with validation
- **🔌 Port Management**: Automatic port conflict detection and scanning
- **⚠️ Error Tracking**: Monitors and displays service errors with history
- **⏱️ Uptime Tracking**: See how long each service has been running
- **🔄 Enhanced Controls**: Per-service and bulk operations
- **📡 Live Updates**: Real-time WebSocket updates without page refreshes
- **🌐 Remote Access**: Host on your Tailnet and manage from anywhere
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

## 📋 Requirements

- Python 3.8 or higher
- Windows, Linux, or macOS
- Tailscale (for remote access)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn psutil
```

### 2. Configure Your Services

Edit `services_config.json` to define your services:

```json
{
  "name": "My Backend Service",
  "kind": "backend",
  "start_cmd": "python backend.py",
  "working_dir": "/path/to/backend",
  "match_keywords": ["python", "backend.py"],
  "ports": [8000],
  "api_url": "http://localhost:8000",
  "tailscale_url": "https://backend.mytailnet.ts.net",
  "description": "Main API server"
}
```

**New Configuration Options:**

- `ports`: List of ports the service uses (for monitoring and conflict detection)
- `api_url`: HTTP API endpoint for the service
- `tailscale_url`: Tailscale URL for remote access
- `description`: What the service does

### 3. Start the Server

```bash
python server.py
```

The server will start on `http://0.0.0.0:8765`

#### Tray Launcher (Windows)

If you want a visible presence with notifications, run `python tray_server.py` (or double-click `start_server.bat`). The tray launcher hosts the same FastAPI server but keeps it headless, provides a system tray menu (`Open Dashboard` + `Exit`), and notifies you if the `/health` endpoint goes unreachable.

### 4. Access the Interface

**Local Access:**
- Open your browser to `http://localhost:8765`

**Remote Access via Tailscale:**
- Get your Tailscale IP: `tailscale ip -4`
- Access from any device on your Tailnet: `http://[your-tailscale-ip]:8765`

## 🎯 Interface Overview

### Header
- **System Stats**: CPU, Memory, and Disk usage
- **Connection Status**: WebSocket connection indicator
- **Settings Button**: Access configuration panel
- **Add Service**: Launch service wizard
- **Refresh**: Manual status update

### Service Cards

Each service displays:
- **Name & Description**: Service identifier and purpose
- **Type Badge**: Backend/Frontend/Other classification
- **Status**: Running (green) or Stopped (gray) with live indicator
- **Uptime**: How long the service has been running
- **Ports**: All configured ports with active/inactive status
- **Connection Details**: API URLs and Tailscale URLs (clickable)
- **Process Info**: Number of processes and their PIDs
- **Errors**: Recent error messages (if any)
- **Restart Count**: Number of times restarted
- **Actions**: Start, Stop, and Restart buttons

## 🎨 Settings Menu

Click the **Settings** button to configure:

### Storage Paths
- Logs directory
- Data directory
- Backups directory

### Network & URLs
- Default Tailscale domain
- API base URL

### Performance
- Update interval (1-60 seconds)
- Stats retention period (days)

### Safety
- Port conflict checking
- Auto-restart on failure (planned)

## ➕ Add Service Wizard

Click **Add Service** to launch the wizard with automatic validation for:
- Name uniqueness
- Port conflicts  
- System compatibility

## 🔍 Port Management

- **Automatic Detection**: Scans running services
- **Conflict Detection**: Prevents port overlaps
- **Status Badges**: Shows port accessibility

## 📊 System Monitoring

Real-time dashboard:
- CPU Usage
- Memory (RAM)
- Disk Usage

## ⚠️ Error Tracking & ⏱️ Uptime

- Tracks errors per service
- Shows uptime duration
- Visual error indicators

See **FEATURES.md** for complete details on all enhancements.

## 🔧 Advanced Configuration

### Running as a Background Service

**Windows (using NSSM):**
```bash
# Install NSSM (Non-Sucking Service Manager)
# Download from https://nssm.cc/

nssm install TailscaleServerManager "C:\Python39\python.exe" "C:\path\to\server.py"
nssm set TailscaleServerManager AppDirectory "C:\path\to\tailscale_web_manager"
nssm start TailscaleServerManager
```

**Linux (using systemd):**
Create `/etc/systemd/system/tailscale-manager.service`:

```ini
[Unit]
Description=Tailscale Server Manager
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/tailscale_web_manager
ExecStart=/usr/bin/python3 /path/to/tailscale_web_manager/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tailscale-manager
sudo systemctl start tailscale-manager
```

### Custom Port

Edit `server.py` and change the port in the last line:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8765,  # Change this to your preferred port
    log_level="info"
)
```

### HTTPS/TLS

For HTTPS, use a reverse proxy like Caddy or nginx, or use Tailscale's built-in HTTPS:

```bash
tailscale serve https / http://localhost:8765
```

## 🐛 Troubleshooting

### Services Not Detected

If services show as "Stopped" but are running:
1. Check that `match_keywords` accurately identifies the process
2. Use Task Manager (Windows) or `ps aux` (Linux) to see exact process names
3. Add more specific keywords to avoid false negatives

### WebSocket Connection Issues

- Check that port 8765 isn't blocked by firewall
- Verify the server is running: `netstat -an | grep 8765`
- Check browser console for WebSocket errors (F12)

### Permission Issues

On Linux, you may need elevated privileges to manage some processes:
```bash
sudo python server.py
```

## 🎨 Customization

### Colors and Theme

Edit the CSS variables in `index.html` under the `:root` selector:

```css
:root {
    --bg-primary: #0a0f1e;      /* Main background */
    --accent-primary: #6366f1;   /* Primary accent color */
    --accent-secondary: #8b5cf6; /* Secondary accent */
    /* ... more variables */
}
```

### Auto-refresh Rate

Change the WebSocket update interval in `server.py`:

```python
await asyncio.sleep(5)  # Update every 5 seconds (change this)
```

## 📝 Example Service Configurations

### Python FastAPI Backend
```json
{
  "name": "FastAPI API Server",
  "kind": "backend",
  "start_cmd": "uvicorn main:app --host 0.0.0.0 --port 8000",
  "working_dir": "/home/user/api",
  "match_keywords": ["uvicorn", "main:app"]
}
```

### Node.js Server
```json
{
  "name": "Node.js Backend",
  "kind": "backend",
  "start_cmd": "node server.js",
  "working_dir": "/home/user/node-app",
  "match_keywords": ["node", "server.js"]
}
```

### Docker Container
```json
{
  "name": "Docker Redis",
  "kind": "backend",
  "start_cmd": "docker start redis-container",
  "working_dir": null,
  "match_keywords": ["redis-container"]
}
```

### Browser Frontend
```json
{
  "name": "Chrome Admin Panel",
  "kind": "frontend",
  "start_cmd": "start chrome --app=https://admin.myapp.com",
  "working_dir": null,
  "match_keywords": ["chrome", "admin.myapp.com"]
}
```

## 🔒 Security Notes

- This manager runs with the same privileges as your user account
- Services it starts inherit those privileges
- For production use, consider:
  - Running behind authentication (reverse proxy with auth)
  - Using Tailscale ACLs to restrict access
  - Running with minimal required privileges
  - Using environment variables for sensitive configs

## 📜 License

MIT License - feel free to modify and use as you wish!

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 💡 Tips

1. **Start services on boot**: Add the manager itself to startup/systemd
2. **Monitor logs**: Check `journalctl -u tailscale-manager -f` (Linux) or Event Viewer (Windows)
3. **Backup configs**: Keep `services_config.json` in version control
4. **Test changes**: Use the "Refresh" button after editing configs (restart manager to reload)
5. **Use Tailscale DNS**: Access via `http://server-name:8765` instead of IP

## 🎯 Future Ideas

- [ ] Service health checks
- [ ] Automatic restart on failure
- [ ] Resource usage graphs (CPU/Memory)
- [ ] Service logs viewer
- [ ] Email/Slack notifications
- [ ] Service dependency chains
- [ ] Scheduled start/stop times
- [ ] Multi-server support
- [ ] Mobile app (PWA)

---

Made with ❤️ for Tailscale enthusiasts
