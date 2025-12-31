# API Endpoints - Product Intelligence Dropi

## Resumen

Este sistema usa dos fuentes de datos:

| Fuente | Base URL | Datos |
|--------|----------|-------|
| **Dropi** | `https://api.dropi.co` | Catálogo, stock, precios, proveedores |
| **DropKiller** | `https://extension-api.dropkiller.com` | Historial de ventas (8 días) |

---

## 1. Dropi API

### 1.1 Catálogo de Productos

```http
GET https://api.dropi.co/api/products/productlist/v1/index
```

**Respuesta:** Lista de productos con información completa

```json
{
  "isSuccess": true,
  "objects": [
    {
      "id": 1645891,
      "sku": "BU75JKFuzGEatMz0WoHL",
      "name": "set Destellos de Oro en baño de oro",
      "type": "SIMPLE",
      "sale_price": 30000,
      "suggested_price": 99900,
      "categories": [{"name": "Bisutería"}, {"name": "Moda"}],
      "user": {
        "id": 274355,
        "name": "Leidy",
        "store_name": "Gloobex",
        "plan": {"name": "SUPPLIER PREMIUM"},
        "category_user": {"name": "VERIFICADO"}
      },
      "warehouse_product": [
        {"id": 1853733, "stock": 82, "warehouse_id": 16617}
      ],
      "variations": [],
      "gallery": [{"urlS3": "colombia/products/1645891/imagen.jpeg"}]
    }
  ],
  "status": 200
}
```

**Campos clave:**
- `id` → ID único del producto (usar para DropKiller)
- `sale_price` → Precio del proveedor
- `suggested_price` → Precio sugerido de venta
- `warehouse_product[].stock` → Stock disponible
- `user.category_user.name` → Estado del proveedor (VERIFICADO, PREMIUM, etc.)

---

### 1.2 Detalle de Producto

```http
GET https://api.dropi.co/api/products/productlist/v1/show/?id={product_id}
```

**Ejemplo:**
```http
GET https://api.dropi.co/api/products/productlist/v1/show/?id=1938915
```

**Respuesta:** Información detallada del producto incluyendo variaciones y bodegas.

---

### 1.3 Lista de Proveedores

```http
GET https://api.dropi.co/api/products/getDataProductsSuplier?type_user=S
```

**Respuesta:** Lista de proveedores con conteo de productos y categorías.

---

### 1.4 Detalle de Usuario/Proveedor

```http
GET https://api.dropi.co/api/users/{user_id}
```

---

## 2. DropKiller API

### 2.1 Historial de Ventas (⭐ ENDPOINT CLAVE)

```http
GET https://extension-api.dropkiller.com/api/v3/history?ids={product_ids}&country={country_code}
```

**Parámetros:**
- `ids` → IDs de productos separados por coma (ej: `1645891,2017300,1390113`)
- `country` → Código de país: `CO` (Colombia), `EC` (Ecuador), etc.

**Ejemplo:**
```http
GET https://extension-api.dropkiller.com/api/v3/history?ids=1645891,2017300&country=CO
```

**Respuesta:**
```json
[
  {
    "id": "286996ae-66b4-4961-8120-65bf4dfb4f18",
    "name": "set destellos de oro en bano de oro",
    "externalId": "1645891",
    "country": "CO",
    "platform": "DROPI",
    "createdAt": "2025-02-05 00:00:00",
    "salePrice": 30000,
    "history": [
      {
        "date": "2025-12-24",
        "stock": 82,
        "billing": 0,
        "salePrice": 30000,
        "soldUnits": 0,
        "stockAdjustment": false,
        "stockAdjustmentReason": null
      }
    ]
  }
]
```

**Campos clave:**
- `externalId` → ID del producto en Dropi
- `history[].soldUnits` → ⭐ Unidades vendidas ese día
- `history[].billing` → Facturación del día
- `history[].stock` → Stock al final del día
- `history[].stockAdjustment` → Si hubo reposición de inventario

---

## 3. Flujo de Integración

```
1. GET Dropi /index → Todos los productos
2. Filtrar localmente:
   • Stock ≥ 50 unidades
   • Margen ≥ 40%
   • Precio $25,000 - $150,000 COP
3. GET DropKiller /history?ids=X,Y,Z&country=CO
   → Obtener ventas de los últimos 8 días
4. Filtrar por ventas:
   • SUM(soldUnits) últimos 8 días ≥ 3
5. Scoring final → TOP productos
```

---

## 4. Cálculos Clave

### Margen
```
margen = ((suggested_price - sale_price) / suggested_price) * 100
```

### Ventas 8 días
```
ventas_8d = SUM(history[].soldUnits)
```

### Facturación 8 días
```
facturacion_8d = SUM(history[].billing)
```

---

## 5. Países Soportados

| País | Código | Dominio Dropi |
|------|--------|---------------|
| Colombia | `CO` | app.dropi.co |
| Ecuador | `EC` | app.dropi.ec |
| México | `MX` | app.dropi.mx |
| Panamá | `PA` | app.dropi.pa |

---

## 6. Notas Importantes

### DropKiller API
- ✅ **No requiere autenticación** (API pública)
- ✅ Soporta batch de múltiples IDs
- ⚠️ Solo tiene historial de productos que ya fueron trackeados
- ⚠️ Puede haber rate limiting (no documentado)

### Dropi API
- ✅ **No requiere autenticación** para endpoints de catálogo
- ❌ **NO expone datos de ventas** - solo stock y precios
- Los endpoints autenticados (crear órdenes, etc.) requieren token
