class TestParadas:
    def test_list_paradas(self, client, auth_header):
        response = client.get("/api/paradas/", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_by_id(self, client, auth_header):
        response = client.get("/api/paradas/1", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["codigo"] == "PAR-2026-001"

    def test_get_by_id_not_found(self, client, auth_header):
        response = client.get("/api/paradas/9999", headers=auth_header)
        assert response.status_code == 404

    def test_create_parada(self, client, auth_header_residente):
        import uuid
        from app.core.database import SessionLocal
        from app.models.parada import Parada

        code = f"T{uuid.uuid4().hex[:8].upper()}"
        response = client.post(
            "/api/paradas/",
            json={
                "codigo": code,
                "nombre": "Parada de prueba",
                "fecha_inicio": "2026-07-01",
            },
            headers=auth_header_residente,
        )
        assert response.status_code == 201
        db = SessionLocal()
        try:
            p = db.query(Parada).filter_by(codigo=code).first()
            if p:
                db.delete(p)
                db.commit()
        finally:
            db.close()

    def test_create_parada_duplicada(self, client, auth_header_residente):
        response = client.post(
            "/api/paradas/",
            json={
                "codigo": "PAR-2026-001",
                "nombre": "Duplicada",
                "fecha_inicio": "2026-07-01",
            },
            headers=auth_header_residente,
        )
        assert response.status_code == 400

    def test_update_parada(self, client, auth_header_residente):
        response = client.put(
            "/api/paradas/1",
            json={"observaciones": "Actualizada desde tests"},
            headers=auth_header_residente,
        )
        assert response.status_code == 200

    def test_create_parada_sin_permiso(self, client, auth_header_lider):
        response = client.post(
            "/api/paradas/",
            json={
                "codigo": "PAR-NOPERM",
                "nombre": "Sin permiso",
                "fecha_inicio": "2026-07-01",
            },
            headers=auth_header_lider,
        )
        assert response.status_code == 403
