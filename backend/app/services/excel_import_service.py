from sqlalchemy.orm import Session
from fastapi import HTTPException
import io
from typing import Any
import pandas as pd  # type: ignore

from ..models import GrupoTrabajo, GrupoIntegrante, Usuario, Rol, Parada
from ..core.security import hash_password
from .especialidad_service import EspecialidadService


class ExcelImportService:
    def __init__(self, db: Session):
        self.db = db
        self._especialidad_service = EspecialidadService(db)

    def _get_rol_id(self, cargo: str) -> int:
        cargo = cargo.upper().strip() if isinstance(cargo, str) else ""
        if "SUPERVISOR DE OPERACION" in cargo:
            codigo = "SUP_MEC"
        elif "SUPERVISOR DE SEGURIDAD" in cargo or "SSOMA" in cargo:
            codigo = "SUP_SSOMA"
        else:
            codigo = "TRABAJADOR"
        rol = self.db.query(Rol).filter(Rol.codigo == codigo).first()
        return rol.id if rol else 1

    def importar_excel(self, file: bytes, parada_id: int):
        parada = self.db.query(Parada).filter(Parada.id == parada_id).first()
        if not parada:
            raise HTTPException(status_code=404, detail="Parada no encontrada")

        try:
            df_full = pd.read_excel(io.BytesIO(file), header=None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error leyendo archivo Excel: {str(e)}")

        resumen = {
            "filas_procesadas": 0,
            "grupos_creados": 0,
            "grupos_actualizados": 0,
            "usuarios_creados": 0,
            "usuarios_actualizados": 0,
            "integrantes_agregados": 0,
            "errores": 0,
            "warnings": 0
        }
        errores: list[dict[str, Any]] = []
        warnings: list[str] = []
        grupos_detalle = []

        group_headers = []
        for row_idx, row in df_full.iterrows():
            for col_idx, cell in enumerate(row):
                if isinstance(cell, str) and cell.upper().startswith("GRUPO "):
                    group_headers.append({
                        "row": row_idx,
                        "col": col_idx,
                        "nombre": cell.strip()
                    })

        if group_headers:
            for gh in group_headers:
                nombre_grupo = gh["nombre"]
                col_start = gh["col"]
                row_start = gh["row"] + 2

                miembros: list[dict[str, Any]] = []

                for r in range(row_start, len(df_full)):
                    if col_start + 3 >= len(df_full.columns):
                        break

                    dni_val = df_full.iloc[r, col_start + 2]
                    if pd.isna(dni_val) or str(dni_val).strip() == "":
                        break

                    nombre_val = str(df_full.iloc[r, col_start + 1]).strip()
                    dni_str = str(dni_val).replace(".0", "").strip()
                    cargo_val = str(df_full.iloc[r, col_start + 3]).strip()

                    if not dni_str.isdigit() or len(dni_str) != 8:
                        errores.append({"fila": r, "dni": dni_str, "error": "DNI inválido"})
                        resumen["errores"] += 1
                        continue

                    miembros.append({
                        "dni": dni_str,
                        "nombre_completo": nombre_val,
                        "cargo": cargo_val,
                        "fila": r
                    })

                if not miembros:
                    continue

                # Nueva lógica: primer técnico = líder, luego trabajadores
                # Resetear flags
                primer_tecnico = True

                codigo_grupo = f"GRP-{nombre_grupo.split('-')[0].replace('GRUPO', '').strip()}"
                if not codigo_grupo or codigo_grupo == "GRP-":
                    codigo_grupo = f"GRP-TMP-{resumen['grupos_creados']}"

                g = self.db.query(GrupoTrabajo).filter(
                    GrupoTrabajo.codigo == codigo_grupo,
                    GrupoTrabajo.parada_id == parada_id
                ).first()
                if g:
                    g.nombre = nombre_grupo
                    self.db.commit()
                    resumen["grupos_actualizados"] += 1
                else:
                    g = GrupoTrabajo(
                        codigo=codigo_grupo,
                        nombre=nombre_grupo,
                        parada_id=parada_id,
                        estado="Activo"
                    )
                    self.db.add(g)
                    self.db.commit()
                    self.db.refresh(g)
                    resumen["grupos_creados"] += 1

                grupos_detalle.append({"id": g.id, "nombre": g.nombre})

                for m in miembros:
                    resumen["filas_procesadas"] += 1
                    u = self.db.query(Usuario).filter(Usuario.dni == m["dni"]).first()

                    nombre_completo = str(m["nombre_completo"])
                    nombres = nombre_completo
                    apellido = ""
                    parts = nombre_completo.split(" ")
                    if len(parts) > 1:
                        nombres = parts[-1]
                        apellido = " ".join(parts[:-1])

                    # Obtener o crear especialidad
                    especialidad = self._especialidad_service.get_or_create(m["cargo"])

                    if u:
                        u.nombre = nombres
                        u.apellido = apellido
                        u.especialidad_id = especialidad.id
                        self.db.commit()
                        resumen["usuarios_actualizados"] += 1
                    else:
                        u = Usuario(
                            dni=str(m["dni"]),
                            nombre=nombres,
                            apellido=apellido,
                            password_hash=hash_password(str(m["dni"])),
                            rol_id=self._get_rol_id(str(m["cargo"])),
                            especialidad_id=especialidad.id,
                            activo=True
                        )
                        self.db.add(u)
                        self.db.commit()
                        self.db.refresh(u)
                        resumen["usuarios_creados"] += 1

                    # Desactivar membresías previas de técnicos
                    if u.rol.codigo in ("LIDER_MEC", "TRABAJADOR"):
                        self.db.query(GrupoIntegrante).filter(
                            GrupoIntegrante.usuario_id == u.id,
                            GrupoIntegrante.activo,
                            GrupoIntegrante.grupo_id != g.id
                        ).update({"activo": False})

                    # Agregar como integrante
                    existente = self.db.query(GrupoIntegrante).filter(
                        GrupoIntegrante.grupo_id == g.id,
                        GrupoIntegrante.usuario_id == u.id
                    ).first()

                    es_lider = False
                    if u.rol.codigo not in ("SUP_MEC", "SUP_SSOMA"):
                        if primer_tecnico:
                            es_lider = True
                            primer_tecnico = False

                    if existente:
                        if not existente.activo or existente.es_lider_frente != es_lider:
                            existente.activo = True
                            existente.es_lider_frente = es_lider
                    else:
                        nuevo = GrupoIntegrante(
                            grupo_id=g.id,
                            usuario_id=u.id,
                            activo=True,
                            es_lider_frente=es_lider,
                        )
                        self.db.add(nuevo)
                    resumen["integrantes_agregados"] += 1

                self.db.commit()

        else:
            raise HTTPException(status_code=400, detail="Formato no reconocido. Use la plantilla estándar o el formato SERMUL válido.")

        return {
            "resumen": resumen,
            "errores": errores,
            "warnings": warnings,
            "grupos_creados_detalle": grupos_detalle
        }
