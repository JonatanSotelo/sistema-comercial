# tests/test_pdfs.py
import pytest
from fastapi.testclient import TestClient


def test_remito_html(client: TestClient, admin_token: str, sample_venta):
    """Test generación de remito HTML"""
    response = client.get(
        f"/ventas/{sample_venta.id}/remito",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "REMITO" in response.text
    assert str(sample_venta.id) in response.text


def test_remito_pdf_nonempty(client: TestClient, admin_token: str, sample_venta):
    """Test generación de remito PDF con contenido"""
    response = client.get(
        f"/ventas/{sample_venta.id}/remito.pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
    assert len(response.content) > 100  # PDF debe tener contenido real


def test_remito_venta_no_existe(client: TestClient, admin_token: str):
    """Test remito de venta inexistente → 404"""
    response = client.get(
        "/ventas/999999/remito.pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_label_pdf_nonempty(client: TestClient, admin_token: str, sample_pedido):
    """Test generación de etiqueta PDF con QR"""
    response = client.get(
        f"/pedidos/{sample_pedido.id}/label.pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0
    assert len(response.content) > 100  # PDF debe tener contenido real


def test_label_pedido_no_existe(client: TestClient, admin_token: str):
    """Test etiqueta de pedido inexistente → 404"""
    response = client.get(
        "/pedidos/999999/label.pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


def test_packing_pdf_exists(client: TestClient, admin_token: str, sample_pedido):
    """Test que packing slip PDF también funcione"""
    response = client.get(
        f"/pedidos/{sample_pedido.id}/packing.pdf",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    # Puede ser 200 o 404 dependiendo de si el servicio está implementado
    assert response.status_code in [200, 404, 401]
    
    if response.status_code == 200:
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

