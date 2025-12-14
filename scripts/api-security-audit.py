#!/usr/bin/env python3
import os
import re

def audit_api_endpoints():
    print("🔍 AgriDAO API Security Audit")
    print("=" * 40)
    
    backend_dir = "backend/app/routers"
    issues = []
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                # Check for missing authentication
                if '@router.' in content and 'Depends(get_current_user)' not in content:
                    issues.append(f"⚠️ {filepath}: Missing authentication dependency")
                
                # Check for SQL injection risks
                if re.search(r'execute.*%|format.*sql', content, re.IGNORECASE):
                    issues.append(f"🚨 {filepath}: Potential SQL injection risk")
                
                # Check for missing input validation
                if 'router.post' in content and 'Pydantic' not in content:
                    issues.append(f"⚠️ {filepath}: Missing input validation")
    
    print(f"📊 Found {len(issues)} potential security issues:")
    for issue in issues[:10]:  # Show first 10
        print(f"   {issue}")
    
    return len(issues)

if __name__ == "__main__":
    audit_api_endpoints()
