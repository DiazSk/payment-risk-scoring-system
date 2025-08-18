#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request

def download_dashboard_files():
    """Download dashboard files from GitHub if they don't exist"""
    if not os.path.exists('dashboard'):
        os.makedirs('dashboard')
        print("📁 Created dashboard directory")
    
    files_to_download = [
        ('dashboard/app.py', 'https://raw.githubusercontent.com/DiazSk/credit-card-fraud-detection-system/main/dashboard/app.py'),
        ('dashboard/components.py', 'https://raw.githubusercontent.com/DiazSk/credit-card-fraud-detection-system/main/dashboard/components.py')
    ]
    
    for local_path, url in files_to_download:
        if not os.path.exists(local_path):
            print(f"📥 Downloading {local_path}...")
            urllib.request.urlretrieve(url, local_path)
            print(f"✅ Downloaded {local_path}")
        else:
            print(f"✅ {local_path} already exists")

def main():
    port = os.getenv('PORT', '8080')
    
    print("🔍 Current directory contents:")
    print(os.listdir('.'))
    
    # Download dashboard files if needed
    download_dashboard_files()
    
    print("📂 Dashboard directory contents:")
    print(os.listdir('dashboard'))
    
    # Start streamlit
    print(f"🚀 Starting Streamlit on port {port}")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main()