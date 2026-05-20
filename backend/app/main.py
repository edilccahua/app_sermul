from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import auth

app = FastAPI(
    title="SERMUL API",
    description="Sistema de Gestión de Herramientas para Paradas de Planta",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
