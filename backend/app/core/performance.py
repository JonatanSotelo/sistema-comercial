# app/core/performance.py
"""
Optimizaciones de performance: queries, indices, caching.
"""
from sqlalchemy import Index
from sqlalchemy.orm import Query, Session
from typing import List, Optional


def optimize_query_with_index(query: Query, model, index_fields: List[str]) -> Query:
    """
    Optimiza una query asegurando que use índices apropiados.
    
    Args:
        query: Query de SQLAlchemy
        model: Modelo de la tabla
        index_fields: Campos que deberían estar indexados
    
    Returns:
        Query optimizada (sin cambios, pero con awareness de índices)
    """
    # Esta función es informativa - los índices se crean en los modelos
    # Pero puede usarse para logging/debugging de queries
    return query


def paginate_efficiently(
    query: Query,
    page: int,
    per_page: int,
    max_per_page: int = 100
) -> tuple[List, int]:
    """
    Paginación eficiente con límite máximo.
    
    Args:
        query: Query a paginar
        page: Número de página (1-based)
        per_page: Items por página
        max_per_page: Máximo permitido
    
    Returns:
        (items, total_count)
    """
    per_page = min(per_page, max_per_page)
    offset = (page - 1) * per_page
    
    # Obtener total (puede ser costoso en tablas grandes)
    # Considerar cachear este valor
    total = query.count()
    
    # Obtener items paginados
    items = query.offset(offset).limit(per_page).all()
    
    return items, total


def bulk_insert_optimized(session: Session, model_class, data_list: List[dict]):
    """
    Inserción masiva optimizada (bulk insert).
    
    Args:
        session: Sesión de SQLAlchemy
        model_class: Clase del modelo
        data_list: Lista de diccionarios con datos
    """
    if not data_list:
        return []
    
    # Usar bulk_insert_mappings para mejor performance
    session.bulk_insert_mappings(model_class, data_list)
    session.commit()


def prefetch_related(session: Session, query: Query, *relationships):
    """
    Prefetch de relaciones para evitar N+1 queries.
    
    Args:
        session: Sesión de SQLAlchemy
        query: Query base
        relationships: Nombres de relaciones a prefetch
    
    Returns:
        Query con joinedload/selectinload
    """
    from sqlalchemy.orm import joinedload, selectinload
    
    for rel in relationships:
        query = query.options(selectinload(rel))
    
    return query


# Configuración de índices recomendados (documentación)
RECOMMENDED_INDEXES = {
    "productos": ["nombre", "codigo", "categoria", "activo"],
    "clientes": ["nombre", "email"],
    "proveedores": ["nombre", "email", "cuit"],
    "ventas": ["fecha", "cliente_id", "estado"],
    "compras": ["fecha", "proveedor_id", "estado"],
    "users": ["username", "email"],
}


def log_slow_query(query_str: str, duration_ms: float, threshold_ms: float = 100):
    """
    Registra queries lentas para análisis.
    
    Args:
        query_str: String de la query
        duration_ms: Duración en milisegundos
        threshold_ms: Umbral para considerar "lenta"
    """
    if duration_ms > threshold_ms:
        print(f"⚠️ SLOW QUERY ({duration_ms:.2f}ms): {query_str[:200]}")


