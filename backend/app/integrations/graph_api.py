"""
Microsoft Graph API Integration

Responsibilities:
• Authenticate with Microsoft Entra (Azure AD)
• Publish content to SharePoint document libraries
• Post content to Teams channels
• Upload files and manage permissions
• Handle authentication token refresh

Architecture Decision:
- MSAL for secure OAuth2 authentication
- Retry logic for transient API failures
- Support both SharePoint and Teams publishing
- Proper error handling and logging
- Token caching for performance
"""

from typing import Optional, Dict, Any
import msal
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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

logger = get_logger(__name__)


class GraphAPIError(Exception):
    """Base exception for Microsoft Graph API errors."""
    pass


class GraphAuthenticationError(GraphAPIError):
    """Raised when authentication fails."""
    pass


class GraphAPIClient:
    """
    Production-ready Microsoft Graph API client.
    
    Features:
    - Secure authentication with Microsoft Entra
    - SharePoint document upload
    - Teams channel posting
    - Automatic token refresh
    - Retry logic for resilience
    
    Example:
        client = GraphAPIClient()
        result = client.publish_to_sharepoint(
            site_id="contoso.sharepoint.com",
            file_name="report.docx",
            content="Report content..."
        )
    """
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize Microsoft Graph API client.
        
        Args:
            tenant_id: Microsoft Entra tenant ID
            client_id: App registration client ID
            client_secret: App registration client secret
        """
        self.tenant_id = tenant_id or settings.GRAPH_TENANT_ID
        self.client_id = client_id or settings.GRAPH_CLIENT_ID
        self.client_secret = client_secret or settings.GRAPH_CLIENT_SECRET
        
        # Initialize MSAL confidential client
        self.msal_app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
        )
        
        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        # Configure requests session with retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        logger.info("Initialized Microsoft Graph API client")
    
    def _get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
        
        Raises:
            GraphAuthenticationError: If authentication fails
        """
        # Check if cached token is still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        
        try:
            logger.debug("Acquiring new access token")
            
            # Acquire token using client credentials flow
            result = self.msal_app.acquire_token_for_client(
                scopes=[settings.GRAPH_SCOPES]
            )
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                # Set expiry with 5-minute buffer
                expires_in = result.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 300
                
                logger.info("Successfully acquired access token")
                return self._access_token
            else:
                error_description = result.get("error_description", "Unknown error")
                logger.error(f"Failed to acquire token: {error_description}")
                raise GraphAuthenticationError(f"Authentication failed: {error_description}")
                
        except Exception as e:
            logger.error(f"Token acquisition error: {str(e)}", exc_info=True)
            raise GraphAuthenticationError(f"Failed to authenticate: {str(e)}") from e
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Graph API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to v1.0)
            json: JSON payload
            data: Binary data
            headers: Additional headers
        
        Returns:
            Response JSON
        
        Raises:
            GraphAPIError: On API errors
        """
        token = self._get_access_token()
        
        url = f"{self.GRAPH_API_ENDPOINT}/{endpoint.lstrip('/')}"
        
        request_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                data=data,
                headers=request_headers,
                timeout=30,
            )
            
            response.raise_for_status()
            
            # Return JSON if present
            if response.content:
                return response.json()
            return {"status": "success"}
            
        except requests.HTTPError as e:
            error_msg = f"Graph API HTTP error: {e.response.status_code}"
            if e.response.content:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{error_msg} - {error_detail.get('error', {}).get('message', '')}"
                except:
                    pass
            logger.error(error_msg, exc_info=True)
            raise GraphAPIError(error_msg) from e
        except Exception as e:
            logger.error(f"Graph API request failed: {str(e)}", exc_info=True)
            raise GraphAPIError(f"Request failed: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(GraphAPIError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def publish_to_sharepoint(
        self,
        file_name: str,
        content: str,
        site_id: Optional[str] = None,
        drive_id: Optional[str] = None,
        folder_path: str = "",
    ) -> Dict[str, Any]:
        """
        Upload document to SharePoint.
        
        Args:
            file_name: Name of the file to create
            content: File content (text)
            site_id: SharePoint site ID (defaults to config)
            drive_id: SharePoint drive ID (defaults to config)
            folder_path: Path within drive (e.g., "Reports/2024")
        
        Returns:
            Dictionary with upload metadata including URL
        
        Raises:
            GraphAPIError: On upload failure
        """
        site_id = site_id or settings.SHAREPOINT_SITE_ID
        drive_id = drive_id or settings.SHAREPOINT_DRIVE_ID
        
        if not site_id or not drive_id:
            raise GraphAPIError("SharePoint site_id and drive_id must be configured")
        
        try:
            logger.info(
                f"Publishing to SharePoint",
                extra={"file_name": file_name, "folder": folder_path}
            )
            
            # Construct endpoint for file upload
            if folder_path:
                endpoint = f"drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
            else:
                endpoint = f"drives/{drive_id}/root:/{file_name}:/content"
            
            # Upload file
            response = self._make_request(
                method="PUT",
                endpoint=endpoint,
                data=content.encode("utf-8"),
                headers={"Content-Type": "text/plain"},
            )
            
            result = {
                "status": "published",
                "file_name": file_name,
                "web_url": response.get("webUrl"),
                "id": response.get("id"),
                "created_at": response.get("createdDateTime"),
            }
            
            logger.info(
                f"Successfully published to SharePoint",
                extra={"file_name": file_name, "url": result.get("web_url")}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"SharePoint publish failed: {str(e)}", exc_info=True)
            raise GraphAPIError(f"SharePoint upload failed: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(GraphAPIError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def post_to_teams(
        self,
        team_id: str,
        channel_id: str,
        message: str,
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post message to Teams channel.
        
        Args:
            team_id: Microsoft Teams team ID
            channel_id: Channel ID within the team
            message: Message content (supports basic HTML)
            subject: Optional message subject
        
        Returns:
            Dictionary with post metadata
        
        Raises:
            GraphAPIError: On posting failure
        """
        try:
            logger.info(
                f"Posting to Teams",
                extra={"team_id": team_id, "channel_id": channel_id}
            )
            
            # Construct message payload
            payload = {
                "body": {
                    "contentType": "html",
                    "content": message,
                }
            }
            
            if subject:
                payload["subject"] = subject
            
            # Post message
            endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
            response = self._make_request(
                method="POST",
                endpoint=endpoint,
                json=payload,
            )
            
            result = {
                "status": "posted",
                "message_id": response.get("id"),
                "web_url": response.get("webUrl"),
                "created_at": response.get("createdDateTime"),
            }
            
            logger.info(
                f"Successfully posted to Teams",
                extra={"message_id": result.get("message_id")}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Teams post failed: {str(e)}", exc_info=True)
            raise GraphAPIError(f"Teams posting failed: {str(e)}") from e
    
    def get_user_profile(self, user_id: str = "me") -> Dict[str, Any]:
        """
        Get user profile information.
        
        Args:
            user_id: User ID or "me" for authenticated user
        
        Returns:
            User profile data
        """
        endpoint = f"users/{user_id}"
        return self._make_request("GET", endpoint)
    
    def list_sharepoint_sites(self) -> list[Dict[str, Any]]:
        """
        List available SharePoint sites.
        
        Returns:
            List of SharePoint sites
        """
        endpoint = "sites"
        response = self._make_request("GET", endpoint)
        return response.get("value", [])


# Global client instance
_graph_client: Optional[GraphAPIClient] = None


def get_graph_client() -> GraphAPIClient:
    """
    Get or create global Microsoft Graph client.
    
    Returns:
        Shared GraphAPIClient instance
    """
    global _graph_client
    if _graph_client is None:
        _graph_client = GraphAPIClient()
    return _graph_client


def publish_to_sharepoint(
    file_name: str,
    content: str,
    folder_path: str = ""
) -> Dict[str, Any]:
    """
    Simplified SharePoint publishing interface.
    
    Args:
        file_name: Name of file to create
        content: File content
        folder_path: Destination folder
    
    Returns:
        Publishing result
    """
    client = get_graph_client()
    return client.publish_to_sharepoint(
        file_name=file_name,
        content=content,
        folder_path=folder_path,
    )
