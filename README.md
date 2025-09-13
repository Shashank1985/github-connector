# SourceSense

A GitHub metadata extraction application built using the Atlan Application SDK, Temporal and Pythin. It orchestrates a workflow that connects to the GitHub API to intelligently extract user and repository metadata, which is then processed and stored in JSON format.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)
- A github account with a Personal Access Token (PAT)

### Installation Guides
- [macOS Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/MAC.md)
- [Linux Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/LINUX.md)
- [Windows Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/WINDOWS.md)

## Quick Start


1.  **Start and activate virtual environment in the project directory**
    ```bash
    uv venv
    .venv\Scripts\Activate
    ```


