import uuid

def test_get_grupos(client, auth_header):
    response = client.get("/api/grupos", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_grupo_not_found(client, auth_header):
    response = client.get("/api/grupos/9999", headers=auth_header)
    assert response.status_code == 404

def test_get_grupos_con_filtro_parada(client, auth_header):
    response = client.get("/api/grupos?parada_id=1", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for g in data:
        assert g["parada_id"] == 1

def test_get_grupos_con_filtro_estado(client, auth_header):
    response = client.get("/api/grupos?estado=Activo", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for g in data:
        assert g["estado"] == "Activo"

def test_agregar_integrante_duplicado(client, auth_header_residente):
    unique_code = f"GRP-{uuid.uuid4().hex[:6]}"
    grupo_in = {
        "codigo": unique_code,
        "nombre": "Grupo Test Duplicado",
        "parada_id": 1,
        "lider_id": 1,
        "supervisor_id": 1
    }
    response = client.post("/api/grupos/", json=grupo_in, headers=auth_header_residente)
    assert response.status_code == 201
    grupo_id = response.json()["id"]

    req_integrante = {"usuario_id": 1}
    response = client.post(f"/api/grupos/{grupo_id}/integrantes", json=req_integrante, headers=auth_header_residente)
    assert response.status_code == 200

    response = client.post(f"/api/grupos/{grupo_id}/integrantes", json=req_integrante, headers=auth_header_residente)
    assert response.status_code == 400
    assert "ya es integrante activo" in response.json()["detail"].lower()
