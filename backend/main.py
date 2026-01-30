from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import zipfile
import io
import json
from typing import Optional
import os

app = FastAPI(title="Product Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage
PRODUCTS = []
DATA_URL = os.getenv("DATA_URL", "https://pub-b30a404e74844ba9afc36fbe8d311ec8.r2.dev/dropkiller_COMPLETO.zip")

@app.on_event("startup")
async def load_data():
    global PRODUCTS
    print(f"Descargando datos desde {DATA_URL}...")
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.get(DATA_URL)
        print(f"Descargado: {len(response.content) / 1024 / 1024:.1f} MB")
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            for name in zf.namelist():
                if name.endswith('.json'):
                    with zf.open(name) as f:
                        PRODUCTS = json.load(f)
                        print(f"Cargados {len(PRODUCTS)} productos")
                        break

@app.get("/")
def root():
    return {"status": "ok", "productos": len(PRODUCTS)}

@app.get("/api/productos")
def buscar_productos(
    q: Optional[str] = Query(None, description="Buscar por nombre"),
    min_ventas: Optional[int] = Query(None, description="Ventas mínimas últimos 30 días"),
    max_ventas: Optional[int] = Query(None, description="Ventas máximas últimos 30 días"),
    min_precio: Optional[float] = Query(None, description="Precio mínimo"),
    max_precio: Optional[float] = Query(None, description="Precio máximo"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    limit: int = Query(50, le=200, description="Límite de resultados"),
    offset: int = Query(0, description="Offset para paginación"),
    sort_by: str = Query("ventas30d", description="Ordenar por: ventas30d, precio, nombre"),
    sort_order: str = Query("desc", description="asc o desc")
):
    results = PRODUCTS.copy()
    
    # Filtrar por búsqueda
    if q:
        q_lower = q.lower()
        results = [p for p in results if q_lower in p.get('name', '').lower()]
    
    # Filtrar por ventas
    if min_ventas is not None:
        results = [p for p in results if p.get('last30DaysSales', 0) >= min_ventas]
    if max_ventas is not None:
        results = [p for p in results if p.get('last30DaysSales', 0) <= max_ventas]
    
    # Filtrar por precio
    if min_precio is not None:
        results = [p for p in results if p.get('price', 0) >= min_precio]
    if max_precio is not None:
        results = [p for p in results if p.get('price', 0) <= max_precio]
    
    # Filtrar por categoría
    if categoria:
        cat_lower = categoria.lower()
        results = [p for p in results if cat_lower in p.get('category', '').lower()]
    
    # Ordenar
    sort_key = {
        'ventas30d': lambda x: x.get('last30DaysSales', 0),
        'precio': lambda x: x.get('price', 0),
        'nombre': lambda x: x.get('name', '').lower()
    }.get(sort_by, lambda x: x.get('last30DaysSales', 0))
    
    results.sort(key=sort_key, reverse=(sort_order == 'desc'))
    
    total = len(results)
    results = results[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "productos": results
    }

@app.get("/api/productos/{producto_id}")
def obtener_producto(producto_id: str):
    for p in PRODUCTS:
        if p.get('id') == producto_id:
            return p
    return {"error": "Producto no encontrado"}

@app.get("/api/stats")
def estadisticas():
    if not PRODUCTS:
        return {"error": "No hay datos cargados"}
    
    ventas = [p.get('last30DaysSales', 0) for p in PRODUCTS]
    precios = [p.get('price', 0) for p in PRODUCTS if p.get('price', 0) > 0]
    
    return {
        "total_productos": len(PRODUCTS),
        "ventas_promedio_30d": sum(ventas) / len(ventas) if ventas else 0,
        "precio_promedio": sum(precios) / len(precios) if precios else 0,
        "top_vendedores": len([p for p in PRODUCTS if p.get('last30DaysSales', 0) > 100])
    }

@app.get("/api/trending")
def productos_trending(limit: int = Query(20, le=100)):
    """Productos con mayor crecimiento en ventas"""
    # Calcular tendencia basada en historial
    trending = []
    for p in PRODUCTS:
        history = p.get('history', [])
        if len(history) >= 14:
            recent = sum(h.get('soldUnits', 0) for h in history[-7:])
            previous = sum(h.get('soldUnits', 0) for h in history[-14:-7])
            if previous > 0:
                growth = ((recent - previous) / previous) * 100
                trending.append({**p, 'growth': growth})
    
    trending.sort(key=lambda x: x['growth'], reverse=True)
    return trending[:limit]
