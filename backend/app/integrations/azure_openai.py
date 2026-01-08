from app.core.config import settings

def chat(prompt: str, context: str = "") -> str:
    return f"Generated content for: {prompt}"
