from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .catalogo_material import CatalogoMaterial


class InventarioFisico(Base):
    __tablename__ = "inventario_fisico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(50), unique=True)
    catalogo_id: Mapped[int] = mapped_column(
        ForeignKey("catalogo_materiales.id"), nullable=False
    )
    numero_serie: Mapped[str | None] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="Disponible")
    ubicacion_fisica: Mapped[str | None] = mapped_column(String(100))
    ubicacion_macro: Mapped[str] = mapped_column(String(20), nullable=False, default="Ciudad")
    fecha_adquisicion: Mapped[date | None] = mapped_column(Date)
    fecha_ultima_inspeccion: Mapped[date | None] = mapped_column(Date)
    proxima_inspeccion: Mapped[date | None] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    catalogo: Mapped["CatalogoMaterial"] = relationship("CatalogoMaterial", lazy="joined")
