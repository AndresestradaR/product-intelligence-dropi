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
    sort_by: str = Query("ventas30d", description="Ordenar por: ventas30d, ventasTotal, precio, nombre"),
    sort_order: str = Query("desc", description="asc o desc")
):
    results = PRODUCTS.copy()
    
    # Filtrar por búsqueda
    if q:
        q_lower = q.lower()
        results = [p for p in results if q_lower in p.get('name', '').lower()]
    
    # Filtrar por ventas (últimos 30 días)
    if min_ventas is not None:
        results = [p for p in results if p.get('soldUnitsLast30Days', 0) >= min_ventas]
    if max_ventas is not None:
        results = [p for p in results if p.get('soldUnitsLast30Days', 0) <= max_ventas]
    
    # Filtrar por precio
    if min_precio is not None:
        results = [p for p in results if p.get('salePrice', 0) >= min_precio]
    if max_precio is not None:
        results = [p for p in results if p.get('salePrice', 0) <= max_precio]
    
    # Filtrar por categoría
    if categoria:
        cat_lower = categoria.lower()
        results = [p for p in results if cat_lower in (p.get('baseCategory', {}).get('name', '') or '').lower()]
    
    # Ordenar
    sort_key = {
        'ventas30d': lambda x: x.get('soldUnitsLast30Days', 0),
        'ventasTotal': lambda x: x.get('totalSoldUnits', 0),
        'precio': lambda x: x.get('salePrice', 0),
        'nombre': lambda x: x.get('name', '').lower()
    }.get(sort_by, lambda x: x.get('soldUnitsLast30Days', 0))
    
    results.sort(key=sort_key, reverse=(sort_order == 'desc'))
    
    total = len(results)
    
    # Simplificar respuesta (sin historial completo para listados)
    results_simplified = []
    for p in results[offset:offset + limit]:
        results_simplified.append({
            "id": p.get("id"),
            "externalId": p.get("externalId"),
            "name": p.get("name"),
            "salePrice": p.get("salePrice"),
            "suggestedPrice": p.get("suggestedPrice"),
            "totalSoldUnits": p.get("totalSoldUnits"),
            "soldUnitsLast30Days": p.get("soldUnitsLast30Days"),
            "soldUnitsLast7Days": p.get("soldUnitsLast7Days"),
            "billingLast30Days": p.get("billingLast30Days"),
            "stock": p.get("stock"),
            "status": p.get("status"),
            "category": p.get("baseCategory", {}).get("name") if p.get("baseCategory") else None,
            "provider": p.get("provider", {}).get("name") if p.get("provider") else None,
            "image": p.get("multimedia", [{}])[0].get("url") if p.get("multimedia") else None
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "productos": results_simplified
    }

@app.get("/api/productos/{producto_id}")
def obtener_producto(producto_id: str):
    for p in PRODUCTS:
        if p.get('id') == producto_id or p.get('externalId') == producto_id:
            return p
    return {"error": "Producto no encontrado"}

@app.get("/api/stats")
def estadisticas():
    if not PRODUCTS:
        return {"error": "No hay datos cargados"}
    
    ventas_30d = [p.get('soldUnitsLast30Days', 0) for p in PRODUCTS]
    ventas_total = [p.get('totalSoldUnits', 0) for p in PRODUCTS]
    precios = [p.get('salePrice', 0) for p in PRODUCTS if p.get('salePrice', 0) > 0]
    
    # Top categorías
    categorias = {}
    for p in PRODUCTS:
        cat = p.get('baseCategory', {}).get('name', 'Sin categoría') if p.get('baseCategory') else 'Sin categoría'
        categorias[cat] = categorias.get(cat, 0) + p.get('soldUnitsLast30Days', 0)
    top_cats = sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_productos": len(PRODUCTS),
        "ventas_promedio_30d": round(sum(ventas_30d) / len(ventas_30d), 1) if ventas_30d else 0,
        "ventas_total": sum(ventas_total),
        "precio_promedio": round(sum(precios) / len(precios), 0) if precios else 0,
        "productos_con_ventas": len([p for p in PRODUCTS if p.get('soldUnitsLast30Days', 0) > 0]),
        "top_100_ventas": len([p for p in PRODUCTS if p.get('soldUnitsLast30Days', 0) > 100]),
        "top_categorias": [{"categoria": cat, "ventas_30d": ventas} for cat, ventas in top_cats]
    }

@app.get("/api/trending")
def productos_trending(limit: int = Query(20, le=100)):
    """Productos con mayor crecimiento en ventas (últimos 7 días vs 7 días anteriores)"""
    trending = []
    for p in PRODUCTS:
        historial = p.get('historial', [])
        if len(historial) >= 14:
            # Últimos 7 días
            recent = sum(h.get('soldUnits', 0) for h in historial[-7:])
            # 7 días anteriores
            previous = sum(h.get('soldUnits', 0) for h in historial[-14:-7])
            if previous > 0:
                growth = ((recent - previous) / previous) * 100
                trending.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "salePrice": p.get("salePrice"),
                    "soldUnitsLast30Days": p.get("soldUnitsLast30Days"),
                    "ventas_ultimos_7d": recent,
                    "ventas_previos_7d": previous,
                    "growth_percent": round(growth, 1),
                    "category": p.get("baseCategory", {}).get("name") if p.get("baseCategory") else None,
                    "image": p.get("multimedia", [{}])[0].get("url") if p.get("multimedia") else None
                })
    
    trending.sort(key=lambda x: x['growth_percent'], reverse=True)
    return trending[:limit]

@app.get("/api/categorias")
def listar_categorias():
    """Lista todas las categorías disponibles"""
    categorias = {}
    for p in PRODUCTS:
        cat = p.get('baseCategory', {}).get('name') if p.get('baseCategory') else None
        if cat:
            categorias[cat] = categorias.get(cat, 0) + 1
    
    return sorted([{"name": k, "count": v} for k, v in categorias.items()], key=lambda x: x['count'], reverse=True)
