# app/core/cache.py
"""
Sistema de caché con Redis para optimizar performance.
"""
import json
from typing import Optional, Any, Callable
from functools import wraps
import redis
from app.core.settings import settings


class CacheManager:
    """Gestor de caché con Redis."""
    
    def __init__(self):
        """Inicializa la conexión a Redis."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379",
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Verificar conexión
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"⚠️ Redis no disponible, cache deshabilitado: {e}")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error obteniendo del cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Guarda un valor en el caché.
        
        Args:
            key: Clave del caché
            value: Valor a guardar (será serializado a JSON)
            ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Error guardando en cache {key}: {e}")
            return False
    
    def delete(self, key: str):
        """Elimina una clave del caché."""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error eliminando del cache {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str):
        """Elimina todas las claves que coinciden con un patrón."""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error eliminando patrón {pattern}: {e}")
            return False
    
    def invalidate_module(self, module: str):
        """Invalida todo el caché de un módulo (ej: 'productos')."""
        return self.delete_pattern(f"{module}:*")


# Instancia global del cache manager
cache = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        ttl: Tiempo de vida en segundos
        key_prefix: Prefijo para la clave de caché
    
    Ejemplo:
        @cached(ttl=600, key_prefix="productos")
        def get_productos_activos(db):
            return db.query(Producto).filter(Producto.activo==True).all()
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché basada en función y parámetros
            cache_key = f"{key_prefix}:{func.__name__}"
            
            # Agregar args/kwargs a la clave (simple)
            if args:
                cache_key += f":{hash(str(args))}"
            if kwargs:
                cache_key += f":{hash(str(sorted(kwargs.items())))}"
            
            # Intentar obtener del caché
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


