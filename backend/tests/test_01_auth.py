def test_login_ok(client):
    r = client.post("/auth/login", json={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    j = r.json()
    assert "access_token" in j and j.get("token_type") == "bearer"

def test_me_ok(client, auth_headers):
    r = client.get("/users/usuarios/me", headers=auth_headers)
    assert r.status_code == 200
    me = r.json()
    assert me.get("username") == "admin"
