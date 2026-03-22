import os
import pathlib
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = pathlib.Path(__file__).parent

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=os.environ.get(
        "SESSION_SERVICE_URI",
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres",
    ),
    web=True,
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)