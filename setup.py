#!/usr/bin/env python3
"""
Setup and verification script for Tailscale Server Manager
Checks dependencies, configuration, and helps with first-time setup
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = ['fastapi', 'uvicorn', 'psutil']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking required files...")
    required_files = [
        'server.py',
        'index.html',
        'requirements.txt'
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
            missing.append(file)
    
    return len(missing) == 0, missing

def check_port_available(port=8765):
    """Check if the default port is available"""
    print(f"\n🔌 Checking port {port}...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  Port {port} is already in use")
            print(f"   💡 You can use a different port: python server.py 8766")
            return False
        else:
            print(f"   ✅ Port {port} is available")
            return True
    except Exception as e:
        print(f"   ⚠️  Could not check port: {e}")
        return True

def create_config_files():
    """Create configuration files if they don't exist"""
    print("\n⚙️  Checking configuration files...")
    
    # services_config.json
    if not Path('services_config.json').exists():
        print("   📝 Creating services_config.json...")
        default_config = '''[
  {
    "name": "Example Service",
    "kind": "backend",
    "start_cmd": "echo 'Replace with your actual start command'",
    "working_dir": null,
    "match_keywords": ["example", "service"],
    "ports": [8000],
    "api_url": "http://localhost:8000",
    "tailscale_url": null,
    "description": "This is an example service - replace with your actual service"
  }
]'''
        Path('services_config.json').write_text(default_config)
        print("   ✅ Created services_config.json")
    else:
        print("   ✅ services_config.json exists")
    
    # settings.json
    if not Path('settings.json').exists():
        print("   📝 Creating settings.json...")
        default_settings = '''{
  "storage_paths": {
    "logs": "./logs",
    "data": "./data",
    "backups": "./backups"
  },
  "scheduled_tasks": [],
  "stats_retention_days": 30,
  "auto_restart_on_failure": false,
  "check_port_conflicts": true,
  "default_tailscale_domain": "",
  "update_interval_seconds": 5,
  "api_base_url": "http://localhost:8765"
}'''
        Path('settings.json').write_text(default_settings)
        print("   ✅ Created settings.json")
    else:
        print("   ✅ settings.json exists")

def check_tailscale():
    """Check if Tailscale is installed and running"""
    print("\n🔗 Checking Tailscale...")
    try:
        result = subprocess.run(['tailscale', 'status'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            # Try to get IP
            ip_result = subprocess.run(['tailscale', 'ip', '-4'],
                                     capture_output=True,
                                     text=True,
                                     timeout=5)
            if ip_result.returncode == 0:
                ip = ip_result.stdout.strip()
                print(f"   ✅ Tailscale is running")
                print(f"   📍 Your Tailscale IP: {ip}")
                return True, ip
            else:
                print(f"   ⚠️  Tailscale is installed but not connected")
                return False, None
        else:
            print(f"   ⚠️  Tailscale is installed but not running")
            return False, None
    except FileNotFoundError:
        print(f"   ℹ️  Tailscale not installed (optional)")
        return False, None
    except Exception as e:
        print(f"   ⚠️  Could not check Tailscale: {e}")
        return False, None

def install_dependencies(missing):
    """Offer to install missing dependencies"""
    print(f"\n📦 Missing dependencies: {', '.join(missing)}")
    response = input("   Install them now? (y/n): ").lower().strip()
    
    if response == 'y':
        print("   Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, 
                         check=True)
            print("   ✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("   ❌ Installation failed")
            print("   💡 Try manually: pip install -r requirements.txt")
            return False
    return False

def main():
    print("=" * 60)
    print("🛡️  Tailscale Server Manager - Setup & Verification")
    print("=" * 60)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
        print("\n❌ Python 3.8+ is required")
        print("💡 Install from: https://www.python.org/downloads/")
        return 1
    
    # Check files
    files_ok, missing_files = check_files()
    if not files_ok:
        all_good = False
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("💡 Make sure you're in the correct directory")
        return 1
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        all_good = False
        if not install_dependencies(missing_deps):
            print("\n❌ Dependencies are missing")
            print("💡 Install manually: pip install -r requirements.txt")
            return 1
        else:
            # Re-check after installation
            deps_ok, _ = check_dependencies()
            if not deps_ok:
                return 1
    
    # Create config files
    create_config_files()
    
    # Check port
    port_ok = check_port_available()
    if not port_ok:
        all_good = False
    
    # Check Tailscale
    tailscale_ok, tailscale_ip = check_tailscale()
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All checks passed! Ready to start.")
        print("=" * 60)
        print("\n🚀 To start the server:\n")
        print("   python server.py")
        print("\n🌐 Access the interface at:\n")
        print("   Local:     http://localhost:8765")
        if tailscale_ip:
            print(f"   Tailscale: http://{tailscale_ip}:8765")
        print("   API Docs:  http://localhost:8765/docs")
        print("\n" + "=" * 60)
        print("\n📝 Next steps:")
        print("   1. Start the server (command above)")
        print("   2. Open the interface in your browser")
        print("   3. Click 'Settings' to configure")
        print("   4. Click 'Add Service' to add your services")
        print("\n💡 For headless operation, see: TROUBLESHOOTING.md")
        print("💡 To test connection: python test_connection.py")
        print("\n" + "=" * 60)
    else:
        print("⚠️  Some checks failed - see above")
        print("=" * 60)
        print("\n📖 Check TROUBLESHOOTING.md for solutions")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
