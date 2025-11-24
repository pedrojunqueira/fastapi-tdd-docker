import logging
from functools import lru_cache

from pydantic import AnyUrl, computed_field
from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl | None = None

    # Azure Authentication Configuration
    tenant_id: str = ""
    app_client_id: str = ""
    openapi_client_id: str = ""
    backend_cors_origins: list[str] = ["http://localhost:8004"]
    scope_description: str = "user_impersonation"

    @computed_field
    @property
    def scope_name(self) -> str:
        return f"api://{self.app_client_id}/{self.scope_description}"

    @computed_field
    @property
    def scopes(self) -> dict:
        return {
            self.scope_name: self.scope_description,
        }

    @computed_field
    @property
    def openapi_authorization_url(self) -> str:
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        )

    @computed_field
    @property
    def openapi_token_url(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
