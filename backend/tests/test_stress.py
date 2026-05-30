"""
test_stress.py — Pruebas de estrés para el flujo de check-out concurrente.

Objetivo:
- Lanzar N peticiones REALES (via httpx) simultáneas de check-out sobre el mismo material.
- Verificar que la lógica del servicio garantiza consistencia de contadores.
- Validar que las peticiones excedentes de stock reciben HTTP 400.
- Confirmar tiempos de respuesta < 3 segundos por petición.

NOTA: Estas pruebas usan httpx para llamadas HTTP reales al servidor uvicorn
      que corre dentro del mismo contenedor en localhost:8000.
      Si el servidor no está disponible, los tests se omiten automáticamente.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from app.core.database import SessionLocal
from app.models.catalogo_material import CatalogoMaterial

# ── Dependencia opcional de httpx ─────────────────────────────────────────────
try:
    import httpx  # type: ignore
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

BASE_URL = "http://localhost:8000"
GRUPO_ID = 1
PARADA_ID = 1
N_REQUESTS = 50          # Peticiones concurrentes totales (algunas fallarán por falta de stock)
TIMEOUT_SEG = 3.0


def _check_servidor_disponible() -> bool:
    """Verifica si el servidor FastAPI está levantado en localhost:8000."""
    if not _HTTPX_AVAILABLE:
        return False
    try:
        resp = httpx.get(f"{BASE_URL}/api/health", timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False


def _get_token_httpx() -> str:
    """Obtiene token del almacenero vía HTTP real."""
    resp = httpx.post(
        f"{BASE_URL}/api/auth/login",
        json={"dni": "11223344", "password": "11223344"},
        timeout=5.0,
    )
    assert resp.status_code == 200, f"Login falló: {resp.text}"
    return resp.json()["access_token"]


def _do_checkout_httpx(catalogo_id: int, token: str) -> tuple[int, float]:
    """Ejecuta un check-out vía HTTP real y retorna (status_code, tiempo_seg)."""
    start = time.perf_counter()
    resp = httpx.post(
        f"{BASE_URL}/api/inventario/check-out",
        json={
            "catalogo_id": catalogo_id,
            "cantidad": 1,
            "grupo_id": GRUPO_ID,
            "parada_id": PARADA_ID,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=TIMEOUT_SEG + 2,
    )
    elapsed = time.perf_counter() - start
    return resp.status_code, elapsed


def _get_material_con_mas_stock() -> tuple[int, int, str]:
    """
    Retorna (catalogo_id, cant_disponible, nombre) del material con mayor stock disponible.
    Busca entre materiales devolutivos (herramientas) que tengan al menos 1 disponible.
    """
    db = SessionLocal()
    try:
        material = (
            db.query(CatalogoMaterial)
            .filter(
                CatalogoMaterial.cant_disponible > 0,
                CatalogoMaterial.activo.is_(True),
            )
            .order_by(CatalogoMaterial.cant_disponible.desc())
            .first()
        )
        if material is None:
            return 0, 0, "Sin material disponible"
        return material.id, material.cant_disponible, material.nombre
    finally:
        db.close()


def _get_stock_actual(catalogo_id: int) -> tuple[int, int]:
    """Retorna (cant_disponible, cant_en_uso) para un material dado."""
    db = SessionLocal()
    try:
        material = (
            db.query(CatalogoMaterial)
            .filter(CatalogoMaterial.id == catalogo_id)
            .first()
        )
        assert material is not None, f"Material ID {catalogo_id} no existe"
        return material.cant_disponible, material.cant_en_uso
    finally:
        db.close()


# ── Fixture de skip automático ────────────────────────────────────────────────
@pytest.fixture(scope="class")
def servidor_disponible():
    if not _check_servidor_disponible():
        pytest.skip(
            "Servidor no disponible en localhost:8000. "
            "Levanta el stack con 'docker compose up -d' para correr stress tests."
        )


class TestStressCheckOut:
    """Pruebas de estrés y consistencia del check-out concurrente (HTTP real)."""

    def test_concurrent_checkout_consistencia(self, servidor_disponible):
        """
        Lanza N_REQUESTS check-outs concurrentes al servidor real (uvicorn).
        Usa el material con mayor stock disponible.

        Valida:
        - Solo hay 200 y 400 (ningún 500).
        - Contadores finales consistentes: (disp + en_uso) = total original.
        - Ninguna petición tardó más de TIMEOUT_SEG segundos.
        - Los 200 exitosos no exceden el stock disponible inicial.
        """
        catalogo_id, disp_antes, nombre = _get_material_con_mas_stock()
        if disp_antes == 0:
            pytest.skip("Sin stock disponible. Restaura la BD con docker compose down -v && up.")

        _, en_uso_antes = _get_stock_actual(catalogo_id)
        total_antes = disp_antes + en_uso_antes

        token = _get_token_httpx()

        resultados: list[tuple[int, float]] = []
        with ThreadPoolExecutor(max_workers=N_REQUESTS) as executor:
            futures = [
                executor.submit(_do_checkout_httpx, catalogo_id, token)
                for _ in range(N_REQUESTS)
            ]
            for fut in as_completed(futures):
                resultados.append(fut.result())

        codigos = [r[0] for r in resultados]
        tiempos = [r[1] for r in resultados]

        exitosos = codigos.count(200)
        fallidos = codigos.count(400)

        # Verificación 1: Solo hay 200 y 400, nada de 500
        codigos_invalidos = [c for c in codigos if c not in (200, 400)]
        assert not codigos_invalidos, (
            f"Respuestas inesperadas (no 200/400): {codigos_invalidos}"
        )

        # Verificación 2: Tiempos < TIMEOUT_SEG
        lentos = [t for t in tiempos if t > TIMEOUT_SEG]
        assert not lentos, (
            f"{len(lentos)} petición(es) superaron {TIMEOUT_SEG}s: "
            f"{[f'{t:.3f}s' for t in lentos]}"
        )

        # Verificación 3: Consistencia de contadores en BD
        disp_despues, en_uso_despues = _get_stock_actual(catalogo_id)
        total_despues = disp_despues + en_uso_despues

        # El total no puede cambiar (sin pérdidas)
        assert total_antes == total_despues, (
            f"Total cambió: antes={total_antes}, después={total_despues}. "
            "Posible inconsistencia en contadores."
        )

        # Los exitosos NO pueden superar el stock inicial
        assert exitosos <= disp_antes, (
            f"Exitosos ({exitosos}) > stock disponible inicial ({disp_antes}). "
            "¡Stock negativo o race condition sin bloqueo!"
        )

        # La suma exitosos + fallidos == total requests
        assert exitosos + fallidos == N_REQUESTS

        print(
            f"\n[Stress] Material: '{nombre}' (id={catalogo_id}) | "
            f"Stock inicial: {disp_antes} | "
            f"{N_REQUESTS} requests → {exitosos} OK, {fallidos} sin stock | "
            f"t_max={max(tiempos):.3f}s | t_avg={sum(tiempos)/len(tiempos):.3f}s"
        )

    def test_checkout_tiempo_individual(self, servidor_disponible):
        """Verifica que un check-out individual responda en < TIMEOUT_SEG."""
        catalogo_id, disp, _ = _get_material_con_mas_stock()
        if disp < 1:
            pytest.skip("Sin stock disponible para este test individual")

        token = _get_token_httpx()
        _, elapsed = _do_checkout_httpx(catalogo_id, token)
        assert elapsed < TIMEOUT_SEG, (
            f"Check-out individual tardó {elapsed:.3f}s (límite: {TIMEOUT_SEG}s)"
        )
