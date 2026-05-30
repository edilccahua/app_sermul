class TestHistorial:
    def test_list_historial(self, client, auth_header):
        response = client.get("/api/historial/", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "items" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data
        assert isinstance(data["items"], list)

    def test_filter_by_parada(self, client, auth_header):
        response = client.get("/api/historial/?parada_id=1", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["parada_id"] == 1

    def test_filter_by_tipo(self, client, auth_header):
        response = client.get("/api/historial/?tipo=Entrega", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["tipo_movimiento"] == "Entrega"

    def test_filter_by_fecha_desde(self, client, auth_header):
        response = client.get(
            "/api/historial/?fecha_desde=2026-01-01T00:00:00", headers=auth_header
        )
        assert response.status_code == 200

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/historial/")
        assert response.status_code == 401
