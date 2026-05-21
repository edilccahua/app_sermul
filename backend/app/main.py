from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import auth, catalogo, check, historial, inventario, paradas

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
app.include_router(catalogo.router, prefix="/api/catalogo", tags=["catalogo"])
app.include_router(check.router, prefix="/api/inventario", tags=["check"])
app.include_router(inventario.router, prefix="/api/inventario", tags=["inventario"])
app.include_router(paradas.router, prefix="/api/paradas", tags=["paradas"])
app.include_router(historial.router, prefix="/api/historial", tags=["historial"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
