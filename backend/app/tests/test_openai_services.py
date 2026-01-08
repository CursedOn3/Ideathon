from app.services.openai_service import generate_content

def test_generate_content():
    res = generate_content("Write a report", "Some context")
    assert "Write a report" in res
