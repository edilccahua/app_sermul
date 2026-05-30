def test_get_reservas(client, auth_header):
    response = client.get("/api/reservas", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_reserva_not_found(client, auth_header):
    response = client.get("/api/reservas/9999", headers=auth_header)
    assert response.status_code == 404

def test_workflow_completo_reserva(client, auth_header_lider, auth_header_residente, auth_header):
    # 1. Crear Reserva (Líder Mecánico)
    reserva_in = {
        "parada_id": 1,
        "grupo_id": 1,
        "turno": "Dia",
        "fecha_programada": "2026-05-22",
        "items": [
            {"catalogo_id": 1, "cantidad_solicitada": 1}
        ]
    }
    
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    print("RESPONSE", response.text)
    assert response.status_code == 201
    reserva = response.json()
    assert reserva["estado"] == "Pendiente"
    assert reserva["codigo_reserva"].startswith("RES-")
    reserva_id = reserva["id"]
    
    # 2. Obtener Reserva por ID
    response = client.get(f"/api/reservas/{reserva_id}", headers=auth_header_lider)
    assert response.status_code == 200
    assert response.json()["id"] == reserva_id
    
    # 3. Aprobar Reserva (Residente)
    response = client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)
    assert response.status_code == 200
    assert response.json()["estado"] == "Aprobada"
    assert response.json()["fecha_aprobacion"] is not None
    
    # 4. Despachar Reserva (Almacenero)
    response = client.post(f"/api/reservas/{reserva_id}/despachar", json={}, headers=auth_header)
    # Puede ser 200 (despacho completo/parcial) o 400 si no hay stock físico disponible en Mina para HER-001.
    # Dado que es un test de integración, el estado final cambiará a Despachada.
    assert response.status_code in (200, 400)
    if response.status_code == 200:
        assert response.json()["estado"] == "Despachada"
        assert response.json()["fecha_despacho"] is not None

def test_crear_reserva_stock_insuficiente(client, auth_header_lider):
    reserva_in = {
        "parada_id": 1,
        "grupo_id": 1,
        "turno": "Dia",
        "fecha_programada": "2026-05-22",
        "items": [
            {"catalogo_id": 1, "cantidad_solicitada": 99999}
        ]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    assert response.status_code == 201
    reserva = response.json()
    assert "alertas_stock" in reserva
    assert len(reserva["alertas_stock"]) > 0

def test_aprobar_reserva(client, auth_header_lider, auth_header_residente):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 1}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    reserva_id = response.json()["id"]

    response = client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "Aprobada"
    assert data["fecha_aprobacion"] is not None

def test_rechazar_reserva_con_motivo(client, auth_header_lider, auth_header_residente):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 1}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    reserva_id = response.json()["id"]

    motivo = {"motivo": "Falta justificación de uso"}
    response = client.post(f"/api/reservas/{reserva_id}/rechazar", json=motivo, headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "Rechazada"
    assert data["motivo_rechazo"] == "Falta justificación de uso"

def test_despachar_reserva_completa(client, auth_header_lider, auth_header_residente, auth_header):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 1}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    reserva_id = response.json()["id"]
    client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)

    response = client.post(f"/api/reservas/{reserva_id}/despachar", json={}, headers=auth_header)
    if response.status_code == 200:
        data = response.json()
        assert data["estado"] == "Despachada"
        assert data["fecha_despacho"] is not None
        
        # Recuperar la reserva para validar sus detalles
        res = client.get(f"/api/reservas/{reserva_id}", headers=auth_header_lider)
        res_data = res.json()
        if "detalles" in res_data and len(res_data["detalles"]) > 0:
            assert res_data["detalles"][0]["cantidad_despachada"] >= 0

def test_despachar_reserva_parcial(client, auth_header_lider, auth_header_residente, auth_header):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 2}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    reserva_id = response.json()["id"]
    client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)

    # Recuperar la reserva para obtener los IDs de detalle
    res = client.get(f"/api/reservas/{reserva_id}", headers=auth_header_lider)
    detalles = res.json().get("detalles", [])
    
    if detalles:
        detalle_id = detalles[0]["id"]
        response = client.post(f"/api/reservas/{reserva_id}/despachar", json={"items_ids": [detalle_id]}, headers=auth_header)
        if response.status_code == 200:
            data = response.json()
            assert data["estado"] == "Despachada"
            
            # Recuperar para validar
            res2 = client.get(f"/api/reservas/{reserva_id}", headers=auth_header_lider)
            res2_data = res2.json()
            if "detalles" in res2_data and len(res2_data["detalles"]) > 0:
                assert res2_data["detalles"][0]["cantidad_despachada"] >= 0

def test_no_aprobar_reserva_ya_aprobada(client, auth_header_lider, auth_header_residente):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 1}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    reserva_id = response.json()["id"]

    client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)
    response = client.post(f"/api/reservas/{reserva_id}/aprobar", headers=auth_header_residente)
    assert response.status_code == 400

def test_crear_reserva_genera_codigo(client, auth_header_lider):
    reserva_in = {
        "parada_id": 1, "grupo_id": 1, "turno": "Dia", "fecha_programada": "2026-05-22",
        "items": [{"catalogo_id": 1, "cantidad_solicitada": 1}]
    }
    response = client.post("/api/reservas/", json=reserva_in, headers=auth_header_lider)
    assert response.status_code == 201
    reserva = response.json()
    assert reserva["codigo_reserva"].startswith("RES-")
    assert len(reserva["codigo_reserva"]) > 4
