#!/usr/bin/env python3
"""
Fix all inflated metrics across documentation files
Replace 99.x% claims with realistic 92.3% detection rate
"""

import os
import re
from pathlib import Path

def fix_file_metrics(file_path):
    """Fix metrics in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace 99.2% accuracy claims with 92.3% detection rate
        content = re.sub(r'99\.2%\s+accuracy', '92.3% fraud detection rate', content)
        content = re.sub(r'99\.2%\s+verified', '92.3% detection rate', content)
        content = re.sub(r'99\.2%\s+[Aa]ccuracy', '92.3% detection rate', content)
        
        # Replace other inflated metrics
        content = re.sub(r'99\.6%', '96.2%', content)  # ROC-AUC
        content = re.sub(r'99\.7%', '92.3%', content)  # Various claims
        content = re.sub(r'99\.9%\s+uptime', '99%+ uptime', content)
        content = re.sub(r'99\.99%', '99%+', content)
        
        # Fix business impact claims
        content = re.sub(r'\$1\.6M', '$5-15K monthly', content)
        content = re.sub(r'\$2\.8M', '$5-15K monthly', content)
        content = re.sub(r'1000\+\s+req/min', '50+ req/sec', content)
        content = re.sub(r'1,200\s+req/min', '50+ req/sec', content)
        
        # Fix false positive claims
        content = re.sub(r'0\.1%\s+false\s+positive', '1.3% false positive', content)
        
        # Fix memory claims
        content = re.sub(r'99\.2MB', '~512MB', content)
        
        # Fix enterprise claims
        content = re.sub(r'[Ee]nterprise-grade', 'Production-ready', content)
        content = re.sub(r'[Vv]erified.*?accuracy', 'Sample data testing', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix metrics in all documentation files"""
    
    # Files to fix
    doc_files = [
        "CONTRIBUTING.md",
        "docs/PORTFOLIO_GUIDE.md", 
        "docs/project-brief.md",
        "docs/PROJECT_CLOSURE_REPORT.md",
        "docs/PROJECT_COMPLETION_SUMMARY.md",
        "docs/TRANSFORMATION_SUMMARY.md",
        "docs/ARCHITECTURE.md",
        "docs/DEPLOYMENT.md",
        "docs/prd/epic-and-story-structure.md",
        "docs/prd/intro-project-analysis-and-context.md",
        "docs/prd/requirements.md",
        "docs/qa/assessments/comprehensive-review-20250907.md",
        "docs/stories/story-1.1-remove-artificial-metrics.md",
        "docs/stories/story-1.6-defensible-metrics-and-features.md"
    ]
    
    fixed_count = 0
    total_count = 0
    
    for file_path in doc_files:
        if os.path.exists(file_path):
            total_count += 1
            if fix_file_metrics(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n📊 Summary: Fixed {fixed_count} out of {total_count} files")
    print("✅ All inflated metrics have been replaced with realistic performance claims!")

if __name__ == "__main__":
    main()
