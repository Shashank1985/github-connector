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
import yake
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
        return user_metadata

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
        return repository_metadata
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def extract_keywords_activity(self, repo_metadata: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Extracts keywords from repository descriptions and adds them as tags.
        
        :param repo_metadata: A list of dictionaries, each containing a repository's metadata.
        :return: The updated list of dictionaries with added keyword tags.
        """
        kw_extractor = yake.KeywordExtractor(top=5) # Initialize YAKE with a limit of 5 keywords
        for repo in repo_metadata:
            description = repo.get("description")
            if description:
                keywords = [kw[0] for kw in kw_extractor.extract_keywords(description)]
                repo["auto_tags"] = keywords
            else:
                repo["auto_tags"] = []

        output_file = "github_repo_metadata_with_tags.json"
        with open(output_file, "w") as f:
            json.dump(repo_metadata, f, indent=4)
        
        logger.info(f"Successfully extracted keywords and saved the updated metadata to '{output_file}'.")
        return repo_metadata
    
    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_data_quality_metrics_activity(self, raw_data) -> Dict[str, Any]:
        """
        Calculates data quality metrics from the extracted metadata.
        
        :param raw_data: A dictionary containing 'user_data' and 'repo_data'.
        :return: A dictionary containing the calculated data quality metrics.
        """
        print("type of raw_data in activity:", type(raw_data))
        user_metadata = raw_data.get("user_data", {})
        repo_metadata = raw_data.get("repo_data", [])
        print("REPO METADATA IN ACTIVITY:",repo_metadata)
        # Calculate metrics
        quality_metrics = {
            "total_public_repos": len(repo_metadata),
            "total_followers": user_metadata.get("followers", 0),
            "total_following": user_metadata.get("following", 0),
            "average_stars_per_repo": sum(repo.get("star_count", 0) for repo in repo_metadata) / len(repo_metadata) if repo_metadata else 0,
            "total_public_gists": user_metadata.get("public_gists", 0),
            "repos_with_description_percentage": (sum(1 for repo in repo_metadata if repo.get("description")) / len(repo_metadata)) * 100 if repo_metadata else 0,
            "repos_with_auto_tags_percentage": (sum(1 for repo in repo_metadata if repo.get("auto_tags")) / len(repo_metadata)) * 100 if repo_metadata else 0,
        }

        output_file = "github_quality_metrics.json"
        with open(output_file, "w") as f:
            json.dump(quality_metrics, f, indent=4)

        logger.info("Successfully calculated data quality metrics and saved them to '%s'.", output_file)
        return quality_metrics