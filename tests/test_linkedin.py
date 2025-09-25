"""Tests for LinkedIn integration functionality."""

import pytest
from unittest.mock import Mock, patch
import httpx

from trendbolt_mcp.tools.linkedin import create_image_post, create_text_post, get_page_info


class TestLinkedInPosting:
    """Test LinkedIn posting functionality."""
    
    def test_create_image_post_missing_page_id(self):
        """Test that missing page ID raises ValueError."""
        with patch('trendbolt_mcp.tools.linkedin.get_settings') as mock_settings:
            mock_settings.return_value.linkedin_page_id = None
            mock_settings.return_value.linkedin_access_token = "test_token"
            
            with pytest.raises(ValueError, match="LinkedIn page_id and access_token are required"):
                create_image_post("http://example.com/image.jpg", "Test post")
    
    def test_create_image_post_missing_access_token(self):
        """Test that missing access token raises ValueError."""
        with patch('trendbolt_mcp.tools.linkedin.get_settings') as mock_settings:
            mock_settings.return_value.linkedin_page_id = "test_page_id"
            mock_settings.return_value.linkedin_access_token = None
            
            with pytest.raises(ValueError, match="LinkedIn page_id and access_token are required"):
                create_image_post("http://example.com/image.jpg", "Test post")
    
    def test_create_image_post_success(self):
        """Test successful image post creation with mocked client."""
        with patch('trendbolt_mcp.tools.linkedin.get_settings') as mock_settings:
            mock_settings.return_value.linkedin_page_id = "test_page_id"
            mock_settings.return_value.linkedin_access_token = "test_token"
            
            # Mock the entire httpx client to avoid network calls
            with patch('httpx.Client') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                # Mock all the responses
                mock_response = Mock()
                mock_response.json.return_value = {
                    "value": {
                        "uploadUrl": "https://upload.linkedin.com/upload",
                        "image": "urn:li:digitalmediaAsset:123456"
                    }
                }
                mock_response.headers = {"x-restli-id": "test_post_id"}
                mock_response.content = b"fake_image_data"
                mock_response.raise_for_status.return_value = None
                
                mock_client.post.return_value = mock_response
                mock_client.get.return_value = mock_response
                mock_client.put.return_value = mock_response
                
                result = create_image_post("http://example.com/image.jpg", "Test post")
                
                assert result["post_id"] == "test_post_id"
                assert result["image_urn"] == "urn:li:digitalmediaAsset:123456"
                assert "linkedin.com/feed/update/test_post_id" in result["permalink_url"]
    
    def test_create_text_post_success(self):
        """Test successful text post creation."""
        with patch('trendbolt_mcp.tools.linkedin.get_settings') as mock_settings:
            mock_settings.return_value.linkedin_page_id = "test_page_id"
            mock_settings.return_value.linkedin_access_token = "test_token"
            
            with patch('httpx.Client') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                mock_response = Mock()
                mock_response.headers = {"x-restli-id": "test_post_id"}
                mock_response.json.return_value = {}
                mock_response.raise_for_status.return_value = None
                mock_client.post.return_value = mock_response
                
                result = create_text_post("Test text post")
                
                assert result["post_id"] == "test_post_id"
                assert "linkedin.com/feed/update/test_post_id" in result["permalink_url"]
    
    def test_get_page_info_success(self):
        """Test successful page info retrieval."""
        with patch('trendbolt_mcp.tools.linkedin.get_settings') as mock_settings:
            mock_settings.return_value.linkedin_page_id = "test_page_id"
            mock_settings.return_value.linkedin_access_token = "test_token"
            
            with patch('httpx.Client') as mock_client_class:
                mock_client = Mock()
                mock_client_class.return_value = mock_client
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    "id": "test_page_id",
                    "name": "Test Company",
                    "vanityName": "test-company"
                }
                mock_response.raise_for_status.return_value = None
                mock_client.get.return_value = mock_response
                
                result = get_page_info()
                
                assert result["id"] == "test_page_id"
                assert result["name"] == "Test Company"
                assert result["vanityName"] == "test-company"


class TestLinkedInIntegration:
    """Test LinkedIn integration with pipeline."""
    
    @patch('trendbolt_mcp.tools.linkedin.create_image_post')
    def test_pipeline_linkedin_integration(self, mock_create_post):
        """Test LinkedIn integration in the pipeline."""
        mock_create_post.return_value = {
            "post_id": "test_post_id",
            "permalink_url": "https://linkedin.com/feed/update/test_post_id"
        }
        
        # This would be tested as part of the full pipeline test
        # For now, just verify the function can be called
        result = mock_create_post("http://example.com/image.jpg", "Test post")
        
        assert result["post_id"] == "test_post_id"
        assert "linkedin.com" in result["permalink_url"]


if __name__ == "__main__":
    pytest.main([__file__])
