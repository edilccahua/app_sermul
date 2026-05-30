from sqlalchemy import func as sa_func, text as sa_text, Integer as sa_Integer
from sqlalchemy.orm import Session

from ..models import CatalogoMaterial, GrupoTrabajo, HistorialMovimiento, Parada, Reserva


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_residente_kpis(self, parada_id: int | None = None):
        # ── Métricas globales de inventario (no varían por parada) ──────────
        metricas = (
            self.db.query(
                sa_func.coalesce(sa_func.sum(CatalogoMaterial.cant_disponible), 0).label("disponibles"),
                sa_func.coalesce(sa_func.sum(CatalogoMaterial.cant_en_uso), 0).label("en_uso"),
                sa_func.coalesce(sa_func.sum(CatalogoMaterial.cant_malograda), 0).label("malogradas"),
                sa_func.coalesce(sa_func.sum((CatalogoMaterial.cant_disponible + CatalogoMaterial.cant_en_uso + CatalogoMaterial.cant_malograda + CatalogoMaterial.cant_perdida) * CatalogoMaterial.costo_reposicion), 0).label("costo_inventario"),
            )
        ).first()
        disponibles = (metricas.disponibles or 0) if metricas else 0
        en_uso = (metricas.en_uso or 0) if metricas else 0
        malogradas = (metricas.malogradas or 0) if metricas else 0  # type: ignore[union-attr]
        costo_inventario = float((metricas.costo_inventario or 0) if metricas else 0)  # type: ignore[union-attr]

        # ── Pérdidas desde historial ────────────────────────────────────────
        perdidas_q = self.db.query(
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad * CatalogoMaterial.costo_reposicion), 0.0).label("costo"),
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad), 0).label("cant"),
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Perdida"
        )
        total_perdidas = perdidas_q.first()
        costo_total_perdidas = float(total_perdidas.costo) if total_perdidas else 0.0
        herramientas_perdidas = int(total_perdidas.cant) if total_perdidas else 0

        # ── Pérdidas por parada ─────────────────────────────────────────────
        perdidas_pp_q = self.db.query(
            Parada.id.label("parada_id"),
            Parada.codigo.label("codigo_parada"),
            Parada.nombre.label("nombre_parada"),
            Parada.fecha_inicio.label("fecha_inicio"),
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad * CatalogoMaterial.costo_reposicion), 0.0).label("total_lost"),
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad), 0).label("count_lost"),
        ).join(
            HistorialMovimiento, HistorialMovimiento.parada_id == Parada.id
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Perdida"
        )
        if parada_id:
            perdidas_pp_q = perdidas_pp_q.filter(Parada.id == parada_id)
        perdidas_pp = perdidas_pp_q.group_by(Parada.id, Parada.codigo, Parada.nombre, Parada.fecha_inicio).order_by(Parada.fecha_inicio.asc()).all()

        perdidas_por_parada = [
            {
                "parada_id": p.parada_id,
                "codigo_parada": p.codigo_parada,
                "nombre_parada": p.nombre_parada,
                "total_perdido": float(p.total_lost),
                "cantidad_perdidas": int(p.count_lost),
            } for p in perdidas_pp
        ]

        # ── Top grupos (NETO: Entregas - Devoluciones - Pérdidas) ──────────
        entregas = self.db.query(
            HistorialMovimiento.grupo_destino_id,
            sa_func.sum(HistorialMovimiento.cantidad).label("total_entrega"),
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Entrega",
            HistorialMovimiento.grupo_destino_id.isnot(None),
        )
        if parada_id:
            entregas = entregas.filter(HistorialMovimiento.parada_id == parada_id)
        entregas_cte = entregas.group_by(
            HistorialMovimiento.grupo_destino_id,
        ).cte("entregas")

        retornos = self.db.query(
            HistorialMovimiento.grupo_destino_id,
            sa_func.sum(HistorialMovimiento.cantidad).label("total_retorno"),
        ).filter(
            HistorialMovimiento.tipo_movimiento.in_(["Devolucion", "Perdida"]),
            HistorialMovimiento.grupo_destino_id.isnot(None),
        )
        if parada_id:
            retornos = retornos.filter(HistorialMovimiento.parada_id == parada_id)
        retornos_cte = retornos.group_by(
            HistorialMovimiento.grupo_destino_id,
        ).cte("retornos")

        neto_expr = (entregas_cte.c.total_entrega - sa_func.coalesce(retornos_cte.c.total_retorno, 0))

        netos = self.db.query(
            entregas_cte.c.grupo_destino_id,
            neto_expr.label("neto"),
        ).outerjoin(
            retornos_cte,
            entregas_cte.c.grupo_destino_id == retornos_cte.c.grupo_destino_id,
        ).filter(
            neto_expr > 0
        ).order_by(
            neto_expr.desc(),
        ).subquery()

        top_grupos = self.db.query(
            GrupoTrabajo.id.label("grupo_id"),
            GrupoTrabajo.codigo.label("codigo_grupo"),
            GrupoTrabajo.nombre.label("nombre_grupo"),
            netos.c.neto.label("herramientas_en_uso"),
        ).join(
            netos, GrupoTrabajo.id == netos.c.grupo_destino_id,
        ).order_by(
            sa_func.cast(GrupoTrabajo.codigo, sa_Integer).asc(),
        ).all()

        top_grupos_herramientas = [
            {
                "grupo_id": g.grupo_id,
                "codigo_grupo": g.codigo_grupo,
                "nombre_grupo": g.nombre_grupo,
                "herramientas_en_uso": int(g.herramientas_en_uso),
            } for g in top_grupos
        ]

        # ── Herramientas más usadas ─────────────────────────────────────────
        herramientas_q = self.db.query(
            CatalogoMaterial.id.label("catalogo_id"),
            CatalogoMaterial.codigo_interno.label("codigo_interno"),
            CatalogoMaterial.nombre.label("nombre"),
            sa_func.sum(HistorialMovimiento.cantidad).label("veces_usada"),
        ).join(
            HistorialMovimiento, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Entrega"
        )
        if parada_id:
            herramientas_q = herramientas_q.filter(HistorialMovimiento.parada_id == parada_id)
        herramientas = herramientas_q.group_by(
            CatalogoMaterial.id, CatalogoMaterial.codigo_interno, CatalogoMaterial.nombre
        ).order_by(
            sa_func.sum(HistorialMovimiento.cantidad).desc()
        ).limit(10).all()

        herramientas_mas_usadas = [
            {
                "catalogo_id": h.catalogo_id,
                "codigo_interno": h.codigo_interno,
                "nombre": h.nombre,
                "veces_usada": int(h.veces_usada),
            } for h in herramientas
        ]

        # ── Paradas activas ─────────────────────────────────────────────────
        paradas_q = self.db.query(Parada).filter(Parada.estado.in_(["Activa", "Finalizada"])).order_by(Parada.estado.asc(), Parada.fecha_inicio.desc())
        if parada_id:
            paradas_q = paradas_q.filter(Parada.id == parada_id)
        paradas_activas = paradas_q.all()

        # ── Reservas pendientes ─────────────────────────────────────────────
        reservas_q = self.db.query(sa_func.count(Reserva.id)).filter(
            Reserva.estado == "Pendiente",
        )
        if parada_id:
            reservas_q = reservas_q.filter(Reserva.parada_id == parada_id)
        reservas_pendientes = reservas_q.scalar() or 0

        reservas_lista_q = self.db.query(
            Reserva.id,
            Reserva.fecha_programada.label("fecha_reserva"),
            GrupoTrabajo.nombre.label("grupo_nombre")
        ).join(
            GrupoTrabajo, Reserva.grupo_id == GrupoTrabajo.id
        ).filter(
            Reserva.estado == "Pendiente"
        )
        if parada_id:
            reservas_lista_q = reservas_lista_q.filter(Reserva.parada_id == parada_id)
        reservas_pendientes_lista = reservas_lista_q.order_by(Reserva.fecha_programada.desc()).limit(5).all()

        tabla_reservas = [
            {
                "id": r.id,
                "fecha": r.fecha_reserva.isoformat() if r.fecha_reserva else None,
                "grupo": r.grupo_nombre
            } for r in reservas_pendientes_lista
        ]

        # ── Pendientes de cierre (D-03: restar devoluciones) ────────────────
        entregas_p = self.db.query(
            HistorialMovimiento.catalogo_id,
            HistorialMovimiento.grupo_destino_id,
            sa_func.sum(HistorialMovimiento.cantidad).label("total_entrega")
        ).join(
            Parada, HistorialMovimiento.parada_id == Parada.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Entrega",
            HistorialMovimiento.grupo_destino_id.isnot(None),
            Parada.estado.in_(["Activa", "Finalizada"])
        )
        if parada_id:
            entregas_p = entregas_p.filter(HistorialMovimiento.parada_id == parada_id)
        entregas_p_cte = entregas_p.group_by(
            HistorialMovimiento.catalogo_id,
            HistorialMovimiento.grupo_destino_id
        ).cte("entregas_p")

        retornos_p = self.db.query(
            HistorialMovimiento.catalogo_id,
            HistorialMovimiento.grupo_destino_id,
            sa_func.sum(HistorialMovimiento.cantidad).label("total_retorno")
        ).join(
            Parada, HistorialMovimiento.parada_id == Parada.id
        ).filter(
            HistorialMovimiento.tipo_movimiento.in_(["Devolucion", "Perdida", "Paso_Mantenimiento"]),
            HistorialMovimiento.grupo_destino_id.isnot(None),
            Parada.estado.in_(["Activa", "Finalizada"])
        )
        if parada_id:
            retornos_p = retornos_p.filter(HistorialMovimiento.parada_id == parada_id)
        retornos_p_cte = retornos_p.group_by(
            HistorialMovimiento.catalogo_id,
            HistorialMovimiento.grupo_destino_id
        ).cte("retornos_p")

        neto_p_expr = (entregas_p_cte.c.total_entrega - sa_func.coalesce(retornos_p_cte.c.total_retorno, 0))

        total_pendientes_query = self.db.query(sa_func.sum(neto_p_expr)).select_from(entregas_p_cte).outerjoin(
            retornos_p_cte,
            (entregas_p_cte.c.catalogo_id == retornos_p_cte.c.catalogo_id) &
            (entregas_p_cte.c.grupo_destino_id == retornos_p_cte.c.grupo_destino_id)
        ).filter(neto_p_expr > 0)
        pendientes = int(total_pendientes_query.scalar() or 0)

        # ── Top Grupos con Pérdidas ─────────────────────────────────────────
        grupos_perdidas_q = self.db.query(
            GrupoTrabajo.id.label("grupo_id"),
            GrupoTrabajo.codigo.label("codigo_grupo"),
            GrupoTrabajo.nombre.label("nombre_grupo"),
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad), 0).label("cantidad_perdida"),
            sa_func.coalesce(sa_func.sum(HistorialMovimiento.cantidad * CatalogoMaterial.costo_reposicion), 0.0).label("valor_perdido")
        ).join(
            HistorialMovimiento, GrupoTrabajo.id == HistorialMovimiento.grupo_destino_id
        ).join(
            CatalogoMaterial, HistorialMovimiento.catalogo_id == CatalogoMaterial.id
        ).filter(
            HistorialMovimiento.tipo_movimiento == "Perdida"
        )
        if parada_id:
            grupos_perdidas_q = grupos_perdidas_q.filter(HistorialMovimiento.parada_id == parada_id)
        
        grupos_perdidas_items = grupos_perdidas_q.group_by(
            GrupoTrabajo.id, GrupoTrabajo.codigo, GrupoTrabajo.nombre
        ).all()

        top_grupos_perdidas = [
            {
                "grupo_id": g.grupo_id,
                "codigo_grupo": g.codigo_grupo,
                "nombre_grupo": g.nombre_grupo,
                "cantidad_perdida": int(g.cantidad_perdida),
                "valor_perdido": float(g.valor_perdido)
            } for g in grupos_perdidas_items
        ]

        # ── EPPs por vencer (D-08: real en vez de stub) ─────────────────────
        epps_por_vencer = (
            self.db.execute(
                sa_text("""
                    SELECT COUNT(*) FROM catalogo_materiales
                    WHERE requiere_certificacion = true
                      AND vida_util_dias IS NOT NULL
                      AND activo = true
                      AND created_at + (vida_util_dias * INTERVAL '1 day')
                          BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '180 days'
                """),
            ).scalar()
        ) or 0

        return {
            "herramientas_disponibles": int(disponibles),
            "herramientas_en_uso": int(en_uso),
            "herramientas_malogradas": int(malogradas),
            "herramientas_perdidas": herramientas_perdidas,
            "costo_total_perdidas": costo_total_perdidas,
            "costo_total_inventario": costo_inventario,
            "perdidas_por_parada": perdidas_por_parada,
            "top_grupos_herramientas": top_grupos_herramientas,
            "herramientas_mas_usadas": herramientas_mas_usadas,
            "paradas_activas": paradas_activas,
            "pendientes_cierre": pendientes,
            "reservas_pendientes": int(reservas_q.scalar() or 0),
            "epps_por_vencer": int(epps_por_vencer or 0),
            "top_grupos_perdidas": top_grupos_perdidas,
            "tabla_reservas_pendientes": tabla_reservas,
        }
