from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..models.grupo_trabajo import GrupoTrabajo
from ..models.parada import Parada
from ..schemas.check import CheckOutMasivoRequest, CheckInMasivoRequest


class CheckInOutService:
    def __init__(self, db: Session):
        self.db = db

    def check_out(
        self, catalogo_id: int, cantidad: int, grupo_id: int,
        parada_id: int, usuario_id: int,
        observacion_entrega: str | None = None,
    ):
        material = self.db.query(CatalogoMaterial).filter(
            CatalogoMaterial.id == catalogo_id
        ).with_for_update(of=CatalogoMaterial).first()
        if not material:
            raise ValueError(f"Material con ID {catalogo_id} no encontrado")
        if material.cant_disponible < cantidad:
            raise ValueError(
                f"Stock insuficiente. Solicitado: {cantidad}, Disponible: {material.cant_disponible}"
            )

        grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == grupo_id).first()
        if not grupo:
            raise ValueError(f"Grupo con ID {grupo_id} no encontrado")

        parada = self.db.query(Parada).filter(Parada.id == parada_id).first()
        if not parada:
            raise ValueError(f"Parada con ID {parada_id} no encontrada")

        with self.db.begin_nested():
            material.cant_disponible -= cantidad
            material.cant_en_uso += cantidad

            movimiento = HistorialMovimiento(
                id=uuid.uuid4(),
                timestamp=datetime.now(timezone.utc),
                tipo_movimiento="Entrega",
                catalogo_id=catalogo_id,
                cantidad=cantidad,
                parada_id=parada_id,
                grupo_destino_id=grupo_id,
                usuario_ejecuta_id=usuario_id,
                observacion_entrega=observacion_entrega,
                estado_origen="Disponible",
                estado_destino="En_Uso",
            )
            self.db.add(movimiento)
            self.db.flush()

        self.db.commit()
        return {
            "movimiento_id": str(movimiento.id),
            "tipo": "Entrega",
            "catalogo_id": catalogo_id,
            "cantidad": cantidad,
            "mensaje": f"Entregado: {cantidad} x {material.nombre} a {grupo.nombre}",
        }

    def check_in(
        self, catalogo_id: int, cant_buen_estado: int,
        cant_malograda: int, usuario_id: int,
        parada_id: int | None = None,
        observacion_recepcion: str | None = None,
        descripcion_dano: str | None = None,
    ):
        if cant_buen_estado + cant_malograda == 0:
            raise ValueError("Debe devolver al menos una unidad")

        material = self.db.query(CatalogoMaterial).filter(
            CatalogoMaterial.id == catalogo_id
        ).with_for_update(of=CatalogoMaterial).first()
        if not material:
            raise ValueError(f"Material con ID {catalogo_id} no encontrado")

        total_devuelto = cant_buen_estado + cant_malograda
        if material.cant_en_uso < total_devuelto:
            raise ValueError(
                f"No hay tantas unidades en uso. En uso: {material.cant_en_uso}, "
                f"Intentando devolver: {total_devuelto}"
            )

        if parada_id is None:
            ultima_entrega = (
                self.db.query(HistorialMovimiento)
                .filter(
                    HistorialMovimiento.catalogo_id == catalogo_id,
                    HistorialMovimiento.tipo_movimiento == "Entrega",
                )
                .order_by(HistorialMovimiento.timestamp.desc())
                .first()
            )
            if not ultima_entrega:
                raise ValueError(
                    "No se encontró una entrega previa para este material. "
                    "Especifique la parada_id para registrar la devolución."
                )
            parada_id = ultima_entrega.parada_id
            grupo_id = ultima_entrega.grupo_destino_id
        else:
            ultima_entrega_parada = (
                self.db.query(HistorialMovimiento)
                .filter(
                    HistorialMovimiento.catalogo_id == catalogo_id,
                    HistorialMovimiento.parada_id == parada_id,
                    HistorialMovimiento.tipo_movimiento == "Entrega",
                )
                .order_by(HistorialMovimiento.timestamp.desc())
                .first()
            )
            grupo_id = ultima_entrega_parada.grupo_destino_id if ultima_entrega_parada else None

        with self.db.begin_nested():
            material.cant_en_uso -= total_devuelto

            mov_bueno = None
            mov_malo = None

            if cant_buen_estado > 0:
                material.cant_disponible += cant_buen_estado
                mov_bueno = HistorialMovimiento(
                    id=uuid.uuid4(),
                    timestamp=datetime.now(timezone.utc),
                    tipo_movimiento="Devolucion",
                    catalogo_id=catalogo_id,
                    cantidad=cant_buen_estado,
                    parada_id=parada_id,
                    grupo_destino_id=grupo_id,
                    usuario_ejecuta_id=usuario_id,
                    observacion_recepcion=observacion_recepcion,
                    estado_origen="En_Uso",
                    estado_destino="Disponible",
                )
                self.db.add(mov_bueno)

            if cant_malograda > 0:
                material.cant_malograda += cant_malograda
                mov_malo = HistorialMovimiento(
                    id=uuid.uuid4(),
                    timestamp=datetime.now(timezone.utc),
                    tipo_movimiento="Paso_Mantenimiento",
                    catalogo_id=catalogo_id,
                    cantidad=cant_malograda,
                    parada_id=parada_id,
                    grupo_destino_id=grupo_id,
                    usuario_ejecuta_id=usuario_id,
                    observacion_recepcion=observacion_recepcion or descripcion_dano,
                    estado_origen="En_Uso",
                    estado_destino="Malograda",
                )
                self.db.add(mov_malo)

            self.db.flush()

        self.db.commit()
        movimiento_id = str(mov_bueno.id) if mov_bueno else str(mov_malo.id)  # type: ignore[union-attr]

        return {
            "movimiento_id": movimiento_id,
            "tipo": "Devolucion",
            "catalogo_id": catalogo_id,
            "cantidad": total_devuelto,
            "mensaje": (
                f"Devuelto: {cant_buen_estado} en buen estado"
                + (f", {cant_malograda} malogradas" if cant_malograda > 0 else "")
            ),
        }

    # ── Check-Out Masivo (transacción atómica) ─────────────────────────────

    def check_out_masivo(self, request: CheckOutMasivoRequest, usuario_id: int) -> dict:
        if not request.items:
            raise ValueError("No hay items para despachar")

        grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == request.grupo_id).first()
        if not grupo:
            raise ValueError(f"Grupo con ID {request.grupo_id} no encontrado")

        parada = self.db.query(Parada).filter(Parada.id == request.parada_id).first()
        if not parada:
            raise ValueError(f"Parada con ID {request.parada_id} no encontrada")

        # Transacción atómica: validar + mutar en un solo savepoint
        try:
            procesados = 0
            with self.db.begin_nested():
                for item in request.items:
                    if item.cantidad <= 0:
                        continue

                    material = self.db.query(CatalogoMaterial).filter(
                        CatalogoMaterial.id == item.catalogo_id
                    ).with_for_update(of=CatalogoMaterial).first()
                    if not material:
                        raise ValueError(f"Material con ID {item.catalogo_id} no encontrado")
                    if material.cant_disponible < item.cantidad:
                        raise ValueError(
                            f"Stock insuficiente para '{material.nombre}'. "
                            f"Solicitado: {item.cantidad}, Disponible: {material.cant_disponible}"
                        )

                    material.cant_disponible -= item.cantidad
                    material.cant_en_uso += item.cantidad

                    movimiento = HistorialMovimiento(
                        id=uuid.uuid4(),
                        timestamp=datetime.now(timezone.utc),
                        tipo_movimiento="Entrega",
                        catalogo_id=item.catalogo_id,
                        cantidad=item.cantidad,
                        parada_id=request.parada_id,
                        grupo_destino_id=request.grupo_id,
                        usuario_ejecuta_id=usuario_id,
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
            "mensaje": f"Despacho masivo exitoso: {procesados} items procesados.",
        }

    # ── Check-In Masivo ────────────────────────────────────────────────────

    def check_in_masivo(self, request: CheckInMasivoRequest, usuario_id: int) -> dict:
        if not request.items:
            raise ValueError("No hay items para devolver")

        resultados = []
        for item in request.items:
            if item.cantidad_devuelta <= 0:
                continue

            if item.estado == "Operativa":
                resultado = self.check_in(
                    catalogo_id=item.catalogo_id,
                    cant_buen_estado=item.cantidad_devuelta,
                    cant_malograda=0,
                    usuario_id=usuario_id,
                    parada_id=request.parada_id,
                    observacion_recepcion=item.observacion,
                )
            elif item.estado == "Malograda":
                if not item.observacion:
                    raise ValueError(
                        f"Debe describir el daño para '{item.catalogo_id}' marcado como Malograda"
                    )
                resultado = self.check_in(
                    catalogo_id=item.catalogo_id,
                    cant_buen_estado=0,
                    cant_malograda=item.cantidad_devuelta,
                    usuario_id=usuario_id,
                    parada_id=request.parada_id,
                    descripcion_dano=item.observacion,
                )
            elif item.estado == "Perdida":
                resultado = self.registrar_perdida(
                    catalogo_id=item.catalogo_id,
                    cantidad=item.cantidad_devuelta,
                    grupo_id=request.grupo_id,
                    parada_id=request.parada_id,
                    usuario_id=usuario_id,
                    observaciones=item.observacion,
                )
            else:
                continue

            resultados.append(resultado)

        return {
            "procesados": len(resultados),
            "mensaje": f"Devolución masiva: {len(resultados)} ítems procesados.",
        }

    # ── Registrar Pérdida ──────────────────────────────────────────────────

    def registrar_perdida(
        self, catalogo_id: int, cantidad: int, grupo_id: int,
        parada_id: int, usuario_id: int, observaciones: str | None = None,
    ):
        material = self.db.query(CatalogoMaterial).filter(
            CatalogoMaterial.id == catalogo_id
        ).with_for_update(of=CatalogoMaterial).first()

        if not material:
            raise ValueError(f"Material con ID {catalogo_id} no encontrado")
        if material.cant_en_uso < cantidad:
            raise ValueError(
                f"No hay tantas unidades en uso. En uso: {material.cant_en_uso}, "
                f"Intentando marcar pérdida: {cantidad}"
            )

        material.cant_en_uso -= cantidad
        material.cant_perdida += cantidad

        movimiento = HistorialMovimiento(
            id=uuid.uuid4(),
            timestamp=datetime.now(timezone.utc),
            tipo_movimiento="Perdida",
            catalogo_id=catalogo_id,
            cantidad=cantidad,
            parada_id=parada_id,
            grupo_destino_id=grupo_id,
            usuario_ejecuta_id=usuario_id,
            observaciones=observaciones or "Registrado como pérdida en devolución masiva",
            estado_origen="En_Uso",
            estado_destino="Perdida",
        )
        self.db.add(movimiento)
        self.db.commit()
        return {
            "movimiento_id": str(movimiento.id),
            "tipo": "Perdida",
            "catalogo_id": catalogo_id,
            "cantidad": cantidad,
            "mensaje": f"Registrada pérdida: {cantidad} x {material.nombre}",
        }
