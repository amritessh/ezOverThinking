# src/config/settings.py
from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_title: str = "ezOverThinking API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    allowed_hosts: List[str] = ["*"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: str = ""
    
    # State Management
    state_ttl: int = 3600  # 1 hour
    
    # Database Settings
    database_url: str = "postgresql://user:password@localhost:5432/ezoverthinking"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # Agent Settings
    max_conversation_length: int = 50
    max_anxiety_level: int = 5
    default_escalation_threshold: int = 3
    
    # Analytics
    analytics_enabled: bool = True
    analytics_retention_days: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 