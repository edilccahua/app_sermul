import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..models.parada import Parada
from ..schemas.parada import (
    CierreParadaResponse,
    ParadaCreate,
    ParadaUpdate,
    PendienteItem,
    ResolucionPendienteItem,
)

_TIPOS_SALIDA = {"Entrega"}
_TIPOS_ENTRADA = {"Devolucion", "Paso_Mantenimiento"}


class ParadaService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Parada]:
        return (
            self.db.query(Parada)
            .order_by(Parada.fecha_inicio.desc())
            .all()
        )

    def get_by_id(self, parada_id: int) -> Parada:
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
        return parada

    def create(self, data: ParadaCreate, usuario_id: int | None = None) -> Parada:
        existing = (
            self.db.query(Parada)
            .filter(Parada.codigo == data.codigo)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de parada ya existe",
            )
        parada = Parada(
            codigo=data.codigo,
            nombre=data.nombre,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            estado=data.estado,
            empresa_contratista=data.empresa_contratista or "SERMUL EIRL",
            gerencia_contrato=data.gerencia_contrato,
            responsable_cma=data.responsable_cma,
            ubicacion=data.ubicacion,
            creado_por_id=usuario_id,
        )
        self.db.add(parada)
        self.db.commit()
        self.db.refresh(parada)
        return parada

    def update(self, parada_id: int, data: ParadaUpdate, usuario_id: int | None = None) -> Parada:
        parada = self.get_by_id(parada_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(parada, field, value)
        parada.actualizado_por_id = usuario_id
        self.db.commit()
        self.db.refresh(parada)
        return parada

    def _calcular_pendientes(self, parada_id: int) -> list[PendienteItem]:
        salidas = (
            self.db.query(
                HistorialMovimiento.catalogo_id,
                func.sum(HistorialMovimiento.cantidad).label("total"),
            )
            .filter(
                HistorialMovimiento.parada_id == parada_id,
                HistorialMovimiento.tipo_movimiento.in_(_TIPOS_SALIDA),
            )
            .group_by(HistorialMovimiento.catalogo_id)
            .all()
        )

        entradas = (
            self.db.query(
                HistorialMovimiento.catalogo_id,
                func.sum(HistorialMovimiento.cantidad).label("total"),
            )
            .filter(
                HistorialMovimiento.parada_id == parada_id,
                HistorialMovimiento.tipo_movimiento.in_(_TIPOS_ENTRADA),
            )
            .group_by(HistorialMovimiento.catalogo_id)
            .all()
        )

        entradas_map = {row.catalogo_id: row.total for row in entradas}
        pendientes: list[PendienteItem] = []

        for row in salidas:
            devuelto = entradas_map.get(row.catalogo_id, 0)
            pendiente = row.total - devuelto
            if pendiente > 0:
                material = (
                    self.db.query(CatalogoMaterial)
                    .filter(CatalogoMaterial.id == row.catalogo_id)
                    .first()
                )
                if material:
                    pendientes.append(
                        PendienteItem(
                            catalogo_id=row.catalogo_id,
                            nombre=material.nombre,
                            codigo_interno=material.codigo_interno,
                            cantidad_pendiente=pendiente,
                        )
                    )

        return pendientes

    def simular_cierre(self, parada_id: int) -> CierreParadaResponse:
        parada = self.get_by_id(parada_id)

        pendientes = self._calcular_pendientes(parada_id)
        n = len(pendientes)
        mensaje = (
            f"Simulación de cierre. {n} tipo(s) de herramienta(s) pendiente(s) de resolución."
            if n > 0
            else "Simulación de cierre. Sin herramientas pendientes."
        )

        return CierreParadaResponse(
            parada_id=parada_id,
            estado=parada.estado,
            pendientes=pendientes,
            mensaje=mensaje,
        )

    def resolver_pendientes(
        self,
        parada_id: int,
        resoluciones: list[ResolucionPendienteItem],
        usuario_id: int | None = None,
    ) -> dict:
        parada = self.get_by_id(parada_id)
        if parada.estado != "Finalizada":
            parada.estado = "Finalizada"
            parada.fecha_fin = datetime.now(timezone.utc).date()
            self.db.add(parada)

        resueltos = []
        con_continuidad = []

        with self.db.begin_nested():
            for resolucion in resoluciones:
                material = (
                    self.db.query(CatalogoMaterial)
                    .filter(CatalogoMaterial.id == resolucion.catalogo_id)
                    .first()
                )
                if not material:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Material ID {resolucion.catalogo_id} no encontrado",
                    )

                if resolucion.accion == "Continuidad":
                    con_continuidad.append(material.nombre)
                    # CROSS Audit
                    mov = HistorialMovimiento(
                        id=uuid.uuid4(),
                        timestamp=datetime.now(timezone.utc),
                        tipo_movimiento="Ajuste_Inventario",
                        catalogo_id=resolucion.catalogo_id,
                        cantidad=resolucion.cantidad,
                        parada_id=parada_id,
                        usuario_ejecuta_id=usuario_id,
                        estado_origen="En_Uso",
                        estado_destino="En_Uso",
                        observaciones=f"[CONTINUIDAD] Herramienta puesta en gracia de 3 días por cierre de parada {parada.codigo}",
                    )
                    self.db.add(mov)
                    continue

                if material.cant_en_uso < resolucion.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"'{material.nombre}': cant_en_uso ({material.cant_en_uso}) "
                            f"< cantidad solicitada ({resolucion.cantidad})"
                        ),
                    )

                if resolucion.accion == "Devolver":
                    material.cant_en_uso -= resolucion.cantidad
                    material.cant_disponible += resolucion.cantidad
                    tipo_mov = "Devolucion"
                    estado_destino = "Disponible"

                else:  # Perdida
                    material.cant_en_uso -= resolucion.cantidad
                    material.cant_perdida += resolucion.cantidad
                    tipo_mov = "Perdida"
                    estado_destino = "Perdida"

                mov = HistorialMovimiento(
                    id=uuid.uuid4(),
                    timestamp=datetime.now(timezone.utc),
                    tipo_movimiento=tipo_mov,
                    catalogo_id=resolucion.catalogo_id,
                    cantidad=resolucion.cantidad,
                    parada_id=parada_id,
                    usuario_ejecuta_id=usuario_id,
                    estado_origen="En_Uso",
                    estado_destino=estado_destino,
                    observaciones=f"Resolución de cierre de parada {parada.codigo}",
                )
                self.db.add(mov)
                resueltos.append(material.nombre)

            self.db.flush()

        self.db.commit()

        return {
            "resueltos": resueltos,
            "en_continuidad": con_continuidad,
            "mensaje": (
                f"{len(resueltos)} ítem(s) resuelto(s). "
                f"{len(con_continuidad)} ítem(s) en Continuidad (auto-cierre en 3 días)."
            ),
        }
