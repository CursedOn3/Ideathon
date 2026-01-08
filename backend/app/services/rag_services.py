from app.integrations.ai_search import search_documents

def build_context(query: str) -> str:
    docs = search_documents(query)
    return "\n".join(docs[:5])
