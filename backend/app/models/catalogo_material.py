from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base

if TYPE_CHECKING:
    from .categoria_material import CategoriaMaterial
    from .usuario import Usuario


class CatalogoMaterial(Base):
    __tablename__ = "catalogo_materiales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_interno: Mapped[str] = mapped_column(String(15), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias_materiales.id"), nullable=False
    )
    tipo_material: Mapped[str] = mapped_column(String(30), nullable=False)
    marca: Mapped[str | None] = mapped_column(String(100))
    modelo: Mapped[str | None] = mapped_column(String(100))
    fecha_ingreso: Mapped[date | None] = mapped_column(Date, server_default=func.current_date())
    costo_reposicion: Mapped[float | None] = mapped_column(Numeric(10, 2))
    moneda: Mapped[str] = mapped_column(String(3), default="PEN")
    proveedor: Mapped[str | None] = mapped_column(String(200))
    vida_util_dias: Mapped[int | None] = mapped_column(Integer)
    requiere_certificacion: Mapped[bool] = mapped_column(Boolean, default=False)
    es_devolutivo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    stock_minimo: Mapped[int | None] = mapped_column(Integer)
    unidad_medida: Mapped[str | None] = mapped_column(String(20))
    talla: Mapped[str | None] = mapped_column(String(20))
    cant_disponible: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cant_en_uso: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cant_malograda: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cant_perdida: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    creado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    actualizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    imagen_url: Mapped[str | None] = mapped_column(String(500))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    categoria: Mapped["CategoriaMaterial"] = relationship("CategoriaMaterial", lazy="joined")
    creado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[creado_por_id], lazy="joined")
    actualizado_por: Mapped["Usuario | None"] = relationship("Usuario", foreign_keys=[actualizado_por_id], lazy="joined")
