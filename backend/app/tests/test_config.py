from app.core.config import settings

def test_settings_loaded():
    assert settings.AZURE_OPENAI_API_KEY is not None
    assert settings.AI_SEARCH_INDEX_NAME is not None