"""
Azure AI Search Integration for RAG

Responsibilities:
• Connect to Azure AI Search index for document retrieval
• Perform semantic and vector search over enterprise documents
• Extract relevant passages with metadata for citation
• Support hybrid search (keyword + semantic + vector)
• Handle search errors and retries gracefully

Architecture Decision:
- Centralized search logic enables consistent RAG behavior
- Returns structured results with relevance scores for citation
- Supports both semantic and vector search for better relevance
- Implements result re-ranking for optimal context selection
- Provides detailed metadata for transparency and attribution
"""

from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import time

from app.core.config import settings
from app.core.logging import get_logger
from app.models.report import Citation

logger = get_logger(__name__)


class AISearchError(Exception):
    """Base exception for AI Search errors."""
    pass


class SearchResult:
    """
    Represents a single search result from Azure AI Search.
    
    Encapsulates document content and metadata needed for RAG and citation.
    """
    
    def __init__(
        self,
        document_id: str,
        content: str,
        title: Optional[str] = None,
        source: Optional[str] = None,
        url: Optional[str] = None,
        score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.document_id = document_id
        self.content = content
        self.title = title or "Unknown Document"
        self.source = source or self.title
        self.url = url
        self.score = score
        self.metadata = metadata or {}
    
    def to_citation(self) -> Citation:
        """
        Convert search result to a Citation object.
        
        Returns:
            Citation with source attribution
        """
        return Citation(
            text=self.content[:500],  # Truncate to reasonable excerpt
            source=self.source,
            source_type="document",
            relevance_score=self.score,
            url=self.url,
        )
    
    def __repr__(self) -> str:
        return f"SearchResult(id={self.document_id}, score={self.score:.2f}, source={self.source})"


class AzureAISearchClient:
    """
    Production-ready Azure AI Search client for RAG.
    
    Features:
    - Semantic search with Azure AI
    - Vector search support
    - Hybrid search combining multiple strategies
    - Automatic retry on transient failures
    - Result re-ranking
    - Citation-ready output
    
    Example:
        client = AzureAISearchClient()
        results = await client.search(
            query="What are the benefits of AI in healthcare?",
            top_k=5
        )
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        index_name: Optional[str] = None,
    ):
        """
        Initialize Azure AI Search client.
        
        Args:
            endpoint: AI Search service endpoint
            api_key: AI Search admin key
            index_name: Name of the search index
        """
        self.endpoint = endpoint or settings.AI_SEARCH_ENDPOINT
        self.api_key = api_key or settings.AI_SEARCH_API_KEY
        self.index_name = index_name or settings.AI_SEARCH_INDEX_NAME
        
        # Initialize search client
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.api_key),
        )
        
        logger.info(
            f"Initialized Azure AI Search client",
            extra={"index_name": self.index_name}
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(AzureError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[str] = None,
        use_semantic: bool = True,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Search documents using Azure AI Search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: OData filter expression
            use_semantic: Enable semantic search (if configured)
            min_score: Minimum relevance score threshold
        
        Returns:
            List of SearchResult objects ordered by relevance
        
        Raises:
            AISearchError: On search failures after retries
        """
        start_time = time.time()
        top_k = top_k or settings.AI_SEARCH_TOP_K
        min_score = min_score if min_score is not None else settings.AI_SEARCH_MIN_SCORE
        
        try:
            logger.debug(
                f"Executing search query",
                extra={
                    "query": query[:100],
                    "top_k": top_k,
                    "use_semantic": use_semantic,
                }
            )
            
            # Configure search parameters
            search_params = {
                "search_text": query,
                "top": top_k,
                "filter": filters,
                "include_total_count": True,
            }
            
            # Enable semantic search if configured
            if use_semantic and settings.AI_SEARCH_SEMANTIC_CONFIG:
                search_params.update({
                    "query_type": QueryType.SEMANTIC,
                    "semantic_configuration_name": settings.AI_SEARCH_SEMANTIC_CONFIG,
                    "query_caption": QueryCaptionType.EXTRACTIVE,
                    "query_answer": QueryAnswerType.EXTRACTIVE,
                })
            
            # Execute search
            results = self.client.search(**search_params)
            
            # Parse results
            search_results = []
            for result in results:
                # Extract relevance score
                score = result.get("@search.score", 0.0)
                
                # Apply minimum score threshold
                if score < min_score:
                    continue
                
                # Extract semantic captions if available
                content = result.get("content", "")
                if "@search.captions" in result and result["@search.captions"]:
                    # Use semantic caption for better relevance
                    captions = result["@search.captions"]
                    if captions and len(captions) > 0:
                        content = captions[0].get("text", content)
                
                search_result = SearchResult(
                    document_id=result.get("id", result.get("document_id", "unknown")),
                    content=content,
                    title=result.get("title"),
                    source=result.get("source") or result.get("title"),
                    url=result.get("url"),
                    score=score,
                    metadata={
                        "page_number": result.get("page_number"),
                        "created_at": result.get("created_at"),
                        "author": result.get("author"),
                        "category": result.get("category"),
                    },
                )
                search_results.append(search_result)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Search completed successfully",
                extra={
                    "results_count": len(search_results),
                    "duration_seconds": round(duration, 2),
                    "min_score": min_score,
                }
            )
            
            return search_results
            
        except AzureError as e:
            duration = time.time() - start_time
            logger.error(
                f"Search failed: {str(e)}",
                extra={
                    "duration_seconds": round(duration, 2),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise AISearchError(f"Search error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected search error: {str(e)}", exc_info=True)
            raise AISearchError(f"Unexpected error: {str(e)}") from e
    
    def search_with_vector(
        self,
        query: str,
        vector: List[float],
        top_k: Optional[int] = None,
        vector_field: str = "content_vector",
    ) -> List[SearchResult]:
        """
        Perform hybrid search using both text and vector.
        
        Args:
            query: Text search query
            vector: Query embedding vector
            top_k: Number of results
            vector_field: Name of vector field in index
        
        Returns:
            List of SearchResult objects
        """
        top_k = top_k or settings.AI_SEARCH_TOP_K
        
        try:
            # Create vector query
            vector_query = VectorizedQuery(
                vector=vector,
                k_nearest_neighbors=top_k,
                fields=vector_field,
            )
            
            # Execute hybrid search
            results = self.client.search(
                search_text=query,
                vector_queries=[vector_query],
                top=top_k,
            )
            
            # Parse results (similar to regular search)
            search_results = []
            for result in results:
                search_result = SearchResult(
                    document_id=result.get("id", "unknown"),
                    content=result.get("content", ""),
                    title=result.get("title"),
                    source=result.get("source") or result.get("title"),
                    url=result.get("url"),
                    score=result.get("@search.score", 0.0),
                )
                search_results.append(search_result)
            
            logger.info(f"Vector search completed: {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}", exc_info=True)
            raise AISearchError(f"Vector search error: {str(e)}") from e
    
    def get_context_for_rag(
        self,
        query: str,
        top_k: int = 5,
        max_context_length: int = 4000,
    ) -> tuple[str, List[Citation]]:
        """
        Retrieve and format context for RAG.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            max_context_length: Maximum total context length in characters
        
        Returns:
            Tuple of (formatted_context, citations)
        
        Example:
            context, citations = client.get_context_for_rag(
                "What are AI ethics principles?"
            )
        """
        # Search for relevant documents
        results = self.search(query=query, top_k=top_k)
        
        # Build context string and citations
        context_parts = []
        citations = []
        current_length = 0
        
        for idx, result in enumerate(results, 1):
            # Create citation
            citation = result.to_citation()
            citations.append(citation)
            
            # Format context entry
            entry = f"[Source {idx}: {result.source}]\n{result.content}\n\n"
            entry_length = len(entry)
            
            # Check length limit
            if current_length + entry_length > max_context_length:
                # Truncate if needed
                remaining = max_context_length - current_length
                if remaining > 100:  # Only add if reasonable space left
                    entry = entry[:remaining] + "...\n\n"
                    context_parts.append(entry)
                break
            
            context_parts.append(entry)
            current_length += entry_length
        
        context = "".join(context_parts)
        
        logger.debug(
            f"RAG context prepared",
            extra={
                "query": query[:100],
                "sources_count": len(citations),
                "context_length": len(context),
            }
        )
        
        return context, citations
    
    def close(self) -> None:
        """Close the search client."""
        self.client.close()


# Global client instance
_search_client: Optional[AzureAISearchClient] = None


def get_search_client() -> AzureAISearchClient:
    """
    Get or create global Azure AI Search client.
    
    Returns:
        Shared AzureAISearchClient instance
    """
    global _search_client
    if _search_client is None:
        _search_client = AzureAISearchClient()
    return _search_client


def search_documents(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Simplified search interface.
    
    Args:
        query: Search query
        top_k: Number of results
    
    Returns:
        List of search results
    """
    client = get_search_client()
    return client.search(query=query, top_k=top_k)