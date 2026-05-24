from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..models.grupo_trabajo import GrupoTrabajo
from ..models.parada import Parada


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
        ).first()
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
        observacion_recepcion: str | None = None,
        descripcion_dano: str | None = None,
    ):
        if cant_buen_estado + cant_malograda == 0:
            raise ValueError("Debe devolver al menos una unidad")

        material = self.db.query(CatalogoMaterial).filter(
            CatalogoMaterial.id == catalogo_id
        ).first()
        if not material:
            raise ValueError(f"Material con ID {catalogo_id} no encontrado")

        total_devuelto = cant_buen_estado + cant_malograda
        if material.cant_en_uso < total_devuelto:
            raise ValueError(
                f"No hay tantas unidades en uso. En uso: {material.cant_en_uso}, "
                f"Intentando devolver: {total_devuelto}"
            )

        ultima_entrega = (
            self.db.query(HistorialMovimiento)
            .filter(
                HistorialMovimiento.catalogo_id == catalogo_id,
                HistorialMovimiento.tipo_movimiento == "Entrega",
            )
            .order_by(HistorialMovimiento.timestamp.desc())
            .first()
        )
        parada_id = ultima_entrega.parada_id if ultima_entrega else 1
        grupo_id = ultima_entrega.grupo_destino_id if ultima_entrega else None

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
