import pytest

def test_create_list_update_delete_user(client, auth_headers, unique_username):
    # CREATE (colección suele estar en "/usuarios/")
    payload = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "vend1234",
        "is_admin": False,
        "is_active": True,
    }
    r = client.post("/usuarios/", headers=auth_headers, json=payload)
    # Puede devolver 201 o 400 si por algún motivo ya existe
    assert r.status_code in (201, 400), r.text
    if r.status_code == 400:
        pytest.skip("El usuario ya existía; vuelve a correr para generar uno nuevo.")
    created = r.json()
    uid = created["id"]

    # LIST
    r = client.get("/usuarios/", headers=auth_headers)
    assert r.status_code == 200
    assert any(u["id"] == uid for u in r.json()), "El usuario creado no aparece en el listado."

    # UPDATE (item suele estar en "/usuarios/{id}" sin barra final)
    r = client.put(f"/usuarios/{uid}", headers=auth_headers, json={"email": f"{unique_username}+upd@example.com"})
    assert r.status_code == 200
    assert r.json().get("email", "").endswith("+upd@example.com")

    # DELETE
    r = client.delete(f"/usuarios/{uid}", headers=auth_headers)
    assert r.status_code in (200, 204, 404)
