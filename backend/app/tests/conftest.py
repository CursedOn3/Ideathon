"""
Pytest Configuration

Configures test environment, fixtures, and settings for the test suite.
"""

import pytest
import asyncio
from typing import Generator

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    monkeypatch.setenv("AI_SEARCH_ENDPOINT", "https://test.search.windows.net")
    monkeypatch.setenv("AI_SEARCH_API_KEY", "test-search-key")
    monkeypatch.setenv("AI_SEARCH_INDEX_NAME", "test-index")
    monkeypatch.setenv("GRAPH_TENANT_ID", "test-tenant-id")
    monkeypatch.setenv("GRAPH_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GRAPH_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("ENVIRONMENT", "testing")
