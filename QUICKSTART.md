# 🚀 Quick Start Guide

## Installation (2 minutes)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your services:**
   - Edit `services_config.json`
   - Add your actual services and their start commands
   - Update `match_keywords` to match your processes

3. **Start the server:**
   
   **Windows:**
   ```bash
   start_server.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./start_server.sh
   ```
   
   Or directly:
   ```bash
   python server.py
   ```

4. **Access the interface:**
   - Local: http://localhost:8765
   - Tailscale: http://[your-tailscale-ip]:8765

## First Time Setup

### Find Your Tailscale IP
```bash
tailscale ip -4
```

### Test Your Configuration

1. Open the web interface
2. You should see all your configured services
3. Try clicking "Refresh" to test the connection
4. Test start/stop on a safe service

## Configuring Services

Each service needs:
- **name**: What to call it
- **kind**: "backend", "frontend", or "other"  
- **start_cmd**: Command to launch it
- **working_dir**: Where to run from (or null)
- **match_keywords**: How to find it in process list

### Example: Finding match_keywords

**Windows:**
```cmd
tasklist | findstr python
tasklist | findstr chrome
```

**Linux/Mac:**
```bash
ps aux | grep python
ps aux | grep chrome
```

Look at the output and choose unique keywords that identify your process.

## Common Issues

**"Service not detected" but it's running:**
- Your `match_keywords` don't match the actual process
- Check running processes and update keywords
- Make sure keywords are case-insensitive matches

**"Can't connect to WebSocket":**
- Server isn't running on port 8765
- Firewall blocking the port
- Check `netstat -an | grep 8765`

**"Permission denied" when stopping service:**
- Service running as different user
- Try running server with elevated privileges
- Or adjust service to run as same user

## Tips

1. Start with one test service first
2. Use specific keywords to avoid false matches
3. Keep `services_config.json` backed up
4. Access via Tailscale for remote management
5. Check browser console (F12) for debug info

## What's Next?

- Set up as a system service for auto-start
- Add all your services to the config
- Create a bookmark for easy access
- Share the Tailscale URL with your team

Enjoy your new server manager! 🎉
