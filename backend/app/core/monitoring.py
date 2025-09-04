# app/core/monitoring.py
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio
from fastapi import Request, Response
from app.core.settings import settings

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsCollector:
    """Recolector de métricas básicas"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times: deque = deque(maxlen=1000)
        self.endpoint_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"count": 0, "errors": 0})
        self.start_time = time.time()
    
    def record_request(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Registra una request"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        endpoint_key = f"{method} {endpoint}"
        self.endpoint_stats[endpoint_key]["count"] += 1
        
        if status_code >= 400:
            self.error_count += 1
            self.endpoint_stats[endpoint_key]["errors"] += 1
        
        # Log requests importantes
        if status_code >= 400:
            logger.warning(f"Request failed: {method} {endpoint} - {status_code} - {response_time:.3f}s")
        elif response_time > 5.0:  # Requests lentas
            logger.warning(f"Slow request: {method} {endpoint} - {response_time:.3f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas actuales"""
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "average_response_time": avg_response_time,
            "endpoint_stats": dict(self.endpoint_stats)
        }

# Instancia global del recolector
metrics = MetricsCollector()

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self):
        self.last_db_check = None
        self.db_status = "unknown"
        self.last_backup_check = None
        self.backup_status = "unknown"
    
    async def check_database(self, db) -> Dict[str, Any]:
        """Verifica la salud de la base de datos"""
        try:
            start_time = time.time()
            result = db.execute("SELECT 1").fetchone()
            response_time = time.time() - start_time
            
            self.db_status = "healthy"
            self.last_db_check = datetime.now()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "last_check": self.last_db_check.isoformat()
            }
        except Exception as e:
            self.db_status = "unhealthy"
            self.last_db_check = datetime.now()
            
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": self.last_db_check.isoformat()
            }
    
    async def check_backup_system(self) -> Dict[str, Any]:
        """Verifica el sistema de backup"""
        try:
            # Verificar si el directorio de backup existe y es escribible
            import os
            backup_dir = settings.BACKUP_DIR
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
            
            # Verificar permisos de escritura
            test_file = os.path.join(backup_dir, "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            
            self.backup_status = "healthy"
            self.last_backup_check = datetime.now()
            
            return {
                "status": "healthy",
                "backup_dir": backup_dir,
                "last_check": self.last_backup_check.isoformat()
            }
        except Exception as e:
            self.backup_status = "unhealthy"
            self.last_backup_check = datetime.now()
            
            logger.error(f"Backup system health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": self.last_backup_check.isoformat()
            }
    
    async def get_system_health(self, db) -> Dict[str, Any]:
        """Obtiene el estado general del sistema"""
        db_health = await self.check_database(db)
        backup_health = await self.check_backup_system()
        
        overall_status = "healthy"
        if db_health["status"] != "healthy" or backup_health["status"] != "healthy":
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "database": db_health,
            "backup": backup_health,
            "metrics": metrics.get_metrics()
        }

# Instancia global del health checker
health_checker = HealthChecker()

class AlertManager:
    """Gestor de alertas"""
    
    def __init__(self):
        self.alerts: deque = deque(maxlen=100)
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% de error rate
            "response_time": 5.0,  # 5 segundos
            "consecutive_errors": 5  # 5 errores consecutivos
        }
        self.consecutive_errors = 0
    
    def check_alerts(self, metrics_data: Dict[str, Any]):
        """Verifica si se deben generar alertas"""
        current_time = datetime.now()
        
        # Alerta por error rate alto
        if metrics_data["error_rate"] > self.alert_thresholds["error_rate"]:
            self._add_alert("HIGH_ERROR_RATE", f"Error rate is {metrics_data['error_rate']:.2%}", current_time)
        
        # Alerta por response time alto
        if metrics_data["average_response_time"] > self.alert_thresholds["response_time"]:
            self._add_alert("HIGH_RESPONSE_TIME", f"Average response time is {metrics_data['average_response_time']:.2f}s", current_time)
        
        # Alerta por errores consecutivos
        if metrics_data["total_errors"] > 0:
            self.consecutive_errors += 1
            if self.consecutive_errors >= self.alert_thresholds["consecutive_errors"]:
                self._add_alert("CONSECUTIVE_ERRORS", f"{self.consecutive_errors} consecutive errors", current_time)
        else:
            self.consecutive_errors = 0
    
    def _add_alert(self, alert_type: str, message: str, timestamp: datetime):
        """Agrega una alerta"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": timestamp.isoformat(),
            "severity": "warning"
        }
        self.alerts.append(alert)
        logger.warning(f"ALERT: {alert_type} - {message}")
    
    def get_alerts(self, limit: int = 10) -> list:
        """Obtiene las alertas recientes"""
        return list(self.alerts)[-limit:]

# Instancia global del alert manager
alert_manager = AlertManager()

async def monitoring_middleware(request: Request, call_next):
    """Middleware para monitoreo de requests"""
    start_time = time.time()
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular métricas
    response_time = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code
    
    # Registrar métricas
    metrics.record_request(endpoint, method, status_code, response_time)
    
    # Verificar alertas
    current_metrics = metrics.get_metrics()
    alert_manager.check_alerts(current_metrics)
    
    # Agregar headers de monitoreo
    response.headers["X-Response-Time"] = f"{response_time:.3f}"
    response.headers["X-Request-ID"] = f"{int(time.time() * 1000)}"
    
    return response
