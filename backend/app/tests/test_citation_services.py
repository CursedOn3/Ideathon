from app.services.citation_service import extract_citations

def test_extract_citations():
    citations = extract_citations(["doc1", "doc2"])
    assert len(citations) == 2
