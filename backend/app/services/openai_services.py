from app.integrations.azure_openai import chat

def generate_content(prompt: str, context: str):
    return chat(prompt, context)
