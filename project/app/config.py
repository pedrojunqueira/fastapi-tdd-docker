import logging
from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = "dev"
    testing: bool = 0
    database_url: AnyUrl = None

    # Azure JWT Configuration
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    jwt_algorithm: str = "RS256"
    jwt_audience: str = ""  # Usually the client_id for Entra ID
    use_mock_auth: bool = True  # Enable mock auth for development


@lru_cache
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
