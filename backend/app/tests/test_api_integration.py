"""
Integration Tests for Content Generation API

Tests the full content generation workflow including all agents.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from app.main import app
from app.models.report import ContentType, CitationFormat

client = TestClient(app)


class TestContentAPI:
    """Test suite for content generation API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/content/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "content-generation"
    
    @pytest.mark.asyncio
    @patch("app.agents.planning_agent.get_openai_service")
    @patch("app.agents.research_agent.get_rag_service")
    @patch("app.agents.drafting_agent.get_openai_service")
    @patch("app.agents.editing_agent.get_openai_service")
    async def test_generate_content_success(
        self,
        mock_editing_service,
        mock_drafting_service,
        mock_research_service,
        mock_planning_service,
    ):
        """Test successful content generation."""
        # Mock planning agent response
        mock_planning_service.return_value.generate_structured_output = AsyncMock(
            return_value={
                "title": "Test Report",
                "executive_summary_needed": True,
                "overall_strategy": "Test strategy",
                "key_points": ["Point 1", "Point 2"],
                "sections": [
                    {
                        "title": "Introduction",
                        "description": "Introduction section",
                        "research_queries": ["test query"],
                        "word_count_target": 300,
                    }
                ],
            }
        )
        
        # Mock research agent response
        mock_research_service.return_value.retrieve_and_build_context = Mock(
            return_value=(
                "Test context from research",
                [
                    Mock(
                        id="cite-1",
                        text="Test citation",
                        source="Test Source",
                        relevance_score=0.9,
                    )
                ],
            )
        )
        
        # Mock drafting agent response
        mock_drafting_service.return_value.generate_with_context = AsyncMock(
            return_value="Generated section content"
        )
        
        # Mock editing agent response
        mock_editing_service.return_value.generate_with_context = AsyncMock(
            return_value="Edited and polished content\n\nReferences\n[1] Test Source"
        )
        
        # Make request
        request_data = {
            "prompt": "Generate a test report about AI",
            "content_type": "report",
            "citation_format": "APA",
            "max_words": 500,
            "include_citations": True,
            "tags": ["test", "ai"],
        }
        
        response = client.post("/api/v1/content/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["report"] is not None
        assert data["report"]["title"] == "Test Report"
        assert len(data["report"]["sections"]) > 0
    
    def test_generate_content_validation_error(self):
        """Test content generation with invalid input."""
        # Missing required field 'prompt'
        request_data = {
            "content_type": "report",
        }
        
        response = client.post("/api/v1/content/generate", json=request_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data


class TestRootEndpoints:
    """Test suite for root and utility endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "ContentForge"
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "dependencies" in data
