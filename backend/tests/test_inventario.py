class TestStock:
    def test_list_stock(self, client, auth_header):
        response = client.get("/api/inventario/", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_by_tipo_material(self, client, auth_header):
        response = client.get("/api/inventario/?tipo_material=HERRAMIENTA_DEVOLUTIVA", headers=auth_header)
        assert response.status_code == 200
        for item in response.json():
            assert item.get("tipo_material") in ("HERRAMIENTA_DEVOLUTIVA", "EPP_DEVOLUTIVO")

    def test_get_stock_by_id(self, client, auth_header):
        response = client.get("/api/inventario/1", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "cant_disponible" in data
        assert "cant_en_uso" in data

    def test_get_stock_by_id_not_found(self, client, auth_header):
        response = client.get("/api/inventario/9999", headers=auth_header)
        assert response.status_code == 404

    def test_buscar_por_short_code(self, client, auth_header):
        response = client.get("/api/inventario/buscar?short_code=TALNEU-ATLAS", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["codigo_interno"] == "TALNEU-ATLAS"
        assert "cant_disponible" in data[0]

    def test_buscar_short_code_parcial(self, client, auth_header):
        response = client.get("/api/inventario/buscar?short_code=TALELC", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any("TALELC" in item["codigo_interno"] for item in data)

    def test_buscar_short_code_inexistente(self, client, auth_header):
        response = client.get("/api/inventario/buscar?short_code=ZZZZZZ", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []
