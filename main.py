# main.py
import asyncio
from pathlib import Path
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from application_sdk.application import BaseApplication
from application_sdk.common.error_codes import ApiError
from application_sdk.observability.logger_adaptor import get_logger

from app.activities import GitHubActivities
from app.workflow import GitHubWorkflow

APPLICATION_NAME = "github-connector"

logger = get_logger(__name__)

TEMPLATES_PATH = Path(__file__).parent / "frontend" / "templates"
STATIC_PATH = Path(__file__).parent / "frontend" / "static"

templates = Jinja2Templates(directory=TEMPLATES_PATH)


async def setup_app_and_server():
    """
    Initializes and sets up the application and its FastAPI server.
    """
    try:
        application = BaseApplication(name=APPLICATION_NAME)

        application.server.mount(
            "/static", StaticFiles(directory=STATIC_PATH), name="static"
        )

        @application.server.get("/", response_class=HTMLResponse)
        async def read_root(request: Request):
            return templates.TemplateResponse("index.html", {"request": request})

        @application.server.post("/api/start_extraction")
        async def start_extraction(username: str, pat: str):
            workflow_config = {
                "username": username,
                "pat": pat
            }
            try:
                workflow_run = await application.start_workflow(
                    workflow_class=GitHubWorkflow,
                    workflow_id=f"github_extraction_{username}",
                    workflow_config=workflow_config,
                )
                return {"status": "started", "workflow_id": workflow_run.workflow_id}
            except Exception as e:
                logger.error(f"Failed to start workflow: {e}")
                return {"status": "failed", "error": str(e)}

        await application.setup_workflow(
            workflow_and_activities_classes=[(GitHubWorkflow, GitHubActivities)]
        )
        await application.start_worker()

        await application.setup_server(workflow_class=GitHubWorkflow)
        await application.start_server()

    except ApiError:
        logger.error(f"{ApiError.SERVER_START_ERROR}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(setup_app_and_server())