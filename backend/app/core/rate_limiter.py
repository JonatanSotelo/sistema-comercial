# app/core/rate_limiter.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio

class RateLimiter:
    """Rate limiter simple en memoria"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, Deque[float]] = defaultdict(lambda: deque())
    
    def is_allowed(self, client_ip: str) -> bool:
        """Verifica si el cliente puede hacer una request"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Limpiar requests antiguas
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Verificar si excede el límite
        if len(client_requests) >= self.max_requests:
            return False
        
        # Agregar la request actual
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """Obtiene el número de requests restantes"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Limpiar requests antiguas
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))
    
    def get_reset_time(self, client_ip: str) -> float:
        """Obtiene el tiempo de reset del rate limit"""
        client_requests = self.requests[client_ip]
        if not client_requests:
            return time.time()
        
        return client_requests[0] + self.window_seconds

# Instancia global del rate limiter
rate_limiter = RateLimiter()

async def check_rate_limit(request: Request) -> None:
    """Middleware para verificar rate limit"""
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        reset_time = rate_limiter.get_reset_time(client_ip)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "remaining": remaining,
                "reset_time": reset_time,
                "retry_after": int(reset_time - time.time())
            }
        )

def get_rate_limit_headers(client_ip: str) -> Dict[str, str]:
    """Obtiene headers de rate limit para la respuesta"""
    remaining = rate_limiter.get_remaining_requests(client_ip)
    reset_time = rate_limiter.get_reset_time(client_ip)
    
    return {
        "X-RateLimit-Limit": str(rate_limiter.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset_time))
    }
