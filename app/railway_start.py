#!/usr/bin/env python3
"""
Railway Service Starter - Detects and starts the appropriate service
"""

import os
import sys
import subprocess

def main():
    service_type = os.getenv('SERVICE_TYPE', 'api')
    port = os.getenv('PORT', '8080')
    
    print(f"🔍 Service Type: {service_type}")
    print(f"📍 Port: {port}")
    
    if service_type == 'dashboard':
        print("🎨 Starting Dashboard Service...")
        
        # Install streamlit first
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit", "pandas", "plotly", "requests"])
        
        # Start streamlit using python module
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "dashboard/app.py",
            "--server.port", port,
            "--server.address", "0.0.0.0"
        ]
    else:
        print("🚀 Starting API Service...")
        cmd = [sys.executable, "app/main.py"]
    
    print(f"📌 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())