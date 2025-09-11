# app/activities.py

from typing import Any, Dict, Optional, cast

from application_sdk.activities.common.models import ActivityStatistics
from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.base import BaseMetadataExtractionActivitiesState
from application_sdk.observability.decorators.observability_decorator import observability
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.services.secretstore import SecretStore
from temporalio import activity

from app.clients import GitHubClient

logger = get_logger(__name__)
activity.logger = logger
metrics = get_metrics()
traces = get_traces()


class GitHubActivitiesState(BaseMetadataExtractionActivitiesState):
    """
    State object for the GitHub metadata extraction activities.
    This class holds shared resources, such as the GitHub client,
    that should be initialized once per workflow run.
    """
    def __init__(self, token_secret_key: str):
        self.github_client = GitHubClient(token_secret_key=token_secret_key)


class GitHubActivities:
    """
    This class contains the activities for the GitHub metadata extraction application.
    It uses a state object to access a shared GitHub client instance.
    """

    def __init__(self, state: GitHubActivitiesState) -> None:
        self.state = state

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def preflight_check(self, workflow_args: Dict[str, Any]) -> Optional[ActivityStatistics]:
        """Performs a preflight check, including credential validation."""
        try:
            # The client is already initialized in the state object. We just use it here.
            await self.state.github_client.get_user_metadata(username=workflow_args["username"])
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
        Fetches metadata for a GitHub user or organization.
        
        :param workflow_args: The workflow arguments, including the GitHub username.
        :return: A dictionary containing the user's metadata.
        """
        return await self.state.github_client.get_user_metadata(username=workflow_args["username"])

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_repositories_metadata_activity(self, workflow_args: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Fetches metadata for all public repositories of a user or organization.
        
        :param workflow_args: The workflow arguments, including the GitHub username.
        :return: A list of dictionaries, each containing a repository's metadata.
        """
        return await self.state.github_client.get_repositories_metadata(username=workflow_args["username"])