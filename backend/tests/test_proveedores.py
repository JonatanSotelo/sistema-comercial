import httpx

def test_list_proveedores(client: httpx.Client, auth_headers: dict):
    r = client.get("/proveedores?page=1&size=10", headers=auth_headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "items" in data and "total" in data

def test_export_proveedores(client: httpx.Client, auth_headers: dict, excel_mime_prefix: str):
    r = client.get("/proveedores/export", headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith(excel_mime_prefix)
