
from typing import Optional
from fastapi import Request
from .services_api_client import ApiClient

def get_token(request: Request) -> Optional[str]:
    return request.session.get("access_token")

def get_api(request: Request) -> ApiClient:
    token = get_token(request)
    return ApiClient(token=token)
