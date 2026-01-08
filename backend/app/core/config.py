"""
Core Configuration Module for ContentForge

Responsibilities:
• Load and validate environment variables using Pydantic
• Provide type-safe access to configuration across the application
• Support multiple environments (dev, staging, production)
• Implement security best practices (no hardcoded secrets)

Architecture Decision:
- Using Pydantic Settings for automatic validation and type coercion
- Fail-fast approach: missing required vars will raise ValidationError on startup
- Centralized configuration prevents scattered env access throughout codebase
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings with environment-based configuration.
    
    All settings are loaded from environment variables or .env file.
    Required fields will cause application startup failure if missing.
    """
    
    # ========================================
    # Application Settings
    # ========================================
    APP_NAME: str = Field(default="ContentForge", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # ========================================
    # API Settings
    # ========================================
    API_V1_PREFIX: str = Field(default="/api/v1", description="API route prefix")
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # ========================================
    # Azure OpenAI Configuration
    # ========================================
    AZURE_OPENAI_ENDPOINT: str = Field(..., description="Azure OpenAI service endpoint")
    AZURE_OPENAI_API_KEY: str = Field(..., description="Azure OpenAI API key")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(
        default="gpt-4o",
        description="Azure OpenAI deployment/model name"
    )
    AZURE_OPENAI_API_VERSION: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    AZURE_OPENAI_MAX_RETRIES: int = Field(default=3, description="Max retry attempts for OpenAI calls")
    AZURE_OPENAI_TIMEOUT: int = Field(default=120, description="Request timeout in seconds")
    AZURE_OPENAI_TEMPERATURE: float = Field(default=0.7, description="Default temperature for generation")
    AZURE_OPENAI_MAX_TOKENS: int = Field(default=4000, description="Default max tokens for generation")
    
    # ========================================
    # Azure AI Search Configuration (RAG)
    # ========================================
    AI_SEARCH_ENDPOINT: str = Field(..., description="Azure AI Search service endpoint")
    AI_SEARCH_API_KEY: str = Field(..., description="Azure AI Search admin key")
    AI_SEARCH_INDEX_NAME: str = Field(
        default="contentforge-documents",
        description="AI Search index for document retrieval"
    )
    AI_SEARCH_SEMANTIC_CONFIG: Optional[str] = Field(
        default=None,
        description="Semantic search configuration name"
    )
    AI_SEARCH_TOP_K: int = Field(default=5, description="Number of documents to retrieve")
    AI_SEARCH_MIN_SCORE: float = Field(default=0.7, description="Minimum relevance score threshold")
    
    # ========================================
    # Microsoft Graph API Configuration
    # ========================================
    GRAPH_TENANT_ID: str = Field(..., description="Microsoft Entra tenant ID")
    GRAPH_CLIENT_ID: str = Field(..., description="Microsoft Entra app client ID")
    GRAPH_CLIENT_SECRET: str = Field(..., description="Microsoft Entra app client secret")
    GRAPH_SCOPES: str = Field(
        default="https://graph.microsoft.com/.default",
        description="Microsoft Graph API scopes"
    )
    SHAREPOINT_SITE_ID: Optional[str] = Field(
        default=None,
        description="SharePoint site ID for publishing"
    )
    SHAREPOINT_DRIVE_ID: Optional[str] = Field(
        default=None,
        description="SharePoint drive ID for document uploads"
    )
    
    # ========================================
    # Content Generation Settings
    # ========================================
    MAX_CONTENT_LENGTH: int = Field(default=10000, description="Maximum content length in words")
    CITATION_FORMAT: str = Field(default="APA", description="Citation format: APA, MLA, Chicago")
    ENABLE_CONTENT_SAFETY: bool = Field(default=True, description="Enable Azure Content Safety checks")
    
    # ========================================
    # Database & Caching (Future)
    # ========================================
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection string")
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection string for caching")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is one of the allowed values."""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v.lower()
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    @validator("AZURE_OPENAI_TEMPERATURE")
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is in valid range."""
        if not 0 <= v <= 2:
            raise ValueError("AZURE_OPENAI_TEMPERATURE must be between 0 and 2")
        return v
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are loaded once and reused.
    This is important for performance and consistency.
    
    Returns:
        Settings: Validated application settings
    """
    return Settings()


# Global settings instance
# Import this throughout the application
settings = get_settings()