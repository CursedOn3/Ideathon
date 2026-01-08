"""
Research Agent - RAG-Powered Information Retrieval

Responsibilities:
• Execute research queries using Azure AI Search
• Retrieve relevant enterprise documents
• Build context for each content section
• Track source citations
• Filter and validate retrieved information

Architecture Decision:
- Centralized research logic ensures consistent RAG behavior
- Returns both context AND citations for transparency
- Supports per-section research for focused retrieval
- Critical for grounding content in enterprise knowledge
"""

from typing import List, Tuple, Dict, Any
import time

from app.services.rag_service import get_rag_service, RAGService
from app.models.report import Citation, AgentStep
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResearchResult:
    """Container for research results."""
    
    def __init__(self, context: str, citations: List[Citation]):
        self.context = context
        self.citations = citations
    
    def __repr__(self) -> str:
        return f"ResearchResult(citations={len(self.citations)}, context_length={len(self.context)})"


class ResearchAgent:
    """
    Research Agent - Retrieves and aggregates information using RAG.
    
    Uses Azure AI Search to find relevant enterprise documents
    and builds context for the Drafting Agent to use.
    
    Example:
        agent = ResearchAgent()
        result = agent.research(
            queries=["AI ethics principles", "Healthcare AI regulations"]
        )
    """
    
    def __init__(self, rag_service: RAGService | None = None):
        """Initialize research agent."""
        self.rag_service = rag_service or get_rag_service()
        logger.info("Initialized Research Agent")
    
    def research(
        self,
        queries: List[str],
        top_k_per_query: int = 3,
        max_total_context: int = 4000,
    ) -> Tuple[ResearchResult, AgentStep]:
        """
        Execute research queries and aggregate results.
        
        Args:
            queries: List of research queries
            top_k_per_query: Documents to retrieve per query
            max_total_context: Maximum total context length
        
        Returns:
            Tuple of (ResearchResult, AgentStep with metadata)
        """
        start_time = time.time()
        
        logger.info(
            f"Starting research",
            extra={"query_count": len(queries), "top_k": top_k_per_query}
        )
        
        try:
            all_context_parts = []
            all_citations = []
            tokens_used = 0
            
            for query in queries:
                logger.debug(f"Researching: {query}")
                
                # Retrieve context and citations for this query
                context, citations = self.rag_service.retrieve_and_build_context(
                    query=query,
                    top_k=top_k_per_query,
                    max_context_tokens=max_total_context // len(queries),  # Distribute budget
                )
                
                if context:
                    all_context_parts.append(f"# Research: {query}\n{context}")
                    all_citations.extend(citations)
            
            # Combine all research
            combined_context = "\n\n".join(all_context_parts)
            
            # Deduplicate citations
            unique_citations = self._deduplicate_citations(all_citations)
            
            duration = time.time() - start_time
            
            # Create result
            result = ResearchResult(
                context=combined_context,
                citations=unique_citations,
            )
            
            # Create agent step record
            agent_step = AgentStep(
                agent_name="ResearchAgent",
                step_type="research",
                input_data={
                    "queries": queries,
                    "top_k_per_query": top_k_per_query,
                },
                output_data={
                    "context_length": len(combined_context),
                    "citations_count": len(unique_citations),
                },
                duration_seconds=duration,
            )
            
            logger.info(
                f"Research completed",
                extra={
                    "queries_executed": len(queries),
                    "citations_found": len(unique_citations),
                    "context_length": len(combined_context),
                    "duration_seconds": round(duration, 2),
                }
            )
            
            return result, agent_step
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="ResearchAgent",
                step_type="research",
                input_data={"queries": queries},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            raise
    
    def research_section(
        self,
        section_title: str,
        research_queries: List[str],
        word_count_target: int,
    ) -> Tuple[ResearchResult, AgentStep]:
        """
        Research for a specific content section.
        
        Args:
            section_title: Title of the section
            research_queries: Queries specific to this section
            word_count_target: Target word count for the section
        
        Returns:
            Tuple of (ResearchResult, AgentStep)
        """
        logger.info(f"Researching section: {section_title}")
        
        # Adjust context budget based on word count target
        # Rule of thumb: 1 word ≈ 1.3 tokens, allocate 2x for context
        context_budget = int(word_count_target * 1.3 * 2)
        
        return self.research(
            queries=research_queries,
            top_k_per_query=2,  # Fewer per query, more focused
            max_total_context=context_budget,
        )
    
    def _deduplicate_citations(self, citations: List[Citation]) -> List[Citation]:
        """Remove duplicate citations based on source and page."""
        seen = set()
        unique = []
        
        for citation in citations:
            key = f"{citation.source}:{citation.page_number or 'none'}"
            if key not in seen:
                seen.add(key)
                unique.append(citation)
        
        return unique


# Global agent instance
_research_agent: ResearchAgent | None = None


def get_research_agent() -> ResearchAgent:
    """Get or create global research agent instance."""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent()
    return _research_agent
