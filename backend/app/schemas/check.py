from pydantic import BaseModel, Field


class CheckOutRequest(BaseModel):
    catalogo_id: int
    cantidad: int = Field(ge=1, default=1)
    grupo_id: int
    parada_id: int
    observacion_entrega: str | None = None


class CheckInRequest(BaseModel):
    catalogo_id: int
    cant_buen_estado: int = Field(ge=0, default=0)
    cant_malograda: int = Field(ge=0, default=0)
    parada_id: int | None = None
    observacion_recepcion: str | None = None
    descripcion_dano: str | None = None


class CheckResponse(BaseModel):
    movimiento_id: str
    tipo: str
    catalogo_id: int
    cantidad: int
    mensaje: str


class CheckOutMasivoItem(BaseModel):
    catalogo_id: int
    cantidad: int = Field(ge=1, default=1)
    observacion_entrega: str | None = None


class CheckOutMasivoRequest(BaseModel):
    grupo_id: int
    parada_id: int
    items: list[CheckOutMasivoItem]


class CheckInMasivoItem(BaseModel):
    catalogo_id: int
    cantidad_devuelta: int = Field(ge=0, default=0)
    estado: str = Field(pattern=r"^(Operativa|Malograda|Perdida)$")
    observacion: str | None = None


class CheckInMasivoRequest(BaseModel):
    grupo_id: int
    parada_id: int
    items: list[CheckInMasivoItem]
