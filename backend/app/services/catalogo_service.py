from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.categoria_material import CategoriaMaterial
from ..schemas.catalogo import CatalogoCreate, CatalogoUpdate


class CatalogoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[CatalogoMaterial]:
        return (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.activo.is_(True))
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )

    def get_by_id(self, catalogo_id: int) -> CatalogoMaterial:
        catalogo = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == catalogo_id)
            .first()
        )
        if not catalogo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material de catálogo no encontrado",
            )
        return catalogo

    def create(self, data: CatalogoCreate, usuario_id: int | None = None) -> CatalogoMaterial:
        existing = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.codigo_interno == data.codigo_interno)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código interno ya existe",
            )
        categoria = (
            self.db.query(CategoriaMaterial)
            .filter(CategoriaMaterial.id == data.categoria_id)
            .first()
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )

        payload = data.model_dump()

        if payload.get("es_devolutivo") is None:
            payload["es_devolutivo"] = "DEVOLUTIVO" in (data.tipo_material or "").upper()

        if payload.get("fecha_ingreso") is None:
            payload["fecha_ingreso"] = date.today()

        payload["creado_por_id"] = usuario_id

        catalogo = CatalogoMaterial(**payload)
        self.db.add(catalogo)
        self.db.commit()
        self.db.refresh(catalogo)
        return catalogo

    def update(self, catalogo_id: int, data: CatalogoUpdate, usuario_id: int | None = None) -> CatalogoMaterial:
        catalogo = self.get_by_id(catalogo_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(catalogo, field, value)
        catalogo.actualizado_por_id = usuario_id
        self.db.commit()
        self.db.refresh(catalogo)
        return catalogo

    def search(self, term: str) -> list[CatalogoMaterial]:
        return (
            self.db.query(CatalogoMaterial)
            .filter(
                CatalogoMaterial.activo.is_(True),
                or_(
                    CatalogoMaterial.nombre.ilike(f"%{term}%"),
                    CatalogoMaterial.codigo_interno.ilike(f"%{term}%"),
                ),
            )
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )

    def update_stock(self, catalogo_id: int, field: str, delta: int) -> CatalogoMaterial:
        valid_fields = {"cant_disponible", "cant_en_uso", "cant_malograda", "cant_perdida"}
        if field not in valid_fields:
            raise ValueError(f"Campo inválido: {field}. Válidos: {valid_fields}")

        material = self.get_by_id(catalogo_id)
        if not material:
            raise ValueError(f"Material con ID {catalogo_id} no encontrado")

        current = getattr(material, field)
        nuevo_valor = current + delta
        if nuevo_valor < 0:
            raise ValueError(f"{field} no puede ser negativo (actual: {current}, delta: {delta})")

        setattr(material, field, nuevo_valor)
        self.db.commit()
        self.db.refresh(material)
        return material
