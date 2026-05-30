from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .usuario import Usuario


class Parada(Base):
    __tablename__ = "paradas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="Planificada")
    empresa_contratista: Mapped[str] = mapped_column(String(200), default="SERMUL EIRL")
    gerencia_contrato: Mapped[str | None] = mapped_column(String(200))
    responsable_cma: Mapped[str | None] = mapped_column(String(200))
    ubicacion: Mapped[str | None] = mapped_column(String(100))
    creado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    actualizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    creado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[creado_por_id], lazy="joined")
    actualizado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[actualizado_por_id], lazy="joined")
