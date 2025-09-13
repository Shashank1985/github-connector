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

## Quick Start and Steps to test the project


1.  **Start and activate virtual environment in the project directory**
    ```bash
    uv venv
    .venv\Scripts\Activate (Windows) or source .venv/bin/activate(Linux)
    uv sync
    ```

2.  **Download Required Components**
    ```bash
    uv run poe download-components
    ```

3.  **Set up .env file**
    Create a .env file with the following details.
    The username must correspond to the user who's metadata you want to extract.
    The PAT must be yours to authenticate yourself.
    ```bash
    GITHUB_USERNAME="<your-github-username>"
    GITHUB_PAT="<your-github-pat>"
    ```

4.  **Start dependencies**
    In Windows, this is a 2 step process
    Run dapr in one terminal
    ```bash
    poe start-dapr
    ```
    Run temporal in another
    ```bash
    poe start-temporal
    ```

    In linux, you can start both with the command
    ```bash
    poe start-deps
    ```

5.  **Start app**
    Open a new terminal and run 
    ```bash
    python main.py
    ```

6.  **Send POST request through cURL or Postman**
    You can use this command to send the POST request to start the workflow.
    ```bash
    curl -X POST http://localhost:8000/workflows/v1/start -H "Content-Type:application/json" -d '{"input":"test"}'
    ```
    or simply use PostMan and send a POST request with dummy data to the endpoint workflows/v1/start.
    Upon successful completion of the workflow, you will find 4 different json files with different metadata related information of the 

7.  **Stop the server**
    You can either chose to kill the terminals on which the processes are running or use
    ```bash
    poe stop-deps
    ```
**Access the application:**
This app does not have a frontend right now.
- **Temporal UI**: http://localhost:8233

## Features

- **Intelligent Metadata Extraction**: The application connects to the GitHub API to extract valuable metadata about a specified user and their public repositories. This includes details such as a user's follower count and a repository's star count, fork count, and description.
- **Automated Tagging**: It automatically extracts relevant keywords from repository descriptions and adds them as tags, enriching the metadata with valuable business context.
- **Data Quality Metrics**: The app calculates and reports on key quality metrics, such as the percentage of repositories with a description or automated tags, providing immediate insights into data completeness.
- **Workflow Orchestration**: The project leverages the Temporal.io framework to orchestrate a robust, multi-stage workflow that ensures all data extraction and enrichment tasks are executed reliably and in the correct order.
- **Scalability and Resilience**: By utilizing parallel execution for API calls and including a built-in retry policy, the application is designed to be both highly performant and resilient to transient network or API failures.
- **High Code Quality & Test Coverage**: The project adheres to software engineering best practices with a clean, modular code design and includes a comprehensive suite of unit tests to ensure reliability and maintainability.


