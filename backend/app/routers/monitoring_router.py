# app/routers/monitoring_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.monitoring import metrics, health_checker, alert_manager
from app.core.deps import require_admin
from typing import Dict, Any

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@router.get("/health")
async def get_health(db: Session = Depends(get_db)):
    """Health check completo del sistema"""
    return await health_checker.get_system_health(db)

@router.get("/metrics")
async def get_metrics():
    """Métricas del sistema"""
    return metrics.get_metrics()

@router.get("/alerts")
async def get_alerts(limit: int = 10, admin_user = Depends(require_admin)):
    """Obtener alertas recientes (solo admin)"""
    return {
        "alerts": alert_manager.get_alerts(limit),
        "total_alerts": len(alert_manager.alerts)
    }

@router.get("/status")
async def get_status():
    """Estado básico del sistema"""
    current_metrics = metrics.get_metrics()
    
    status = "healthy"
    if current_metrics["error_rate"] > 0.05:  # 5% error rate
        status = "degraded"
    if current_metrics["error_rate"] > 0.1:  # 10% error rate
        status = "unhealthy"
    
    return {
        "status": status,
        "uptime": current_metrics["uptime_seconds"],
        "requests": current_metrics["total_requests"],
        "errors": current_metrics["total_errors"],
        "error_rate": current_metrics["error_rate"],
        "avg_response_time": current_metrics["average_response_time"]
    }

@router.get("/endpoints")
async def get_endpoint_stats(admin_user = Depends(require_admin)):
    """Estadísticas por endpoint (solo admin)"""
    return {
        "endpoints": metrics.endpoint_stats,
        "total_endpoints": len(metrics.endpoint_stats)
    }

@router.post("/alerts/clear")
async def clear_alerts(admin_user = Depends(require_admin)):
    """Limpiar alertas (solo admin)"""
    alert_manager.alerts.clear()
    return {"message": "Alertas limpiadas"}

@router.get("/performance")
async def get_performance_stats(admin_user = Depends(require_admin)):
    """Estadísticas de rendimiento (solo admin)"""
    current_metrics = metrics.get_metrics()
    
    # Calcular percentiles de response time
    response_times = list(metrics.response_times)
    if response_times:
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        p50 = sorted_times[int(n * 0.5)]
        p95 = sorted_times[int(n * 0.95)]
        p99 = sorted_times[int(n * 0.99)]
    else:
        p50 = p95 = p99 = 0
    
    return {
        "response_time_percentiles": {
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "average": current_metrics["average_response_time"]
        },
        "request_volume": {
            "total_requests": current_metrics["total_requests"],
            "requests_per_minute": current_metrics["total_requests"] / (current_metrics["uptime_seconds"] / 60) if current_metrics["uptime_seconds"] > 0 else 0
        },
        "error_analysis": {
            "total_errors": current_metrics["total_errors"],
            "error_rate": current_metrics["error_rate"],
            "consecutive_errors": alert_manager.consecutive_errors
        }
    }
