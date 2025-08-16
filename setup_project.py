#!/usr/bin/env python3
"""
Project Setup Script for E-Commerce Fraud Detection System
Run this script to create the complete project structure
"""

import os
import sys
from pathlib import Path

def create_project_structure():
    """Creates the complete folder structure for the fraud detection project"""
    
    # Define project structure
    structure = {
        'app': [
            '__init__.py',
            'main.py',
            'models.py', 
            'predictor.py',
            'monitoring.py'
        ],
        'data': [
            'raw/.gitkeep',
            'processed/.gitkeep',
            'sample_data.csv'
        ],
        'models': [
            '.gitkeep'
        ],
        'notebooks': [
            '01_EDA.ipynb',
            '02_Feature_Engineering.ipynb', 
            '03_Model_Training.ipynb',
            '04_Model_Evaluation.ipynb'
        ],
        'src': [
            '__init__.py',
            'data_pipeline.py',
            'feature_engineering.py',
            'model_training.py',
            'evaluation.py',
            'utils.py'
        ],
        'dashboard': [
            'app.py',
            'components.py'
        ],
        'tests': [
            '__init__.py',
            'test_api.py',
            'test_model.py',
            'test_pipeline.py'
        ],
        'deployment': [
            'kubernetes/.gitkeep',
            'terraform/.gitkeep'
        ],
        'config': [
            'config.py',
            'logging_config.py'
        ]
    }
    
    # Root files
    root_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.env.example',
        '.gitignore',
        'setup.py'
    ]
    
    print("🚀 Setting up E-Commerce Fraud Detection System project structure...")
    
    # Create directories and files
    for folder, files in structure.items():
        folder_path = Path(folder)
        folder_path.mkdir(exist_ok=True, parents=True)
        print(f"✅ Created directory: {folder}/")
        
        for file in files:
            file_path = folder_path / file
            if '/' in file:  # Handle subdirectories
                file_path.parent.mkdir(exist_ok=True, parents=True)
            
            if not file_path.exists():
                file_path.touch()
                print(f"   📄 Created file: {file_path}")
    
    # Create root files
    for file in root_files:
        file_path = Path(file)
        if not file_path.exists():
            file_path.touch()
            print(f"✅ Created root file: {file}")
    
    print("\n🎉 Project structure created successfully!")
    print("📁 Project tree:")
    print_tree(".", max_depth=2)

def print_tree(directory, prefix="", max_depth=2, current_depth=0):
    """Print directory tree structure"""
    if current_depth >= max_depth:
        return
    
    directory = Path(directory)
    if not directory.is_dir():
        return
    
    items = sorted(directory.iterdir())
    
    for i, item in enumerate(items):
        if item.name.startswith('.'):
            continue
            
        is_last = i == len(items) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension, max_depth, current_depth + 1)

def create_gitignore():
    """Create a comprehensive .gitignore file"""
    gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
models/*.pkl
models/*.joblib
data/raw/*
!data/raw/.gitkeep
logs/
mlruns/
.mlflow/

# Docker
.dockerignore
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Created .gitignore file")

def create_env_example():
    """Create example environment file"""
    env_content = """
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/fraud_detection
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Configuration
MODEL_PATH=models/
MODEL_VERSION=v1.0.0

# Monitoring
MLFLOW_TRACKING_URI=http://localhost:5000
EVIDENTLY_PROJECT_ID=fraud_detection

# AWS Configuration (if using)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=fraud-detection-models

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content.strip())
    
    print("✅ Created .env.example file")

if __name__ == "__main__":
    create_project_structure()
    create_gitignore()
    create_env_example()
    
    print("\n🎯 Next Steps:")
    print("1. Run: python -m venv venv")
    print("2. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
    print("3. Install: pip install -r requirements.txt")
    print("4. Copy: cp .env.example .env (and configure your settings)")
    print("5. Start coding! 🚀")