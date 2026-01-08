"""
Editing Agent - Quality Assurance & Refinement

Responsibilities:
• Review and improve generated content
• Check grammar, clarity, and coherence
• Ensure consistent tone and style
• Verify citation accuracy
• Format content professionally
• Apply final polish

Architecture Decision:
- Final quality gate before content delivery
- Focuses on refinement, not rewriting
- Validates all citations are properly attributed
- Ensures brand voice and style compliance
- Critical for production-ready output
"""

from typing import Tuple, List
import time

from app.services.openai_service import get_openai_service, OpenAIService
from app.services.citation_service import get_citation_service, CitationService
from app.models.report import Citation, AgentStep, ContentType, CitationFormat
from app.core.logging import get_logger

logger = get_logger(__name__)


class EditingAgent:
    """
    Editing Agent - Refines and polishes generated content.
    
    Performs quality assurance, grammar checks, style refinement,
    and citation validation on drafted content.
    
    Example:
        agent = EditingAgent()
        edited = await agent.edit_content(
            content="Draft content...",
            citations=[...],
            content_type=ContentType.REPORT
        )
    """
    
    def __init__(
        self,
        openai_service: OpenAIService | None = None,
        citation_service: CitationService | None = None,
    ):
        """Initialize editing agent."""
        self.openai_service = openai_service or get_openai_service()
        self.citation_service = citation_service or get_citation_service()
        logger.info("Initialized Editing Agent")
    
    async def edit_content(
        self,
        content: str,
        citations: List[Citation],
        content_type: ContentType = ContentType.REPORT,
        citation_format: CitationFormat = CitationFormat.APA,
    ) -> Tuple[str, AgentStep]:
        """
        Edit and refine content.
        
        Args:
            content: Draft content to edit
            citations: List of citations used
            content_type: Type of content
            citation_format: Preferred citation format
        
        Returns:
            Tuple of (edited_content, AgentStep)
        """
        start_time = time.time()
        
        logger.info(
            f"Editing content",
            extra={
                "content_length": len(content),
                "citations_count": len(citations),
            }
        )
        
        # Build editing prompt
        prompt = self._build_editing_prompt(content, content_type)
        
        # System instruction
        system_instruction = """You are an expert editor specializing in business and technical content.

Your role is to REFINE, not rewrite. Focus on:
1. Grammar, punctuation, and spelling
2. Clarity and readability
3. Logical flow between paragraphs
4. Consistent tone and style
5. Professional formatting

CRITICAL RULES:
- Preserve all factual content
- Do not remove or alter citations
- Do not add new information
- Make minimal, targeted improvements
- Maintain the author's voice
"""
        
        try:
            # Edit content
            edited_content = await self.openai_service.generate_with_context(
                prompt=prompt,
                context="",  # No additional context needed for editing
                system_instruction=system_instruction,
                temperature=0.3,  # Lower temperature for consistent editing
                max_tokens=len(content) // 2,  # Roughly same length as input
            )
            
            # Add reference list if citations exist
            if citations:
                reference_list = self.citation_service.generate_reference_list(
                    citations=citations,
                    style=citation_format,
                )
                edited_content += f"\n\n{reference_list}"
            
            duration = time.time() - start_time
            
            # Create agent step record
            agent_step = AgentStep(
                agent_name="EditingAgent",
                step_type="editing",
                input_data={
                    "original_length": len(content),
                    "citations_count": len(citations),
                },
                output_data={
                    "edited_length": len(edited_content),
                    "word_count": len(edited_content.split()),
                },
                duration_seconds=duration,
            )
            
            logger.info(
                f"Content edited successfully",
                extra={
                    "original_words": len(content.split()),
                    "edited_words": len(edited_content.split()),
                    "duration_seconds": round(duration, 2),
                }
            )
            
            return edited_content, agent_step
            
        except Exception as e:
            logger.error(f"Editing failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="EditingAgent",
                step_type="editing",
                input_data={},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            raise
    
    async def fact_check(
        self,
        content: str,
        citations: List[Citation],
    ) -> Tuple[bool, List[str], AgentStep]:
        """
        Verify content claims against citations.
        
        Args:
            content: Content to fact-check
            citations: Available citations
        
        Returns:
            Tuple of (all_verified, issues_found, AgentStep)
        """
        start_time = time.time()
        
        logger.info("Performing fact-check")
        
        # Build citation context
        citation_context = "\n\n".join([
            f"[{i+1}] {cite.source}: {cite.text}"
            for i, cite in enumerate(citations)
        ])
        
        prompt = f"""Review the following content and verify that all factual claims are supported by the provided sources.

Content:
{content}

Available Sources:
{citation_context}

Identify any claims that are NOT supported by the sources. List them clearly.
If all claims are supported, respond with "VERIFIED: All claims are supported."
"""
        
        system_instruction = """You are a meticulous fact-checker.
Your job is to ensure every claim has source support.
Be thorough but fair in your assessment."""
        
        try:
            result = await self.openai_service.generate_with_context(
                prompt=prompt,
                context="",
                system_instruction=system_instruction,
                temperature=0.2,
            )
            
            # Parse result
            verified = "VERIFIED" in result.upper()
            issues = [] if verified else [result]
            
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="EditingAgent",
                step_type="fact_checking",
                input_data={"content_length": len(content)},
                output_data={"verified": verified, "issues_count": len(issues)},
                duration_seconds=duration,
            )
            
            logger.info(
                f"Fact-check completed: {'PASSED' if verified else 'ISSUES FOUND'}",
                extra={"duration_seconds": round(duration, 2)}
            )
            
            return verified, issues, agent_step
            
        except Exception as e:
            logger.error(f"Fact-check failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="EditingAgent",
                step_type="fact_checking",
                input_data={},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            return False, [f"Fact-check error: {str(e)}"], agent_step
    
    def _build_editing_prompt(self, content: str, content_type: ContentType) -> str:
        """Build the editing prompt."""
        
        type_guidance = {
            ContentType.REPORT: "formal and analytical",
            ContentType.ARTICLE: "engaging and informative",
            ContentType.MARKETING_COPY: "persuasive and compelling",
            ContentType.EMAIL: "professional but conversational",
            ContentType.SUMMARY: "concise and clear",
            ContentType.PRESENTATION: "punchy and impactful",
        }
        
        tone = type_guidance.get(content_type, "professional")
        
        prompt = f"""Edit and refine the following content.

Content Type: {content_type.value}
Desired Tone: {tone}

Content to Edit:
{content}

Instructions:
1. Fix any grammar, spelling, or punctuation errors
2. Improve clarity and readability
3. Ensure smooth transitions between ideas
4. Maintain consistent {tone} tone
5. Keep all factual content and citations intact
6. Format professionally with proper paragraphs

Provide the edited version:
"""
        
        return prompt


# Global agent instance
_editing_agent: EditingAgent | None = None


def get_editing_agent() -> EditingAgent:
    """Get or create global editing agent instance."""
    global _editing_agent
    if _editing_agent is None:
        _editing_agent = EditingAgent()
    return _editing_agent
