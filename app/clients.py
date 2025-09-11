import httpx
from typing import Any, Dict, Optional
import time

from application_sdk.clients.base import BaseClient
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.services.secretstore import SecretStore

logger = get_logger(__name__)


class GitHubClient(BaseClient):
    """
    Client to interact with the GitHub API for metadata extraction.
    This class handles authentication and makes API calls to fetch
    user and repository information.
    """

    def __init__(self, token_secret_key: Optional[str] = None):
        """
        Initializes the GitHub client.
        
        Args:
            token_secret_key: The key to retrieve the GitHub Personal Access Token from the SecretStore.
        """
        super().__init__()
        self.token_secret_key = token_secret_key
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Retrieves the authenticated HTTP client instance.
        """
        if self.client is None:
            headers = {}
            if self.token_secret_key:
                # Retrieve the GitHub token securely from the SecretStore
                try:
                    credentials = await SecretStore.get_credentials(self.token_secret_key)
                    token = credentials.get("token")  # Assuming the key in secret is 'token'
                    headers["Authorization"] = f"token {token}"
                    logger.info("Successfully retrieved GitHub token from SecretStore.")
                except Exception as e:
                    logger.error(f"Failed to retrieve GitHub token from SecretStore: {e}")
                    raise RuntimeError("Failed to retrieve GitHub credentials.")

            self.client = httpx.AsyncClient(headers=headers, base_url="https://api.github.com")

        return self.client

    async def get_user_metadata(self, username: str) -> Dict[str, Any]:
        """
        Fetches metadata for a given GitHub user or organization.

        :param username: The GitHub username or organization name.
        :return: A dictionary containing the user's metadata.
        """
        client = await self._get_client()
        url = f"/users/{username}"
        try:
            response = await client.get(url)
            response.raise_for_status()
            user_data = response.json()
            return {
                "name": user_data.get("name") or user_data.get("login"),
                "profile_url": user_data.get("html_url"),
                "bio": user_data.get("bio"),
                "followers": user_data.get("followers"),
                "following": user_data.get("following"),
                "repository_count": user_data.get("public_repos"),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching user data for {username}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while fetching user data for {username}: {e}")
            raise

    async def get_repositories_metadata(self, username: str) -> list[Dict[str, Any]]:
        """
        Fetches all public repositories for a given user or organization.

        :param username: The GitHub username or organization name.
        :return: A list of dictionaries, where each dictionary contains a repository's metadata.
        """
        client = await self._get_client()
        repos = []
        page = 1
        per_page = 100
        while True:
            url = f"/users/{username}/repos?page={page}&per_page={per_page}"
            try:
                response = await client.get(url)
                response.raise_for_status()
                page_repos = response.json()
                if not page_repos:
                    break
                
                for repo in page_repos:
                    repos.append({
                        "name": repo.get("name"),
                        "description": repo.get("description"),
                        "language": repo.get("language"),
                        "star_count": repo.get("stargazers_count"),
                        "fork_count": repo.get("forks_count"),
                        "issue_count": repo.get("open_issues_count"),
                        "created_at": repo.get("created_at"),
                        "updated_at": repo.get("updated_at"),
                        "url": repo.get("html_url"),
                    })
                
                page += 1
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching repositories for {username}: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"An error occurred while fetching repositories for {username}: {e}")
                raise

        return repos