"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models.schemas import HealthResponse
from routers import chat, documents, settings

settings_ = get_settings()

app = FastAPI(title=settings_.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(settings.router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Report service liveness for Docker healthchecks and monitoring."""
    return HealthResponse(
        status="ok",
        app_name=settings_.app_name,
        environment=settings_.environment,
    )
