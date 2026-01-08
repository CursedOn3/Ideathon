from app.core.logging import logger

def test_logger_exists():
    assert logger.name == "contentforge"