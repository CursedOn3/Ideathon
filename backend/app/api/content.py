"""
Content Generation API Routes

Responsibilities:
• Expose content generation endpoints
• Orchestrate multi-agent workflow
• Handle request validation
• Manage async operations
• Return structured responses

Architecture Decision:
- RESTful API design
- Async endpoints for better performance
- Clear request/response models
- Comprehensive error handling
- Detailed logging for debugging
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio

from app.models.report import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    Report,
    ContentSection,
    ContentStatus,
    AgentStep,
)
from app.agents.planning_agent import get_planning_agent
from app.agents.research_agent import get_research_agent
from app.agents.drafting_agent import get_drafting_agent
from app.agents.editing_agent import get_editing_agent
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
    """
    Generate content using multi-agent AI orchestration.
    
    Workflow:
    1. Planning Agent: Decompose request into structured plan
    2. Research Agent: Retrieve relevant documents for each section
    3. Drafting Agent: Generate content for each section
    4. Editing Agent: Refine and polish final content
    
    Args:
        request: Content generation request with prompt and parameters
    
    Returns:
        ContentGenerationResponse with generated report or error
    """
    logger.info(
        f"Content generation request received",
        extra={
            "prompt": request.prompt[:100],
            "content_type": request.content_type.value,
        }
    )
    
    try:
        # Initialize report
        report = Report(
            title="",  # Will be set by planning agent
            prompt=request.prompt,
            content_type=request.content_type,
            citation_format=request.citation_format,
            status=ContentStatus.GENERATING,
            tags=request.tags,
            metadata=request.metadata,
        )
        
        # Step 1: Planning
        logger.info("Step 1: Planning")
        planning_agent = get_planning_agent()
        plan, planning_step = await planning_agent.create_plan(
            prompt=request.prompt,
            content_type=request.content_type,
            max_words=request.max_words or 2000,
        )
        
        report.title = plan.title
        report.add_agent_step(planning_step)
        
        # Step 2: Research for each section
        logger.info(f"Step 2: Research ({len(plan.sections)} sections)")
        research_agent = get_research_agent()
        drafting_agent = get_drafting_agent()
        
        all_citations = []
        
        for section_plan in plan.sections:
            # Research for this section
            if section_plan.research_queries:
                research_result, research_step = research_agent.research(
                    queries=section_plan.research_queries,
                    top_k_per_query=2,
                )
                report.add_agent_step(research_step)
                all_citations.extend(research_result.citations)
                context = research_result.context
            else:
                context = ""
            
            # Draft this section
            logger.info(f"Drafting section: {section_plan.title}")
            content, drafting_step = await drafting_agent.draft_section(
                title=section_plan.title,
                description=section_plan.description,
                context=context,
                citations=research_result.citations if section_plan.research_queries else [],
                word_count_target=section_plan.word_count_target,
                content_type=request.content_type,
                overall_topic=request.prompt,
            )
            report.add_agent_step(drafting_step)
            
            # Add section to report
            report.add_section(
                title=section_plan.title,
                content=content,
                citations=research_result.citations if section_plan.research_queries else [],
            )
        
        # Step 3: Generate executive summary if needed
        if plan.executive_summary_needed:
            logger.info("Step 3: Generating executive summary")
            full_content = "\n\n".join([s.content for s in report.sections])
            summary, summary_step = await drafting_agent.draft_executive_summary(
                full_content=full_content,
                title=report.title,
                max_words=150,
            )
            report.executive_summary = summary
            report.add_agent_step(summary_step)
        
        # Step 4: Editing
        logger.info("Step 4: Final editing")
        editing_agent = get_editing_agent()
        
        # Combine all content for editing
        full_draft = ""
        if report.executive_summary:
            full_draft += f"# Executive Summary\n\n{report.executive_summary}\n\n"
        
        for section in report.sections:
            full_draft += f"# {section.title}\n\n{section.content}\n\n"
        
        # Edit full content
        edited_content, editing_step = await editing_agent.edit_content(
            content=full_draft,
            citations=all_citations,
            content_type=request.content_type,
            citation_format=request.citation_format,
        )
        report.add_agent_step(editing_step)
        
        # Store all citations
        report.citations = all_citations
        
        # Mark as completed
        report.mark_completed()
        
        logger.info(
            f"Content generation completed successfully",
            extra={
                "report_id": report.id,
                "sections": len(report.sections),
                "citations": len(report.citations),
                "total_tokens": report.total_tokens_used,
            }
        )
        
        return ContentGenerationResponse(
            success=True,
            report=report,
            message=f"Successfully generated {len(report.sections)} sections with {len(report.citations)} citations",
        )
        
    except Exception as e:
        logger.error(f"Content generation failed: {str(e)}", exc_info=True)
        
        return ContentGenerationResponse(
            success=False,
            error=str(e),
            message="Content generation failed. Please try again.",
        )


@router.get("/report/{report_id}", response_model=Report)
async def get_report(report_id: str) -> Report:
    """
    Get a generated report by ID.
    
    Note: In production, this would retrieve from a database.
    Currently returns a placeholder response.
    
    Args:
        report_id: Unique report identifier
    
    Returns:
        Report object
    """
    # TODO: Implement database retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Report retrieval not yet implemented. Add database integration.",
    )


@router.get("/reports", response_model=list[Report])
async def list_reports(
    limit: int = 10,
    offset: int = 0,
    user_id: str | None = None,
) -> list[Report]:
    """
    List generated reports.
    
    Note: In production, this would query a database with pagination.
    
    Args:
        limit: Maximum number of reports to return
        offset: Number of reports to skip
        user_id: Optional filter by user ID
    
    Returns:
        List of reports
    """
    # TODO: Implement database query
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Report listing not yet implemented. Add database integration.",
    )


@router.delete("/report/{report_id}")
async def delete_report(report_id: str) -> Dict[str, Any]:
    """
    Delete a report.
    
    Args:
        report_id: Report to delete
    
    Returns:
        Confirmation message
    """
    # TODO: Implement database deletion
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Report deletion not yet implemented. Add database integration.",
    )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "content-generation",
        "version": "1.0.0",
    }
