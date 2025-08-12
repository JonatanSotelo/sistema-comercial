import pytest

def test_auditoria_optional(client, auth_headers):
    # Si el router no existe, 404 -> test se marca como xpassed/skip
    r = client.get("/auditoria", headers=auth_headers)
    if r.status_code == 404:
        pytest.skip("Router /auditoria no está habilitado en este despliegue.")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
