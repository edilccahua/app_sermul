class TestCheckOut:
    def test_check_out_exitoso(self, client, auth_header):
        # Asegurar que haya al menos una unidad disponible en Mina
        inv = client.get("/api/inventario/?estado=Disponible&ubicacion=Mina", headers=auth_header)
        if inv.status_code == 200 and len(inv.json()) > 0:
            code = inv.json()[0]["catalogo"]["codigo_interno"]
        else:
            # Reponer una unidad a Disponible/Mina para poder testear
            client.put(
                "/api/inventario/2/ubicacion",
                json={"ubicacion_macro": "Mina"},
                headers=auth_header,
            )
            code = "HER-001"

        response = client.post(
            "/api/inventario/check-out",
            json={"short_code": code, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["movimiento"]["tipo_movimiento"] == "Entrega"
        assert data["unidad"]["estado"] == "En_Uso"

    def test_check_out_short_code_inexistente(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"short_code": "NO-EXISTE", "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 404

    def test_check_out_grupo_inexistente(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"short_code": "HER-001", "grupo_id": 9999, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 404

    def test_check_out_sin_unidades_disponibles(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"short_code": "CONS-001", "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_out_sin_permiso(self, client, auth_header_lider):
        response = client.post(
            "/api/inventario/check-out",
            json={"short_code": "HER-001", "grupo_id": 1, "parada_id": 1},
            headers=auth_header_lider,
        )
        assert response.status_code == 403


class TestCheckIn:
    def test_check_in_exitoso(self, client, auth_header):
        # Buscar una unidad que ya esté En_Uso en el inventario
        inv = client.get("/api/inventario/?estado=En_Uso", headers=auth_header)
        if inv.status_code != 200 or len(inv.json()) == 0:
            # Si no hay, hacemos check-out para generar una
            out = client.post(
                "/api/inventario/check-out",
                json={"short_code": "HER-001", "grupo_id": 1, "parada_id": 1},
                headers=auth_header,
            )
            assert out.status_code == 200
            unidad_id = out.json()["unidad"]["id"]
        else:
            unidad_id = inv.json()[0]["id"]

        response = client.post(
            "/api/inventario/check-in",
            json={"inventario_id": unidad_id, "buen_estado": True},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["movimiento"]["tipo_movimiento"] == "Devolucion"
        assert data["unidad"]["estado"] == "Disponible"

    def test_check_in_no_en_uso(self, client, auth_header):
        # Unidad 5 está En_Transito_Compra (no En_Uso)
        response = client.post(
            "/api/inventario/check-in",
            json={"inventario_id": 5, "buen_estado": True},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_in_unidad_inexistente(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-in",
            json={"inventario_id": 9999, "buen_estado": True},
            headers=auth_header,
        )
        assert response.status_code == 404

    def test_check_in_sin_permiso(self, client, auth_header_lider):
        response = client.post(
            "/api/inventario/check-in",
            json={"inventario_id": 1, "buen_estado": True},
            headers=auth_header_lider,
        )
        assert response.status_code == 403
