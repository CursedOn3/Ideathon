"""
RAG (Retrieval-Augmented Generation) Service

Responsibilities:
• Orchestrate document retrieval and context building
• Manage context window and token limits
• Rank and filter retrieved documents
• Build optimized context for LLM consumption
• Track source attribution for citations

Architecture Decision:
- Centralizes RAG logic for consistency across agents
- Implements intelligent context truncation
- Prioritizes relevance over quantity
- Preserves source metadata for citation tracking
"""

from typing import List, Tuple, Optional
from app.integrations.ai_search import get_search_client, SearchResult
from app.models.report import Citation
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RAGService:
    """
    Service for Retrieval-Augmented Generation.
    
    Handles document retrieval, context building, and
    citation tracking for grounded content generation.
    """
    
    def __init__(self):
        """Initialize RAG service with search client."""
        self.search_client = get_search_client()
    
    def retrieve_and_build_context(
        self,
        query: str,
        top_k: int = 5,
        max_context_tokens: int = 3000,
    ) -> Tuple[str, List[Citation]]:
        """
        Retrieve relevant documents and build context string.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            max_context_tokens: Maximum context size (approximate)
        
        Returns:
            Tuple of (context_string, citations_list)
        """
        logger.info(f"Retrieving context for query: {query[:100]}")
        
        # Search for relevant documents
        search_results = self.search_client.search(
            query=query,
            top_k=top_k,
            use_semantic=True,
        )
        
        if not search_results:
            logger.warning(f"No search results found for query: {query}")
            return "", []
        
        # Build context and extract citations
        context_parts = []
        citations = []
        estimated_tokens = 0
        
        for idx, result in enumerate(search_results, 1):
            # Create citation
            citation = result.to_citation()
            citation.id = f"cite-{idx}"
            citations.append(citation)
            
            # Format document for context
            doc_context = self._format_document_for_context(
                content=result.content,
                source=result.source,
                citation_number=idx,
            )
            
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            doc_tokens = len(doc_context) // 4
            
            if estimated_tokens + doc_tokens > max_context_tokens:
                logger.debug(f"Context limit reached, truncating at {idx} documents")
                break
            
            context_parts.append(doc_context)
            estimated_tokens += doc_tokens
        
        context = "\n\n".join(context_parts)
        
        logger.info(
            f"Built RAG context",
            extra={
                "documents_included": len(citations),
                "context_length": len(context),
                "estimated_tokens": estimated_tokens,
            }
        )
        
        return context, citations
    
    def _format_document_for_context(
        self,
        content: str,
        source: str,
        citation_number: int,
    ) -> str:
        """
        Format a document for LLM context.
        
        Args:
            content: Document content
            source: Source attribution
            citation_number: Citation reference number
        
        Returns:
            Formatted document string
        """
        return f"[{citation_number}] Source: {source}\n{content}"
    
    def rerank_results(
        self,
        results: List[SearchResult],
        query: str,
    ) -> List[SearchResult]:
        """
        Re-rank search results for better relevance.
        
        Currently returns results as-is (sorted by search score).
        Future: Implement cross-encoder re-ranking.
        
        Args:
            results: Initial search results
            query: Original query
        
        Returns:
            Re-ranked results
        """
        # For now, trust AI Search's scoring
        # Future enhancement: Use cross-encoder model
        return results


# Global service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
