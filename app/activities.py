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
from app.transformer import GitHubAtlasTransformer
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
        return await client.get_user_metadata(username=username)

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
        return await client.get_repositories_metadata(username=username)

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    def transform_data_activity(self, raw_data: Dict[str, Any]) -> List[Any]:
        """
        Transforms raw data from GitHub API into Atlan assets.
        This activity runs synchronously as the transformation logic does not involve async I/O.

        :param raw_data: A dictionary containing raw 'user_data' and 'repo_data'.
        :return: A list of transformed Atlan assets.
        """
        connection_name = "GitHub API"
        connection_qualified_name = "default/github/user_example"

        transformer = GitHubAtlasTransformer(
            connection_name=connection_name,
            connection_qualified_name=connection_qualified_name
        )

        return transformer.transform_assets(raw_data)

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def upload_assets(self, assets: List[Any]) -> None:
        """
        Uploads the transformed assets to Atlan.

        :param assets: A list of Atlan assets to be uploaded.
        """
        try:
            client = AtlanClient()
            response = await client.save_assets(assets=assets, replace_atlan_tags=True)
            logger.info(f"Successfully uploaded {len(response.assets_created)} assets to Atlan.")
        except Exception as e:
            logger.error(f"Failed to upload assets to Atlan: {e}")
            raise