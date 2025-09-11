# app/transformer.py

from typing import Any, Dict, List
from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.observability.logger_adaptor import get_logger

from pyatlan.client.atlan import AtlanClient
from pyatlan.model.assets import Connection, Folder
from pyatlan.model.enums import AtlanConnectorType

logger = get_logger(__name__)


class GitHubAtlasTransformer(AtlasTransformer):
    """
    Transforms raw GitHub API data into Atlan metadata assets.
    We use generic Connection and Folder assets to represent
    the GitHub-specific metadata hierarchy.
    """

    def __init__(self, connection_name: str, connection_qualified_name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connection_name = connection_name
        self.connection_qualified_name = connection_qualified_name
        # The client will be initialized in the activity, not the transformer
        self.client = None

    def transform_assets(self, raw_data: Dict[str, Any]) -> List[Any]:
        """
        Transforms the raw data into a list of Atlan assets.
        
        :param raw_data: A dictionary containing 'user_data' and 'repo_data' from the activities.
        :return: A list of transformed Atlan assets.
        """
        user_data = raw_data.get("user_data", {})
        repo_data = raw_data.get("repo_data", [])

        assets = []

        # Create the top-level Connection asset
        connection = self.transform_connection()
        assets.append(connection)

        # Create a Folder asset for the user/organization, linked to the connection
        if user_data:
            user_folder = self.transform_user_to_folder(user_data, connection)
            assets.append(user_folder)

            # Create a Folder asset for each repository, linked to the user's folder
            for repo in repo_data:
                repo_folder = self.transform_repository_to_folder(repo, user_folder)
                assets.append(repo_folder)

        return assets

    def transform_connection(self) -> Connection:
        """
        Transforms the connection details into an Atlan Connection asset.
        
        :return: A pyatlan Connection object.
        """
        return Connection.create(
            name=self.connection_name,
            qualified_name=self.connection_qualified_name,
            connector_type=AtlanConnectorType.S3 # Use a generic connector type as there is no GitHub type
        )

    def transform_user_to_folder(self, user_data: Dict[str, Any], connection: Connection) -> Folder:
        """
        Transforms a GitHub user/organization into an Atlan Folder asset.
        
        :param user_data: The dictionary of user metadata.
        :param connection: The parent Connection asset.
        :return: A pyatlan Folder object.
        """
        qualified_name = f"{connection.qualified_name}/{user_data['name']}"
        
        return Folder.create(
            name=user_data.get("name"),
            qualified_name=qualified_name,
            connection_qualified_name=connection.qualified_name,
            description=user_data.get("bio"),
        )

    def transform_repository_to_folder(self, repo_data: Dict[str, Any], user_folder: Folder) -> Folder:
        """
        Transforms a GitHub repository into an Atlan Folder asset.
        
        :param repo_data: The dictionary of repository metadata.
        :param user_folder: The parent Folder asset (representing the user).
        :return: A pyatlan Folder object.
        """
        qualified_name = f"{user_folder.qualified_name}/{repo_data['name']}"
        
        return Folder.create(
            name=repo_data.get("name"),
            qualified_name=qualified_name,
            connection_qualified_name=user_folder.qualified_name,
            description=repo_data.get("description"),
        )