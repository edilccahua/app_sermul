from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status

from ..models import CatalogoMaterial, GrupoTrabajo, GrupoIntegrante, HistorialMovimiento, Usuario
from ..schemas.grupo import GrupoCreate, GrupoUpdate

import uuid


class GrupoService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        parada_id: int | None = None,
        usuario_id: int | None = None,
    ):
        query = self.db.query(GrupoTrabajo).options(
            selectinload(GrupoTrabajo.integrantes),
        )
        if parada_id:
            query = query.filter(GrupoTrabajo.parada_id == parada_id)
        if usuario_id is not None:
            query = query.filter(
                GrupoTrabajo.id.in_(
                    self.db.query(GrupoIntegrante.grupo_id).filter(
                        GrupoIntegrante.usuario_id == usuario_id,
                        GrupoIntegrante.activo.is_(True),
                    )
                )
            )
        return query.all()

    def get_by_id(self, grupo_id: int):
        grupo = self.db.query(GrupoTrabajo).options(
            selectinload(GrupoTrabajo.integrantes),
        ).filter(GrupoTrabajo.id == grupo_id).first()
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo no encontrado",
            )
        return grupo

    def create(self, data: GrupoCreate, usuario_id: int | None = None):
        nuevo_grupo = GrupoTrabajo(
            codigo=data.codigo,
            nombre=data.nombre,
            parada_id=data.parada_id,
            descripcion=data.descripcion,
            circuito_area=data.circuito_area,
            creado_por_id=usuario_id,
        )
        self.db.add(nuevo_grupo)
        self.db.commit()
        self.db.refresh(nuevo_grupo)
        return nuevo_grupo

    def update(self, grupo_id: int, data: GrupoUpdate, usuario_id: int | None = None):
        grupo = self.db.query(GrupoTrabajo).filter(
            GrupoTrabajo.id == grupo_id
        ).first()
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grupo, field, value)
        grupo.actualizado_por_id = usuario_id

        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def add_integrante(self, grupo_id: int, usuario_id: int, es_lider_frente: bool = False):
        grupo = self.db.query(GrupoTrabajo).filter(
            GrupoTrabajo.id == grupo_id
        ).first()
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo no encontrado",
            )

        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        existente = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.grupo_id == grupo_id,
            GrupoIntegrante.usuario_id == usuario_id,
            GrupoIntegrante.activo,
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario ya es integrante activo",
            )

        if usuario.rol.codigo in ("LIDER_MEC", "TRABAJADOR"):
            otro_activo = self.db.query(GrupoIntegrante).filter(
                GrupoIntegrante.usuario_id == usuario_id,
                GrupoIntegrante.activo,
                GrupoIntegrante.grupo_id != grupo_id,
            ).first()
            if otro_activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El técnico ya pertenece a otro grupo activo (ID {otro_activo.grupo_id}). Desactivarlo primero.",
                )

        if es_lider_frente:
            lider_existente = self.db.query(GrupoIntegrante).filter(
                GrupoIntegrante.grupo_id == grupo_id,
                GrupoIntegrante.es_lider_frente.is_(True),
                GrupoIntegrante.activo.is_(True),
            ).first()
            if lider_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Este grupo ya tiene un líder asignado",
                )

        nuevo_integrante = GrupoIntegrante(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            activo=True,
            es_lider_frente=es_lider_frente,
        )
        self.db.add(nuevo_integrante)
        self.db.commit()
        return nuevo_integrante

    def remove_integrante(
        self, grupo_id: int, usuario_id: int, forzar_perdida: bool = False,
    ):
        integrante = self.db.query(GrupoIntegrante).filter(
            GrupoIntegrante.grupo_id == grupo_id,
            GrupoIntegrante.usuario_id == usuario_id,
            GrupoIntegrante.activo.is_(True),
        ).first()

        if not integrante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integrante activo no encontrado",
            )

        herramientas_perdidas = []

        if forzar_perdida:
            rows = self.db.execute(
                text("""
                    SELECT catalogo_id, codigo_interno, nombre_herramienta, cantidad_en_uso
                    FROM v_herramientas_en_uso
                    WHERE grupo_id = :gid
                """),
                {"gid": grupo_id},
            ).mappings().all()

            for row in rows:
                cant = row["cantidad_en_uso"]
                if cant <= 0:
                    continue

                material = self.db.query(CatalogoMaterial).filter(
                    CatalogoMaterial.id == row["catalogo_id"]
                ).with_for_update(of=CatalogoMaterial).first()

                if material:
                    material.cant_en_uso -= cant
                    material.cant_perdida += cant

                    mov = HistorialMovimiento(
                        id=uuid.uuid4(),
                        timestamp=datetime.now(timezone.utc),
                        tipo_movimiento="Perdida",
                        catalogo_id=row["catalogo_id"],
                        cantidad=cant,
                        parada_id=integrante.grupo.parada_id,
                        grupo_destino_id=grupo_id,
                        observaciones="Pérdida automática por desactivación de integrante",
                        estado_origen="En_Uso",
                        estado_destino="Perdida",
                    )
                    self.db.add(mov)
                    herramientas_perdidas.append({
                        "catalogo_id": row["catalogo_id"],
                        "codigo_interno": row["codigo_interno"],
                        "nombre": row["nombre_herramienta"],
                        "cantidad": cant,
                    })

        integrante.activo = False
        integrante.fecha_salida = datetime.now(timezone.utc).date()
        self.db.commit()

        return {
            "mensaje": (
                f"Integrante desactivado. {len(herramientas_perdidas)} "
                f"herramienta(s) marcada(s) como pérdida."
            ),
            "herramientas_perdidas": herramientas_perdidas,
        }

    def get_herramientas_en_uso_integrante(self, grupo_id: int, usuario_id: int):
        rows = self.db.execute(
            text("""
                SELECT catalogo_id, codigo_interno, nombre_herramienta AS nombre,
                       cantidad_en_uso AS cantidad
                FROM v_herramientas_en_uso
                WHERE grupo_id = :gid
            """),
            {"gid": grupo_id},
        ).mappings().all()

        herramientas = [dict(r) for r in rows] if rows else []
        return {
            "herramientas": herramientas,
            "total": len(herramientas),
        }

    def get_herramientas_en_uso_grupo(self, grupo_id: int):
        """
        Retorna por herramienta: prestado, devuelto, perdido y falta
        (falta = prestado - devuelto - perdido).
        """
        rows = self.db.execute(
            text("""
                SELECT
                    cm.id                 AS catalogo_id,
                    cm.codigo_interno,
                    cm.nombre             AS nombre,
                    COALESCE(SUM(CASE WHEN h.tipo_movimiento = 'Entrega'   THEN h.cantidad ELSE 0 END), 0)   AS prestado,
                    COALESCE(SUM(CASE WHEN h.tipo_movimiento = 'Devolucion' THEN h.cantidad ELSE 0 END), 0)  AS devuelto,
                    COALESCE(SUM(CASE WHEN h.tipo_movimiento IN ('Perdida','CierrePerdida') THEN h.cantidad ELSE 0 END), 0) AS perdido
                FROM historial_movimientos h
                JOIN catalogo_materiales cm ON h.catalogo_id = cm.id
                WHERE h.grupo_destino_id = :gid
                  AND h.tipo_movimiento IN ('Entrega','Devolucion','Perdida','CierrePerdida')
                GROUP BY cm.id, cm.codigo_interno, cm.nombre
                HAVING COALESCE(SUM(CASE WHEN h.tipo_movimiento = 'Entrega' THEN h.cantidad ELSE 0 END), 0) > 0
                ORDER BY cm.nombre
            """),
            {"gid": grupo_id},
        ).mappings().all()

        resultado = []
        for r in rows:
            prestado  = int(r["prestado"])
            devuelto  = int(r["devuelto"])
            perdido   = int(r["perdido"])
            falta     = max(0, prestado - devuelto - perdido)
            resultado.append({
                "catalogo_id":    r["catalogo_id"],
                "codigo_interno": r["codigo_interno"],
                "nombre":         r["nombre"],
                "prestado":       prestado,
                "devuelto":       devuelto,
                "perdido":        perdido,
                "falta":          falta,
            })

        return {
            "herramientas": resultado,
            "total": len(resultado),
        }
