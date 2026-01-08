"""
Planning Agent - Multi-Agent Orchestrator

Responsibilities:
• Decompose user prompts into structured tasks
• Determine content structure (sections, subsections)
• Identify research queries needed
• Create execution plan for other agents
• Allocate token budget across sections

Architecture Decision:
- First agent in the pipeline - sets the foundation
- Uses structured output for clear execution plans
- Enables parallel execution when tasks are independent
- Critical for complex, multi-section content generation
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.services.openai_service import get_openai_service
from app.models.report import ContentType, AgentStep
from app.core.logging import get_logger
import time

logger = get_logger(__name__)


class ContentSection(BaseModel):
    """Planned content section."""
    title: str = Field(..., description="Section title")
    description: str = Field(..., description="What should be covered")
    research_queries: List[str] = Field(default_factory=list, description="Queries for research agent")
    word_count_target: int = Field(default=300, description="Target word count")


class ContentPlan(BaseModel):
    """Structured content generation plan."""
    title: str = Field(..., description="Content title")
    executive_summary_needed: bool = Field(default=True, description="Whether to include summary")
    sections: List[ContentSection] = Field(default_factory=list, description="Content sections")
    overall_strategy: str = Field(..., description="High-level content strategy")
    key_points: List[str] = Field(default_factory=list, description="Key points to cover")


class PlanningAgent:
    """
    Planning Agent - Orchestrates multi-agent content generation.
    
    This agent analyzes user prompts and creates detailed execution
    plans for the Research, Drafting, and Editing agents.
    
    Example:
        agent = PlanningAgent()
        plan = await agent.create_plan(
            prompt="Create a report on AI ethics in healthcare",
            content_type=ContentType.REPORT
        )
    """
    
    def __init__(self):
        """Initialize planning agent."""
        self.openai_service = get_openai_service()
        logger.info("Initialized Planning Agent")
    
    async def create_plan(
        self,
        prompt: str,
        content_type: ContentType = ContentType.REPORT,
        max_words: int = 2000,
    ) -> tuple[ContentPlan, AgentStep]:
        """
        Create structured content generation plan.
        
        Args:
            prompt: User's content request
            content_type: Type of content to generate
            max_words: Target total word count
        
        Returns:
            Tuple of (ContentPlan, AgentStep with execution metadata)
        """
        start_time = time.time()
        
        logger.info(
            f"Creating content plan",
            extra={
                "content_type": content_type.value,
                "max_words": max_words,
            }
        )
        
        # Build planning prompt
        planning_prompt = self._build_planning_prompt(
            user_prompt=prompt,
            content_type=content_type,
            max_words=max_words,
        )
        
        # Define expected output schema
        output_schema = {
            "title": "string",
            "executive_summary_needed": "boolean",
            "overall_strategy": "string",
            "key_points": ["string"],
            "sections": [
                {
                    "title": "string",
                    "description": "string",
                    "research_queries": ["string"],
                    "word_count_target": "integer"
                }
            ]
        }
        
        # Generate plan using LLM
        try:
            plan_dict = await self.openai_service.generate_structured_output(
                prompt=planning_prompt,
                output_schema=output_schema,
            )
            
            # Parse into ContentPlan model
            plan = ContentPlan(**plan_dict)
            
            duration = time.time() - start_time
            
            # Create agent step record
            agent_step = AgentStep(
                agent_name="PlanningAgent",
                step_type="planning",
                input_data={
                    "prompt": prompt,
                    "content_type": content_type.value,
                    "max_words": max_words,
                },
                output_data=plan.model_dump(),
                duration_seconds=duration,
            )
            
            logger.info(
                f"Created content plan successfully",
                extra={
                    "sections_count": len(plan.sections),
                    "duration_seconds": round(duration, 2),
                }
            )
            
            return plan, agent_step
            
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}", exc_info=True)
            duration = time.time() - start_time
            
            # Create error agent step
            agent_step = AgentStep(
                agent_name="PlanningAgent",
                step_type="planning",
                input_data={"prompt": prompt},
                output_data={},
                duration_seconds=duration,
                error=str(e),
            )
            
            raise
    
    def _build_planning_prompt(
        self,
        user_prompt: str,
        content_type: ContentType,
        max_words: int,
    ) -> str:
        """Build the planning prompt for the LLM."""
        
        content_type_guidance = self._get_content_type_guidance(content_type)
        
        prompt = f"""You are an expert content strategist and planner.

User Request: {user_prompt}

Content Type: {content_type.value}
Target Length: {max_words} words

Your task is to create a detailed content generation plan.

{content_type_guidance}

Requirements:
1. Create a compelling title
2. Determine if an executive summary is needed
3. Define 3-7 logical sections (fewer for short content, more for long reports)
4. For each section:
   - Provide a clear, descriptive title
   - Describe what should be covered in 1-2 sentences
   - Specify 1-3 research queries to find relevant information
   - Allocate a word count target (total across sections should match {max_words})
5. Formulate an overall content strategy
6. Identify 5-8 key points that must be addressed

The plan should be comprehensive, logical, and actionable for content generation agents.
"""
        
        return prompt
    
    def _get_content_type_guidance(self, content_type: ContentType) -> str:
        """Get specific guidance based on content type."""
        
        guidance_map = {
            ContentType.REPORT: """
For a REPORT:
- Include executive summary
- Use formal, professional tone
- Structure with clear sections: Introduction, Analysis, Findings, Recommendations, Conclusion
- Emphasize data and evidence
- Include citations for all claims
""",
            ContentType.SUMMARY: """
For a SUMMARY:
- Be concise and focused
- Use bullet points or short paragraphs
- Highlight only the most critical information
- No need for extensive sections
""",
            ContentType.ARTICLE: """
For an ARTICLE:
- Engaging introduction with a hook
- Logical flow of ideas
- Mix of information and narrative
- Strong conclusion
""",
            ContentType.MARKETING_COPY: """
For MARKETING COPY:
- Focus on benefits and value proposition
- Use persuasive language
- Include clear call-to-action
- Emphasize customer pain points and solutions
""",
            ContentType.EMAIL: """
For an EMAIL:
- Clear subject line (use as title)
- Brief and scannable
- Professional but personable tone
- Specific call-to-action
""",
            ContentType.PRESENTATION: """
For a PRESENTATION:
- Slide-friendly structure
- Each section = potential slide
- Concise, impactful content
- Visual-first thinking
""",
        }
        
        return guidance_map.get(content_type, "Create well-structured, professional content.")


# Global agent instance
_planning_agent: PlanningAgent | None = None


def get_planning_agent() -> PlanningAgent:
    """Get or create global planning agent instance."""
    global _planning_agent
    if _planning_agent is None:
        _planning_agent = PlanningAgent()
    return _planning_agent
