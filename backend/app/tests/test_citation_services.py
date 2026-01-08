from app.services.citation_services import extract_citations

def test_extract_citations():
    citations = extract_citations(["doc1", "doc2"])
    assert len(citations) == 2
