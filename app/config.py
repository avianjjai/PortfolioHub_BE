from pydantic_settings import BaseSettings
from typing import Optional, List
import json
import os

class Settings(BaseSettings):
    # Database settings
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "portfolio"
    
    # JWT settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings - can be set via environment variable as JSON array or comma-separated
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle CORS_ORIGINS from environment variable
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            try:
                # Try to parse as JSON array
                self.cors_origins = json.loads(cors_env)
            except json.JSONDecodeError:
                # Fall back to comma-separated values
                self.cors_origins = [origin.strip() for origin in cors_env.split(",")]

settings = Settings()
