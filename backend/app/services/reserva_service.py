from sqlalchemy import case, select
from sqlalchemy.orm import Session, lazyload
from fastapi import HTTPException, status
from datetime import datetime, timezone
import random

from ..models import GrupoTrabajo, Reserva, ReservaDetalle, CatalogoMaterial, HistorialMovimiento, GrupoIntegrante
from ..schemas.reserva import ReservaCreate


class ReservaService:
    def __init__(self, db: Session):
        self.db = db

    def _calcular_stock_disponible(self, catalogo_id: int) -> int:
        material = self.db.query(CatalogoMaterial).filter(
            CatalogoMaterial.id == catalogo_id
        ).first()
        return material.cant_disponible if material else 0

    def create(self, data: ReservaCreate, usuario_id: int):
        year = datetime.now().year
        last_reserva = self.db.query(Reserva).filter(Reserva.codigo_reserva.like(f"RES-{year}-%")).order_by(Reserva.id.desc()).first()
        seq = 1
        if last_reserva:
            try:
                seq = int(last_reserva.codigo_reserva.split("-")[-1]) + 1
            except Exception:
                seq = random.randint(1000, 9999)
        codigo_reserva = f"RES-{year}-{seq:03d}"

        reserva_activa = self.db.query(Reserva).filter(
            Reserva.grupo_id == data.grupo_id,
            Reserva.estado.in_(["Pendiente", "Aprobada"])
        ).first()

        if reserva_activa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Este grupo ya tiene la Reserva {reserva_activa.codigo_reserva} en curso."
            )

        nueva_reserva = Reserva(
            codigo_reserva=codigo_reserva,
            parada_id=data.parada_id,
            grupo_id=data.grupo_id,
            creado_por_id=usuario_id,
            turno=data.turno,
            fecha_programada=data.fecha_programada,
            estado="Pendiente"
        )
        self.db.add(nueva_reserva)
        self.db.flush()

        alertas_stock = []
        for item in data.items:
            detalle = ReservaDetalle(
                reserva_id=nueva_reserva.id,
                catalogo_id=item.catalogo_id,
                cantidad_solicitada=item.cantidad_solicitada
            )
            self.db.add(detalle)

            stock = self._calcular_stock_disponible(item.catalogo_id)
            if stock < item.cantidad_solicitada:
                cat = self.db.get(CatalogoMaterial, item.catalogo_id)
                alertas_stock.append({
                    "catalogo_id": item.catalogo_id,
                    "nombre": cat.nombre if cat else "Desconocido",
                    "solicitado": item.cantidad_solicitada,
                    "disponible": stock,
                    "mensaje": f"Stock insuficiente para {cat.nombre if cat else 'Desconocido'}"
                })

        self.db.commit()

        reserva_con_stock = self.get_by_id(nueva_reserva.id)
        setattr(reserva_con_stock, "alertas_stock", alertas_stock)
        return reserva_con_stock

    def get_all(self, grupo_id: int | None = None, estado: str | None = None, parada_id: int | None = None):
        query = self.db.query(Reserva)
        if grupo_id:
            query = query.filter(Reserva.grupo_id == grupo_id)
        if estado:
            query = query.filter(Reserva.estado == estado)
        if parada_id:
            query = query.filter(Reserva.parada_id == parada_id)
        query = query.join(GrupoTrabajo, Reserva.grupo_id == GrupoTrabajo.id, isouter=True)
        query = query.order_by(
            case((Reserva.estado == 'Pendiente', 0), else_=1),
            GrupoTrabajo.codigo,
        )
        reservas = query.all()
        for reserva in reservas:
            self._enrich_detalles(reserva)
        return reservas

    def _enrich_detalles(self, reserva):
        for detalle in reserva.detalles:
            setattr(detalle, "cantidad_disponible", self._calcular_stock_disponible(detalle.catalogo_id))
            if detalle.catalogo:
                setattr(detalle, "codigo_interno", detalle.catalogo.codigo_interno)
                setattr(detalle, "nombre", detalle.catalogo.nombre)
                setattr(detalle, "descripcion", detalle.catalogo.descripcion)
                setattr(detalle, "marca", detalle.catalogo.marca)
            else:
                setattr(detalle, "codigo_interno", "N/A")
                setattr(detalle, "nombre", "N/A")
        if reserva.grupo:
            integrantes = self.db.query(GrupoIntegrante).filter(
                GrupoIntegrante.grupo_id == reserva.grupo.id,
                GrupoIntegrante.activo
            ).all()
            setattr(reserva.grupo, "integrantes", integrantes)
        setattr(reserva, "alertas_stock", getattr(reserva, 'alertas_stock', []))

    def get_by_id(self, reserva_id: int):
        reserva = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")

        self._enrich_detalles(reserva)
        return reserva

    def aprobar(self, reserva_id: int, usuario_id: int):
        reserva = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva or reserva.estado != "Pendiente":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo reservas pendientes pueden ser aprobadas")

        reserva.estado = "Aprobada"
        reserva.aprobado_por_id = usuario_id
        reserva.actualizado_por_id = usuario_id
        reserva.fecha_aprobacion = datetime.now(timezone.utc)
        self.db.commit()
        return self.get_by_id(reserva.id)

    def rechazar(self, reserva_id: int, usuario_id: int, motivo: str):
        reserva = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva or reserva.estado != "Pendiente":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo reservas pendientes pueden ser rechazadas")

        reserva.estado = "Rechazada"
        reserva.aprobado_por_id = usuario_id
        reserva.actualizado_por_id = usuario_id
        reserva.fecha_aprobacion = datetime.now(timezone.utc)
        reserva.motivo_rechazo = motivo
        self.db.commit()
        return self.get_by_id(reserva.id)

    def despachar(self, reserva_id: int, usuario_id: int, items_ids: list[int] | None = None):
        reserva = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva or reserva.estado != "Aprobada":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solo reservas aprobadas pueden ser despachadas")

        now = datetime.now(timezone.utc)

        with self.db.begin_nested():
            for detalle in reserva.detalles:
                if items_ids is not None and detalle.id not in items_ids:
                    continue

                faltante = detalle.cantidad_solicitada - detalle.cantidad_despachada
                if faltante <= 0:
                    continue

                material = self.db.execute(
                    select(CatalogoMaterial)
                    .where(CatalogoMaterial.id == detalle.catalogo_id)
                    .options(lazyload("*"))
                    .with_for_update()
                ).scalar_one_or_none()

                if material is None:
                    continue

                a_despachar = min(faltante, material.cant_disponible)
                if a_despachar <= 0:
                    continue

                material.cant_disponible -= a_despachar
                material.cant_en_uso += a_despachar

                detalle.cantidad_despachada += a_despachar

                import uuid
                movimiento = HistorialMovimiento(
                    id=uuid.uuid4(),
                    timestamp=now,
                    tipo_movimiento="Entrega",
                    catalogo_id=detalle.catalogo_id,
                    cantidad=a_despachar,
                    parada_id=reserva.parada_id,
                    grupo_destino_id=reserva.grupo_id,
                    usuario_ejecuta_id=usuario_id,
                    reserva_id=reserva.id,
                    estado_origen="Disponible",
                    estado_destino="En_Uso",
                )
                self.db.add(movimiento)

            reserva.estado = "Despachada"
            reserva.despachado_por_id = usuario_id
            reserva.actualizado_por_id = usuario_id
            reserva.fecha_despacho = now

        self.db.commit()
        return self.get_by_id(reserva.id)
