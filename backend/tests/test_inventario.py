class TestInventario:
    def test_list_inventario(self, client, auth_header):
        response = client.get("/api/inventario/", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_by_estado(self, client, auth_header):
        response = client.get("/api/inventario/?estado=Disponible", headers=auth_header)
        assert response.status_code == 200
        for item in response.json():
            assert item["estado"] == "Disponible"

    def test_filter_by_ubicacion(self, client, auth_header):
        response = client.get("/api/inventario/?ubicacion=Mina", headers=auth_header)
        assert response.status_code == 200
        for item in response.json():
            assert item["ubicacion_macro"] == "Mina"

    def test_get_by_id(self, client, auth_header):
        response = client.get("/api/inventario/1", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_by_id_not_found(self, client, auth_header):
        response = client.get("/api/inventario/9999", headers=auth_header)
        assert response.status_code == 404

    def test_buscar_por_short_code(self, client, auth_header):
        response = client.get("/api/inventario/buscar?short_code=HER-001", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_cambiar_ubicacion(self, client, auth_header):
        response = client.put(
            "/api/inventario/1/ubicacion",
            json={"ubicacion_macro": "Mina"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["ubicacion_macro"] == "Mina"

    def test_cambiar_ubicacion_invalida(self, client, auth_header):
        response = client.put(
            "/api/inventario/1/ubicacion",
            json={"ubicacion_macro": "Marte"},
            headers=auth_header,
        )
        assert response.status_code == 400
