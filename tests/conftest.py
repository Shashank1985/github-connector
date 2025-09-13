import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from app.activities import GitHubActivities
from app.workflow import GitHubWorkflow
import yake
import pytest_asyncio


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {"GITHUB_USERNAME": "testuser", "GITHUB_PAT": "test_pat"}):
        yield

@pytest.fixture
def mock_github_client():
    """Mock the GitHubClient class to prevent actual API calls."""
    with patch("app.activities.GitHubClient") as mock:
        instance = mock.return_value
        instance.get_user_metadata = AsyncMock(return_value={"login": "testuser", "followers": 10, "public_gists": 5})
        instance.get_repositories_metadata = AsyncMock(return_value=[{"name": "repo1", "description": "A Python project", "stargazers_count": 15}, {"name": "repo2", "description": None, "stargazers_count": 20}])
        yield instance

@pytest.fixture
def mock_yake_extractor():
    """Mock the YAKE! KeywordExtractor."""
    with patch("yake.KeywordExtractor") as mock_yake:
        instance = mock_yake.return_value
        instance.extract_keywords.return_value = [("python project", 0.1), ("cool code", 0.2)]
        yield instance

@pytest_asyncio.fixture(scope="module")
async def temporal_client():
    """Provides a mocked Temporal client for workflow testing."""
    env = await WorkflowEnvironment.start_time_skipping()
    async with env:
        worker = Worker(
            env.client,
            task_queue="github_extractor_task_queue",
            workflows=[GitHubWorkflow],
            activities=[GitHubActivities().preflight_check, GitHubActivities().fetch_user_metadata_activity, GitHubActivities().fetch_repositories_metadata_activity, GitHubActivities().extract_keywords_activity, GitHubActivities().fetch_data_quality_metrics_activity],
        )
        async with worker:
            yield env.client