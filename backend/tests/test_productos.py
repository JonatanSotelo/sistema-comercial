def test_productos_list_ok(client, admin_token):
    r = client.get("/productos?page=1&size=5", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert "items" in r.json()

def test_productos_paginacion_invalida(client, admin_token):
    r = client.get("/productos?size=-1", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code in (400, 422)

def test_productos_filtro_inexistente(client, admin_token):
    r = client.get("/productos?search=__noexiste__", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

def test_productos_export_excel(client, admin_token):
    r = client.get("/productos/export", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    ct = r.headers.get("content-type","")
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in ct or "application/octet-stream" in ct
