"""
Load .env values
Provide access to all keys/URLs
"""

from pydantic import BaseSettings

class Settings(BaseSettings):
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AI_SEARCH_ENDPOINT: str
    AI_SEARCH_API_KEY: str
    AI_SEARCH_INDEX_NAME: str
    GRAPH_TENANT_ID: str
    GRAPH_CLIENT_ID: str
    GRAPH_CLIENT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()