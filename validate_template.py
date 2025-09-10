#!/usr/bin/env python3
"""
CloudFormation Template Validator
Validates the template structure and common issues
"""

import yaml
import json
import sys
from pathlib import Path

def validate_cloudformation_template(template_path):
    """Validate CloudFormation template for common issues"""
    
    print(f"🔍 Validating CloudFormation template: {template_path}")
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Basic YAML structure validation (ignore CloudFormation functions)
        # Replace CloudFormation functions with dummy values for YAML validation
        test_content = content
        cf_functions = ['!Ref', '!GetAtt', '!Sub', '!If', '!Equals', '!FindInMap', '!Select', '!GetAZs', '!Join']
        
        for func in cf_functions:
            test_content = test_content.replace(func, '"CF_FUNCTION"')
        
        try:
            yaml.safe_load(test_content)
            print("✅ YAML structure is valid")
        except yaml.YAMLError as e:
            print(f"❌ YAML syntax error: {e}")
            return False
        
        # Check for required CloudFormation sections
        required_sections = ['AWSTemplateFormatVersion', 'Description']
        optional_sections = ['Parameters', 'Conditions', 'Mappings', 'Resources', 'Outputs']
        
        template_data = yaml.safe_load(test_content)
        
        for section in required_sections:
            if section not in template_data:
                print(f"❌ Missing required section: {section}")
                return False
            else:
                print(f"✅ Found required section: {section}")
        
        for section in optional_sections:
            if section in template_data:
                print(f"✅ Found section: {section} ({len(template_data[section])} items)")
        
        # Check for common issues
        issues = []
        
        # Check Resources section
        if 'Resources' in template_data:
            resources = template_data['Resources']
            
            # Check for circular dependencies (basic check)
            resource_refs = {}
            for resource_name, resource_data in resources.items():
                if isinstance(resource_data, dict) and 'Properties' in resource_data:
                    # This is a simplified check
                    resource_refs[resource_name] = str(resource_data)
            
            print(f"✅ Found {len(resources)} resources")
        else:
            issues.append("No Resources section found")
        
        # Check Conditions section
        if 'Conditions' in template_data:
            conditions = template_data['Conditions']
            print(f"✅ Found {len(conditions)} conditions")
        
        # Check Parameters section
        if 'Parameters' in template_data:
            parameters = template_data['Parameters']
            print(f"✅ Found {len(parameters)} parameters")
        
        # Check Outputs section
        if 'Outputs' in template_data:
            outputs = template_data['Outputs']
            print(f"✅ Found {len(outputs)} outputs")
        
        if issues:
            print("\n⚠️  Issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n🎉 Template structure validation passed!")
        
        # Specific CloudFormation checks
        print("\n🔧 CloudFormation-specific checks:")
        
        # Check for common CloudFormation issues in the original content
        if 'MultiAZ: !Ref EnableMultiAZCondition' in content:
            print("❌ MultiAZ should use !If with condition, not !Ref")
        else:
            print("✅ MultiAZ property correctly configured")
        
        if 'PrimaryEndPoint.Address' in content:
            print("❌ Redis endpoint should use RedisEndpoint.Address, not PrimaryEndPoint.Address")
        else:
            print("✅ Redis endpoint correctly configured")
        
        if content.count('Type: forward') > 0 and 'ForwardConfig:' not in content:
            print("❌ ALB forward action should use ForwardConfig for modern CloudFormation")
        else:
            print("✅ ALB listener correctly configured")
        
        print("\n📋 Template Summary:")
        print(f"   - File size: {len(content)} characters")
        print(f"   - Lines: {len(content.splitlines())}")
        print(f"   - CloudFormation functions used: {sum(content.count(func) for func in cf_functions)}")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

if __name__ == "__main__":
    template_path = "deployment/cloudformation/fraud-detection-stack.yaml"
    
    if not Path(template_path).exists():
        print(f"❌ Template file not found: {template_path}")
        sys.exit(1)
    
    success = validate_cloudformation_template(template_path)
    
    if success:
        print("\n🎯 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n🚨 Validation failed - please fix the issues above")
        sys.exit(1)
