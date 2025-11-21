# 🌟 Enhanced Features

## Overview

Your Tailscale Server Manager has been completely rebuilt with powerful new features for production server management!

## ✨ New Features

### 1. ⚙️ Comprehensive Settings Menu

Access via the **Settings** button in the header. Configure:

#### Storage Paths
- **Logs Directory**: Where service logs are stored
- **Data Directory**: Application data location
- **Backups Directory**: Backup file location

#### Network & URLs
- **Default Tailscale Domain**: Your tailnet domain (e.g., `mytailnet.ts.net`)
- **API Base URL**: The manager's own API URL

#### Performance & Monitoring
- **Update Interval**: How often to refresh status (1-60 seconds)
- **Stats Retention**: How long to keep historical data (1-365 days)

#### Safety & Validation
- **Check Port Conflicts**: Validate ports when adding services
- **Auto-restart on Failure**: Automatically restart crashed services (coming soon)

### 2. 📊 System Statistics Dashboard

Real-time monitoring of:
- **CPU Usage**: Current system CPU percentage
- **Memory**: RAM usage with GB display
- **Disk Usage**: Storage utilization

Updates automatically via WebSocket every few seconds.

### 3. 🔍 Enhanced Service Cards

Each service now displays:

#### Basic Info
- **Name**: Service identifier
- **Description**: What the service does
- **Type Badge**: Backend/Frontend/Other
- **Status Indicator**: Running (green) or Stopped (gray)

#### Connection Details
- **Ports**: All configured ports with live status
  - Green badge = port is active and accessible
  - Gray badge = port is not in use
- **API URL**: Clickable link to service API
- **Tailscale URL**: Clickable link to Tailnet access

#### Runtime Information
- **Uptime**: How long service has been running
  - Format: `Xd Xh Xm` or `Xh Xm` or `Xm Xs`
- **Process Count**: Number of running processes
- **PIDs**: Actual process IDs
- **Restart Count**: How many times restarted

#### Error Tracking
- **Last Error**: Most recent error message (if any)
- **Error History**: Up to 10 recent errors tracked
- Services with errors show with red border

### 4. ➕ Add Service Wizard

Click **Add Service** to launch the wizard. Features:

#### Required Fields
- **Service Name**: Unique identifier
- **Type**: Backend, Frontend, or Other
- **Start Command**: How to launch the service
- **Match Keywords**: How to find it in process list

#### Optional Fields
- **Working Directory**: Where to run the command
- **Ports**: Comma-separated list of ports (e.g., `8000, 8001`)
- **API URL**: Service API endpoint
- **Tailscale URL**: Tailnet access URL
- **Description**: What the service does

#### Automatic Validation
Before adding, the system checks:
- ✅ Name uniqueness
- ✅ Port conflicts with existing services
- ✅ Current port availability
- ⚠️ Warnings about potential issues

### 5. 🔍 Port Conflict Detection

**Check Port Conflicts** button scans all services for:
- Services using the same port
- Ports already in use by other processes
- Potential accessibility issues

When adding a service, automatic validation prevents conflicts.

### 6. 📡 Port Scanning

For running services, the manager can:
- **Auto-detect** actual ports in use
- **Compare** configured vs. actual ports
- **Validate** port accessibility

Access via API: `POST /api/service/{name}/scan-ports`

### 7. 🎨 Visual Enhancements

#### Modern Dark Theme
- ChatOps Neon-inspired design
- Purple/blue gradient accents
- Smooth animations
- Hover effects on cards

#### Status Indicators
- **Green dot**: Connected/Running
- **Red dot**: Disconnected/Stopped
- **Pulsing animation**: Active status

#### Toast Notifications
- **Success**: Green border, checkmark
- **Error**: Red border, X mark
- **Warning**: Orange border, warning sign
- Auto-dismiss after 3 seconds

### 8. 🔄 Enhanced Control Actions

#### Per-Service Actions
- **Start**: Launch the service
- **Stop**: Gracefully terminate (or force kill)
- **Restart**: Stop then start with tracking

#### Bulk Actions
- **Stop All Backends**: Stops all backend services
- **Stop All Frontends**: Stops all frontend services
- **Stop All Other**: Stops other service types
- Confirmation prompts for safety

### 9. 📈 Runtime Tracking

The manager tracks for each service:
- **Start time**: When last started
- **Uptime calculation**: Live uptime display
- **Restart count**: Number of restarts
- **Error history**: Recent error messages
- **Process details**: CPU, memory, PIDs

### 10. 🌐 API Enhancements

New endpoints:

#### Settings Management
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

#### Service Management
- `POST /api/service/add` - Add new service
- `DELETE /api/service/{name}` - Remove service
- `POST /api/service/{name}/scan-ports` - Scan ports

#### System Information
- `GET /api/stats` - Get system statistics
- `GET /api/port-conflicts` - Check port conflicts

### 11. 🔒 Safety Features

#### Validation
- Name uniqueness checks
- Port conflict prevention
- Required field validation
- Keyword validation

#### Confirmation Prompts
- Bulk stop operations
- Port conflict warnings
- Destructive actions

#### Error Handling
- Graceful degradation
- Error message display
- Auto-reconnect on disconnect

### 12. 📱 Responsive Design

Works perfectly on:
- **Desktop**: Full feature set
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly controls

Adaptive grid layouts adjust to screen size.

## 🎯 Usage Examples

### Adding a Backend Service

1. Click **Add Service**
2. Fill in details:
   - Name: "PostgreSQL Database"
   - Type: Backend
   - Command: `pg_ctl start`
   - Keywords: `postgres`
   - Ports: `5432`
   - API: `postgresql://localhost:5432`
3. Click **Add Service**
4. System validates and confirms

### Monitoring Service Health

Each card shows:
- ✅ Status (running/stopped)
- ⏱️ Uptime (2d 5h 23m)
- 🔌 Ports (5432 - active)
- 🔄 Restarts (3)
- ⚠️ Errors (if any)

### Configuring Settings

1. Click **Settings**
2. Update paths:
   - Logs: `/var/log/myapp`
   - Data: `/data/myapp`
3. Set update interval: `10` seconds
4. Enable port conflict checking
5. Save

### Checking Port Conflicts

1. Click **Check Port Conflicts**
2. Review any conflicts found
3. Fix conflicts in service configs
4. Re-check to confirm

## 🔄 WebSocket Updates

Real-time updates via WebSocket:
- Service status every N seconds
- System stats every N seconds
- Immediate updates after actions
- Auto-reconnect on disconnect

No page refreshes needed!

## 🎨 Customization

All colors and styles are CSS variables in `:root`.

To customize:
1. Open `index.html`
2. Find `:root` section
3. Modify colors:
   ```css
   --accent-primary: #6366f1;  /* Your color */
   --bg-primary: #0a0f1e;      /* Your background */
   ```

## 📝 Configuration Files

### services_config.json
```json
{
  "name": "My Service",
  "kind": "backend",
  "start_cmd": "python app.py",
  "working_dir": "/path/to/app",
  "match_keywords": ["python", "app.py"],
  "ports": [8000, 8001],
  "api_url": "http://localhost:8000",
  "tailscale_url": "https://app.mytailnet.ts.net",
  "description": "My awesome service"
}
```

### settings.json
```json
{
  "storage_paths": {
    "logs": "./logs",
    "data": "./data",
    "backups": "./backups"
  },
  "check_port_conflicts": true,
  "update_interval_seconds": 5,
  "stats_retention_days": 30
}
```

## 🚀 Performance

- **WebSocket**: Minimal bandwidth, instant updates
- **Efficient scanning**: Only checks relevant processes
- **Cached data**: Reduces API calls
- **Lazy loading**: Fast initial page load

## 🛡️ Security Notes

- Settings stored locally (not cloud)
- No external dependencies (except Tailscale)
- Process control limited to user permissions
- Configurable validation rules

## 📚 API Documentation

See `ARCHITECTURE.md` for complete API reference.

## 🎉 What's Next?

Planned features:
- [ ] Scheduled tasks (cron-like)
- [ ] Email/Slack notifications
- [ ] Service health checks
- [ ] Log viewer
- [ ] Resource graphs
- [ ] Service dependencies
- [ ] Multi-server support

## 💡 Tips & Tricks

1. **Use descriptive names** for easy identification
2. **Add descriptions** to remember what services do
3. **Configure ports** for better monitoring
4. **Check conflicts** before deploying
5. **Monitor uptime** to catch issues early
6. **Review errors** in service cards
7. **Use Tailscale URLs** for remote access
8. **Set update interval** based on your needs
9. **Bookmark the page** for quick access
10. **Check system stats** for resource planning

---

**Enjoy your enhanced server manager!** 🎉
