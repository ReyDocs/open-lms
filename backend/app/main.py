from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from sqlalchemy import select
from app.infrastructure.database.connection import engine, Base, AsyncSessionLocal
from app.infrastructure.database.models import *  # noqa: F403, F401
from app.infrastructure.database.models.system_setting_model import SystemSettingModel
from app.infrastructure.jobs.due_date_reminders import send_due_date_reminders
from app.presentation.api.v1.router import api_v1_router
from app.presentation.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

logger = logging.getLogger(__name__)


async def _run_due_date_reminders():
    while True:
        try:
            await send_due_date_reminders()
        except Exception:
            logger.exception("Due date reminder job failed")
        await asyncio.sleep(5 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(select(SystemSettingModel))).scalars().all()
        persisted_settings = {row.key: row.value for row in rows}
        settings.app_name = persisted_settings.get("app_name", settings.app_name)
        settings.app_logo_url = persisted_settings.get("app_logo_url") or None
        settings.support_email = persisted_settings.get("support_email", settings.support_email)
        settings.maintenance_mode = persisted_settings.get(
            "maintenance_mode", str(settings.maintenance_mode)
        ).lower() == "true"
    reminder_task = asyncio.create_task(_run_due_date_reminders())
    try:
        yield
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="OpenLMS — Clean Architecture Higher Education LMS Backend",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Routers
    app.include_router(api_v1_router)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.app_name,
            "env": settings.app_env,
        }

    return app


app = create_app()
