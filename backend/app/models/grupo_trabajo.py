from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .parada import Parada
    from .usuario import Usuario


class GrupoTrabajo(Base):
    __tablename__ = "grupos_trabajo"
    __table_args__ = (
        UniqueConstraint("codigo", "parada_id", name="uq_grupo_codigo_parada"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    parada_id: Mapped[int] = mapped_column(
        ForeignKey("paradas.id"), nullable=False
    )
    lider_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False
    )
    supervisor_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), nullable=False
    )
    estado: Mapped[str] = mapped_column(String(20), default="Activo")
    descripcion: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    parada: Mapped["Parada"] = relationship("Parada", lazy="joined")
    lider: Mapped["Usuario"] = relationship(
        "Usuario", foreign_keys=[lider_id], lazy="joined"
    )
    supervisor: Mapped["Usuario"] = relationship(
        "Usuario", foreign_keys=[supervisor_id], lazy="joined"
    )
