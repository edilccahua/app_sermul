from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .grupo_trabajo import GrupoTrabajo
    from .parada import Parada
    from .usuario import Usuario
    from .reserva_detalle import ReservaDetalle


class Reserva(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_reserva: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    parada_id: Mapped[int] = mapped_column(ForeignKey("paradas.id"), nullable=False)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupos_trabajo.id"), nullable=False)
    creado_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    turno: Mapped[str | None] = mapped_column(String(10), nullable=True)  # Dia / Noche
    fecha_programada: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="Pendiente")
    aprobado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_aprobacion: Mapped[datetime | None] = mapped_column(DateTime)
    despachado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    actualizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    fecha_despacho: Mapped[datetime | None] = mapped_column(DateTime)
    motivo_rechazo: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    parada: Mapped["Parada"] = relationship("Parada", lazy="joined")
    grupo: Mapped["GrupoTrabajo"] = relationship("GrupoTrabajo", lazy="joined")
    creado_por: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[creado_por_id], lazy="joined")
    aprobado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[aprobado_por_id], lazy="joined")
    despachado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[despachado_por_id], lazy="joined")
    actualizado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[actualizado_por_id], lazy="joined")
    detalles: Mapped[list["ReservaDetalle"]] = relationship("ReservaDetalle", lazy="joined")
