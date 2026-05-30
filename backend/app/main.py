from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.scheduler import create_scheduler
from .api import auth, catalogo, check, historial, inventario, paradas, grupos, reservas, dashboards, usuarios, prestamo_personal, especialidades


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación (startup / shutdown)."""
    scheduler = create_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="SERMUL API",
    description="Sistema de Gestión de Herramientas para Paradas de Planta",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
app.include_router(catalogo.router, prefix="/api/catalogo", tags=["catalogo"])
app.include_router(check.router, prefix="/api/inventario", tags=["check"])
app.include_router(inventario.router, prefix="/api/inventario", tags=["inventario"])
app.include_router(paradas.router, prefix="/api/paradas", tags=["paradas"])
app.include_router(historial.router, prefix="/api/historial", tags=["historial"])
app.include_router(grupos.router, prefix="/api/grupos", tags=["grupos"])
app.include_router(reservas.router, prefix="/api/reservas", tags=["reservas"])
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["dashboards"])
app.include_router(prestamo_personal.router, prefix="/api/prestamo-personal", tags=["prestamo-personal"])
app.include_router(especialidades.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

