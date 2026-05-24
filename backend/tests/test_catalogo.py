class TestCatalogo:
    def test_list_catalogo(self, client, auth_header):
        response = client.get("/api/catalogo/", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_by_id(self, client, auth_header):
        response = client.get("/api/catalogo/1", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "cant_disponible" in data
        assert "cant_en_uso" in data

    def test_get_by_id_not_found(self, client, auth_header):
        response = client.get("/api/catalogo/9999", headers=auth_header)
        assert response.status_code == 404

    def test_search(self, client, auth_header):
        response = client.get("/api/catalogo/search?q=Amoladora", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert any("Amoladora" in item.get("nombre", "") for item in data)

    def test_create_catalogo(self, client, auth_header):
        import uuid
        from app.core.database import SessionLocal
        from app.models.catalogo_material import CatalogoMaterial

        code = f"T{uuid.uuid4().hex[:8].upper()}"
        response = client.post(
            "/api/catalogo/",
            json={
                "codigo_interno": code,
                "nombre": "Herramienta de prueba",
                "categoria_id": 1,
                "tipo_material": "HERRAMIENTA_DEVOLUTIVA",
                "es_devolutivo": True,
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["codigo_interno"] == code
        assert "cant_disponible" in data
        db = SessionLocal()
        try:
            cat = db.query(CatalogoMaterial).filter_by(codigo_interno=code).first()
            if cat:
                db.delete(cat)
                db.commit()
        finally:
            db.close()

    def test_create_duplicate_code_fails(self, client, auth_header):
        response = client.post(
            "/api/catalogo/",
            json={
                "codigo_interno": "TALNEU-ATLAS",
                "nombre": "Duplicado",
                "categoria_id": 1,
                "tipo_material": "HERRAMIENTA_DEVOLUTIVA",
                "es_devolutivo": True,
            },
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_update_catalogo(self, client, auth_header):
        original = client.get("/api/catalogo/1", headers=auth_header).json()["nombre"]
        response = client.put(
            "/api/catalogo/1",
            json={"nombre": "Nombre Actualizado"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Nombre Actualizado"
        client.put("/api/catalogo/1", json={"nombre": original}, headers=auth_header)

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/catalogo/")
        assert response.status_code == 401

    def test_sin_permiso_retorna_403(self, client, auth_header_lider):
        response = client.post(
            "/api/catalogo/",
            json={
                "codigo_interno": "NO-PERM",
                "nombre": "x",
                "categoria_id": 1,
                "tipo_material": "HERRAMIENTA_DEVOLUTIVA",
                "es_devolutivo": True,
            },
            headers=auth_header_lider,
        )
        assert response.status_code == 403


class TestStockManagement:
    def test_update_stock_exitoso(self, client, auth_header):
        original = client.get("/api/catalogo/27", headers=auth_header).json()
        disp = original["cant_disponible"]
        response = client.put(
            "/api/catalogo/27/stock?field=cant_disponible&delta=-1",
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["cant_disponible"] == disp - 1
        # Restaurar
        client.put("/api/catalogo/27/stock?field=cant_disponible&delta=1", headers=auth_header)

    def test_update_stock_negativo(self, client, auth_header):
        response = client.put(
            "/api/catalogo/27/stock?field=cant_disponible&delta=-99999",
            headers=auth_header,
        )
        assert response.status_code == 400

    def test_update_stock_campo_invalido(self, client, auth_header):
        response = client.put(
            "/api/catalogo/1/stock?field=estado&delta=1",
            headers=auth_header,
        )
        assert response.status_code == 400
