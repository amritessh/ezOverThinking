# api/main_minimal.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Minimal lifespan function"""
    logger.info("🚀 Starting minimal ezOverThinking API server...")
    yield
    logger.info("🔄 Shutting down minimal server...")


# Create FastAPI app
app = FastAPI(
    title="ezOverThinking API (Minimal)",
    description="The AI-powered overthinking amplification system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Basic CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "Welcome to ezOverThinking API (Minimal)",
        "version": "1.0.0",
        "status": "ready_to_overthink",
        "docs": "/docs",
        "health": "/health",
    }

# Health endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "message": "ezOverThinking API is running (minimal mode)",
        "version": "1.0.0",
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": {"code": exc.status_code, "message": exc.detail, "type": "http_error"}
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return {
        "error": {
            "code": 500,
            "message": "Internal server error",
            "type": "server_error",
        }
    } 