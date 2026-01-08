"""
Unit Tests for Domain Models

Tests Report, Citation, and related models for validation and behavior.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.report import (
    Report,
    Citation,
    ContentSection,
    AgentStep,
    ContentType,
    ContentStatus,
    CitationFormat,
    ContentGenerationRequest,
)


class TestCitation:
    """Test suite for Citation model."""
    
    def test_citation_creation(self):
        """Test creating a valid citation."""
        citation = Citation(
            text="AI adoption increased by 35%",
            source="Enterprise AI Report 2024",
            source_type="document",
            page_number=12,
            relevance_score=0.92,
        )
        
        assert citation.text == "AI adoption increased by 35%"
        assert citation.source == "Enterprise AI Report 2024"
        assert citation.page_number == 12
        assert citation.relevance_score == 0.92
        assert citation.id is not None
    
    def test_citation_validation(self):
        """Test citation validation rules."""
        # Empty text should fail
        with pytest.raises(ValidationError):
            Citation(text="", source="Test Source")
        
        # Invalid relevance score should fail
        with pytest.raises(ValidationError):
            Citation(
                text="Test",
                source="Source",
                relevance_score=1.5,  # Must be 0-1
            )


class TestContentSection:
    """Test suite for ContentSection model."""
    
    def test_section_creation(self):
        """Test creating a content section."""
        section = ContentSection(
            title="Introduction",
            content="This is the introduction content.",
            order=0,
        )
        
        assert section.title == "Introduction"
        assert section.content == "This is the introduction content."
        assert section.order == 0
        assert len(section.citations) == 0
    
    def test_section_content_length_validation(self):
        """Test content length validation."""
        # Create content exceeding word limit
        long_content = " ".join(["word"] * 6000)
        
        with pytest.raises(ValidationError):
            ContentSection(
                title="Test",
                content=long_content,
            )


class TestReport:
    """Test suite for Report model."""
    
    def test_report_creation(self):
        """Test creating a report."""
        report = Report(
            title="Q4 AI Market Analysis",
            prompt="Analyze the AI market for Q4",
            content_type=ContentType.REPORT,
        )
        
        assert report.title == "Q4 AI Market Analysis"
        assert report.content_type == ContentType.REPORT
        assert report.status == ContentStatus.DRAFT
        assert report.id is not None
        assert isinstance(report.created_at, datetime)
    
    def test_add_section(self):
        """Test adding sections to report."""
        report = Report(
            title="Test Report",
            prompt="Test prompt",
        )
        
        report.add_section(
            title="Introduction",
            content="Introduction content",
        )
        
        report.add_section(
            title="Body",
            content="Body content",
        )
        
        assert len(report.sections) == 2
        assert report.sections[0].title == "Introduction"
        assert report.sections[1].title == "Body"
    
    def test_add_citation(self):
        """Test adding citations to report."""
        report = Report(title="Test", prompt="Test")
        
        citation = Citation(
            text="Test citation",
            source="Test Source",
        )
        
        report.add_citation(citation)
        
        assert len(report.citations) == 1
        assert report.citations[0].source == "Test Source"
    
    def test_mark_completed(self):
        """Test marking report as completed."""
        report = Report(title="Test", prompt="Test")
        
        report.mark_completed()
        
        assert report.status == ContentStatus.COMPLETED
    
    def test_mark_published(self):
        """Test marking report as published."""
        report = Report(title="Test", prompt="Test")
        
        report.mark_published(sharepoint_url="https://sharepoint.com/report")
        
        assert report.status == ContentStatus.PUBLISHED
        assert report.published_at is not None
        assert report.sharepoint_url == "https://sharepoint.com/report"
    
    def test_get_word_count(self):
        """Test word count calculation."""
        report = Report(title="Test", prompt="Test")
        
        report.add_section(
            title="Section 1",
            content="This is a test section with ten words exactly.",
        )
        
        report.add_section(
            title="Section 2",
            content="Another section with five words.",
        )
        
        word_count = report.get_word_count()
        
        assert word_count == 15


class TestContentGenerationRequest:
    """Test suite for ContentGenerationRequest model."""
    
    def test_valid_request(self):
        """Test creating a valid content generation request."""
        request = ContentGenerationRequest(
            prompt="Generate a report on AI ethics",
            content_type=ContentType.REPORT,
            max_words=2000,
        )
        
        assert request.prompt == "Generate a report on AI ethics"
        assert request.content_type == ContentType.REPORT
        assert request.max_words == 2000
    
    def test_prompt_length_validation(self):
        """Test prompt length validation."""
        # Too short
        with pytest.raises(ValidationError):
            ContentGenerationRequest(prompt="Hi")
        
        # Too long
        with pytest.raises(ValidationError):
            ContentGenerationRequest(prompt="a" * 3000)
    
    def test_max_words_validation(self):
        """Test max words validation."""
        # Below minimum
        with pytest.raises(ValidationError):
            ContentGenerationRequest(
                prompt="Valid prompt here",
                max_words=50,
            )
        
        # Above maximum
        with pytest.raises(ValidationError):
            ContentGenerationRequest(
                prompt="Valid prompt here",
                max_words=15000,
            )
