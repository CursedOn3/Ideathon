"""
Drafting Agent - Content Generation

Responsibilities:
• Generate content sections based on research context
• Follow content plan structure
• Maintain consistent tone and style
• Incorporate citations naturally
• Respect word count targets

Architecture Decision:
- Receives structured input from Planning and Research agents
- Generates one section at a time for quality and control
- Uses retrieved context to ground all claims
- Implements anti-hallucination safeguards
- Tracks token usage for cost management
"""

from typing import List, Dict, Any, Tuple
import time

from app.services.openai_service import get_openai_service, OpenAIService
from app.models.report import Citation, AgentStep, ContentType
from app.core.logging import get_logger

logger = get_logger(__name__)


class DraftingAgent:
    """
    Drafting Agent - Generates content from research and plan.
    
    Creates well-structured, factual content grounded in
    retrieved enterprise documents.
    
    Example:
        agent = DraftingAgent()
        content = await agent.draft_section(
            title="Introduction",
            description="Overview of AI ethics",
            context="[Retrieved documents...]",
            word_count=300
        )
    """
    
    def __init__(self, openai_service: OpenAIService | None = None):
        """Initialize drafting agent."""
        self.openai_service = openai_service or get_openai_service()
        logger.info("Initialized Drafting Agent")
    
    async def draft_section(
        self,
        title: str,
        description: str,
        context: str,
        citations: List[Citation],
        word_count_target: int = 300,
        content_type: ContentType = ContentType.REPORT,
        overall_topic: str = "",
    ) -> Tuple[str, AgentStep]:
        """
        Generate a single content section.
        
        Args:
            title: Section title
            description: What the section should cover
            context: Retrieved research context
            citations: Available citations
            word_count_target: Target word count
            content_type: Type of content being generated
            overall_topic: Overall content topic for context
        
        Returns:
            Tuple of (generated_content, AgentStep)
        """
        start_time = time.time()
        
        logger.info(
            f"Drafting section: {title}",
            extra={"word_count_target": word_count_target}
        )
        
        # Build drafting prompt
        prompt = self._build_drafting_prompt(
            title=title,
            description=description,
            word_count_target=word_count_target,
            content_type=content_type,
            overall_topic=overall_topic,
        )
        
        # Build system instruction
        system_instruction = self._build_system_instruction(content_type)
        
        try:
            # Generate content
            content = await self.openai_service.generate_with_context(
                prompt=prompt,
                context=context,
                system_instruction=system_instruction,
                temperature=0.7,
                max_tokens=self._calculate_max_tokens(word_count_target),
            )
            
            duration = time.time() - start_time
            
            # Create agent step record
            agent_step = AgentStep(
                agent_name="DraftingAgent",
                step_type="drafting",
                input_data={
                    "title": title,
                    "description": description,
                    "word_count_target": word_count_target,
                    "context_length": len(context),
                },
                output_data={
                    "content_length": len(content),
                    "word_count": len(content.split()),
                },
                duration_seconds=duration,
                tokens_used=self._estimate_tokens(content),
            )
            
            logger.info(
                f"Section drafted successfully",
                extra={
                    "title": title,
                    "word_count": len(content.split()),
                    "target": word_count_target,
                    "duration_seconds": round(duration, 2),
                }
            )
            
            return content, agent_step
            
        except Exception as e:
            logger.error(f"Drafting failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="DraftingAgent",
                step_type="drafting",
                input_data={"title": title},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            raise
    
    async def draft_executive_summary(
        self,
        full_content: str,
        title: str,
        max_words: int = 150,
    ) -> Tuple[str, AgentStep]:
        """
        Generate executive summary from full content.
        
        Args:
            full_content: Complete content to summarize
            title: Content title
            max_words: Maximum words for summary
        
        Returns:
            Tuple of (summary, AgentStep)
        """
        start_time = time.time()
        
        logger.info("Generating executive summary")
        
        prompt = f"""Create a concise executive summary for the following content.

Title: {title}

Requirements:
- Maximum {max_words} words
- Highlight key findings and main points
- Use clear, professional language
- Be specific and actionable

Content to summarize:
{full_content[:6000]}  # Truncate if very long
"""
        
        system_instruction = """You are an expert at creating concise, impactful executive summaries.
Focus on the most important takeaways and recommendations."""
        
        try:
            summary = await self.openai_service.generate_with_context(
                prompt=prompt,
                context="",
                system_instruction=system_instruction,
                temperature=0.5,
                max_tokens=self._calculate_max_tokens(max_words),
            )
            
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="DraftingAgent",
                step_type="summary_generation",
                input_data={"full_content_length": len(full_content)},
                output_data={"summary_length": len(summary)},
                duration_seconds=duration,
            )
            
            logger.info(f"Executive summary generated ({len(summary.split())} words)")
            
            return summary, agent_step
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            agent_step = AgentStep(
                agent_name="DraftingAgent",
                step_type="summary_generation",
                input_data={},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            raise
    
    def _build_drafting_prompt(
        self,
        title: str,
        description: str,
        word_count_target: int,
        content_type: ContentType,
        overall_topic: str,
    ) -> str:
        """Build the drafting prompt."""
        
        prompt = f"""Generate content for the following section:

Section Title: {title}
Description: {description}
Target Length: ~{word_count_target} words
Content Type: {content_type.value}
"""
        
        if overall_topic:
            prompt += f"Overall Topic: {overall_topic}\n"
        
        prompt += f"""
Requirements:
1. Write clear, professional content
2. Base ALL claims on the provided context
3. Do NOT make up facts or statistics
4. If context lacks information, acknowledge the limitation
5. Use specific examples and evidence
6. Maintain logical flow
7. Target approximately {word_count_target} words

Write the section content now:
"""
        
        return prompt
    
    def _build_system_instruction(self, content_type: ContentType) -> str:
        """Build system instruction based on content type."""
        
        base_instruction = """You are an expert business content writer specializing in enterprise content.

CRITICAL RULES:
1. Only use information from the provided context
2. Never fabricate data, statistics, or facts
3. If asked about something not in context, state that clearly
4. Cite sources appropriately
5. Write in a professional, clear style

"""
        
        type_specific = {
            ContentType.REPORT: "Use formal, analytical tone. Focus on facts and evidence.",
            ContentType.ARTICLE: "Use engaging, informative tone. Balance data with narrative.",
            ContentType.MARKETING_COPY: "Use persuasive, benefit-focused language. Emphasize value.",
            ContentType.EMAIL: "Use professional but conversational tone. Be concise.",
            ContentType.SUMMARY: "Use clear, bullet-point style. Focus on key points only.",
            ContentType.PRESENTATION: "Use concise, impactful language. Think in slide format.",
        }
        
        return base_instruction + type_specific.get(content_type, "")
    
    def _calculate_max_tokens(self, word_count: int) -> int:
        """Calculate max tokens based on word count."""
        # Rule of thumb: 1 word ≈ 1.3 tokens
        # Add 20% buffer
        return int(word_count * 1.3 * 1.2)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4


# Global agent instance
_drafting_agent: DraftingAgent | None = None


def get_drafting_agent() -> DraftingAgent:
    """Get or create global drafting agent instance."""
    global _drafting_agent
    if _drafting_agent is None:
        _drafting_agent = DraftingAgent()
    return _drafting_agent
