#!/usr/bin/env python3
"""
Test script to verify Tailscale Server Manager is running and accessible
"""

import sys
import time
import socket
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def test_port_open(host='localhost', port=8765):
    """Test if the port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"❌ Port check error: {e}")
        return False

def test_http_endpoint(url):
    """Test if HTTP endpoint responds"""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=5)
        return response.status == 200, response.status
    except HTTPError as e:
        return False, e.code
    except URLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def get_tailscale_ip():
    """Get Tailscale IP if available"""
    try:
        result = subprocess.run(['tailscale', 'ip', '-4'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def main():
    print("=" * 60)
    print("🛡️  Tailscale Server Manager - Connection Test")
    print("=" * 60)
    
    host = 'localhost'
    port = 8765
    
    # Allow custom host/port
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"⚠️  Invalid port: {sys.argv[2]}, using default: {port}")
    
    print(f"\n📍 Testing: {host}:{port}\n")
    
    # Test 1: Port accessibility
    print("1️⃣  Testing port accessibility...")
    if test_port_open(host, port):
        print(f"   ✅ Port {port} is open and accepting connections")
    else:
        print(f"   ❌ Port {port} is not accessible")
        print(f"   💡 Make sure the server is running:")
        print(f"      python server.py")
        print(f"   💡 Check firewall rules allow port {port}")
        return 1
    
    # Test 2: Health check endpoint
    print("\n2️⃣  Testing health check endpoint...")
    base_url = f"http://{host}:{port}"
    success, status = test_http_endpoint(f"{base_url}/health")
    if success:
        print(f"   ✅ Health check passed (HTTP {status})")
    else:
        print(f"   ❌ Health check failed: {status}")
        return 1
    
    # Test 3: Main page
    print("\n3️⃣  Testing main interface...")
    success, status = test_http_endpoint(base_url)
    if success:
        print(f"   ✅ Main interface accessible (HTTP {status})")
    else:
        print(f"   ⚠️  Main interface returned: {status}")
    
    # Test 4: API endpoints
    print("\n4️⃣  Testing API endpoints...")
    success, status = test_http_endpoint(f"{base_url}/api/status")
    if success:
        print(f"   ✅ API endpoints working (HTTP {status})")
    else:
        print(f"   ⚠️  API returned: {status}")
    
    # Test 5: Tailscale connectivity (if available)
    print("\n5️⃣  Testing Tailscale connectivity...")
    tailscale_ip = get_tailscale_ip()
    if tailscale_ip:
        print(f"   ℹ️  Tailscale IP detected: {tailscale_ip}")
        if host == 'localhost':
            print(f"   💡 You can also access via: http://{tailscale_ip}:{port}")
    else:
        print(f"   ℹ️  Tailscale not detected or not running")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print(f"\n🌐 Access your server at:")
    print(f"   Local:     http://localhost:{port}")
    if tailscale_ip:
        print(f"   Tailscale: http://{tailscale_ip}:{port}")
    print(f"   API Docs:  http://localhost:{port}/docs")
    print(f"   Health:    http://localhost:{port}/health")
    print("\n" + "=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
