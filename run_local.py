#!/usr/bin/env python3
"""
Local development server runner - no Docker needed!
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(cmd, name, background=False):
    """Run a command and handle output"""
    print(f"🚀 Starting {name}...")
    if background:
        process = subprocess.Popen(cmd, shell=True)
        print(f"✅ {name} started in background (PID: {process.pid})")
        return process
    else:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0

def check_service(url, name):
    """Check if a service is responding"""
    import requests
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is responding at {url}")
            return True
        else:
            print(f"⚠️ {name} responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} is not responding: {e}")
        return False

def main():
    print("🎯 ezOverThinking Local Development Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Please run this from the project root directory")
        sys.exit(1)
    
    # Start Redis (if available)
    print("\n📦 Starting Redis...")
    try:
        redis_process = run_command("redis-server --port 6379", "Redis", background=True)
        time.sleep(2)
        if check_service("http://localhost:6379", "Redis"):
            print("✅ Redis is running")
        else:
            print("⚠️ Redis not available - some features may not work")
    except Exception as e:
        print(f"⚠️ Could not start Redis: {e}")
    
    # Start PostgreSQL (if available)
    print("\n🐘 Starting PostgreSQL...")
    try:
        # Try to start PostgreSQL if it's installed
        pg_process = run_command("pg_ctl -D /usr/local/var/postgres start", "PostgreSQL", background=True)
        time.sleep(3)
        print("✅ PostgreSQL started (or already running)")
    except Exception as e:
        print(f"⚠️ PostgreSQL not available: {e}")
    
    # Start Backend API
    print("\n🔧 Starting Backend API...")
    backend_process = run_command(
        "uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload",
        "Backend API",
        background=True
    )
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(5)
    
    # Test backend
    if check_service("http://localhost:8000/health", "Backend API"):
        print("✅ Backend is ready!")
    else:
        print("❌ Backend failed to start")
        return
    
    # Start Frontend
    print("\n🎨 Starting Streamlit Frontend...")
    frontend_process = run_command(
        "streamlit run frontend/main.py --server.port 8501 --server.address 0.0.0.0",
        "Streamlit Frontend",
        background=True
    )
    
    # Wait for frontend to start
    print("⏳ Waiting for frontend to start...")
    time.sleep(5)
    
    # Test frontend
    if check_service("http://localhost:8501", "Streamlit Frontend"):
        print("✅ Frontend is ready!")
    else:
        print("❌ Frontend failed to start")
    
    print("\n" + "=" * 50)
    print("🎉 Local Development Setup Complete!")
    print("\n📱 Access your app:")
    print("   Frontend: http://localhost:8501")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n🛑 To stop all services, press Ctrl+C")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        # Cleanup processes
        if 'backend_process' in locals():
            backend_process.terminate()
        if 'frontend_process' in locals():
            frontend_process.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main() 