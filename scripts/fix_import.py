#!/usr/bin/env python3
"""
Quick fix for import issues
Creates the proper project structure and moves files to correct locations
"""

import os
import shutil
from pathlib import Path

def fix_project_structure():
    """Create proper project structure and fix imports"""
    
    print("🔧 Fixing project structure and imports...")
    
    # Create necessary directories
    directories = [
        'src',
        'app', 
        'config',
        'data/raw',
        'data/processed', 
        'models',
        'dashboard',
        'tests',
        'logs',
        '.vscode'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create __init__.py files to make directories Python packages
    init_files = [
        'src/__init__.py',
        'app/__init__.py', 
        'config/__init__.py',
        'tests/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")
    
    # Check if source files exist in current directory and move them
    source_files = {
        'data_pipeline.py': 'src/data_pipeline.py',
        'feature_engineering.py': 'src/feature_engineering.py', 
        'utils.py': 'src/utils.py',
        'config.py': 'config/config.py'
    }
    
    for source, destination in source_files.items():
        if Path(source).exists():
            shutil.move(source, destination)
            print(f"✅ Moved {source} → {destination}")
        else:
            print(f"⚠️  {source} not found in current directory")
    
    # Create VS Code settings
    vscode_settings = """{
    "python.analysis.extraPaths": ["./src"],
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.analysis.autoImportCompletions": true,
    "python.analysis.typeCheckingMode": "basic"
}"""
    
    with open('.vscode/settings.json', 'w') as f:
        f.write(vscode_settings)
    print("✅ Created VS Code settings")
    
    # Create a simple test to verify imports work
    test_imports_code = '''
# Test imports
import sys
sys.path.append('src')

try:
    from data_pipeline import FraudDataPipeline
    print("✅ data_pipeline imported successfully")
except ImportError as e:
    print(f"❌ data_pipeline import failed: {e}")

try:
    from feature_engineering import FraudFeatureEngineer  
    print("✅ feature_engineering imported successfully")
except ImportError as e:
    print(f"❌ feature_engineering import failed: {e}")

try:
    from utils import DataUtils
    print("✅ utils imported successfully")
except ImportError as e:
    print(f"❌ utils import failed: {e}")

print("\\n🎯 If all imports succeeded, your project is ready!")
'''
    
    with open('test_imports_only.py', 'w') as f:
        f.write(test_imports_code)
    print("✅ Created import test script")

def create_missing_source_files():
    """Create the source files if they don't exist"""
    
    # Check if we need to create the source files
    required_files = ['src/data_pipeline.py', 'src/feature_engineering.py', 'src/utils.py']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"\n⚠️  Missing source files: {missing_files}")
        print("📝 You need to copy the source code from the artifacts into these files:")
        
        for file in missing_files:
            print(f"   - Create {file} with the corresponding artifact content")
        
        return False
    
    print("✅ All source files exist")
    return True

def main():
    """Main fix function"""
    print("🚀 FIXING IMPORT ISSUES")
    print("=" * 40)
    
    # Fix project structure
    fix_project_structure()
    
    # Check for source files
    files_exist = create_missing_source_files()
    
    print("\n" + "=" * 40)
    print("🎯 NEXT STEPS:")
    
    if files_exist:
        print("1. Restart VS Code (or reload window: Ctrl+Shift+P → 'Reload Window')")
        print("2. Run: python test_imports_only.py")
        print("3. If imports work, run: python test_complete_pipeline.py")
    else:
        print("1. Copy the artifact code into the missing files:")
        for missing in ['src/data_pipeline.py', 'src/feature_engineering.py', 'src/utils.py']:
            if not Path(missing).exists():
                print(f"   - Create {missing}")
        print("2. Restart VS Code")
        print("3. Run this script again")
    
    print("\n✅ Import fix script completed!")

if __name__ == "__main__":
    main()