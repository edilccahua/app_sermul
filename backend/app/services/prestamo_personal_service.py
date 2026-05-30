import uuid
from datetime import datetime, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..models.parada import Parada
from ..models.usuario import Usuario
from ..schemas.prestamo_personal import DevolucionPersonalRequest, PrestamoPersonalRequest


class PrestamoPersonalService:
    def __init__(self, db: Session):
        self.db = db

    def _get_parada_activa(self) -> Parada:
        parada = self.db.query(Parada).filter(Parada.estado == "Activa").first()
        if not parada:
            raise ValueError("No hay una parada activa actualmente para registrar el movimiento.")
        return parada

    def prestar(self, request: PrestamoPersonalRequest, usuario_ejecuta_id: int) -> dict:
        if not request.items:
            raise ValueError("No hay items para prestar")

        parada = self._get_parada_activa()

        receptor = self.db.query(Usuario).filter(Usuario.id == request.usuario_receptor_id).first()
        if not receptor:
            raise ValueError(f"Usuario receptor con ID {request.usuario_receptor_id} no encontrado")

        try:
            procesados = 0
            with self.db.begin_nested():
                for item in request.items:
                    if item.cantidad <= 0:
                        continue

                    material = (
                        self.db.query(CatalogoMaterial)
                        .filter(CatalogoMaterial.id == item.catalogo_id)
                        .with_for_update(of=CatalogoMaterial)
                        .first()
                    )

                    if not material:
                        raise ValueError(f"Material con ID {item.catalogo_id} no encontrado")
                    if material.cant_disponible < item.cantidad:
                        raise ValueError(f"Stock insuficiente para '{material.nombre}'.")

                    material.cant_disponible -= item.cantidad
                    material.cant_en_uso += item.cantidad

                    movimiento = HistorialMovimiento(
                        id=uuid.uuid4(),
                        timestamp=datetime.now(timezone.utc),
                        tipo_movimiento="Entrega",
                        catalogo_id=item.catalogo_id,
                        cantidad=item.cantidad,
                        parada_id=parada.id,
                        grupo_destino_id=None,
                        usuario_receptor_id=request.usuario_receptor_id,
                        usuario_ejecuta_id=usuario_ejecuta_id,
                        observacion_entrega=item.observacion_entrega,
                        estado_origen="Disponible",
                        estado_destino="En_Uso",
                    )
                    self.db.add(movimiento)
                    procesados += 1
                self.db.flush()
            self.db.commit()
        except ValueError:
            self.db.rollback()
            raise

        return {
            "procesados": procesados,
            "mensaje": f"Préstamo personal exitoso: {procesados} items entregados a {receptor.nombre} {receptor.apellido}.",
        }

    def devolver(self, request: DevolucionPersonalRequest, usuario_ejecuta_id: int) -> dict:
        if not request.items:
            raise ValueError("No hay items para devolver")

        parada = self._get_parada_activa()

        try:
            procesados = 0
            with self.db.begin_nested():
                for item in request.items:
                    if item.cantidad_devuelta <= 0:
                        continue

                    material = (
                        self.db.query(CatalogoMaterial)
                        .filter(CatalogoMaterial.id == item.catalogo_id)
                        .with_for_update(of=CatalogoMaterial)
                        .first()
                    )

                    if not material:
                        raise ValueError(f"Material con ID {item.catalogo_id} no encontrado")

                    if material.cant_en_uso < item.cantidad_devuelta:
                        raise ValueError(
                            f"No hay suficientes unidades en uso para '{material.nombre}'."
                        )

                    material.cant_en_uso -= item.cantidad_devuelta

                    # Lógica según estado
                    if item.estado == "Operativa":
                        material.cant_disponible += item.cantidad_devuelta
                        estado_destino = "Disponible"
                        tipo_mov = "Devolucion"
                    elif item.estado == "Malograda":
                        if not item.observacion:
                            raise ValueError(f"Debe describir el daño para '{material.nombre}'")
                        material.cant_malograda += item.cantidad_devuelta
                        estado_destino = "Malograda"
                        tipo_mov = "Paso_Mantenimiento"
                    elif item.estado == "Perdida":
                        material.cant_perdida += item.cantidad_devuelta
                        estado_destino = "Perdida"
                        tipo_mov = "Perdida"
                    else:
                        continue

                    movimiento = HistorialMovimiento(
                        id=uuid.uuid4(),
                        timestamp=datetime.now(timezone.utc),
                        tipo_movimiento=tipo_mov,
                        catalogo_id=item.catalogo_id,
                        cantidad=item.cantidad_devuelta,
                        parada_id=parada.id,
                        grupo_destino_id=None,
                        usuario_receptor_id=request.usuario_receptor_id,
                        usuario_ejecuta_id=usuario_ejecuta_id,
                        observacion_recepcion=item.observacion,
                        estado_origen="En_Uso",
                        estado_destino=estado_destino,
                    )
                    self.db.add(movimiento)
                    procesados += 1
                self.db.flush()
            self.db.commit()
        except ValueError:
            self.db.rollback()
            raise

        return {
            "procesados": procesados,
            "mensaje": f"Devolución personal procesada: {procesados} items.",
        }

    def herramientas_por_usuario(self, usuario_id: int):
        # Query de sumarización
        entregas = func.sum(
            case(
                (HistorialMovimiento.tipo_movimiento == "Entrega", HistorialMovimiento.cantidad),
                else_=0,
            )
        )
        devoluciones = func.sum(
            case(
                (
                    HistorialMovimiento.tipo_movimiento.in_(
                        ["Devolucion", "Perdida", "Paso_Mantenimiento"]
                    ),
                    HistorialMovimiento.cantidad,
                ),
                else_=0,
            )
        )

        query = (
            self.db.query(
                CatalogoMaterial.id.label("catalogo_id"),
                CatalogoMaterial.codigo_interno,
                CatalogoMaterial.nombre,
                CatalogoMaterial.marca,
                (entregas - devoluciones).label("cantidad_en_posesion"),
                func.max(HistorialMovimiento.timestamp).label("fecha_ultimo_prestamo"),
            )
            .join(HistorialMovimiento, CatalogoMaterial.id == HistorialMovimiento.catalogo_id)
            .filter(HistorialMovimiento.usuario_receptor_id == usuario_id)
            .group_by(CatalogoMaterial.id)
            .having((entregas - devoluciones) > 0)
        )

        resultados = []
        for r in query.all():
            resultados.append(
                {
                    "catalogo_id": r.catalogo_id,
                    "codigo_interno": r.codigo_interno,
                    "nombre": r.nombre,
                    "marca": r.marca,
                    "cantidad_en_posesion": r.cantidad_en_posesion,
                    "fecha_ultimo_prestamo": r.fecha_ultimo_prestamo,
                    "parada_nombre": None,
                }
            )
        return resultados
