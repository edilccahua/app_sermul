from datetime import date, datetime

from pydantic import BaseModel, Field

from .especialidad import EspecialidadResponse


class RolResponse(BaseModel):
    id: int
    codigo: str
    nombre: str

    model_config = {"from_attributes": True}


class UsuarioResponse(BaseModel):
    id: int
    dni: str
    nombre: str
    apellido: str
    email: str | None = None
    telefono: str | None = None
    rol_id: int
    activo: bool
    ultimo_acceso: datetime | None = None
    rol: RolResponse | None = None
    especialidad: EspecialidadResponse | None = None

    model_config = {"from_attributes": True}


class PasswordChangeRequest(BaseModel):
    new_password: str = Field(min_length=6, description="Nueva contraseña (mínimo 6 caracteres)")


class UsuarioCreate(BaseModel):
    dni: str = Field(min_length=8, max_length=20)
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    rol_id: int
    email: str | None = None
    telefono: str | None = None
    especialidad_id: int | None = None


class GrupoUsuarioResumen(BaseModel):
    grupo_id: int
    grupo_codigo: str
    grupo_nombre: str
    parada_id: int
    parada_codigo: str
    parada_nombre: str
    fecha_ingreso: date
    fecha_salida: date | None = None
    activo: bool

    model_config = {"from_attributes": True}


class ParadaUsuarioResumen(BaseModel):
    parada_id: int
    parada_codigo: str
    parada_nombre: str
    grupo_codigo: str
    grupo_nombre: str
    lider_nombre: str
    fecha_ingreso: date

    model_config = {"from_attributes": True}


class UsuarioDetalleResponse(UsuarioResponse):
    historial_grupos: list[GrupoUsuarioResumen] = []
    historial_paradas: list[ParadaUsuarioResumen] = []
