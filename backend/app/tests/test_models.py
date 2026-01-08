from app.models.report import Report, Citation

def test_report_model():
    report = Report(title="Test", sections={"body": "Hello"}, citations=[Citation(source="Doc", link="#")])
    assert report.title == "Test"
    assert report.sections["body"] == "Hello"
    assert report.citations[0].source == "Doc"
