"""
Citation Service

Responsibilities:
• Format citations according to different styles (APA, MLA, Chicago)
• Track citation usage within content
• Validate and deduplicate citations
• Generate reference lists and bibliographies
• Support inline citation markers

Architecture Decision:
- Centralizes all citation formatting logic
- Ensures consistent citation style application
- Supports multiple academic and business formats
- Critical for Responsible AI and content transparency
"""

from typing import List, Dict, Optional
from datetime import datetime

from app.models.report import Citation, CitationFormat
from app.core.logging import get_logger

logger = get_logger(__name__)


class CitationService:
    """
    Service for citation management and formatting.
    
    Handles citation style formatting, deduplication,
    and reference list generation.
    """
    
    def format_citation(
        self,
        citation: Citation,
        style: CitationFormat = CitationFormat.APA,
        inline: bool = False,
    ) -> str:
        """
        Format a citation according to specified style.
        
        Args:
            citation: Citation object to format
            style: Citation format (APA, MLA, Chicago, IEEE)
            inline: Whether to format as inline citation
        
        Returns:
            Formatted citation string
        """
        if inline:
            return self._format_inline_citation(citation, style)
        else:
            return self._format_reference_entry(citation, style)
    
    def _format_inline_citation(
        self,
        citation: Citation,
        style: CitationFormat,
    ) -> str:
        """Format inline citation marker."""
        if style == CitationFormat.APA:
            # APA: (Source, year)
            year = citation.retrieved_at.year if citation.retrieved_at else datetime.now().year
            return f"({citation.source}, {year})"
        elif style == CitationFormat.MLA:
            # MLA: (Source page)
            page = f" {citation.page_number}" if citation.page_number else ""
            return f"({citation.source}{page})"
        elif style == CitationFormat.CHICAGO:
            # Chicago: (Source)
            return f"({citation.source})"
        elif style == CitationFormat.IEEE:
            # IEEE: [number]
            return f"[{citation.id}]"
        else:
            return f"[{citation.source}]"
    
    def _format_reference_entry(
        self,
        citation: Citation,
        style: CitationFormat,
    ) -> str:
        """Format full reference entry."""
        source = citation.source
        url = f" Retrieved from {citation.url}" if citation.url else ""
        year = citation.retrieved_at.year if citation.retrieved_at else datetime.now().year
        
        if style == CitationFormat.APA:
            # APA format: Source. (Year). Title.
            page_info = f" (p. {citation.page_number})" if citation.page_number else ""
            return f"{source}. ({year}){page_info}.{url}"
        
        elif style == CitationFormat.MLA:
            # MLA format: Source. Title. Year.
            page_info = f" {citation.page_number}" if citation.page_number else ""
            return f"{source}.{page_info} {year}.{url}"
        
        elif style == CitationFormat.CHICAGO:
            # Chicago format: Source. "Title." Year.
            page_info = f", {citation.page_number}" if citation.page_number else ""
            return f"{source}{page_info}. {year}.{url}"
        
        elif style == CitationFormat.IEEE:
            # IEEE format: [number] Source, year.
            return f"[{citation.id}] {source}, {year}.{url}"
        
        else:
            return f"{source} ({year}){url}"
    
    def generate_reference_list(
        self,
        citations: List[Citation],
        style: CitationFormat = CitationFormat.APA,
    ) -> str:
        """
        Generate formatted reference list.
        
        Args:
            citations: List of citations
            style: Citation format style
        
        Returns:
            Formatted reference list as string
        """
        if not citations:
            return ""
        
        # Deduplicate citations by source
        unique_citations = self.deduplicate_citations(citations)
        
        # Sort citations (typically alphabetically by source)
        sorted_citations = sorted(unique_citations, key=lambda c: c.source.lower())
        
        # Format each citation
        references = []
        for citation in sorted_citations:
            formatted = self.format_citation(citation, style, inline=False)
            references.append(formatted)
        
        # Build reference list
        header = self._get_reference_list_header(style)
        reference_list = f"{header}\n\n" + "\n\n".join(references)
        
        logger.info(
            f"Generated reference list",
            extra={
                "citation_count": len(unique_citations),
                "style": style.value,
            }
        )
        
        return reference_list
    
    def _get_reference_list_header(self, style: CitationFormat) -> str:
        """Get appropriate header for reference list."""
        if style == CitationFormat.APA:
            return "References"
        elif style == CitationFormat.MLA:
            return "Works Cited"
        elif style == CitationFormat.CHICAGO:
            return "Bibliography"
        elif style == CitationFormat.IEEE:
            return "References"
        else:
            return "References"
    
    def deduplicate_citations(self, citations: List[Citation]) -> List[Citation]:
        """
        Remove duplicate citations.
        
        Args:
            citations: List of citations potentially with duplicates
        
        Returns:
            Deduplicated list of citations
        """
        seen_sources = set()
        unique_citations = []
        
        for citation in citations:
            # Use source + page as unique key
            key = f"{citation.source}:{citation.page_number or 'none'}"
            
            if key not in seen_sources:
                seen_sources.add(key)
                unique_citations.append(citation)
        
        logger.debug(
            f"Deduplicated citations",
            extra={
                "original_count": len(citations),
                "unique_count": len(unique_citations),
            }
        )
        
        return unique_citations
    
    def insert_inline_citations(
        self,
        content: str,
        citations: List[Citation],
        style: CitationFormat = CitationFormat.APA,
    ) -> str:
        """
        Insert inline citations into content.
        
        This is a placeholder for more sophisticated citation insertion.
        In production, would use NLP to identify citation points.
        
        Args:
            content: Content text
            citations: List of citations to insert
            style: Citation format
        
        Returns:
            Content with inline citations
        """
        # Simple implementation: append citations to end of each paragraph
        # Production version would use NLP to insert citations appropriately
        
        paragraphs = content.split("\n\n")
        
        if not citations:
            return content
        
        # Distribute citations across paragraphs
        citations_per_para = len(citations) // max(len(paragraphs), 1)
        citation_idx = 0
        
        annotated_paragraphs = []
        for para in paragraphs:
            if citation_idx < len(citations):
                inline_cite = self.format_citation(
                    citations[citation_idx],
                    style,
                    inline=True,
                )
                para = f"{para} {inline_cite}"
                citation_idx += 1
            
            annotated_paragraphs.append(para)
        
        return "\n\n".join(annotated_paragraphs)


# Global service instance
_citation_service: Optional[CitationService] = None


def get_citation_service() -> CitationService:
    """Get or create global citation service instance."""
    global _citation_service
    if _citation_service is None:
        _citation_service = CitationService()
    return _citation_service
