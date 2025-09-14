
import httpx
from typing import Any, Dict, Optional
import time

from application_sdk.clients.base import BaseClient
from application_sdk.observability.logger_adaptor import get_logger

logger = get_logger(__name__)


class GitHubClient(BaseClient):
    """
    Client to interact with the GitHub API for metadata extraction.
    This class handles authentication and makes API calls to fetch
    user and repository information.
    """

    def __init__(self, pat: Optional[str] = None):
        """
        Initializes the GitHub client with a raw PAT.
        
        Args:
            pat: The GitHub Personal Access Token.
        """
        super().__init__()
        self.pat = pat
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Retrieves the authenticated HTTP client instance.
        """
        if self.client is None:
            headers = {}
            if self.pat:
                headers["Authorization"] = f"token {self.pat}"
                logger.info("Using PAT for GitHub API authentication.")
            
            self.client = httpx.AsyncClient(headers=headers, base_url="https://api.github.com")

        return self.client

    async def get_user_metadata(self, username: str) -> Dict[str, Any]:
        """
        Fetches metadata for a given GitHub user or organization, with fallback values.

        :param username: The GitHub username or organization name.
        :return: A dictionary containing the user's metadata with default values for missing data.
        """
        client = await self._get_client()
        url = f"/users/{username}"
        try:
            response = await client.get(url)
            response.raise_for_status()
            user_data = response.json()
            print(user_data)
            return {
                "name": user_data.get("name") or user_data.get("login") or "N/A",
                "node_id": user_data.get("node_id", "N/A"),
                "profile_url": user_data.get("html_url") or "N/A",
                'avatar_url': user_data.get("avatar_url") or "N/A",
                "bio": user_data.get("bio") or "No bio provided.",
                "type": user_data.get("type", "N/A"),
                "company": user_data.get("company") or "N/A",
                "location": user_data.get("location") or "N/A",
                "email": user_data.get("email") or "N/A",
                "blog": user_data.get("blog") or "N/A",
                "twitter_username": user_data.get("twitter_username") or "N/A",
                "created_at": user_data.get("created_at") or "N/A",
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "followers_url": user_data.get("followers_url", "N/A"),
                "following_url": user_data.get("following_url", "N/A"),
                "public_repos": user_data.get("public_repos", 0),
                "public_gists": user_data.get("public_gists", 0),
                "created_at": user_data.get("created_at") or "N/A",
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