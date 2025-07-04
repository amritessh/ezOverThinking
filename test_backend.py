#!/usr/bin/env python3
"""
Simple test script to check if the backend is responding
"""

import requests
import time

def test_backend():
    """Test if the backend is responding"""
    print("Testing backend connection...")
    
    try:
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - backend is not responding")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - backend is not responding")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    if success:
        print("✅ Backend is working!")
    else:
        print("❌ Backend is not working") 