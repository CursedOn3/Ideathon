from app.integrations.azure_openai import chat

def test_chat_response():
    res = chat("Hello")
    assert "Generated content" in res
