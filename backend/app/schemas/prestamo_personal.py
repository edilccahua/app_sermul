from datetime import datetime

from pydantic import BaseModel, Field


class PrestamoPersonalItem(BaseModel):
    catalogo_id: int
    cantidad: int = Field(ge=1, default=1)
    observacion_entrega: str | None = None


class PrestamoPersonalRequest(BaseModel):
    usuario_receptor_id: int
    items: list[PrestamoPersonalItem]


class DevolucionPersonalItem(BaseModel):
    catalogo_id: int
    cantidad_devuelta: int = Field(ge=0, default=0)
    estado: str = Field(pattern=r"^(Operativa|Malograda|Perdida)$")
    observacion: str | None = None


class DevolucionPersonalRequest(BaseModel):
    usuario_receptor_id: int
    items: list[DevolucionPersonalItem]


class PrestamoPersonalResponse(BaseModel):
    procesados: int
    mensaje: str


class HerramientaPrestadaResponse(BaseModel):
    catalogo_id: int
    codigo_interno: str
    nombre: str
    marca: str | None = None
    cantidad_en_posesion: int
    fecha_ultimo_prestamo: datetime | None = None
    parada_nombre: str | None = None
