def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"
    assert j.get("db") == "ok"
