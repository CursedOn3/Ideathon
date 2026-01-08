def extract_citations(docs):
    return [{"source": f"Doc {i}", "link": "#"} for i, _ in enumerate(docs)]
