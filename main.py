import asyncio
import os
from dotenv import load_dotenv

from app.activities import GitHubActivities
from app.workflow import GitHubWorkflow
from application_sdk.application import BaseApplication
from application_sdk.observability.logger_adaptor import get_logger

APPLICATION_NAME = "github_extractor"

logger = get_logger(__name__)

async def main(daemon: bool = True):
    """
    Main function to run the GitHub extractor application.
    It reads credentials from a .env file and starts the workflow.
    """
    # Load environment variables from the .env file
    load_dotenv()
    
    # Get credentials from environment variables
    username = os.getenv("GITHUB_USERNAME")
    pat = os.getenv("GITHUB_PAT")
    
    if not username or not pat:
        logger.error("GITHUB_USERNAME and GITHUB_PAT must be set in the .env file.")
        return

    logger.info("Starting GitHub Extractor application")

    # Initialize application
    app = BaseApplication(name=APPLICATION_NAME)

    # Setup workflow and activities
    await app.setup_workflow(
        workflow_and_activities_classes=[(GitHubWorkflow, GitHubActivities)],
        passthrough_modules=[
            "requests",
            "httpx",
            "urllib3",
            "warnings",
            "os",
            "grpc",
            "pyatlan",
        ],
    )

    # Start the worker to execute activities
    await app.start_worker()

    # Define workflow arguments
    workflow_args = {"username": username, "pat": pat}

    # Start the workflow
    print("Starting workflow with args:", workflow_args)
    # workflow_id = await app.workflow_client.start_workflow(
    #     workflow_class=GitHubWorkflow,
    #     workflow_args=workflow_args,
    # )
    # logger.info(f"Workflow started with ID: {workflow_id}")
    await app.setup_server(workflow_class = GitHubWorkflow)
    await app.start_server()

if __name__ == "__main__":
    asyncio.run(main())
