import logging

from fastapi import FastAPI

from app.api import ping, summaries
from app.api.auth_validation import router as auth_router
from app.db import init_db

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(ping.router)
    application.include_router(
        summaries.router, prefix="/summaries", tags=["summaries"]
    )
    application.include_router(auth_router)

    return application


app = create_application()

init_db(app)
