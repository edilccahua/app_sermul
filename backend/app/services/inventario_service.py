import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..schemas.inventario import AjusteStockRequest


class InventarioService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, tipo_material: str | None = None) -> list[CatalogoMaterial]:
        query = self.db.query(CatalogoMaterial).filter(CatalogoMaterial.activo.is_(True))
        if tipo_material:
            query = query.filter(CatalogoMaterial.tipo_material == tipo_material)
        return query.order_by(CatalogoMaterial.codigo_interno).all()

    def get_by_id(self, catalogo_id: int) -> CatalogoMaterial:
        material = (
            self.db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == catalogo_id, CatalogoMaterial.activo.is_(True))
            .first()
        )
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material no encontrado",
            )
        return material

    def get_by_short_code(self, short_code: str) -> list[CatalogoMaterial]:
        pattern = f"%{short_code}%"
        return (
            self.db.query(CatalogoMaterial)
            .filter(
                CatalogoMaterial.activo.is_(True),
                or_(
                    CatalogoMaterial.codigo_interno.ilike(pattern),
                    CatalogoMaterial.nombre.ilike(pattern),
                ),
            )
            .order_by(CatalogoMaterial.codigo_interno)
            .all()
        )

    def get_en_uso_por_grupo(self, grupo_id: int):
        sql = text("""
            SELECT catalogo_id, codigo_interno, nombre_herramienta,
                   descripcion, marca,
                   costo_reposicion, cantidad_en_uso, ultima_entrega,
                   dias_en_uso, parada_id, codigo_grupo
            FROM v_herramientas_en_uso
            WHERE grupo_id = :gid
            ORDER BY nombre_herramienta
        """)
        return self.db.execute(sql, {"gid": grupo_id}).mappings().all()

    def ajustar_stock(self, usuario_id: int, data: AjusteStockRequest) -> CatalogoMaterial:
        material = self.get_by_id(data.catalogo_id)

        if data.tipo_ajuste == "INGRESO_COMPRA":
            material.cant_disponible += data.cantidad
            tipo_mov = "Ingreso_Compra"
        elif data.tipo_ajuste == "PASE_MALOGRADO":
            if material.cant_disponible < data.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente. Disponible: {material.cant_disponible}",
                )
            material.cant_disponible -= data.cantidad
            material.cant_malograda += data.cantidad
            tipo_mov = "Paso_Mantenimiento"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de ajuste inválido",
            )

        parada_id = data.parada_id
        if not parada_id:
            from ..models.parada import Parada
            parada = self.db.query(Parada).filter(Parada.estado == "Activa").first()
            if not parada:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay parada activa y no se especificó parada_id para el historial",
                )
            parada_id = parada.id

        mov = HistorialMovimiento(
            id=uuid.uuid4(),
            timestamp=datetime.now(timezone.utc),
            tipo_movimiento=tipo_mov,
            catalogo_id=data.catalogo_id,
            parada_id=parada_id,
            cantidad=data.cantidad,
            usuario_ejecuta_id=usuario_id,
            observaciones=data.observaciones,
        )
        self.db.add(mov)
        self.db.commit()
        self.db.refresh(material)
        return material
