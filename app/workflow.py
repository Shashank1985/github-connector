# app/workflows.py
import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, List

from application_sdk.observability.decorators.observability_decorator import observability
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.workflows.metadata_extraction.sql import BaseSQLMetadataExtractionWorkflow
from temporalio import workflow
from temporalio.common import RetryPolicy

from app.activities import GitHubActivities
from app.transformer import GitHubAtlasTransformer

logger = get_logger(__name__)
workflow.logger = logger
metrics = get_metrics()
traces = get_traces()


@workflow.defn
class GitHubWorkflow:

    @observability(logger=logger, metrics=metrics, traces=traces)
    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]):
        """
        Run the GitHub metadata extraction workflow.

        :param workflow_config: The workflow arguments.
        """
        activities_instance = GitHubActivities()

        workflow_args = workflow_config

        retry_policy = RetryPolicy(
            maximum_attempts=6,
            backoff_coefficient=2,
        )

        # 1. Run preflight check activity to validate credentials
        await workflow.execute_activity_method(
            activities_instance.preflight_check,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=60),
        )

        # 2. Fetch raw user and repository data in parallel
        user_metadata_task = workflow.execute_activity_method(
            activities_instance.fetch_user_metadata_activity,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=5),
        )

        repo_metadata_task = workflow.execute_activity_method(
            activities_instance.fetch_repositories_metadata_activity,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=5),
        )

        user_metadata, repo_metadata = await asyncio.gather(user_metadata_task, repo_metadata_task)
        raw_data = {"user_data": user_metadata, "repo_data": repo_metadata}

        # 3. Transform raw data into Atlan assets
        transformed_assets = await workflow.execute_activity_method(
            activities_instance.transform_data_activity,
            raw_data,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 4. Upload the transformed assets to Atlan
        await workflow.execute_activity_method(
            activities_instance.upload_assets,
            transformed_assets,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=10),
        )

    @staticmethod
    def get_activities(activities: GitHubActivities) -> List[Callable[..., Any]]:
        """
        Get the list of activities for the workflow.
        """
        return [
            activities.preflight_check,
            activities.fetch_user_metadata_activity,
            activities.fetch_repositories_metadata_activity,
            activities.transform_data_activity,
            activities.upload_assets,
        ]