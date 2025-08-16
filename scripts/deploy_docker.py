#!/usr/bin/env python3
"""
Docker Deployment Script for E-Commerce Fraud Detection System
Automated deployment with health checks and monitoring
"""

import subprocess
import sys
import time
import requests
import argparse
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerDeployer:
    """Manages Docker deployment of the fraud detection system"""
    
    def __init__(self, project_name="ecommerce-fraud-detection-system"):
        self.project_name = project_name
        self.project_root = Path.cwd()
        
    def check_prerequisites(self):
        """Check if Docker and required files exist"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker is not installed or not running")
                return False
            logger.info(f"✅ {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Docker command not found. Please install Docker")
            return False
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker Compose is not available")
                return False
            logger.info(f"✅ {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Docker Compose not found")
            return False
        
        # Check required files
        required_files = [
            'Dockerfile',
            'docker-compose.yml',
            'requirements.txt',
            'app/main.py',
            'models/model_metadata.json'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        # Check if models exist
        models_dir = self.project_root / "models"
        model_files = list(models_dir.glob("*.pkl"))
        
        if not model_files:
            logger.error("❌ No trained models found. Please run model training first.")
            return False
        
        logger.info(f"✅ Found {len(model_files)} trained models")
        logger.info("✅ All prerequisites satisfied!")
        
        return True
    
    def build_images(self, no_cache=False):
        """Build Docker images"""
        logger.info("🏗️  Building Docker images...")
        
        build_cmd = ['docker', 'compose', 'build']
        if no_cache:
            build_cmd.append('--no-cache')
        
        try:
            result = subprocess.run(build_cmd, check=True)
            logger.info("✅ Docker images built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to build Docker images: {e}")
            return False
    
    def deploy_production(self):
        """Deploy production environment"""
        logger.info("🚀 Deploying production environment...")
        
        try:
            # Stop any existing containers
            subprocess.run(['docker', 'compose', 'down'], check=False)
            
            # Start production services
            subprocess.run(['docker', 'compose', 'up', '-d', 'fraud-api'], check=True)
            
            logger.info("✅ Production deployment started!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Production deployment failed: {e}")
            return False
    
    def deploy_development(self):
        """Deploy development environment"""
        logger.info("🛠️  Deploying development environment...")
        
        try:
            # Stop any existing containers
            subprocess.run(['docker', 'compose', 'down'], check=False)
            
            # Start development services
            subprocess.run(['docker', 'compose', '--profile', 'dev', 'up', '-d'], check=True)
            
            logger.info("✅ Development deployment started!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Development deployment failed: {e}")
            return False
    
    def deploy_full_stack(self):
        """Deploy full stack with monitoring"""
        logger.info("🌟 Deploying full stack with monitoring...")
        
        try:
            # Create nginx directory if it doesn't exist
            nginx_dir = self.project_root / "nginx"
            nginx_dir.mkdir(exist_ok=True)
            
            # Stop any existing containers
            subprocess.run(['docker', 'compose', 'down'], check=False)
            
            # Start all services
            subprocess.run([
                'docker', 'compose', 
                '--profile', 'production', 
                '--profile', 'monitoring', 
                'up', '-d'
            ], check=True)
            
            logger.info("✅ Full stack deployment started!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Full stack deployment failed: {e}")
            return False
    
    def wait_for_api(self, url="http://localhost:8000/health", timeout=60):
        """Wait for API to be ready"""
        logger.info(f"⏳ Waiting for API to be ready at {url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('status') == 'healthy':
                        logger.info("✅ API is healthy and ready!")
                        return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info("   Still waiting...")
            time.sleep(5)
        
        logger.error(f"❌ API not ready within {timeout} seconds")
        return False
    
    def run_health_checks(self):
        """Run comprehensive health checks"""
        logger.info("🩺 Running health checks...")
        
        endpoints_to_check = [
            ("http://localhost:8000/health", "API Health"),
            ("http://localhost:8000/model_info", "Model Info"),
            ("http://localhost:8000/metrics", "Metrics")
        ]
        
        all_healthy = True
        
        for url, name in endpoints_to_check:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {name}: OK")
                else:
                    logger.warning(f"⚠️  {name}: HTTP {response.status_code}")
                    all_healthy = False
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ {name}: Failed - {e}")
                all_healthy = False
        
        return all_healthy
    
    def run_api_test(self):
        """Run a quick API test"""
        logger.info("🧪 Running API test...")
        
        test_transaction = {
            "transaction_amount": 99.99,
            "transaction_hour": 14,
            "transaction_day": 15,
            "transaction_weekend": 0,
            "is_business_hours": 1,
            "card_amount_mean": 75.50,
            "card_txn_count_recent": 2,
            "time_since_last_txn": 1200.0,
            "merchant_risk_score": 0.15,
            "amount_zscore": 0.5,
            "is_amount_outlier": 0
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=test_transaction,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ API test successful!")
                logger.info(f"   Prediction: {'FRAUD' if result['is_fraud'] else 'NORMAL'}")
                logger.info(f"   Risk level: {result['risk_level']}")
                logger.info(f"   Confidence: {result['confidence']:.3f}")
                return True
            else:
                logger.error(f"❌ API test failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API test failed: {e}")
            return False
    
    def show_deployment_info(self, deployment_type="production"):
        """Show deployment information"""
        logger.info("📋 Deployment Information:")
        
        if deployment_type == "production":
            logger.info("🌐 Production Endpoints:")
            logger.info("   API:           http://localhost:8000")
            logger.info("   Health:        http://localhost:8000/health")
            logger.info("   Docs:          http://localhost:8000/docs")
            logger.info("   Interactive:   http://localhost:8000")
        
        elif deployment_type == "development":
            logger.info("🛠️  Development Endpoints:")
            logger.info("   API:           http://localhost:8001")
            logger.info("   Health:        http://localhost:8001/health")
            logger.info("   Docs:          http://localhost:8001/docs")
        
        elif deployment_type == "full":
            logger.info("🌟 Full Stack Endpoints:")
            logger.info("   API (via Nginx): http://localhost")
            logger.info("   API Direct:      http://localhost:8000")
            logger.info("   Grafana:         http://localhost:3000 (admin/fraud_admin_2024)")
            logger.info("   Prometheus:      http://localhost:9090")
        
        logger.info("\n🐳 Docker Management:")
        logger.info("   View logs:       docker compose logs -f")
        logger.info("   Stop services:   docker compose down")
        logger.info("   Restart:         docker compose restart")
        logger.info("   View status:     docker compose ps")
    
    def cleanup(self):
        """Clean up Docker resources"""
        logger.info("🧹 Cleaning up Docker resources...")
        
        try:
            # Stop and remove containers
            subprocess.run(['docker', 'compose', 'down', '-v'], check=True)
            
            # Remove unused images
            subprocess.run(['docker', 'image', 'prune', '-f'], check=True)
            
            logger.info("✅ Cleanup completed!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return False

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy E-Commerce Fraud Detection System")
    parser.add_argument('--mode', choices=['dev', 'prod', 'full', 'test'], default='prod',
                       help='Deployment mode')
    parser.add_argument('--no-cache', action='store_true', help='Build without cache')
    parser.add_argument('--cleanup', action='store_true', help='Clean up resources')
    parser.add_argument('--skip-tests', action='store_true', help='Skip API tests')
    
    args = parser.parse_args()
    
    print("🐳 DOCKER DEPLOYMENT FOR FRAUD DETECTION SYSTEM")
    print("=" * 70)
    
    deployer = DockerDeployer()
    
    # Cleanup mode
    if args.cleanup:
        return deployer.cleanup()
    
    # Check prerequisites
    if not deployer.check_prerequisites():
        logger.error("❌ Prerequisites check failed!")
        return False
    
    # Build images
    if not deployer.build_images(no_cache=args.no_cache):
        logger.error("❌ Failed to build Docker images!")
        return False
    
    # Deploy based on mode
    if args.mode == 'dev':
        success = deployer.deploy_development()
        api_url = "http://localhost:8001"
    elif args.mode == 'prod':
        success = deployer.deploy_production()
        api_url = "http://localhost:8000"
    elif args.mode == 'full':
        success = deployer.deploy_full_stack()
        api_url = "http://localhost:8000"
    elif args.mode == 'test':
        # Test mode - just run tests
        success = True
        api_url = "http://localhost:8000"
    
    if not success:
        logger.error("❌ Deployment failed!")
        return False
    
    # Wait for API to be ready
    if not deployer.wait_for_api(f"{api_url}/health"):
        logger.error("❌ API failed to start!")
        return False
    
    # Run health checks
    if not deployer.run_health_checks():
        logger.warning("⚠️  Some health checks failed")
    
    # Run API test
    if not args.skip_tests:
        if not deployer.run_api_test():
            logger.warning("⚠️  API test failed")
    
    # Show deployment info
    deployer.show_deployment_info(args.mode)
    
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("🎯 Your fraud detection system is now running in Docker containers!")
    print("🌐 Visit http://localhost:8000 to see your API in action!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)