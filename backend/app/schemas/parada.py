from datetime import date, datetime

from pydantic import BaseModel, Field


class ParadaCreate(BaseModel):
    codigo: str = Field(max_length=30)
    nombre: str = Field(max_length=200)
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: str = Field(default="Planificada", max_length=20)
    observaciones: str | None = None


class ParadaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=200)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: str | None = Field(None, max_length=20)
    observaciones: str | None = None


class ParadaResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: str
    observaciones: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
