#!/usr/bin/env python3
"""
Simple test to check if basic FastAPI is working
"""

import requests
import time

def test_basic_connection():
    """Test basic connection to the backend"""
    print("Testing basic backend connection...")
    
    # Test multiple endpoints
    endpoints = [
        "http://localhost:8000/",
        "http://localhost:8000/health",
        "http://localhost:8000/docs"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(endpoint, timeout=3)
            print(f"  Status: {response.status_code}")
            print(f"  Response length: {len(response.text)}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection failed")
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_basic_connection()
    if success:
        print("✅ Backend is responding!")
    else:
        print("❌ Backend is not responding to any endpoints") 