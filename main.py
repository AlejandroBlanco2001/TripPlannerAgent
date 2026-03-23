from phoenix.otel import register
import pathlib
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from config import Config
from contextlib import asynccontextmanager
from tools import scrapper
from fastapi import FastAPI

AGENTS_DIR = pathlib.Path(__file__).parent
config = Config()

tracer_provider = register(
    project_name="default",
    auto_instrument=True,
    endpoint=config.phoenix_collector_endpoint,
)

app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=config.session_service_uri,
    web=config.web_allowed,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scrapper.open_airports_connection(config.airports_sqlite_path)
    yield
    scrapper.close_airports_connection()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)
