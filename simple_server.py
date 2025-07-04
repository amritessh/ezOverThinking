#!/usr/bin/env python3
"""
Simple standalone FastAPI server for testing
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="ezOverThinking API (Standalone)",
    description="Simple test server",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ezOverThinking API (Standalone)",
        "version": "1.0.0",
        "status": "running",
    }

@app.get("/health")
async def health():
    """Health endpoint"""
    return {
        "status": "healthy",
        "message": "Server is running",
        "version": "1.0.0",
    }

if __name__ == "__main__":
    print("Starting standalone server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 