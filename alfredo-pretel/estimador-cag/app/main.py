from fastapi import FastAPI

from app.config import settings
from app.routers import estimations

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API para generar estimaciones de proyectos de software a partir de "
        "transcripciones de reuniones. Arquitectura CAG: el contexto (ejemplos "
        "históricos) se inyecta directamente en el prompt del LLM."
    ),
)

app.include_router(estimations.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
@app.get("/healthz", tags=["health"], include_in_schema=False)
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "provider": settings.llm_provider,
    }