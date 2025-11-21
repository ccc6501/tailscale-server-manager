# 🖥️ Headless Operation Guide

## Running the Server Without a Desktop

This guide covers running Tailscale Server Manager on a headless server (no GUI/desktop environment).

## Quick Start for Headless

### 1. Install and Verify
```bash
# Run setup script
python3 setup.py

# This will check:
# - Python version
# - Dependencies
# - Required files
# - Port availability
# - Create config files
```

### 2. Start the Server
```bash
# Direct (for testing)
python3 server.py

# Or use the startup script
./start_server.sh
```

### 3. Test Connection
```bash
# From the same machine
python3 test_connection.py

# Or manually
curl http://localhost:8765/health
```

### 4. Access from Another Machine
```bash
# Get your Tailscale IP
tailscale ip -4

# Access from any device on your Tailnet
http://[your-tailscale-ip]:8765
```

## Production Deployment Options

### Option 1: systemd (Recommended for Linux)

**Best for:** Production servers, automatic startup on boot

```bash
# 1. Edit the service file
nano tailscale-manager.service

# 2. Update these values:
#    User=YOUR_USERNAME
#    WorkingDirectory=/full/path/to/tailscale_web_manager
#    ExecStart=/usr/bin/python3 /full/path/to/tailscale_web_manager/server.py

# 3. Copy to systemd
sudo cp tailscale-manager.service /etc/systemd/system/

# 4. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable tailscale-manager
sudo systemctl start tailscale-manager

# 5. Check status
sudo systemctl status tailscale-manager

# 6. View logs
sudo journalctl -u tailscale-manager -f
```

**Common systemd Commands:**
```bash
# Start
sudo systemctl start tailscale-manager

# Stop
sudo systemctl stop tailscale-manager

# Restart
sudo systemctl restart tailscale-manager

# Status
sudo systemctl status tailscale-manager

# Logs (live)
sudo journalctl -u tailscale-manager -f

# Logs (last 50 lines)
sudo journalctl -u tailscale-manager -n 50

# Disable auto-start
sudo systemctl disable tailscale-manager

# Enable auto-start
sudo systemctl enable tailscale-manager
```

### Option 2: screen (Good for SSH Sessions)

**Best for:** Development, SSH sessions, temporary deployments

```bash
# 1. Start a screen session
screen -S tailscale-manager

# 2. Run the server
python3 server.py

# 3. Detach (keep server running)
# Press: Ctrl+A, then D

# 4. Reattach later
screen -r tailscale-manager

# 5. List all screens
screen -ls

# 6. Kill a screen
screen -X -S tailscale-manager quit
```

**Screen Cheat Sheet:**
- `Ctrl+A, D` - Detach
- `Ctrl+A, K` - Kill window
- `Ctrl+A, C` - Create new window
- `Ctrl+A, N` - Next window
- `Ctrl+A, ?` - Help

### Option 3: tmux (Alternative to screen)

**Best for:** Power users, advanced terminal multiplexing

```bash
# 1. Start a tmux session
tmux new -s tailscale-manager

# 2. Run the server
python3 server.py

# 3. Detach (keep server running)
# Press: Ctrl+B, then D

# 4. Reattach later
tmux attach -t tailscale-manager

# 5. List sessions
tmux ls

# 6. Kill session
tmux kill-session -t tailscale-manager
```

### Option 4: nohup (Simplest)

**Best for:** Quick deployments, simple setups

```bash
# 1. Start with nohup
nohup python3 server.py > server.log 2>&1 &

# 2. Get the process ID
echo $!

# 3. Check if running
ps aux | grep server.py

# 4. View logs
tail -f server.log

# 5. Stop the server
pkill -f server.py
# Or
kill [PID]
```

### Option 5: Docker (Containerized)

**Best for:** Containerized environments, multi-server deployments

```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["python", "server.py"]
```

```bash
# Build
docker build -t tailscale-manager .

# Run
docker run -d \
  --name tailscale-manager \
  -p 8765:8765 \
  -v $(pwd)/services_config.json:/app/services_config.json \
  -v $(pwd)/settings.json:/app/settings.json \
  --restart unless-stopped \
  tailscale-manager

# View logs
docker logs -f tailscale-manager

# Stop
docker stop tailscale-manager

# Start
docker start tailscale-manager
```

### Option 6: Windows Service (NSSM)

**Best for:** Windows servers

```bash
# 1. Download NSSM from https://nssm.cc/

# 2. Install service
nssm install TailscaleManager "C:\Python3\python.exe" "C:\path\to\server.py"

# 3. Set working directory
nssm set TailscaleManager AppDirectory "C:\path\to\tailscale_web_manager"

# 4. Set restart options
nssm set TailscaleManager AppThrottle 1500
nssm set TailscaleManager AppStopMethodSkip 0

# 5. Start service
nssm start TailscaleManager

# 6. Check status
nssm status TailscaleManager

# 7. View logs (in Event Viewer)
# Or configure log files:
nssm set TailscaleManager AppStdout "C:\logs\tailscale-manager.log"
nssm set TailscaleManager AppStderr "C:\logs\tailscale-manager-error.log"
```

## Accessing the Headless Server

### Via Tailscale (Recommended)

```bash
# 1. Get your server's Tailscale IP
tailscale ip -4

# 2. Access from any device on your Tailnet
http://[tailscale-ip]:8765

# 3. Or use Tailscale machine name
http://[machine-name].[tailnet].ts.net:8765
```

### Via Tailscale HTTPS

```bash
# Enable Tailscale serve
tailscale serve https / http://localhost:8765

# Access via HTTPS (no port needed)
https://[machine-name].[tailnet].ts.net
```

### Via SSH Tunnel (Temporary)

```bash
# From your local machine
ssh -L 8765:localhost:8765 user@server

# Then access
http://localhost:8765
```

### Via Reverse Proxy (Advanced)

**nginx example:**
```nginx
server {
    listen 80;
    server_name manager.example.com;
    
    location / {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring Headless Server

### Check if Running
```bash
# Check process
ps aux | grep server.py

# Check port
netstat -tuln | grep 8765

# Test endpoint
curl http://localhost:8765/health
```

### View Logs

**systemd:**
```bash
sudo journalctl -u tailscale-manager -f
```

**nohup:**
```bash
tail -f server.log
```

**screen/tmux:**
```bash
screen -r tailscale-manager  # or tmux attach
```

**Docker:**
```bash
docker logs -f tailscale-manager
```

### Resource Usage
```bash
# Check CPU and memory
top -p $(pgrep -f server.py)

# Or
ps aux | grep server.py
```

## Automatic Restart on Failure

### systemd (Built-in)
Already configured in the service file:
```ini
Restart=always
RestartSec=10
```

### Supervisor
```ini
[program:tailscale-manager]
command=/usr/bin/python3 /path/to/server.py
directory=/path/to/tailscale_web_manager
user=YOUR_USER
autostart=true
autorestart=true
stderr_logfile=/var/log/tailscale-manager.err.log
stdout_logfile=/var/log/tailscale-manager.out.log
```

### Cron Watchdog
```bash
# Add to crontab (crontab -e)
*/5 * * * * pgrep -f server.py || cd /path/to/tailscale_web_manager && python3 server.py &
```

## Security Best Practices

### 1. Don't Run as Root
```bash
# Create a dedicated user
sudo useradd -r -s /bin/false tailscale-manager

# Update service file
User=tailscale-manager
```

### 2. Use Tailscale ACLs
Restrict access in your Tailscale ACLs:
```json
{
  "acls": [
    {
      "action": "accept",
      "users": ["you@example.com"],
      "ports": ["server:8765"]
    }
  ]
}
```

### 3. Firewall Configuration
```bash
# Only allow from Tailscale interface
sudo ufw allow in on tailscale0 to any port 8765

# Or only allow localhost (use Tailscale serve)
sudo ufw allow from 127.0.0.1 to any port 8765
```

### 4. HTTPS Only
```bash
# Use Tailscale serve for HTTPS
tailscale serve https / http://localhost:8765
```

## Troubleshooting Headless

### Server Won't Start
```bash
# Check if port is available
sudo netstat -tuln | grep 8765

# Check if files exist
ls -la server.py index.html

# Try running directly to see errors
python3 server.py
```

### Can't Connect Remotely
```bash
# Verify server is listening on 0.0.0.0
sudo netstat -tuln | grep 8765
# Should show: 0.0.0.0:8765 (not 127.0.0.1:8765)

# Check firewall
sudo ufw status

# Test from server itself
curl http://localhost:8765/health
```

### WebSocket Issues
```bash
# Check if WebSocket is accessible
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8765/ws
```

### High Resource Usage
```bash
# Check resource usage
top -p $(pgrep -f server.py)

# Increase update interval in Settings
# Settings → Update Interval → 10-30 seconds

# Or restart the service
sudo systemctl restart tailscale-manager
```

## Maintenance

### Update Server
```bash
# Stop the server
sudo systemctl stop tailscale-manager

# Backup configs
cp services_config.json services_config.backup
cp settings.json settings.backup

# Update files (server.py, index.html)

# Restart
sudo systemctl start tailscale-manager

# Check logs
sudo journalctl -u tailscale-manager -f
```

### Backup Data
```bash
# Backup configs
tar -czf backup-$(date +%Y%m%d).tar.gz \
  services_config.json \
  settings.json \
  logs/

# Copy to safe location
scp backup-*.tar.gz user@backup-server:/backups/
```

### Rotate Logs
```bash
# For systemd (automatic via journald)
sudo journalctl --vacuum-time=30d

# For manual logs
find /var/log/tailscale-manager-*.log -mtime +30 -delete
```

## Performance Optimization

### Reduce Update Frequency
Settings → Update Interval → 10-30 seconds

### Run on Different Port
```bash
# Use faster port (if 8765 is slow)
python3 server.py 3000
```

### Limit Resource Usage (systemd)
```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
```

## Quick Commands Reference

```bash
# Setup
python3 setup.py

# Test connection
python3 test_connection.py

# Start (foreground)
python3 server.py

# Start (background with nohup)
nohup python3 server.py > server.log 2>&1 &

# Start (screen)
screen -dmS tailscale-manager python3 server.py

# Start (systemd)
sudo systemctl start tailscale-manager

# Check status
curl http://localhost:8765/health

# View logs (systemd)
sudo journalctl -u tailscale-manager -f

# View logs (nohup)
tail -f server.log

# Stop (nohup)
pkill -f server.py

# Stop (systemd)
sudo systemctl stop tailscale-manager

# Get Tailscale IP
tailscale ip -4
```

## Conclusion

Your server is now running headless! 🎉

For the best experience:
1. Use **systemd** for production
2. Use **screen/tmux** for development
3. Access via **Tailscale** for security
4. Monitor with **journalctl** or logs
5. Set up **auto-restart** for reliability

**Need help?** Check TROUBLESHOOTING.md or run `python3 test_connection.py`
