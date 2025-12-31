# API Endpoints - Product Intelligence Dropi

## Resumen

Este sistema usa dos fuentes de datos:

| Fuente | Base URL | Datos | Auth |
|--------|----------|-------|------|
| **Dropi** | `https://api.dropi.co` | Catálogo, stock, precios, proveedores | No (catálogo) |
| **DropKiller API** | `https://extension-api.dropkiller.com` | Historial de ventas (8 días) | No |
| **DropKiller Dashboard** | `https://app.dropkiller.com` | Filtros avanzados, 500k+ productos | Sí (suscripción) |

---

## 1. Dropi API

### 1.1 Catálogo de Productos

```http
GET https://api.dropi.co/api/products/productlist/v1/index
```

**Nota:** Requiere sesión activa en Dropi. Acceder desde el dashboard de Dropi.

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

---

### 1.3 Lista de Proveedores

```http
GET https://api.dropi.co/api/products/getDataProductsSuplier?type_user=S
```

---

## 2. DropKiller API Pública (Extensión Chrome)

### 2.1 Historial de Ventas (⭐ ENDPOINT CLAVE)

```http
GET https://extension-api.dropkiller.com/api/v3/history?ids={product_ids}&country={country_code}
```

**Parámetros:**
- `ids` → IDs de productos separados por coma (ej: `1645891,2017300,1390113`)
- `country` → Código de país: `CO`, `EC`, `MX`, `PA`, etc.

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

**Notas:**
- ✅ **No requiere autenticación**
- ✅ Soporta batch de múltiples IDs
- ⚠️ Solo tiene historial de productos ya trackeados
- ⚠️ Llamar desde navegador directo (no desde otro dominio por CORS)

---

## 3. DropKiller Dashboard (Requiere Suscripción)

### 3.1 Búsqueda de Productos con Filtros

```http
GET https://app.dropkiller.com/dashboard/products?{params}
```

**Query Parameters:**

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `platform` | Plataforma de dropshipping | `dropi`, `easydrop`, `aliclick` |
| `country` | ID del país (UUID) | `65c75a5f-0c4a-45fb-8c90-5b538805a15a` |
| `limit` | Productos por página | `50` |
| `page` | Número de página | `1` |
| `s7min` | Ventas 7 días mínimo | `10` |
| `s7max` | Ventas 7 días máximo | `100` |
| `s30min` | Ventas 30 días mínimo | `50` |
| `s30max` | Ventas 30 días máximo | `500` |
| `f7min` | Facturación 7 días mínimo | `100000` |
| `f7max` | Facturación 7 días máximo | `5000000` |
| `f30min` | Facturación 30 días mínimo | `500000` |
| `f30max` | Facturación 30 días máximo | `20000000` |
| `stock-min` | Stock mínimo | `50` |
| `stock-max` | Stock máximo | `1000` |
| `price-min` | Precio mínimo | `25000` |
| `price-max` | Precio máximo | `150000` |
| `creation-date` | Rango de fechas | `2025-12-01/2025-12-30` |

**Ejemplo completo:**
```
https://app.dropkiller.com/dashboard/products?platform=dropi&country=65c75a5f-0c4a-45fb-8c90-5b538805a15a&limit=50&page=1&s7min=10&stock-min=50&price-min=25000&price-max=150000
```

---

### 3.2 IDs de Países

| País | UUID | Código |
|------|------|--------|
| Colombia | `65c75a5f-0c4a-45fb-8c90-5b538805a15a` | CO |
| Ecuador | `82811e8b-d17d-4ab9-847a-fa925785d566` | EC |
| México | `98993bd0-955a-4fa3-9612-c9d4389c44d0` | MX |
| Chile | `ad63080c-908d-4757-9548-30decb082b7e` | CL |
| España | `3f18ae66-2f98-4af1-860e-53ed93e5cde0` | ES |
| Perú | `6acfee32-9c25-4f95-b030-a005e488f3fb` | PE |
| Panamá | `c1f01c6a-99c7-4253-b67f-4e2607efae9e` | PA |
| Paraguay | `f2594db9-caee-4221-b4a6-9b6267730a2d` | PY |
| Argentina | `de93b0dd-d9d3-468d-8c44-e9780799a29f` | AR |
| Guatemala | `77c15189-b3b9-4f55-9226-e56c231f87ac` | GT |

---

### 3.3 Plataformas Soportadas

| Plataforma | Valor | Países |
|------------|-------|--------|
| Dropi | `dropi` | AR, CL, CO, EC, ES, GT, MX, PA, PY, PE |
| Easydrop | `easydrop` | CL, EC, MX, PE |
| Aliclick | `aliclick` | PE |
| Dropea | `dropea` | ES |
| Droplatam | `droplatam` | CL, CO, EC, ES, MX, PA, PY, PE |
| Seventy Block | `seventy block` | CO |
| Wimpy | `wimpy` | CO, MX |
| Mastershop | `mastershop` | CO |

---

### 3.4 Detalle de Producto

```http
GET https://app.dropkiller.com/dashboard/tracking/detail/{product_uuid}?platform=dropi
```

**Muestra:**
- Gráfico de ventas diarias (30 días)
- Total de ventas
- Promedio diario
- Facturación
- Historial de stock

---

## 4. Flujo de Integración Recomendado

### Opción A: Usando Dashboard DropKiller (Recomendado)

```
1. Ir a app.dropkiller.com/dashboard/products
2. Aplicar filtros:
   - platform=dropi
   - country=Colombia
   - s7min=10 (ventas 7d)
   - stock-min=50
   - price-min=25000, price-max=150000
3. Revisar productos resultantes
4. Click "Ver detalle" para análisis profundo
```

### Opción B: Usando API Pública

```
1. Obtener catálogo de Dropi (requiere sesión)
2. Filtrar por stock, margen, precio
3. Consultar ventas en batch:
   GET extension-api.dropkiller.com/api/v3/history?ids=X,Y,Z&country=CO
4. Filtrar por soldUnits >= 3
5. Ordenar por ventas
```

---

## 5. Cálculos Clave

### Margen
```
margen = ((suggested_price - sale_price) / suggested_price) * 100
```

### Ventas 8 días (API pública)
```
ventas_8d = SUM(history[].soldUnits)
```

### Ganancia Estimada
```
ganancia = (suggested_price - sale_price) * ventas_periodo
```

---

## 6. Notas Importantes

### DropKiller Dashboard
- ✅ **500,000+ productos** trackeados
- ✅ Filtros avanzados por ventas, facturación, stock
- ✅ Historial de 30 días
- ✅ Múltiples plataformas (Dropi, Easydrop, Aliclick, etc.)
- ⚠️ Requiere suscripción ($24.99 USD/mes plan Advanced)

### DropKiller API Pública
- ✅ **Gratis y sin auth**
- ✅ Batch de múltiples productos
- ⚠️ Solo 8 días de historial
- ⚠️ Solo productos ya trackeados
- ⚠️ CORS bloquea llamadas desde otros dominios

### Dropi API
- ✅ Datos de catálogo completos
- ❌ **NO expone ventas** - solo stock y precios
- ⚠️ Requiere sesión activa en Dropi
