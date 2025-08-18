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
    print(f"📂 Current Directory: {os.getcwd()}")
    print(f"📁 Directory Contents: {os.listdir('.')}")
    
    # Check if dashboard directory exists
    if os.path.exists('dashboard'):
        print(f"✅ Dashboard directory exists")
        print(f"📁 Dashboard contents: {os.listdir('dashboard')}")
    else:
        print(f"❌ Dashboard directory NOT found")
    
    if service_type == 'dashboard':
        print("🎨 Starting Dashboard Service...")
        
        # Check for the app.py file
        if os.path.exists('dashboard/app.py'):
            print("✅ Found dashboard/app.py")
        else:
            print("❌ dashboard/app.py NOT found")
            # Try to find any .py files
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.py'):
                        print(f"   Found: {os.path.join(root, file)}")
        
        # Install streamlit if needed
        print("📦 Ensuring dependencies...")
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