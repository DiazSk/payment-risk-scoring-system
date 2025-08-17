#!/usr/bin/env python3
"""
Railway service detection and startup script
"""
import os
import sys
import subprocess

def main():
    # Get Railway environment info
    service_name = os.environ.get('RAILWAY_SERVICE_NAME', '')
    public_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
    static_url = os.environ.get('RAILWAY_STATIC_URL', '')
    
    print(f"🔍 Detecting service...")
    print(f"Service Name: {service_name}")
    print(f"Public Domain: {public_domain}")
    print(f"Static URL: {static_url}")
    
    # Detect which service to run
    is_dashboard = (
        'dashboard' in service_name.lower() or
        'dashboard' in public_domain.lower() or
        'dashboard' in static_url.lower()
    )
    
    port = os.environ.get('PORT', '8080')
    
    if is_dashboard:
        print("🎨 Starting Dashboard Service...")
        cmd = [
            'streamlit', 'run', 'dashboard/app.py',
            '--server.port', port,
            '--server.address', '0.0.0.0'
        ]
    else:
        print("🚀 Starting API Service...")
        cmd = ['python', 'app/main.py']
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()