#!/usr/bin/env python3
"""
Railway Deployment Helper for Credit Card Fraud Detection System
Automated deployment script for both API and Dashboard
"""

import os
import subprocess
import sys
import json
from pathlib import Path
import requests
import time

class RailwayDeployer:
    """Helper class for Railway deployment"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.api_url = None
        self.dashboard_url = None
        
    def check_prerequisites(self):
        """Check if all required files exist"""
        print("🔍 Checking deployment prerequisites...")
        
        required_files = [
            "app/main.py",
            "dashboard/app.py", 
            "requirements.txt",
            "models/model_metadata.json"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ Missing required files:")
            for file in missing_files:
                print(f"   • {file}")
            return False
        
        # Check if models exist
        models_dir = self.project_root / "models"
        model_files = list(models_dir.glob("*.pkl"))
        
        if len(model_files) < 3:
            print("⚠️  Warning: Only found {len(model_files)} model files")
            print("   Recommend having at least 3 trained models")
        
        print("✅ All prerequisites satisfied!")
        return True
    
    def create_deployment_configs(self):
        """Create necessary deployment configuration files"""
        print("⚙️  Creating deployment configurations...")
        
        # Create .railway directory
        railway_dir = self.project_root / ".railway"
        railway_dir.mkdir(exist_ok=True)
        
        # API service config
        api_config = {
            "name": "credit-card-fraud-api",
            "source": ".",
            "build": {
                "command": "pip install -r requirements.txt"
            },
            "deploy": {
                "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
                "healthcheckPath": "/health"
            },
            "env": {
                "ENVIRONMENT": "production",
                "PYTHONPATH": "/app"
            }
        }
        
        with open(railway_dir / "api-service.json", "w") as f:
            json.dump(api_config, f, indent=2)
        
        # Dashboard service config
        dashboard_config = {
            "name": "credit-card-fraud-dashboard", 
            "source": ".",
            "build": {
                "command": "pip install -r requirements.txt"
            },
            "deploy": {
                "startCommand": "streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true",
                "healthcheckPath": "/"
            },
            "env": {
                "ENVIRONMENT": "production",
                "PYTHONPATH": "/app",
                "STREAMLIT_SERVER_HEADLESS": "true"
            }
        }
        
        with open(railway_dir / "dashboard-service.json", "w") as f:
            json.dump(dashboard_config, f, indent=2)
            
        print("✅ Deployment configurations created!")
    
    def check_railway_cli(self):
        """Check if Railway CLI is installed"""
        try:
            result = subprocess.run(["railway", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Railway CLI not found!")
            print("\n📋 Installation Instructions:")
            print("   Windows: npm install -g @railway/cli")
            print("   macOS: brew install railway")
            print("   Linux: npm install -g @railway/cli")
            print("\n🔗 Or visit: https://docs.railway.app/develop/cli")
            return False
    
    def deploy_api(self):
        """Deploy the FastAPI service"""
        print("🚀 Deploying FastAPI service...")
        
        try:
            # Initialize Railway project (if not exists)
            subprocess.run(["railway", "login"], check=False)
            subprocess.run(["railway", "project", "create", "credit-card-fraud-detection"], check=False)
            
            # Deploy API service
            print("📤 Deploying API to Railway...")
            result = subprocess.run([
                "railway", "up", 
                "--service", "api",
                "--start-command", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ API deployment successful!")
                # Try to extract URL from output
                self.extract_api_url(result.stdout)
            else:
                print("❌ API deployment failed!")
                print(result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment error: {e}")
            return False
        
        return True
    
    def deploy_dashboard(self):
        """Deploy the Streamlit dashboard"""
        print("🎨 Deploying Streamlit dashboard...")
        
        try:
            # Deploy dashboard service
            print("📤 Deploying Dashboard to Railway...")
            result = subprocess.run([
                "railway", "up",
                "--service", "dashboard", 
                "--start-command", "streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dashboard deployment successful!")
                self.extract_dashboard_url(result.stdout)
            else:
                print("❌ Dashboard deployment failed!")
                print(result.stderr)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment error: {e}")
            return False
        
        return True
    
    def extract_api_url(self, output):
        """Extract API URL from Railway output"""
        # Railway typically outputs deployment URL
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'railway.app' in line:
                self.api_url = line.strip()
                print(f"🌐 API URL: {self.api_url}")
                break
    
    def extract_dashboard_url(self, output):
        """Extract Dashboard URL from Railway output"""
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'railway.app' in line:
                self.dashboard_url = line.strip()
                print(f"🌐 Dashboard URL: {self.dashboard_url}")
                break
    
    def test_deployments(self):
        """Test both deployed services"""
        print("🧪 Testing deployed services...")
        
        # Test API
        if self.api_url:
            try:
                response = requests.get(f"{self.api_url}/health", timeout=30)
                if response.status_code == 200:
                    print("✅ API health check passed!")
                else:
                    print(f"⚠️  API health check returned: {response.status_code}")
            except Exception as e:
                print(f"❌ API test failed: {e}")
        
        # Test Dashboard  
        if self.dashboard_url:
            try:
                response = requests.get(self.dashboard_url, timeout=30)
                if response.status_code == 200:
                    print("✅ Dashboard is accessible!")
                else:
                    print(f"⚠️  Dashboard returned: {response.status_code}")
            except Exception as e:
                print(f"❌ Dashboard test failed: {e}")
    
    def show_success_summary(self):
        """Show deployment success summary"""
        print("\n" + "="*70)
        print("🎉 RAILWAY DEPLOYMENT COMPLETED!")
        print("="*70)
        
        print("\n🌐 Your Live URLs:")
        if self.api_url:
            print(f"   📡 API:       {self.api_url}")
            print(f"   📖 API Docs:  {self.api_url}/docs")
            print(f"   💗 Health:    {self.api_url}/health")
        
        if self.dashboard_url:
            print(f"   📊 Dashboard: {self.dashboard_url}")
        
        print("\n🎯 Next Steps:")
        print("   1. Test your API endpoints")
        print("   2. Verify dashboard functionality")
        print("   3. Update your README with live links")
        print("   4. Share with potential employers!")
        
        print("\n💼 Professional Links for Your Resume:")
        print(f"   • Live Demo: {self.dashboard_url or 'Pending...'}")
        print(f"   • API Docs: {self.api_url or 'Pending...'}/docs")
        print("   • GitHub: [Your Repository URL]")
        
        print("\n🚀 Your credit card fraud detection system is now LIVE!")
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚂 RAILWAY DEPLOYMENT FOR CREDIT CARD FRAUD DETECTION")
        print("="*60)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed!")
            return False
        
        # Step 2: CLI Check
        if not self.check_railway_cli():
            print("❌ Railway CLI setup required!")
            return False
        
        # Step 3: Create configs
        self.create_deployment_configs()
        
        # Step 4: Deploy API
        if not self.deploy_api():
            print("❌ API deployment failed!")
            return False
        
        # Step 5: Deploy Dashboard
        if not self.deploy_dashboard():
            print("❌ Dashboard deployment failed!")
            return False
        
        # Step 6: Test deployments
        print("\n⏳ Waiting for services to start up...")
        time.sleep(30)  # Wait for services to be ready
        self.test_deployments()
        
        # Step 7: Success summary
        self.show_success_summary()
        
        return True

def main():
    """Main deployment function"""
    deployer = RailwayDeployer()
    
    print("🎯 Railway Deployment Options:")
    print("1. 🚀 Full Deployment (API + Dashboard)")
    print("2. 📡 API Only")
    print("3. 📊 Dashboard Only")
    print("4. ⚙️  Setup Configuration Only")
    
    choice = input("\n👉 Choose deployment option (1-4): ").strip()
    
    if choice == "1":
        deployer.run_deployment()
    elif choice == "2":
        if deployer.check_prerequisites() and deployer.check_railway_cli():
            deployer.create_deployment_configs()
            deployer.deploy_api()
    elif choice == "3":
        if deployer.check_prerequisites() and deployer.check_railway_cli():
            deployer.create_deployment_configs()
            deployer.deploy_dashboard()
    elif choice == "4":
        deployer.create_deployment_configs()
        print("✅ Configuration files created!")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()