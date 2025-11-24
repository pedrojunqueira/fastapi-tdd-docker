import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ping, summaries
from app.azure import azure_scheme
from app.config import get_settings
from app.db import init_db

log = logging.getLogger("uvicorn")

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()
    yield


def create_application() -> FastAPI:
    application = FastAPI(
        swagger_ui_oauth2_redirect_url="/oauth2-redirect",
        swagger_ui_init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": settings.openapi_client_id,
            "scopes": settings.scope_name,
        },
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    # Configure CORS
    if settings.backend_cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.backend_cors_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    application.include_router(ping.router)
    application.include_router(
        summaries.router, prefix="/summaries", tags=["summaries"]
    )

    return application


app = create_application()

init_db(app)
