from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    phoenix_collector_endpoint: str | None = Field(
        default=None,
        alias="PHOENIX_COLLECTOR_ENDPOINT",
        description="The endpoint to send telemetry data to Phoenix.",
    )
    prod_cors_origin: str | None = Field(
        default=None,
        alias="PROD_CORS_ORIGIN",
        description="The origin of the web application.",
    )
    session_service_uri: str | None = Field(
        default=None,
        alias="SESSION_SERVICE_URI",
        description="The URI of the session service.",
    )
    port: int = Field(
        default=8000,
        alias="PORT",
        description="The port to run the web application on.",
    )
    web_allowed: bool = Field(
        ...,
        alias="WEB_ALLOWED",
        description="Whether the web application is allowed to be accessed.",
    )

    airports_sqlite_path: str = Field(
        ...,
        alias="AIRPORTS_SQLITE_PATH",
        description="The path to the airports.sqlite database.",
    )
    enable_google_cloud_trace: bool = Field(
        True,
        alias="ENABLE_GOOGLE_CLOUD_TRACE",
        description="Whether to enable Google Cloud Trace.",
    )
    google_cloud_project: str = Field(
        "Test"
        alias="GOOGLE_CLOUD_PROJECT",
        description="The Google Cloud project ID to use for tracing.",
    )