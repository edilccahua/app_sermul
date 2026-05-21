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
        assert data["codigo_interno"] == "HER-001"

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
                "tipo_material": "Herramienta",
                "es_devolutivo": True,
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["codigo_interno"] == code
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
                "codigo_interno": "HER-001",
                "nombre": "Duplicado",
                "categoria_id": 1,
                "tipo_material": "Herramienta",
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
                "tipo_material": "Herramienta",
                "es_devolutivo": True,
            },
            headers=auth_header_lider,
        )
        assert response.status_code == 403
