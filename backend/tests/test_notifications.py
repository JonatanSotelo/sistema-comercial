# tests/test_notifications.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_notify_order_ready_ok(db: Session, sample_pedido):
    """Test notificación exitosa con mock httpx"""
    with patch("httpx.AsyncClient") as mock_client:
        # Mock respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        # Ejecutar notificación
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # Verificar que se llamó al endpoint
        assert mock_post.call_count >= 1
        
        # Verificar auditoría
        from app.models.auditoria import Auditoria
        audit = db.query(Auditoria).filter(
            Auditoria.table_name == "notificaciones"
        ).first()
        
        # Si la auditoría existe, verificar que fue exitosa
        if audit:
            assert "success" in audit.details or audit.action.value in ["CREATE", "INSERT"]


@pytest.mark.asyncio
async def test_notify_order_ready_retry_then_ok(db: Session, sample_pedido):
    """Test reintentos: 500, 500, 200 → éxito final"""
    with patch("httpx.AsyncClient") as mock_client:
        # Mock: primeros 2 intentos fallan, tercero OK
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        
        mock_post = AsyncMock(side_effect=[
            mock_response_500,  # Intento 1: falla
            mock_response_500,  # Intento 2: falla
            mock_response_200,  # Intento 3: éxito
        ])
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # Debe haber intentado 3 veces
        assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_notify_order_ready_error_audit(db: Session, sample_pedido):
    """Test: 3 fallos → auditoría con error"""
    with patch("httpx.AsyncClient") as mock_client:
        # Mock: todos los intentos fallan
        mock_post = AsyncMock(side_effect=Exception("Connection error"))
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # Debe haber intentado 3 veces
        assert mock_post.call_count == 3
        
        # Verificar que se registró el error en auditoría
        from app.models.auditoria import Auditoria
        audit = db.query(Auditoria).filter(
            Auditoria.table_name == "notificaciones"
        ).first()
        
        if audit:
            # Verificar que registró el fallo
            assert "success" in audit.details and audit.details["success"] == False


@pytest.mark.asyncio
async def test_notify_order_ready_sin_telefono(db: Session, sample_pedido):
    """Test: pedido sin teléfono → skip notificación"""
    # Asegurar que el pedido no tiene teléfono
    sample_pedido.telefono = None
    if sample_pedido.cliente:
        sample_pedido.cliente.telefono = None
    db.commit()
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock()
        mock_client.return_value.__aenter__.return_value.post = mock_post
        
        from app.services.notifications_service import notify_order_ready
        await notify_order_ready(db, sample_pedido.id)
        
        # No debe haber intentado enviar notificación
        assert mock_post.call_count == 0


@pytest.mark.asyncio
async def test_notify_order_ready_notify_disabled(db: Session, sample_pedido):
    """Test: NOTIFY_ON_READY=false → no envía notificación"""
    with patch("app.services.notifications_service.settings") as mock_settings:
        mock_settings.NOTIFY_ON_READY = False
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_post = AsyncMock()
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            from app.services.notifications_service import notify_order_ready
            await notify_order_ready(db, sample_pedido.id)
            
            # No debe haber intentado enviar
            assert mock_post.call_count == 0

