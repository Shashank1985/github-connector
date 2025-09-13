import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import os
import yake

from app.activities import GitHubActivities

@pytest.fixture(autouse=True)
def mock_file_open():
    """Mock builtins.open to prevent actual file writing."""
    with patch("builtins.open", MagicMock()) as mock:
        yield mock

@pytest.mark.asyncio
async def test_preflight_check_success(mock_github_client):
    """Test preflight_check with a valid PAT."""
    activities = GitHubActivities()
    result = await activities.preflight_check({})
    assert result is None
    mock_github_client.get_user_metadata.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_user_metadata_activity(mock_github_client, mock_file_open):
    """Test fetch_user_metadata_activity saves the correct file."""
    activities = GitHubActivities()
    await activities.fetch_user_metadata_activity({})
    mock_file_open.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_repositories_metadata_activity(mock_github_client, mock_file_open):
    """Test fetch_repositories_metadata_activity saves the correct file."""
    activities = GitHubActivities()
    await activities.fetch_repositories_metadata_activity({})
    mock_file_open.assert_called_once()

@pytest.mark.asyncio
async def test_extract_keywords_activity(mock_yake_extractor):
    """Test extract_keywords_activity correctly adds tags."""
    activities = GitHubActivities()
    repo_data = [{"description": "A python project with cool code"}]
    
    result = await activities.extract_keywords_activity(repo_data)
    
    mock_yake_extractor.extract_keywords.assert_called_once()
    assert result[0]["auto_tags"] == ["python project", "cool code"]

@pytest.mark.asyncio
async def test_fetch_data_quality_metrics_activity(mock_file_open):
    """Test fetch_data_quality_metrics_activity calculates metrics correctly."""
    activities = GitHubActivities()
    raw_data = {
        "user_data": {"followers": 100, "following": 50, "public_gists": 20},
        "repo_data": [
            # Corrected keys to match the activity's logic
            {"name": "repo1", "description": "a desc", "star_count": 10, "auto_tags": ["tag1"]},
            {"name": "repo2", "description": None, "star_count": 20, "auto_tags": []},
        ]
    }
    
    result = await activities.fetch_data_quality_metrics_activity(raw_data)
    assert result["total_public_repos"] == 2
    assert result["total_followers"] == 100
    assert result["average_stars_per_repo"] == 15.0
    assert result["repos_with_description_percentage"] == 50.0
    assert result["repos_with_auto_tags_percentage"] == 50.0
    mock_file_open.assert_called_once()