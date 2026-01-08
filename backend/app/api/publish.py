"""
Publishing API Routes

Responsibilities:
• Publish content to SharePoint
• Post content to Microsoft Teams
• Manage publishing metadata
• Handle publishing errors
• Track publication status

Architecture Decision:
- Separate publishing from generation for flexibility
- Support multiple publishing targets
- Async operations for better UX
- Detailed error handling for external service failures
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.integrations.graph_api import get_graph_client, GraphAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/publish", tags=["publishing"])


class SharePointPublishRequest(BaseModel):
    """Request to publish content to SharePoint."""
    file_name: str = Field(..., description="Name of file to create")
    content: str = Field(..., description="File content")
    folder_path: str = Field(default="", description="Destination folder path")
    site_id: Optional[str] = Field(default=None, description="Optional site ID override")
    drive_id: Optional[str] = Field(default=None, description="Optional drive ID override")


class SharePointPublishResponse(BaseModel):
    """Response from SharePoint publishing."""
    success: bool
    file_name: str
    web_url: Optional[str] = None
    error: Optional[str] = None
    message: str


class TeamsPostRequest(BaseModel):
    """Request to post content to Teams."""
    team_id: str = Field(..., description="Microsoft Teams team ID")
    channel_id: str = Field(..., description="Channel ID within the team")
    message: str = Field(..., description="Message content (HTML supported)")
    subject: Optional[str] = Field(default=None, description="Optional message subject")


class TeamsPostResponse(BaseModel):
    """Response from Teams posting."""
    success: bool
    message_id: Optional[str] = None
    web_url: Optional[str] = None
    error: Optional[str] = None
    message: str


@router.post("/sharepoint", response_model=SharePointPublishResponse)
async def publish_to_sharepoint(request: SharePointPublishRequest) -> SharePointPublishResponse:
    """
    Publish content to SharePoint.
    
    Args:
        request: Publishing request with content and destination
    
    Returns:
        Publishing result with URL if successful
    """
    logger.info(
        f"Publishing to SharePoint",
        extra={
            "file_name": request.file_name,
            "folder": request.folder_path,
        }
    )
    
    try:
        graph_client = get_graph_client()
        
        result = graph_client.publish_to_sharepoint(
            file_name=request.file_name,
            content=request.content,
            site_id=request.site_id,
            drive_id=request.drive_id,
            folder_path=request.folder_path,
        )
        
        logger.info(
            f"Successfully published to SharePoint",
            extra={
                "file_name": request.file_name,
                "url": result.get("web_url"),
            }
        )
        
        return SharePointPublishResponse(
            success=True,
            file_name=request.file_name,
            web_url=result.get("web_url"),
            message="Successfully published to SharePoint",
        )
        
    except GraphAPIError as e:
        logger.error(f"SharePoint publishing failed: {str(e)}", exc_info=True)
        
        return SharePointPublishResponse(
            success=False,
            file_name=request.file_name,
            error=str(e),
            message="Failed to publish to SharePoint",
        )
    except Exception as e:
        logger.error(f"Unexpected publishing error: {str(e)}", exc_info=True)
        
        return SharePointPublishResponse(
            success=False,
            file_name=request.file_name,
            error=str(e),
            message="Unexpected error during publishing",
        )


@router.post("/teams", response_model=TeamsPostResponse)
async def post_to_teams(request: TeamsPostRequest) -> TeamsPostResponse:
    """
    Post content to Microsoft Teams channel.
    
    Args:
        request: Teams posting request
    
    Returns:
        Posting result with message ID if successful
    """
    logger.info(
        f"Posting to Teams",
        extra={
            "team_id": request.team_id,
            "channel_id": request.channel_id,
        }
    )
    
    try:
        graph_client = get_graph_client()
        
        result = graph_client.post_to_teams(
            team_id=request.team_id,
            channel_id=request.channel_id,
            message=request.message,
            subject=request.subject,
        )
        
        logger.info(
            f"Successfully posted to Teams",
            extra={"message_id": result.get("message_id")}
        )
        
        return TeamsPostResponse(
            success=True,
            message_id=result.get("message_id"),
            web_url=result.get("web_url"),
            message="Successfully posted to Teams",
        )
        
    except GraphAPIError as e:
        logger.error(f"Teams posting failed: {str(e)}", exc_info=True)
        
        return TeamsPostResponse(
            success=False,
            error=str(e),
            message="Failed to post to Teams",
        )
    except Exception as e:
        logger.error(f"Unexpected posting error: {str(e)}", exc_info=True)
        
        return TeamsPostResponse(
            success=False,
            error=str(e),
            message="Unexpected error during posting",
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check for publishing service.
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "publishing",
        "version": "1.0.0",
    }
