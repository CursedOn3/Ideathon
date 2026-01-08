"""
Domain Models for ContentForge

Responsibilities:
• Define core business entities (Report, Citation, ContentSection)
• Enforce data validation and business rules
• Provide type safety across the application
• Support serialization for API responses and storage

Architecture Decision:
- Pydantic models provide automatic validation and serialization
- Immutable by default (use Config.frozen for critical data)
- Clear separation between domain models and database models (future)
- Rich type annotations enable better IDE support and runtime checks
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator, HttpUrl


class ContentType(str, Enum):
    """Supported content types for generation."""
    REPORT = "report"
    SUMMARY = "summary"
    ARTICLE = "article"
    MARKETING_COPY = "marketing_copy"
    EMAIL = "email"
    PRESENTATION = "presentation"


class ContentStatus(str, Enum):
    """Content generation and publishing status."""
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    PUBLISHED = "published"


class CitationFormat(str, Enum):
    """Supported citation formats."""
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "Chicago"
    IEEE = "IEEE"


class Citation(BaseModel):
    """
    Represents a source citation with full attribution.
    
    Critical for Responsible AI: Citations enable transparency and
    allow users to verify AI-generated content against source documents.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique citation ID")
    text: str = Field(..., min_length=1, description="Cited text excerpt")
    source: str = Field(..., min_length=1, description="Source document or URL")
    source_type: str = Field(default="document", description="Type of source (document, web, database)")
    page_number: Optional[int] = Field(default=None, description="Page number if applicable")
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Relevance score from RAG")
    url: Optional[HttpUrl] = Field(default=None, description="URL to source if available")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow, description="When citation was retrieved")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cit-123e4567-e89b-12d3-a456-426614174000",
                "text": "AI adoption in enterprises increased by 35% in 2024",
                "source": "Enterprise AI Report 2024",
                "source_type": "document",
                "page_number": 12,
                "relevance_score": 0.92,
                "url": "https://example.com/report",
                "retrieved_at": "2024-01-15T10:30:00Z"
            }
        }


class ContentSection(BaseModel):
    """
    Represents a section within a content piece.
    
    Enables structured content generation where each section
    can have its own citations and metadata.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Section ID")
    title: str = Field(..., min_length=1, max_length=200, description="Section heading")
    content: str = Field(..., min_length=1, description="Section body content")
    order: int = Field(default=0, ge=0, description="Display order")
    citations: List[Citation] = Field(default_factory=list, description="Section-specific citations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional section metadata")
    
    @validator("content")
    def validate_content_length(cls, v: str) -> str:
        """Ensure content is not excessively long."""
        max_words = 5000
        word_count = len(v.split())
        if word_count > max_words:
            raise ValueError(f"Section content exceeds maximum {max_words} words")
        return v


class AgentStep(BaseModel):
    """
    Represents a step in the multi-agent workflow.
    
    Used for tracking and debugging the content generation process.
    """
    
    agent_name: str = Field(..., description="Name of agent that executed this step")
    step_type: str = Field(..., description="Type of operation (planning, research, drafting, editing)")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input to this step")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Output from this step")
    duration_seconds: float = Field(default=0.0, ge=0, description="Execution time")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed by LLM")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Step execution time")
    error: Optional[str] = Field(default=None, description="Error message if step failed")


class Report(BaseModel):
    """
    Main domain model for generated content.
    
    Represents a complete content piece with all metadata,
    citations, and generation tracking information.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report ID")
    title: str = Field(..., min_length=1, max_length=300, description="Report title")
    content_type: ContentType = Field(default=ContentType.REPORT, description="Type of content")
    status: ContentStatus = Field(default=ContentStatus.DRAFT, description="Current status")
    
    # Content structure
    sections: List[ContentSection] = Field(default_factory=list, description="Content sections")
    executive_summary: Optional[str] = Field(default=None, description="Optional summary")
    
    # Citations and sources
    citations: List[Citation] = Field(default_factory=list, description="All citations used")
    citation_format: CitationFormat = Field(default=CitationFormat.APA, description="Citation style")
    
    # Generation metadata
    prompt: str = Field(..., min_length=1, description="Original user prompt")
    agent_steps: List[AgentStep] = Field(default_factory=list, description="Agent execution history")
    total_tokens_used: int = Field(default=0, ge=0, description="Total LLM tokens consumed")
    generation_time_seconds: float = Field(default=0.0, ge=0, description="Total generation time")
    
    # User and timestamps
    user_id: Optional[str] = Field(default=None, description="User who created this content")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    published_at: Optional[datetime] = Field(default=None, description="Publication timestamp")
    
    # Publishing metadata
    sharepoint_url: Optional[HttpUrl] = Field(default=None, description="SharePoint location if published")
    teams_channel: Optional[str] = Field(default=None, description="Teams channel if posted")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rep-123e4567-e89b-12d3-a456-426614174000",
                "title": "Q4 2024 AI Market Analysis",
                "content_type": "report",
                "status": "completed",
                "sections": [
                    {
                        "id": "sec-1",
                        "title": "Executive Summary",
                        "content": "The AI market grew significantly...",
                        "order": 0,
                        "citations": []
                    }
                ],
                "prompt": "Generate a comprehensive Q4 AI market analysis",
                "total_tokens_used": 15000,
                "generation_time_seconds": 45.3,
                "created_at": "2024-01-15T10:00:00Z"
            }
        }
    
    @validator("sections")
    def validate_sections_order(cls, v: List[ContentSection]) -> List[ContentSection]:
        """Ensure sections have sequential ordering."""
        if v:
            # Sort by order field
            v.sort(key=lambda s: s.order)
            # Re-number sequentially
            for i, section in enumerate(v):
                section.order = i
        return v
    
    def add_section(self, title: str, content: str, citations: Optional[List[Citation]] = None) -> None:
        """Add a new section to the report."""
        section = ContentSection(
            title=title,
            content=content,
            order=len(self.sections),
            citations=citations or []
        )
        self.sections.append(section)
    
    def add_citation(self, citation: Citation) -> None:
        """Add a citation to the report."""
        self.citations.append(citation)
    
    def add_agent_step(self, step: AgentStep) -> None:
        """Track an agent execution step."""
        self.agent_steps.append(step)
        if step.tokens_used:
            self.total_tokens_used += step.tokens_used
    
    def mark_completed(self) -> None:
        """Mark report as completed and update metadata."""
        self.status = ContentStatus.COMPLETED
        self.updated_at = datetime.utcnow()
    
    def mark_published(self, sharepoint_url: Optional[str] = None, teams_channel: Optional[str] = None) -> None:
        """Mark report as published with location metadata."""
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if sharepoint_url:
            self.sharepoint_url = sharepoint_url
        if teams_channel:
            self.teams_channel = teams_channel
    
    def get_total_citations(self) -> int:
        """Get total number of citations (report-level + section-level)."""
        section_citations = sum(len(section.citations) for section in self.sections)
        return len(self.citations) + section_citations
    
    def get_word_count(self) -> int:
        """Calculate total word count across all sections."""
        total_words = 0
        if self.executive_summary:
            total_words += len(self.executive_summary.split())
        for section in self.sections:
            total_words += len(section.content.split())
        return total_words


class ContentGenerationRequest(BaseModel):
    """
    Request model for content generation API.
    
    Represents user input for creating new content.
    """
    
    prompt: str = Field(..., min_length=10, max_length=2000, description="Content generation prompt")
    content_type: ContentType = Field(default=ContentType.REPORT, description="Type of content to generate")
    citation_format: CitationFormat = Field(default=CitationFormat.APA, description="Preferred citation format")
    max_words: Optional[int] = Field(default=2000, ge=100, le=10000, description="Target word count")
    include_citations: bool = Field(default=True, description="Include source citations")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Content tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a comprehensive analysis of AI adoption in financial services for Q4 2024",
                "content_type": "report",
                "citation_format": "APA",
                "max_words": 3000,
                "include_citations": True,
                "tags": ["AI", "finance", "Q4-2024"]
            }
        }


class ContentGenerationResponse(BaseModel):
    """
    Response model for content generation API.
    
    Returns the generated report with metadata.
    """
    
    success: bool = Field(..., description="Whether generation succeeded")
    report: Optional[Report] = Field(default=None, description="Generated report if successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    message: str = Field(default="", description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "report": {
                    "id": "rep-123",
                    "title": "AI Adoption in Financial Services - Q4 2024",
                    "status": "completed"
                },
                "message": "Content generated successfully"
            }
        }

