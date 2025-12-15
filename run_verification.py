#!/usr/bin/env python3
import subprocess
import requests
import time
import json

def verify_infrastructure():
    """Verify infrastructure health"""
    print("🏗️ Infrastructure Health Check")
    print("=" * 30)
    
    try:
        # Check if server is accessible
        response = requests.get("http://54.251.65.124/", timeout=10)
        print(f"✅ Server accessible: {response.status_code}")
        
        # Check API health
        api_response = requests.get("http://54.251.65.124/api/health", timeout=10)
        if api_response.status_code == 200:
            health_data = api_response.json()
            print(f"✅ API Health: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ API Health: {api_response.status_code}")
            
    except Exception as e:
        print(f"❌ Server check failed: {e}")

def verify_api_endpoints():
    """Verify API endpoints"""
    print("\n🌐 API Endpoints Check")
    print("=" * 25)
    
    base_url = "http://54.251.65.124/api"
    endpoints = [
        "/health",
        "/docs", 
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {endpoint}: {response.status_code} ({response_time:.0f}ms)")
            
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def verify_frontend():
    """Verify frontend functionality"""
    print("\n💻 Frontend Check")
    print("=" * 18)
    
    try:
        response = requests.get("http://54.251.65.124/", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            
            # Check if it's the React app
            if "AgriDAO" in response.text or "react" in response.text.lower():
                print("✅ React application loaded")
            else:
                print("⚠️ Frontend loaded but content unclear")
        else:
            print(f"❌ Frontend error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")

def verify_security():
    """Verify security measures"""
    print("\n🔒 Security Check")
    print("=" * 17)
    
    try:
        response = requests.get("http://54.251.65.124/", timeout=10)
        headers = response.headers
        
        # Check security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'Content-Security-Policy'
        ]
        
        for header in security_headers:
            if header in headers:
                print(f"✅ {header}: Present")
            else:
                print(f"⚠️ {header}: Missing")
                
        # Check HTTPS
        try:
            https_response = requests.get("https://54.251.65.124/", timeout=5)
            print("✅ HTTPS: Available")
        except:
            print("⚠️ HTTPS: Not configured (HTTP only)")
            
    except Exception as e:
        print(f"❌ Security check failed: {e}")

def verify_performance():
    """Verify performance metrics"""
    print("\n📈 Performance Check")
    print("=" * 20)
    
    # Test response times
    endpoints = [
        "http://54.251.65.124/",
        "http://54.251.65.124/api/health"
    ]
    
    for url in endpoints:
        try:
            times = []
            for _ in range(3):
                start = time.time()
                response = requests.get(url, timeout=10)
                times.append((time.time() - start) * 1000)
                
            avg_time = sum(times) / len(times)
            status = "✅" if avg_time < 2000 else "⚠️" if avg_time < 5000 else "❌"
            print(f"{status} {url.split('/')[-1] or 'Frontend'}: {avg_time:.0f}ms avg")
            
        except Exception as e:
            print(f"❌ {url}: {e}")

def main():
    """Run comprehensive verification"""
    print("🔍 AgriDAO Deployment Verification")
    print("=" * 40)
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Server: 54.251.65.124")
    
    verify_infrastructure()
    verify_api_endpoints() 
    verify_frontend()
    verify_security()
    verify_performance()
    
    print("\n" + "=" * 40)
    print("✅ Verification completed!")
    print("📊 Check results above for any issues")

if __name__ == "__main__":
    main()
