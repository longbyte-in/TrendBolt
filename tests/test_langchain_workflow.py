"""
Test suite for LangChain workflow integration in TrendBolt.

This module tests the LangChain orchestrator, workflow execution,
and integration with existing TrendBolt components.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from trendbolt_mcp.orchestrator.langchain_agent import TrendBoltLangChainAgent, WorkflowState
from trendbolt_mcp.orchestrator.workflow_config import (
    get_workflow_config,
    list_workflow_configs,
    create_custom_config,
    get_content_style
)


class TestWorkflowConfig:
    """Test workflow configuration functionality."""
    
    def test_get_workflow_config(self):
        """Test getting predefined workflow configurations."""
        config = get_workflow_config("tech_news")
        assert config.name == "Technology News"
        assert "technology" in config.subreddits
        assert config.strategy == "hot"
        assert config.min_score == 200
    
    def test_list_workflow_configs(self):
        """Test listing all workflow configurations."""
        configs = list_workflow_configs()
        assert isinstance(configs, list)
        assert "tech_news" in configs
        assert "ai_trends" in configs
        assert len(configs) > 0
    
    def test_create_custom_config(self):
        """Test creating custom workflow configuration."""
        config = create_custom_config(
            name="Test Config",
            subreddits=["test", "example"],
            strategy="top",
            min_score=50
        )
        assert config.name == "Test Config"
        assert config.subreddits == ["test", "example"]
        assert config.strategy == "top"
        assert config.min_score == 50
    
    def test_get_content_style(self):
        """Test getting content style configurations."""
        style = get_content_style("professional")
        assert "voice" in style
        assert "tone" in style
        assert "cta" in style
        assert "hashtags" in style
        
        # Test default fallback
        default_style = get_content_style("nonexistent")
        assert default_style == get_content_style("engaging")


class TestTrendBoltLangChainAgent:
    """Test the main LangChain agent functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('trendbolt_mcp.orchestrator.langchain_agent.get_settings') as mock:
            mock.return_value = Mock(
                llm_provider="openai",
                openai_api_key="test-key",
                reddit_client_id="test-id",
                reddit_client_secret="test-secret",
                reddit_user_agent="test-agent",
                linkedin_access_token="test-token",
                linkedin_page_id="test-page",
                canva_brand_template_id="test-template"
            )
            yield mock
    
    @pytest.fixture
    def agent(self, mock_settings):
        """Create agent instance for testing."""
        with patch('langchain_openai.AzureChatOpenAI'):
            with patch('trendbolt_mcp.orchestrator.langchain_agent.create_react_agent'):
                agent = TrendBoltLangChainAgent()
                return agent
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'tools')
        assert hasattr(agent, 'workflow')
        assert len(agent.tools) > 0
    
    def test_tools_creation(self, agent):
        """Test that all required tools are created."""
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "reddit_trending",
            "reddit_post",
            "generate_content",
            "canva_create_design",
            "canva_get_design",
            "post_to_linkedin"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, agent):
        """Test successful workflow execution."""
        # Mock all the external dependencies
        with patch('trendbolt_mcp.tools.reddit.get_trending') as mock_reddit:
            with patch('trendbolt_mcp.tools.llm.generate_canvas_post') as mock_llm:
                with patch('trendbolt_mcp.tools.canva_connect.create_autofill_job_from_values') as mock_canva:
                    with patch('trendbolt_mcp.tools.canva_connect.get_autofill_job') as mock_canva_status:
                        with patch('trendbolt_mcp.tools.linkedin.create_image_post') as mock_linkedin:
                            
                            # Setup mocks
                            mock_reddit.return_value = [
                                {"title": "Test Topic", "url": "http://test.com", "score": 150}
                            ]
                            mock_llm.return_value = {
                                "title": "Test Title",
                                "description": "Test Description"
                            }
                            mock_canva.return_value = {
                                "success": True,
                                "job": {"id": "test-job-id"}
                            }
                            mock_canva_status.return_value = {
                                "job": {
                                    "status": "success",
                                    "result": {
                                        "design": {
                                            "thumbnail": {"url": "http://test-image.com"}
                                        }
                                    }
                                }
                            }
                            mock_linkedin.return_value = {"post_id": "test-post-id"}
                            
                            # Mock the workflow execution
                            with patch.object(agent, 'workflow') as mock_workflow:
                                mock_workflow.ainvoke = AsyncMock(return_value={
                                    "current_step": "completed",
                                    "selected_topic": {"title": "Test Topic"},
                                    "generated_content": {"title": "Test Title"},
                                    "canva_design": {"thumbnail": {"url": "http://test.com"}},
                                    "linkedin_post": {"post_id": "123"},
                                    "error_log": [],
                                    "metadata": {"started_at": "2024-01-01"}
                                })
                                
                                result = await agent.execute_workflow(
                                    subreddits=["test"],
                                    strategy="hot",
                                    min_score=50
                                )
                                
                                assert result["success"] is True
                                assert result["status"] == "completed"
                                assert "topic" in result
                                assert "content" in result
    
    @pytest.mark.asyncio
    async def test_execute_simple_pipeline(self, agent):
        """Test simple pipeline execution with natural language query."""
        with patch.object(agent, 'agent') as mock_agent:
            mock_agent.ainvoke = AsyncMock(return_value={
                "messages": [Mock(content="Task completed successfully")]
            })
            
            result = await agent.execute_simple_pipeline(
                query="Find trending AI topics",
                subreddits=["artificial"]
            )
            
            assert result["success"] is True
            assert "messages" in result
            assert "response" in result
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, agent):
        """Test workflow handles errors gracefully."""
        with patch.object(agent, 'workflow') as mock_workflow:
            mock_workflow.ainvoke = AsyncMock(side_effect=Exception("Test error"))
            
            result = await agent.execute_workflow()
            
            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]


class TestWorkflowIntegration:
    """Test integration with existing TrendBolt components."""
    
    @pytest.mark.asyncio
    async def test_reddit_integration(self):
        """Test Reddit API integration works with workflow."""
        with patch('trendbolt_mcp.tools.reddit.get_trending') as mock_reddit:
            mock_reddit.return_value = [
                {
                    "id": "t3_test123",
                    "title": "Test Reddit Post",
                    "url": "https://reddit.com/test",
                    "score": 200,
                    "subreddit": "test"
                }
            ]
            
            from trendbolt_mcp.tools.reddit import get_trending
            topics = await get_trending(["test"], strategy="hot", limit=1)
            
            assert len(topics) == 1
            assert topics[0]["title"] == "Test Reddit Post"
            assert topics[0]["score"] == 200
    
    def test_llm_integration(self):
        """Test LLM content generation integration."""
        with patch('trendbolt_mcp.tools.llm.generate_canvas_post') as mock_llm:
            mock_llm.return_value = {
                "title": "Generated Title",
                "headline": "Generated Headline", 
                "description": "Generated description content",
                "image_available": False
            }
            
            from trendbolt_mcp.tools.llm import generate_canvas_post
            
            topic = {"title": "Test Topic", "url": "http://test.com"}
            brand = {"voice": "professional", "cta": "Follow us"}
            
            content = generate_canvas_post(topic=topic, brand=brand)
            
            assert content["title"] == "Generated Title"
            assert content["headline"] == "Generated Headline"
            assert "description" in content
    
    def test_canva_integration(self):
        """Test Canva API integration."""
        with patch('trendbolt_mcp.tools.canva_connect.create_autofill_job_from_values') as mock_canva:
            mock_canva.return_value = {
                "success": True,
                "job": {
                    "id": "test-job-123",
                    "status": "pending"
                }
            }
            
            from trendbolt_mcp.tools.canva_connect import create_autofill_job_from_values
            
            result = create_autofill_job_from_values(
                values={"title": "Test Title", "description": "Test Description"},
                image_fields={}
            )
            
            assert result["success"] is True
            assert result["job"]["id"] == "test-job-123"
    
    def test_linkedin_integration(self):
        """Test LinkedIn API integration."""
        with patch('trendbolt_mcp.tools.linkedin.create_text_post') as mock_linkedin:
            mock_linkedin.return_value = {
                "post_id": "test-post-123",
                "permalink_url": "https://linkedin.com/feed/update/test-post-123"
            }
            
            from trendbolt_mcp.tools.linkedin import create_text_post
            
            result = create_text_post(text="Test LinkedIn post content")
            
            assert result["post_id"] == "test-post-123"
            assert "permalink_url" in result


class TestWorkflowStates:
    """Test workflow state management."""
    
    def test_workflow_state_initialization(self):
        """Test WorkflowState initialization."""
        state = WorkflowState(
            messages=[],
            current_step="discover",
            reddit_topics=[],
            selected_topic=None,
            generated_content=None,
            canva_design=None,
            linkedin_post=None,
            error_log=[],
            metadata={}
        )
        
        assert state["current_step"] == "discover"
        assert state["messages"] == []
        assert state["reddit_topics"] == []
        assert state["error_log"] == []
    
    def test_workflow_state_updates(self):
        """Test workflow state can be updated."""
        state = WorkflowState(
            messages=[],
            current_step="discover",
            reddit_topics=[],
            selected_topic=None,
            generated_content=None,
            canva_design=None,
            linkedin_post=None,
            error_log=[],
            metadata={}
        )
        
        # Update state
        state["current_step"] = "generate"
        state["reddit_topics"] = [{"title": "Test Topic"}]
        
        assert state["current_step"] == "generate"
        assert len(state["reddit_topics"]) == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
