# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue: UI Doesn't Connect to Server

#### Symptoms
- Blank page when accessing http://localhost:8765
- "Connection refused" error
- WebSocket connection fails
- Page loads but shows "Disconnected"

#### Solutions

##### 1. Verify Server is Running
```bash
# Check if process is running
ps aux | grep server.py

# Or on Windows
tasklist | findstr python
```

If not running, start it:
```bash
python server.py
```

##### 2. Test Port Accessibility
```bash
# Run the connection test script
python test_connection.py

# Or manually check the port
curl http://localhost:8765/health

# Or use netcat
nc -zv localhost 8765
```

##### 3. Check Firewall
**Linux:**
```bash
# Check if port is open
sudo ufw status
sudo ufw allow 8765

# Or with firewalld
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=8765/tcp --permanent
sudo firewall-cmd --reload
```

**Windows:**
```powershell
# Add firewall rule
netsh advfirewall firewall add rule name="Tailscale Manager" dir=in action=allow protocol=TCP localport=8765
```

##### 4. Check for Port Conflicts
```bash
# Linux/Mac
netstat -tuln | grep 8765
lsof -i :8765

# Windows
netstat -ano | findstr 8765
```

If port is in use by another process:
- Stop that process, or
- Run server on different port: `python server.py 8766`

##### 5. Verify Files are Present
```bash
# Check all required files exist
ls -la

# You should see:
# - server.py
# - index.html
# - services_config.json
# - settings.json
```

##### 6. Check Server Logs
Look at the console output when starting the server:
```
🛡️  Tailscale Server Manager - Starting
Host: 0.0.0.0
Port: 8765
Services Loaded: 2
Local Access: http://localhost:8765
```

If you see errors, they'll appear here.

##### 7. Test API Directly
```bash
# Test health endpoint
curl http://localhost:8765/health

# Should return:
# {"status":"healthy","version":"2.0.0","services_count":2}

# Test API
curl http://localhost:8765/api/status
```

If API works but UI doesn't, check:
- Browser console (F12) for JavaScript errors
- index.html is in the same directory as server.py

##### 8. Browser Issues
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private mode
- Try a different browser
- Check browser console (F12) for errors

---

### Issue: Server Won't Run Headless

#### Symptoms
- Server stops when you close terminal
- Server won't start on boot
- Gets killed after SSH disconnect

#### Solutions

##### Option 1: Use nohup (Simple)
```bash
nohup python3 server.py > server.log 2>&1 &
```

To stop:
```bash
ps aux | grep server.py
kill [PID]
```

##### Option 2: Use screen (Recommended for SSH)
```bash
# Start a screen session
screen -S tailscale-manager

# Run the server
python3 server.py

# Detach: Press Ctrl+A then D
# Reattach later:
screen -r tailscale-manager
```

##### Option 3: Use systemd (Best for Linux)
```bash
# Copy service file
sudo cp tailscale-manager.service /etc/systemd/system/

# Edit the file
sudo nano /etc/systemd/system/tailscale-manager.service

# Update these lines:
# User=YOUR_USERNAME
# WorkingDirectory=/path/to/tailscale_web_manager
# ExecStart=/usr/bin/python3 /path/to/tailscale_web_manager/server.py

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable tailscale-manager
sudo systemctl start tailscale-manager

# Check status
sudo systemctl status tailscale-manager

# View logs
sudo journalctl -u tailscale-manager -f
```

##### Option 4: Use pm2 (Node.js)
If you have Node.js installed:
```bash
npm install -g pm2
pm2 start server.py --interpreter python3 --name tailscale-manager
pm2 startup
pm2 save
```

##### Option 5: Use Windows Service (NSSM)
```bash
# Download NSSM from https://nssm.cc/

# Install service
nssm install TailscaleManager "C:\Python3\python.exe" "C:\path\to\server.py"
nssm set TailscaleManager AppDirectory "C:\path\to\tailscale_web_manager"
nssm start TailscaleManager

# Check status
nssm status TailscaleManager
```

---

### Issue: Can't Access via Tailscale

#### Symptoms
- Works on localhost but not from other devices
- Tailscale URL doesn't connect
- Connection timeout from remote devices

#### Solutions

##### 1. Get Your Tailscale IP
```bash
tailscale ip -4
```

##### 2. Verify Tailscale is Running
```bash
# Linux/Mac
tailscale status

# Windows
tailscale status
```

##### 3. Check Server is Bound to 0.0.0.0
Server must listen on all interfaces (not just localhost).

In server.py, verify:
```python
host="0.0.0.0"  # ✅ Correct - accessible from network
# NOT
host="127.0.0.1"  # ❌ Wrong - localhost only
```

##### 4. Test from Remote Device
From another device on your Tailnet:
```bash
# Replace with your actual Tailscale IP
curl http://100.x.x.x:8765/health
```

##### 5. Check Tailscale ACLs
Your Tailscale ACL might be blocking the port. Check:
https://login.tailscale.com/admin/acls

##### 6. Use Tailscale Serve (HTTPS)
```bash
# Expose via Tailscale HTTPS
tailscale serve https / http://localhost:8765

# Access via
https://[machine-name].[tailnet].ts.net
```

---

### Issue: WebSocket Connection Fails

#### Symptoms
- Connection status shows "Disconnected"
- No real-time updates
- Have to refresh manually

#### Solutions

##### 1. Check Browser Console
Press F12 and look for WebSocket errors:
```
WebSocket connection to 'ws://localhost:8765/ws' failed
```

##### 2. Verify WebSocket Endpoint
```bash
# Using websocat (install from https://github.com/vi/websocat)
websocat ws://localhost:8765/ws

# Or use an online WebSocket tester
```

##### 3. Check for Proxy/Firewall
Some proxies and firewalls block WebSocket connections.

##### 4. Test with Different Protocol
If using HTTPS, WebSocket must be WSS:
- HTTP → WS (ws://...)
- HTTPS → WSS (wss://...)

---

### Issue: Port Conflicts

#### Symptoms
- "Address already in use" error
- Server won't start
- Port conflict warnings

#### Solutions

##### 1. Find What's Using the Port
```bash
# Linux/Mac
sudo lsof -i :8765

# Windows
netstat -ano | findstr 8765
```

##### 2. Stop Conflicting Process
```bash
# Linux/Mac
kill [PID]

# Windows
taskkill /PID [PID] /F
```

##### 3. Use Different Port
```bash
python server.py 8766
```

##### 4. Use Port Conflict Checker
In the UI, click "Check Port Conflicts" button.

---

### Issue: Services Not Detected

#### Symptoms
- Service shows as "Stopped" but is actually running
- PIDs don't match
- Can't control running services

#### Solutions

##### 1. Check Match Keywords
Keywords must appear in the process command line.

View actual process:
```bash
# Linux/Mac
ps aux | grep [your-service]

# Windows
tasklist /V | findstr [your-service]
```

Update `match_keywords` to match exactly what you see.

##### 2. Make Keywords More Specific
```json
{
  "match_keywords": ["python", "app.py"]
}
```

Be specific enough to identify the right process but not too specific.

##### 3. Check Working Directory
If service can't start, wrong working directory might be the issue:
```json
{
  "working_dir": "/absolute/path/to/service"
}
```

##### 4. Test Start Command Manually
Run the start command yourself:
```bash
cd /path/to/service
python app.py  # or whatever your start_cmd is
```

If it doesn't work manually, fix the command first.

---

### Issue: Permissions Errors

#### Symptoms
- "Permission denied" errors
- Can't stop services
- Can't access files

#### Solutions

##### 1. Run with Appropriate Permissions
```bash
# If managing system services, may need sudo
sudo python3 server.py

# Better: run as service user
sudo -u serviceuser python3 server.py
```

##### 2. Fix File Permissions
```bash
# Make scripts executable
chmod +x start_server.sh
chmod +x test_connection.py

# Fix directory permissions
chmod 755 /path/to/tailscale_web_manager

# Fix file permissions
chmod 644 *.json *.py *.html
```

##### 3. Check Service User Permissions
User running the manager must have permission to:
- Read service configs
- Execute start commands
- Send signals to processes (for stop/restart)

---

### Issue: High CPU/Memory Usage

#### Symptoms
- Server uses too much CPU
- Memory keeps growing
- System becomes slow

#### Solutions

##### 1. Increase Update Interval
Settings → Update Interval → Set to 10-30 seconds instead of 5

##### 2. Reduce Services Count
Monitor fewer services if possible

##### 3. Check for Runaway Processes
```bash
top -p $(pgrep -f server.py)
```

##### 4. Restart Server Periodically
Set up a cron job to restart daily:
```bash
0 3 * * * systemctl restart tailscale-manager
```

---

### Issue: Settings Won't Save

#### Symptoms
- Changes don't persist
- Settings reset after restart
- "Settings not saved" error

#### Solutions

##### 1. Check File Permissions
```bash
ls -la settings.json
chmod 644 settings.json
```

##### 2. Verify JSON Format
```bash
python3 -m json.tool settings.json
```

##### 3. Check Disk Space
```bash
df -h
```

##### 4. Look for File Locks
```bash
lsof | grep settings.json
```

---

## Quick Diagnostic Commands

### Full System Test
```bash
# Run the comprehensive test
python3 test_connection.py

# Should show:
# ✅ Port accessible
# ✅ Health check passed
# ✅ Main interface accessible
# ✅ API endpoints working
```

### Server Status Check
```bash
# Is it running?
ps aux | grep server.py

# What port is it using?
netstat -tuln | grep python

# Any errors in logs?
tail -f server.log  # if using nohup
journalctl -u tailscale-manager -n 50  # if using systemd
```

### Network Connectivity
```bash
# Can I reach the server?
curl -v http://localhost:8765/health

# Can others reach it?
curl -v http://$(tailscale ip -4):8765/health

# Is WebSocket working?
websocat ws://localhost:8765/ws
```

---

## Getting Help

If none of these solutions work:

1. **Run the test script** and save output:
   ```bash
   python3 test_connection.py > test_results.txt 2>&1
   ```

2. **Check server logs** and save them:
   ```bash
   python3 server.py > server_output.txt 2>&1
   ```

3. **Check browser console** (F12) and save any errors

4. **Include your environment**:
   - OS and version
   - Python version: `python3 --version`
   - Are you using Tailscale?
   - How are you running the server? (directly, systemd, screen, etc.)

5. **Report the issue** with all the above information

---

## Prevention Checklist

✅ Server running on 0.0.0.0 (not 127.0.0.1)  
✅ Firewall allows port 8765  
✅ index.html in same directory as server.py  
✅ All required files present  
✅ Python dependencies installed  
✅ No port conflicts  
✅ Proper file permissions  
✅ Running with correct user  
✅ Tailscale is running (for remote access)  
✅ ACLs allow connections (for remote access)  

---

**Still having issues?** Run `python3 test_connection.py` and check the output!
