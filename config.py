from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    phoenix_collector_endpoint: str = Field(
        ...,
        alias="PHOENIX_COLLECTOR_ENDPOINT",
        description="The endpoint to send telemetry data to Phoenix.",
    )
    prod_cors_origin: str = Field(
        ...,
        alias="PROD_CORS_ORIGIN",
        description="The origin of the web application.",
    )
    session_service_uri: str = Field(
        ...,
        alias="SESSION_SERVICE_URI",
        description="The URI of the session service.",
    )
    port: int = Field(
        ...,
        alias="PORT",
        description="The port to run the web application on.",
    )
    web_allowed: bool = Field(
        ...,
        alias="WEB_ALLOWED",
        description="Whether the web application is allowed to be accessed.",
    )
