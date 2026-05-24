from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import CatalogoMaterial, Parada, Reserva, HistorialMovimiento


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_residente_kpis(self):
        metricas = (
            self.db.query(
                func.coalesce(func.sum(CatalogoMaterial.cant_disponible)
                    .filter(CatalogoMaterial.tipo_material.in_(["HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO"])), 0).label("disponibles"),
                func.coalesce(func.sum(CatalogoMaterial.cant_en_uso)
                    .filter(CatalogoMaterial.tipo_material.in_(["HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO"])), 0).label("en_uso"),
                func.coalesce(func.sum(CatalogoMaterial.cant_malograda)
                    .filter(CatalogoMaterial.tipo_material.in_(["HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO"])), 0).label("malogradas"),
                # Nota: cant_perdida y costo_total_perdidas se calculan desde historial abajo
                func.coalesce(func.sum(CatalogoMaterial.cantidad * CatalogoMaterial.costo_reposicion)
                    .filter(CatalogoMaterial.tipo_material.in_(["HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO"])), 0).label("costo_inventario"),
            )
        ).first()

        disponibles = metricas.disponibles or 0
        en_uso = metricas.en_uso or 0
        total = disponibles + en_uso

        # Pérdidas por parada (desde historial)
        perdidas_query = self.db.query(
            Parada.id.label("parada_id"),
            Parada.codigo.label("codigo_parada"),
            Parada.nombre.label("nombre_parada"),
            func.coalesce(func.sum(HistorialMovimiento.cantidad * CatalogoMaterial.costo_reposicion), 0.0).label("total_lost"),
            func.coalesce(func.sum(HistorialMovimiento.cantidad), 0).label("count_lost"),
        ).join(
            HistorialMovimiento, HistorialMovimiento.parada_id == Parada.id
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Perdida"
        ).group_by(
            Parada.id, Parada.codigo, Parada.nombre
        ).all()

        perdidas_por_parada = [
            {
                "parada_id": p.parada_id,
                "codigo_parada": p.codigo_parada,
                "nombre_parada": p.nombre_parada,
                "total_perdido": float(p.total_lost),
                "cantidad_perdidas": int(p.count_lost),
            } for p in perdidas_query
        ]

        # Top Grupos por Herramientas en Uso (desde vista v_herramientas_en_uso)
        top_grupos_query = self.db.query(
            HistorialMovimiento.grupo_destino_id.label("grupo_id"),
            func.sum(HistorialMovimiento.cantidad).label("in_use_count"),
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Entrega",
            CatalogoMaterial.tipo_material.in_(["HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO"]),
        ).group_by(
            HistorialMovimiento.grupo_destino_id
        ).having(
            func.sum(HistorialMovimiento.cantidad) > 0
        ).order_by(
            func.sum(HistorialMovimiento.cantidad).desc()
        ).limit(10).all()

        from ..models import GrupoTrabajo

        top_grupos_herramientas = []
        for g in top_grupos_query:
            grupo = self.db.query(GrupoTrabajo).filter(GrupoTrabajo.id == g.grupo_id).first()
            if grupo:
                top_grupos_herramientas.append({
                    "grupo_id": g.grupo_id,
                    "codigo_grupo": grupo.codigo,
                    "nombre_grupo": grupo.nombre,
                    "herramientas_en_uso": int(g.in_use_count),
                })

        # Herramientas más usadas (COUNT de Entregas por catalogo_id)
        herramientas_query = self.db.query(
            CatalogoMaterial.id.label("catalogo_id"),
            CatalogoMaterial.codigo_interno.label("codigo_interno"),
            CatalogoMaterial.nombre.label("nombre"),
            func.sum(HistorialMovimiento.cantidad).label("veces_usada"),
        ).join(
            HistorialMovimiento, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Entrega"
        ).group_by(
            CatalogoMaterial.id, CatalogoMaterial.codigo_interno, CatalogoMaterial.nombre
        ).order_by(
            func.sum(HistorialMovimiento.cantidad).desc()
        ).limit(10).all()

        herramientas_mas_usadas = [
            {
                "catalogo_id": h.catalogo_id,
                "codigo_interno": h.codigo_interno,
                "nombre": h.nombre,
                "veces_usada": int(h.veces_usada),
            } for h in herramientas_query
        ]

        paradas_activas = self.db.query(Parada).filter(Parada.estado == "Activa").all()
        reservas_pendientes = self.db.query(func.count(Reserva.id)).filter(Reserva.estado == "Pendiente").scalar() or 0

        # Pendientes de cierre: entregas sin devolución en paradas activas
        pendientes_cierre = (
            self.db.query(func.sum(HistorialMovimiento.cantidad))
            .join(Parada, HistorialMovimiento.parada_id == Parada.id)
            .filter(
                HistorialMovimiento.tipo_movimiento == "Entrega",
                Parada.estado == "Activa",
            )
            .scalar()
        ) or 0

        # Pérdidas totales desde historial (fuente de verdad)
        perdidas_totales = self.db.query(
            func.coalesce(func.sum(HistorialMovimiento.cantidad * CatalogoMaterial.costo_reposicion), 0.0),
            func.coalesce(func.sum(HistorialMovimiento.cantidad), 0),
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Perdida"
        ).first()
        costo_total_perdidas = float(perdidas_totales[0] or 0)
        herramientas_perdidas = int(perdidas_totales[1] or 0)

        return {
            "pct_herramientas_en_uso": round(en_uso / total * 100, 1) if total > 0 else 0,
            "herramientas_disponibles": int(disponibles),
            "herramientas_en_uso": int(en_uso),
            "herramientas_malogradas": int(metricas.malogradas or 0),
            "herramientas_perdidas": herramientas_perdidas,
            "costo_total_perdidas": costo_total_perdidas,
            "costo_total_inventario": float(metricas.costo_inventario or 0),
            "perdidas_por_parada": perdidas_por_parada,
            "top_grupos_herramientas": top_grupos_herramientas,
            "herramientas_mas_usadas": herramientas_mas_usadas,
            "paradas_activas": paradas_activas,
            "pendientes_cierre": int(pendientes_cierre),
            "reservas_pendientes": int(reservas_pendientes),
            "epps_por_vencer": 0,
        }
