from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ParadaCreate(BaseModel):
    codigo: str = Field(max_length=30)
    nombre: str = Field(max_length=200)
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: str = Field(default="Planificada", max_length=20)
    empresa_contratista: str = "SERMUL EIRL"
    gerencia_contrato: str | None = None
    responsable_cma: str | None = None
    ubicacion: Literal["Antapaccay", "Tintaya"] | None = None


class ParadaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=200)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: str | None = Field(None, max_length=20)
    empresa_contratista: str | None = None
    gerencia_contrato: str | None = None
    responsable_cma: str | None = None
    ubicacion: Literal["Antapaccay", "Tintaya"] | None = None


class ParadaResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: str
    empresa_contratista: str
    gerencia_contrato: str | None = None
    responsable_cma: str | None = None
    ubicacion: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Cierre de Parada ─────────────────────────────────────────────────────────

class PendienteItem(BaseModel):
    """Herramienta con cantidad pendiente de devolución al cerrar la parada."""
    catalogo_id: int
    nombre: str
    codigo_interno: str
    cantidad_pendiente: int


class CierreParadaResponse(BaseModel):
    """Respuesta del endpoint POST /paradas/{id}/cerrar."""
    parada_id: int
    estado: str
    pendientes: list[PendienteItem]
    mensaje: str


class ResolucionPendienteItem(BaseModel):
    """Un ítem de resolución para herramientas pendientes."""
    catalogo_id: int
    accion: Literal["Devolver", "Perdida", "Continuidad"]
    cantidad: int = Field(ge=1)


class ResolverPendientesRequest(BaseModel):
    """Payload para PUT /paradas/{id}/resolver-pendiente."""
    resoluciones: list[ResolucionPendienteItem]
