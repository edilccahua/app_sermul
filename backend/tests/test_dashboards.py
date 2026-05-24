def test_get_dashboard_residente(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    
    # Validar campos base
    assert "pct_herramientas_en_uso" in data
    assert "herramientas_disponibles" in data
    assert "herramientas_en_uso" in data
    assert "herramientas_malogradas" in data
    assert "herramientas_perdidas" in data
    assert "costo_total_perdidas" in data
    assert "costo_total_inventario" in data
    
    # Validar colecciones y tipos
    assert isinstance(data["perdidas_por_parada"], list)
    assert isinstance(data["top_grupos_herramientas"], list)
    assert isinstance(data["herramientas_mas_usadas"], list)
    assert isinstance(data["paradas_activas"], list)
    
    # Validar que los KPIs tengan valores coherentes
    assert data["herramientas_disponibles"] >= 0
    assert data["herramientas_en_uso"] >= 0
    assert data["costo_total_perdidas"] >= 0.0
    assert data["costo_total_inventario"] >= 0.0
    assert data["epps_por_vencer"] == 0
    assert data["pendientes_cierre"] >= 0
    assert data["reservas_pendientes"] >= 0

def test_dashboard_residente_estructura(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    keys = [
        "pct_herramientas_en_uso", "herramientas_disponibles", "herramientas_en_uso", 
        "herramientas_malogradas", "herramientas_perdidas", "costo_total_perdidas", 
        "costo_total_inventario", "perdidas_por_parada", "top_grupos_herramientas", 
        "herramientas_mas_usadas", "paradas_activas", "pendientes_cierre", 
        "reservas_pendientes", "epps_por_vencer"
    ]
    for key in keys:
        assert key in data

def test_dashboard_saturacion_calculo(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    pct = data["pct_herramientas_en_uso"]
    assert 0 <= pct <= 100
    
    total = data["herramientas_disponibles"] + data["herramientas_en_uso"]
    if total > 0:
        expected_pct = (data["herramientas_en_uso"] / total) * 100
        assert round(pct, 1) == round(expected_pct, 1)
    else:
        assert pct == 0

def test_dashboard_perdidas_por_parada(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    perdidas = data["perdidas_por_parada"]
    assert isinstance(perdidas, list)
    if perdidas:
        item = perdidas[0]
        assert "parada_id" in item
        assert "codigo_parada" in item
        assert "nombre_parada" in item
        assert "total_perdido" in item
        assert "cantidad_perdidas" in item
        assert item["total_perdido"] >= 0
        assert item["cantidad_perdidas"] > 0

def test_dashboard_top_grupos(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    top_grupos = data["top_grupos_herramientas"]
    assert isinstance(top_grupos, list)
    if len(top_grupos) > 1:
        # Check descending order
        for i in range(len(top_grupos) - 1):
            assert top_grupos[i]["herramientas_en_uso"] >= top_grupos[i+1]["herramientas_en_uso"]

def test_dashboard_herramientas_mas_usadas(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    mas_usadas = data["herramientas_mas_usadas"]
    assert isinstance(mas_usadas, list)
    if len(mas_usadas) > 1:
        for i in range(len(mas_usadas) - 1):
            assert mas_usadas[i]["veces_usada"] >= mas_usadas[i+1]["veces_usada"]

def test_dashboard_paradas_activas(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    paradas = data["paradas_activas"]
    assert isinstance(paradas, list)
    for p in paradas:
        assert p["estado"] == "Activa"

def test_dashboard_alertas_reservas_pendientes(client, auth_header_residente):
    response = client.get("/api/dashboards/residente", headers=auth_header_residente)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["reservas_pendientes"], int)
    assert data["reservas_pendientes"] >= 0
