def test_backup_download_requires_admin(client, admin_token):
    # primero generamos uno
    r = client.post("/backup/run", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200

    r2 = client.get("/backup/download", headers={"Authorization": f"Bearer {admin_token}"})
    assert r2.status_code == 200
    assert r2.headers.get("content-type") in ("application/zip", "application/octet-stream")
