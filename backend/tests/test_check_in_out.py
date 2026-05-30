class TestCheckOut:
    def test_check_out_exitoso(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 1, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Entrega"
        assert data["cantidad"] == 1
        assert data["catalogo_id"] == 28

    def test_check_out_sin_stock(self, client, auth_header):
        # Pedir más de lo disponible (TORNIL-STEEL id=28 tiene disp=10)
        response = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 99999, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_out_grupo_inexistente(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 1, "grupo_id": 9999, "parada_id": 1},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_out_sin_permiso(self, client, auth_header_lider):
        response = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 1, "grupo_id": 1, "parada_id": 1},
            headers=auth_header_lider,
        )
        assert response.status_code == 403

    def test_check_out_con_observacion(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 1, "grupo_id": 1, "parada_id": 1, "observacion_entrega": "Entregado con llave de repuesto"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Entrega"
        assert data["cantidad"] == 1
        assert data["catalogo_id"] == 28




class TestCheckIn:
    def test_check_in_exitoso(self, client, auth_header):
        # Primero check-out para tener en uso (TALELC-BOSCH id=7)
        out = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 7, "cantidad": 1, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert out.status_code == 200

        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 7, "cant_buen_estado": 1, "cant_malograda": 0},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["tipo"] == "Devolucion"
        assert data["cantidad"] == 1

    def test_check_in_malograda(self, client, auth_header):
        # Check-out de AMONEU-CHICA id=3 (disp=1)
        out = client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 3, "cantidad": 1, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )
        assert out.status_code == 200, f"Check-out previo falló: {out.text}"

        # Check-in del mismo material (id=3) como malogrado
        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 3, "cant_buen_estado": 0, "cant_malograda": 1, "descripcion_dano": "Motor quemado"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["tipo"] == "Devolucion"

    def test_check_in_mixta(self, client, auth_header):
        # Check-out de 3 unidades (TORNIL-STEEL id=28 tiene disp=10)
        client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 28, "cantidad": 3, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )

        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 28, "cant_buen_estado": 2, "cant_malograda": 1, "descripcion_dano": "Tornillo pasado de rosca"},
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad"] == 3

    def test_check_in_sin_unidades_en_uso(self, client, auth_header):
        # Encontrar dinámicamente un material que no tenga unidades en uso
        resp = client.get("/api/catalogo", headers=auth_header)
        mat_id = next((item["id"] for item in resp.json() if item["cant_en_uso"] == 0), None)
        if not mat_id:
            import pytest
            pytest.skip("No hay materiales con 0 unidades en uso")
            
        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": mat_id, "cant_buen_estado": 1, "cant_malograda": 0},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_in_sin_unidades(self, client, auth_header):
        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 27, "cant_buen_estado": 0, "cant_malograda": 0},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_in_sin_descripcion_dano(self, client, auth_header):
        # Check-out
        client.post(
            "/api/inventario/check-out",
            json={"catalogo_id": 5, "cantidad": 1, "grupo_id": 1, "parada_id": 1},
            headers=auth_header,
        )

        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 5, "cant_buen_estado": 0, "cant_malograda": 1},
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_check_in_sin_permiso(self, client, auth_header_lider):
        response = client.post(
            "/api/inventario/check-in",
            json={"catalogo_id": 27, "cant_buen_estado": 1, "cant_malograda": 0},
            headers=auth_header_lider,
        )
        assert response.status_code == 403
