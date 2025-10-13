# app/core/structured_logging.py
"""
Sistema de logging estructurado para mejor observabilidad.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """Logger con formato JSON estructurado."""
    
    def __init__(self, name: str = "sistema-comercial"):
        """Inicializa el logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Handler para stdout con formato JSON
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Método interno de logging."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "sistema-comercial",
        }
        
        if extra:
            log_data.update(extra)
        
        getattr(self.logger, level.lower())(json.dumps(log_data, default=str))
    
    def info(self, message: str, **kwargs):
        """Log nivel INFO."""
        self._log("INFO", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log nivel WARNING."""
        self._log("WARNING", message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log nivel ERROR."""
        self._log("ERROR", message, kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log nivel DEBUG."""
        self._log("DEBUG", message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log nivel CRITICAL."""
        self._log("CRITICAL", message, kwargs)
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float, user: Optional[str] = None):
        """Log específico para requests HTTP."""
        self.info(
            f"{method} {path} - {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user=user,
            type="http_request"
        )
    
    def log_db_query(self, query: str, duration_ms: float, rows: int):
        """Log específico para queries de BD."""
        self.info(
            f"DB Query - {duration_ms:.2f}ms - {rows} rows",
            query=query[:200],  # Truncar queries largas
            duration_ms=duration_ms,
            rows=rows,
            type="db_query"
        )
    
    def log_cache_hit(self, key: str, hit: bool):
        """Log para operaciones de caché."""
        self.debug(
            f"Cache {'HIT' if hit else 'MISS'}: {key}",
            cache_key=key,
            hit=hit,
            type="cache"
        )
    
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log estructurado de errores."""
        self.error(
            f"Error: {type(error).__name__}: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            type="error"
        )


class JSONFormatter(logging.Formatter):
    """Formatter que convierte logs a JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log record como JSON."""
        # Si el mensaje ya es JSON, retornarlo directamente
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Mensaje no es JSON, convertirlo
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, default=str)


# Instancia global del logger
structured_logger = StructuredLogger()


# Helper para logging simple
def log_info(message: str, **kwargs):
    """Shortcut para logging INFO."""
    structured_logger.info(message, **kwargs)


def log_error(message: str, **kwargs):
    """Shortcut para logging ERROR."""
    structured_logger.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Shortcut para logging WARNING."""
    structured_logger.warning(message, **kwargs)


