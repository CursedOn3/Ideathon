from app.services.rag_service import build_context

def test_build_context():
    context = build_context("Q1")
    assert "Q1" in context
