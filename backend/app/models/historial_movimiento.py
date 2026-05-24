import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .catalogo_material import CatalogoMaterial
    from .grupo_trabajo import GrupoTrabajo
    from .parada import Parada
    from .usuario import Usuario


class HistorialMovimiento(Base):
    __tablename__ = "historial_movimientos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        primary_key=True,
        server_default=func.current_timestamp(),
    )
    tipo_movimiento: Mapped[str] = mapped_column(String(30), nullable=False)
    catalogo_id: Mapped[int] = mapped_column(
        ForeignKey("catalogo_materiales.id"), nullable=False
    )
    parada_id: Mapped[int] = mapped_column(
        ForeignKey("paradas.id"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    usuario_ejecuta_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id")
    )
    grupo_destino_id: Mapped[int | None] = mapped_column(
        ForeignKey("grupos_trabajo.id")
    )
    usuario_receptor_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id")
    )
    tarea_id: Mapped[int | None] = mapped_column(Integer)
    reserva_id: Mapped[int | None] = mapped_column(Integer)
    estado_origen: Mapped[str | None] = mapped_column(String(20))
    estado_destino: Mapped[str | None] = mapped_column(String(20))
    observaciones: Mapped[str | None] = mapped_column(Text)
    observacion_entrega: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacion_recepcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    catalogo: Mapped["CatalogoMaterial"] = relationship(
        "CatalogoMaterial", lazy="joined"
    )
    parada: Mapped["Parada"] = relationship(
        "Parada", lazy="joined"
    )
    grupo_destino: Mapped["GrupoTrabajo | None"] = relationship(
        "GrupoTrabajo", foreign_keys=[grupo_destino_id], lazy="joined"
    )
    usuario_ejecuta: Mapped["Usuario | None"] = relationship(
        "Usuario", foreign_keys=[usuario_ejecuta_id], lazy="joined"
    )
    usuario_receptor: Mapped["Usuario | None"] = relationship(
        "Usuario", foreign_keys=[usuario_receptor_id], lazy="joined"
    )
