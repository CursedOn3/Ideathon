from app.integrations.ai_search import search_documents

def test_search_documents():
    docs = search_documents("Q1 report")
    assert isinstance(docs, list)
    assert "Q1 report" in docs[0]
