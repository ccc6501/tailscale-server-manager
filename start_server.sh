#!/bin/bash

echo "========================================"
echo "Tailscale Server Manager"
echo "========================================"
echo ""
echo "Starting server in headless mode..."
echo "Server will run on http://0.0.0.0:8765"
echo ""
echo "To access:"
echo "- Local:     http://localhost:8765"
echo "- Tailscale: http://[your-tailscale-ip]:8765"
echo ""
echo "Server logs will appear below."
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the server
python3 server.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Server stopped with an error!"
    echo "========================================"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if port 8765 is already in use:"
    echo "   netstat -tuln | grep 8765"
    echo ""
    echo "2. Test the connection:"
    echo "   python3 test_connection.py"
    echo ""
    echo "3. Check server logs above for errors"
    echo ""
fi
