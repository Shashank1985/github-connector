# tests/test_workflow.py
import pytest
from app.workflow import GitHubWorkflow

@pytest.mark.asyncio
async def test_github_workflow_happy_path(temporal_client):
    """Test the complete GitHubWorkflow happy path with mocked activities."""
    # Execute the workflow. The temporal_client fixture handles the mocking of activities.
    await temporal_client.execute_workflow(
        GitHubWorkflow.run,
        {"username": "testuser", "pat": "test_pat"},
        id="test-workflow-id",
        task_queue="github_extractor_task_queue",
    )
    
    