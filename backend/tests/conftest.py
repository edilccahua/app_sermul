import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_header(client):
    """Token de ALMACENERO (Juan Pérez) — CHECK_OUT, CHECK_IN, VER_INVENTARIO, EDITAR_INVENTARIO, CAMBIAR_UBICACION"""
    response = client.post(
        "/api/auth/login",
        json={"dni": "11223344", "password": "11223344"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_residente(client):
    """Token de RESIDENTE (Carlos Rodríguez) — todos los permisos incluido CREAR_PARADA"""
    response = client.post(
        "/api/auth/login",
        json={"dni": "12345678", "password": "12345678"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_lider(client):
    """Token de LIDER_MEC (Pedro Quispe) — solo VER_INVENTARIO, sin CHECK_OUT ni EDITAR_INVENTARIO"""
    response = client.post(
        "/api/auth/login",
        json={"dni": "22334455", "password": "22334455"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
