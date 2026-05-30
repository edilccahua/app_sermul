from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .grupo_integrante import GrupoIntegrante
    from .parada import Parada
    from .usuario import Usuario


class GrupoTrabajo(Base):
    __tablename__ = "grupos_trabajo"
    __table_args__ = (
        UniqueConstraint("codigo", "parada_id", name="grupos_trabajo_codigo_parada_id_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    parada_id: Mapped[int] = mapped_column(
        ForeignKey("paradas.id"), nullable=False
    )
    descripcion: Mapped[str | None] = mapped_column(Text)
    circuito_area: Mapped[str | None] = mapped_column(String(200))
    creado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    actualizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    parada: Mapped["Parada"] = relationship("Parada", lazy="joined")
    integrantes: Mapped[list["GrupoIntegrante"]] = relationship(
        "GrupoIntegrante", back_populates="grupo"
    )
    creado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[creado_por_id], lazy="joined")
    actualizado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[actualizado_por_id], lazy="joined")
