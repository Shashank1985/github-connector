1.  **Clone the repo Start and activate virtual environment in the project directory**
    ```bash
    uv venv
    .venv\Scripts\Activate (Windows) or source .venv/bin/activate(Linux)

    uv sync (for downloading requirements in the venv)
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