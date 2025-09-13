import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.clients import GitHubClient

@pytest.fixture
def mock_httpx_client():
    """Mock a successful httpx.AsyncClient with a request object."""
    mock_client = AsyncMock()
    mock_response = httpx.Response(200, json={"login": "testuser", "name": "Test User"}, request=httpx.Request('GET', 'http://test'))
    mock_client.get.return_value = mock_response
    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client

@pytest.fixture
def mock_httpx_client_repos():
    """Mock a successful httpx.AsyncClient with paginated repos and request objects."""
    mock_client = AsyncMock()
    mock_response_page1 = httpx.Response(200, json=[{"name": "repo1", "description": "a desc", "stargazers_count": 10, "html_url": "url1", "created_at": "date1", "updated_at": "date2"}], request=httpx.Request('GET', 'http://test'))
    mock_response_page2 = httpx.Response(200, json=[], request=httpx.Request('GET', 'http://test'))
    mock_client.get.side_effect = [mock_response_page1, mock_response_page2]
    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client

@pytest.mark.asyncio
async def test_get_user_metadata_success(mock_httpx_client):
    """Test get_user_metadata with a successful response."""
    client = GitHubClient(pat="test_pat")
    user_data = await client.get_user_metadata("testuser")
    assert user_data["name"] == "Test User"
    mock_httpx_client.get.assert_called_once_with("/users/testuser")

@pytest.mark.asyncio
async def test_get_repositories_metadata_success(mock_httpx_client_repos):
    """Test get_repositories_metadata with paginated responses."""
    client = GitHubClient(pat="test_pat")
    repos = await client.get_repositories_metadata("testuser")
    assert len(repos) == 1
    assert repos[0]["name"] == "repo1"
    assert mock_httpx_client_repos.get.call_count == 2

@pytest.mark.asyncio
async def test_get_user_metadata_http_error():
    """Test get_user_metadata with an HTTP error."""
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=httpx.HTTPStatusError("Not Found", request=httpx.Request("GET", "http://test"), response=httpx.Response(404)))):
        client = GitHubClient(pat="test_pat")
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_user_metadata("invaliduser")