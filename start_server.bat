@echo off
echo ========================================
echo Tailscale Server Manager
echo ========================================
echo.
echo Starting server in headless mode...
echo Server will run on http://0.0.0.0:8765
echo.
echo To access:
echo - Local:     http://localhost:8765
echo - Tailscale: http://[your-tailscale-ip]:8765
echo.
echo Server logs will appear below.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the server with the tray launcher
python tray_server.py

REM If server exits, pause to see error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Server stopped with an error!
    echo ========================================
    pause
)
