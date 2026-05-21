from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .grupo_trabajo import GrupoTrabajo
    from .usuario import Usuario


class GrupoIntegrante(Base):
    __tablename__ = "grupos_integrantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos_trabajo.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    fecha_ingreso: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    fecha_salida: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    grupo: Mapped["GrupoTrabajo"] = relationship("GrupoTrabajo", lazy="joined")
    usuario: Mapped["Usuario"] = relationship("Usuario", lazy="joined")
