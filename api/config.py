"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server settings
    port: int = 8000
    environment: str = "development"
    
    # Auth0 settings (mapped from environment variables)
    auth0_domain: Optional[str] = None
    api_audience: Optional[str] = None
    
    @property
    def auth_enabled(self) -> bool:
        """Check if Auth0 authentication is enabled"""
        return bool(self.auth0_domain and self.api_audience)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Environment variable names match field names (case-insensitive)
        # AUTH0_DOMAIN -> auth0_domain
        # API_AUDIENCE -> api_audience
        # ENVIRONMENT -> environment
        # PORT -> port


# Global settings instance
settings = Settings()

