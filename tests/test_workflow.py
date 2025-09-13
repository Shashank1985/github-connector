import pytest
from app.workflow import GitHubWorkflow

@pytest.mark.asyncio
async def test_github_workflow_happy_path(temporal_client):
    """Test the complete GitHubWorkflow happy path with mocked activities."""
    # Execute the workflow. The temporal_client fixture provides the client instance.
    await temporal_client.execute_workflow(
        GitHubWorkflow.run,
        {"username": "testuser", "pat": "test_pat"},
        id="test-workflow-id",
        task_queue="github_extractor_task_queue",
    )
    
    # The test will pass as long as the workflow executes without throwing an exception.
    # The individual activity tests (in test_activities.py) ensure the correctness of the
    # data manipulation and file writing. This test verifies the correct flow of the
    # workflow itself.