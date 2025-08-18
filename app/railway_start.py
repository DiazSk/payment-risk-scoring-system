#!/usr/bin/env python3
"""
Railway service starter - detects and runs the correct service
"""
import os
import sys
import subprocess

def main():
    # Check SERVICE_TYPE environment variable (we set this manually)
    service_type = os.environ.get('SERVICE_TYPE', '').lower()
    port = os.environ.get('PORT', '8080')
    
    print(f"🔍 Service Type: {service_type}")
    print(f"📍 Port: {port}")
    
    if service_type == 'dashboard':
        print("🎨 Starting Dashboard Service...")
        cmd = [
            'streamlit', 'run', 'dashboard/app.py',
            '--server.port', port,
            '--server.address', '0.0.0.0'
        ]
    elif service_type == 'api':
        print("🚀 Starting API Service...")
        cmd = ['python', 'app/main.py']
    else:
        # Default to API if not specified
        print("⚠️ No SERVICE_TYPE set, defaulting to API")
        cmd = ['python', 'app/main.py']
    
    print(f"📌 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()