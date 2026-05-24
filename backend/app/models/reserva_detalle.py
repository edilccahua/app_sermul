from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .catalogo_material import CatalogoMaterial
    from .reserva import Reserva


class ReservaDetalle(Base):
    __tablename__ = "reservas_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    catalogo_id: Mapped[int] = mapped_column(ForeignKey("catalogo_materiales.id"), nullable=False)
    cantidad_solicitada: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cantidad_despachada: Mapped[int] = mapped_column(Integer, default=0)

    reserva: Mapped["Reserva"] = relationship("Reserva", back_populates="detalles")
    catalogo: Mapped["CatalogoMaterial"] = relationship("CatalogoMaterial", lazy="joined")
