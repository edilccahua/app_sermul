from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.inventario_fisico import InventarioFisico
from ..models.historial_movimiento import HistorialMovimiento
from ..models.grupo_trabajo import GrupoTrabajo
from ..models.parada import Parada


class CheckInOutService:
    def __init__(self, db: Session):
        self.db = db

    def check_out(
        self, short_code: str, grupo_id: int, parada_id: int, usuario_id: int
    ) -> tuple[HistorialMovimiento, InventarioFisico]:
        with self.db.begin_nested():
            catalogo = (
                self.db.query(CatalogoMaterial)
                .filter(CatalogoMaterial.codigo_interno == short_code)
                .first()
            )
            if not catalogo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No existe material con código '{short_code}'",
                )

            grupo = (
                self.db.query(GrupoTrabajo)
                .filter(GrupoTrabajo.id == grupo_id)
                .first()
            )
            if not grupo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Grupo no encontrado",
                )

            parada = (
                self.db.query(Parada)
                .filter(Parada.id == parada_id)
                .first()
            )
            if not parada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parada no encontrada",
                )

            unidad = (
                self.db.query(InventarioFisico)
                .filter(
                    InventarioFisico.catalogo_id == catalogo.id,
                    InventarioFisico.estado == "Disponible",
                    InventarioFisico.ubicacion_macro == "Mina",
                )
                .first()
            )
            if not unidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay unidades disponibles de este material en Mina",
                )

            estado_anterior = unidad.estado
            unidad.estado = "En_Uso"

            movimiento = HistorialMovimiento(
                tipo_movimiento="Entrega",
                catalogo_id=catalogo.id,
                inventario_fisico_id=unidad.id,
                parada_id=parada_id,
                grupo_destino_id=grupo_id,
                usuario_ejecuta_id=usuario_id,
                estado_origen=estado_anterior,
                estado_destino="En_Uso",
            )
            self.db.add(movimiento)

        self.db.commit()
        self.db.refresh(unidad)
        self.db.refresh(movimiento)
        return movimiento, unidad

    def check_in(
        self, inventario_id: int, buen_estado: bool, usuario_id: int, dano: str | None = None
    ) -> tuple[HistorialMovimiento, InventarioFisico]:
        with self.db.begin_nested():
            unidad = (
                self.db.query(InventarioFisico)
                .filter(InventarioFisico.id == inventario_id)
                .first()
            )
            if not unidad:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Unidad de inventario no encontrada",
                )

            if unidad.estado != "En_Uso":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La unidad no está en estado 'En_Uso'",
                )

            estado_anterior = unidad.estado
            if buen_estado:
                unidad.estado = "Disponible"
                tipo_mov = "Devolucion"
                observaciones = None
            else:
                unidad.estado = "Malograda"
                tipo_mov = "Paso_Mantenimiento"
                observaciones = dano

            movimiento = HistorialMovimiento(
                tipo_movimiento=tipo_mov,
                catalogo_id=unidad.catalogo_id,
                inventario_fisico_id=unidad.id,
                parada_id=1,
                usuario_ejecuta_id=usuario_id,
                estado_origen=estado_anterior,
                estado_destino=unidad.estado,
                observaciones=observaciones,
            )
            self.db.add(movimiento)

        self.db.commit()
        self.db.refresh(unidad)
        self.db.refresh(movimiento)
        return movimiento, unidad
