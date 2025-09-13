# app/activities.py
from typing import Any, Dict, List, Optional
from application_sdk.activities import ActivitiesInterface
from application_sdk.activities.common.models import ActivityStatistics
from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.clients.atlan import AtlanClient
from application_sdk.observability.decorators.observability_decorator import observability
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from temporalio import activity

from app.clients import GitHubClient
import json
import os

logger = get_logger(__name__)
activity.logger = logger
metrics = get_metrics()
traces = get_traces()

username = os.getenv("GITHUB_USERNAME")
pat = os.getenv("GITHUB_PAT")
class GitHubActivities(ActivitiesInterface):
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def preflight_check(self, workflow_args: Dict[str, Any]) -> Optional[ActivityStatistics]:
        """Performs a preflight check using the provided PAT."""
        try:
            if not pat:
                raise ValueError("Personal Access Token (PAT) is missing.")
            client = GitHubClient(pat=pat)
            await client.get_user_metadata(username=username)
            logger.info("Preflight check passed successfully.")
            return None
        except Exception as e:
            logger.error(f"Preflight check failed: {e}")
            raise

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_user_metadata_activity(self, workflow_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetches metadata for a GitHub user or organization using the provided PAT.
        
        :param workflow_args: The workflow arguments, including the GitHub username and PAT.
        :return: A dictionary containing the user's metadata.
        """
        client = GitHubClient(pat=pat)
        user_metadata= await client.get_user_metadata(username=username)
        output_file = "github_user_metadata.json"
        with open(output_file, "w") as f:
            json.dump(user_metadata, f, indent=4)
        
        print(f"Successfully extracted metadata for '{username}' and saved it to '{output_file}'.")
    

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_repositories_metadata_activity(self, workflow_args: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Fetches metadata for all public repositories of a user or organization.
        
        :param workflow_args: The workflow arguments, including the GitHub username and PAT.
        :return: A list of dictionaries, each containing a repository's metadata.
        """
        client = GitHubClient(pat=pat)
        repository_metadata = await client.get_repositories_metadata(username=username)
        output_file = "github_repo_metadata.json"
        with open(output_file, "w") as f:
            json.dump(repository_metadata, f, indent=4)
        
        print(f"Successfully extracted metadata for '{username}' and saved it to '{output_file}'.")
    