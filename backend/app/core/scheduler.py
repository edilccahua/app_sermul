"""
Cronjob diario para auto-marcar como Pérdida las herramientas en estado "Continuidad"
(en_uso) de paradas finalizadas hace más de 3 días.

Se integra con el lifespan de FastAPI mediante APScheduler BackgroundScheduler.
Usa SessionLocal directamente (fuera del ciclo request/response).
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

from .database import SessionLocal
from ..models.catalogo_material import CatalogoMaterial
from ..models.historial_movimiento import HistorialMovimiento
from ..models.parada import Parada

logger = logging.getLogger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────
DIAS_GRACIA = 3  # Días tras el cierre antes de auto-marcar pérdidas
_TIPOS_SALIDA = {"Entrega"}
_TIPOS_ENTRADA = {"Devolucion", "Paso_Mantenimiento", "Perdida"}


def _auto_marcar_perdidas() -> None:
    """
    Tarea diaria:
    1. Busca paradas 'Finalizada' cuya fecha_fin fue hace más de DIAS_GRACIA días.
    2. Calcula herramientas aún en uso (SUM salidas - SUM entradas) en esa parada.
    3. Genera un movimiento 'Perdida' y ajusta contadores en catalogo_materiales.
    """
    db = SessionLocal()
    try:
        ahora = datetime.now(timezone.utc)
        limite = (ahora - timedelta(days=DIAS_GRACIA)).date()

        paradas_vencidas = (
            db.query(Parada)
            .filter(
                Parada.estado == "Finalizada",
                Parada.fecha_fin <= limite,
            )
            .all()
        )

        if not paradas_vencidas:
            logger.info("[Scheduler] No hay paradas vencidas para procesar.")
            return

        for parada in paradas_vencidas:
            _procesar_parada_vencida(db, parada, ahora)

        db.commit()
        logger.info(
            "[Scheduler] Auto-pérdidas procesadas para %d parada(s).",
            len(paradas_vencidas),
        )

    except Exception as exc:
        db.rollback()
        logger.error("[Scheduler] Error al procesar auto-pérdidas: %s", exc, exc_info=True)
    finally:
        db.close()


def _procesar_parada_vencida(db, parada: Parada, ahora: datetime) -> None:
    """Calcula y registra las pérdidas automáticas de una parada vencida."""
    from sqlalchemy import func

    # Salidas de la parada
    salidas = (
        db.query(
            HistorialMovimiento.catalogo_id,
            func.sum(HistorialMovimiento.cantidad).label("total"),
        )
        .filter(
            HistorialMovimiento.parada_id == parada.id,
            HistorialMovimiento.tipo_movimiento.in_(_TIPOS_SALIDA),
        )
        .group_by(HistorialMovimiento.catalogo_id)
        .all()
    )

    # Entradas de la parada (incluye Perdida para no duplicar)
    entradas = (
        db.query(
            HistorialMovimiento.catalogo_id,
            func.sum(HistorialMovimiento.cantidad).label("total"),
        )
        .filter(
            HistorialMovimiento.parada_id == parada.id,
            HistorialMovimiento.tipo_movimiento.in_(_TIPOS_ENTRADA),
        )
        .group_by(HistorialMovimiento.catalogo_id)
        .all()
    )

    entradas_map = {row.catalogo_id: row.total for row in entradas}

    for row in salidas:
        devuelto = entradas_map.get(row.catalogo_id, 0)
        pendiente = row.total - devuelto
        if pendiente <= 0:
            continue

        material = (
            db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == row.catalogo_id)
            .first()
        )
        if not material:
            continue

        # Ajustar contadores (no bajar de 0 por seguridad)
        cant_a_perder = min(pendiente, material.cant_en_uso)
        if cant_a_perder <= 0:
            continue

        material.cant_en_uso -= cant_a_perder
        material.cant_perdida += cant_a_perder

        mov = HistorialMovimiento(
            id=uuid.uuid4(),
            timestamp=ahora,
            tipo_movimiento="Perdida",
            catalogo_id=row.catalogo_id,
            cantidad=cant_a_perder,
            parada_id=parada.id,
            estado_origen="En_Uso",
            estado_destino="Perdida",
            observaciones=(
                f"Auto-pérdida por Continuidad. Parada {parada.codigo} "
                f"finalizada hace más de {DIAS_GRACIA} días."
            ),
        )
        db.add(mov)

        logger.info(
            "[Scheduler] Parada %s | Material %s | Auto-pérdida: %d unidad(es).",
            parada.codigo,
            material.codigo_interno,
            cant_a_perder,
        )


def create_scheduler() -> BackgroundScheduler:
    """
    Crea y configura el BackgroundScheduler.
    Se ejecuta diariamente a medianoche hora de Lima (UTC-5).
    Usando UTC internamente para evitar problemas de DST.
    """
    scheduler = BackgroundScheduler(timezone="America/Lima")
    scheduler.add_job(
        _auto_marcar_perdidas,
        trigger="cron",
        hour=0,
        minute=0,
        id="auto_perdidas_cierre",
        replace_existing=True,
        misfire_grace_time=3600,  # 1h de gracia si el proceso estaba caído
    )
    return scheduler
