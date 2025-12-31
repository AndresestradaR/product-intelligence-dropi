# API Endpoints - Product Intelligence Dropi

## Resumen

Este sistema usa múltiples fuentes de datos:

| Fuente | Base URL | Datos | Auth |
|--------|----------|-------|------|
| **Dropi** | `https://api.dropi.co` | Catálogo, stock, precios, proveedores | No (catálogo) |
| **DropKiller API** | `https://extension-api.dropkiller.com` | Historial de ventas (8 días) | No |
| **DropKiller Dashboard** | `https://app.dropkiller.com` | Filtros avanzados, 500k+ productos | Sí (suscripción) |
| **Adskiller** | `https://app.dropkiller.com/dashboard/adskiller` | Anuncios FB/TikTok con análisis IA | Sí (suscripción) |

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

### 3.2 IDs de Países (Dashboard Products)

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

## 4. Adskiller API (⭐ ANÁLISIS DE ANUNCIOS CON IA)

### 4.1 Lista de Países Disponibles

```http
GET https://app.dropkiller.com/dashboard/adskiller
```

**Respuesta (12 países):**

| País | UUID | Código |
|------|------|--------|
| Colombia | `10ba518f-80f3-4b8e-b9ba-1a8b62d40c47` | CO |
| México | `40334494-86fc-4fc0-857a-281816247906` | MX |
| Ecuador | `1be5939b-f5b1-41ea-8546-fc72a7381c9d` | EC |
| Perú | `8e7e6e88-2a90-4a8d-b6eb-ed0975c1df59` | PE |
| Chile | `bed193de-9cda-47b7-ab21-fc4abde86bd1` | CL |
| Argentina | `e8a05443-3d9c-4a24-93f0-1d197923d1fe` | AR |
| Bolivia | `de1f3f37-ed5f-4335-b151-974932bcbd83` | BO |
| Costa Rica | `3a44b739-d1c1-4fc5-8742-ae691d09c434` | CR |
| España | `2361e5ee-f992-476c-a380-2a157e384a60` | ES |
| Paraguay | `10c184e2-c7ac-4cfb-9b7f-e24e71b7588b` | PY |
| Uruguay | `13a06d2f-67fe-4c7e-b78d-01e23e68b99e` | UY |
| Venezuela | `2109e408-9cb2-488d-8d79-1e0429691682` | VE |

**Nota:** Adskiller soporta 12 países vs 10 del Dashboard Products (añade BO, CR, UY, VE).

---

### 4.2 Búsqueda de Anuncios

```http
POST https://app.dropkiller.com/dashboard/adskiller
```

**Payload:**
```json
{
  "platform": "facebook",
  "enabled": true,
  "sortBy": "updated_at",
  "order": "desc",
  "countryId": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
  "search": "contraentrega"
}
```

**Parámetros:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `platform` | string | `"facebook"` o `"tiktok"` |
| `enabled` | boolean | Solo anuncios activos |
| `sortBy` | string | Campo para ordenar (`updated_at`, `creation_date`, etc.) |
| `order` | string | `"asc"` o `"desc"` |
| `countryId` | UUID | ID del país de la tabla anterior |
| `search` | string | Término de búsqueda |

---

### 4.3 Estructura de Respuesta (⭐ CON ANÁLISIS IA)

```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": "9777dcba-3225-4807-acf8-0a34cf796133",
        "external_ad_id": "1889921615236314",
        "creation_date": "2025-10-19T10:03:42.171Z",
        "start_date": "2025-10-19T07:00:00.000Z",
        "end_date": "2025-10-19T07:00:00.000Z",
        "last_update": "2025-10-19T10:03:42.171Z",
        "platforms": ["instagram", "facebook", "audience_network", "messenger"],
        "page_name": "Tillas colombia",
        "company_name": "Tillas colombia",
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "views": null,
        "active_time": 13626,
        "title": "",
        "description": "CONTRAENTREGA EN TODOS LOS RINCONES DE COLOMBIA! 🇨🇴...",
        "link": "http://instagram.com/tillascolombia2",
        "cta": "Visit Instagram profile",
        "videos": ["https://ads-scraper-multimedia-prod.s3.amazonaws.com/meta/videos/..."],
        "images": ["https://ads-scraper-multimedia-prod.s3.amazonaws.com/meta/images/..."],
        "url": "https://www.facebook.com/ads/library/?...",
        "page_id": "593483063839180",
        "creative_id": "1889921615236314",
        "country_id": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
        "enabled": true,
        
        "country": {
          "id": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
          "name": "Colombia",
          "code": "CO"
        },
        
        "videoAnalysis": { ... },
        "productAnalysis": { ... },
        "marketingIntelligence": { ... },
        "keywords": [ ... ],
        "salesAngles": [ ... ],
        "emotionalTriggers": [ ... ],
        "targetDemographics": [ ... ],
        "conversionTactics": [ ... ],
        "onScreenText": [ ... ]
      }
    ],
    "pagination": {
      "total": 11780,
      "page": "1",
      "limit": "30",
      "total_pages": 393,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

---

### 4.4 Análisis de Video (videoAnalysis)

```json
{
  "id": "ff538417-67d8-454f-904f-fede2c8c36d3",
  "ad_id": "9777dcba-3225-4807-acf8-0a34cf796133",
  "has_watermark": false,
  "watermark_confidence": 100,
  "watermark_description": "No aplica verificación de marca de agua para anuncios de Meta/Facebook",
  "language": "es",
  "embedding_text": "Nike Air Force 1, zapatillas deportivas, marca Nike, color blanco con verde...",
  "analysis_timestamp": "2025-10-19T10:03:42.185Z"
}
```

---

### 4.5 Análisis de Producto (productAnalysis)

```json
{
  "id": "561b7ab4-ff57-4071-bbf3-08285465f70d",
  "video_analysis_id": "ff538417-67d8-454f-904f-fede2c8c36d3",
  "name": "Nike Air Force 1",
  "brand": "Nike",
  "category": "Zapatillas deportivas",
  "variants": [],
  "benefits": ["Comodidad", "Estilo", "Durabilidad"],
  "claims": [],
  "results": [],
  "packaging_type": "caja",
  "packaging_material": "cartón",
  "color_variants": ["Blanco/Verde"],
  "materials": ["Cuero", "Goma"],
  "how_to": [],
  "applications": ["Uso diario", "Deporte casual"],
  "target_audience": "Jóvenes y adultos",
  "need_state": "Calzado cómodo y con estilo",
  "tone": "Trendy",
  "target_language": "es",
  "logos": ["Nike"],
  "price": null,
  "discount": null
}
```

---

### 4.6 Inteligencia de Marketing (marketingIntelligence)

```json
{
  "id": "574c17c4-ef42-4dcd-b54a-52897a88854f",
  "video_analysis_id": "ff538417-67d8-454f-904f-fede2c8c36d3",
  "niche": "Moda y calzado",
  "sub_niches": ["Calzado deportivo", "Sneakers", "Streetwear"],
  "value_propositions": [
    "Diseño icónico y atemporal",
    "Comodidad para uso diario",
    "Calidad y durabilidad de la marca Nike"
  ],
  "competitive_advantages": [
    "Reconocimiento de marca (Nike)",
    "Diseño icónico y atemporal",
    "Amplia disponibilidad en el mercado"
  ],
  "price_tier": "mid-range",
  "brand_personality": "Trendy, cool, urbana",
  "market_segment": "Jóvenes y adultos interesados en la moda y el deporte",
  "differentiation_strategy": "Diseño icónico y reconocimiento de marca",
  "visual_style": "Estético, moderno, enfocado en el producto",
  "narrative_approach": "Muestra del producto en diferentes ángulos",
  "pacing": "fast",
  "music_mood": "Urbana, enérgica",
  "color_palette": ["Blanco", "Verde"],
  "engagement_drivers": ["Visual appeal", "Marca reconocida", "Estilo de moda"],
  "conversion_signals": [],
  "retention_factors": []
}
```

---

### 4.7 Keywords Extraídas

```json
[
  {
    "id": "bbedec1f-7e77-4122-ac5a-8ef87407bf22",
    "marketing_intelligence_id": "574c17c4-ef42-4dcd-b54a-52897a88854f",
    "keyword": "Estilo",
    "frequency": 1,
    "context": "Atributo del producto",
    "relevance_score": 0.6
  },
  {
    "id": "62dffd26-80b8-4676-a271-20501a068981",
    "keyword": "Nike Air Force 1",
    "frequency": 1,
    "context": "Modelo de zapatillas",
    "relevance_score": 0.8
  }
]
```

---

### 4.8 Ángulos de Venta (salesAngles)

```json
[
  {
    "id": "a14536aa-1d41-4ed2-801f-3d408038deb2",
    "marketing_intelligence_id": "574c17c4-ef42-4dcd-b54a-52897a88854f",
    "angle": "Comodidad y uso diario",
    "description": "Presentar las zapatillas como una opción cómoda y versátil para el día a día",
    "effectiveness_score": 0.6
  },
  {
    "angle": "Estilo y moda",
    "description": "Énfasis en el diseño y la apariencia de las zapatillas como un complemento de moda",
    "effectiveness_score": 0.7
  }
]
```

---

### 4.9 Triggers Emocionales (emotionalTriggers)

```json
[
  {
    "id": "6d82aca3-f993-46a2-a29f-71cba5435602",
    "trigger": "Pertenencia",
    "emotion": "Identificación con la cultura urbana y el streetwear",
    "intensity": "medium"
  },
  {
    "trigger": "Deseo",
    "emotion": "Aspiración a la moda y al estilo",
    "intensity": "medium"
  }
]
```

---

### 4.10 Demografía Target (targetDemographics)

```json
[
  {
    "id": "340e87ae-ba77-4c4d-8ccf-95531d00ddbf",
    "age_range": "15-35",
    "gender": "Unisex",
    "income_level": "Medio",
    "lifestyle": ["Urbano", "Activo", "Interesado en la moda"],
    "interests": ["Moda", "Deporte", "Música", "Cultura urbana"],
    "pain_points": [
      "Buscar calzado cómodo y con estilo",
      "Estar a la moda",
      "Encontrar productos de calidad y duraderos"
    ]
  }
]
```

---

### 4.11 Tácticas de Conversión (conversionTactics)

```json
[
  {
    "id": "f022215e-05f9-43c1-a871-5e5cdc20566d",
    "tactic": "Precio promocional",
    "description": "Se ofrece un precio reducido para impulsar la compra",
    "urgency_level": "low"
  },
  {
    "tactic": "Envío gratis",
    "description": "Se elimina el costo de envío para facilitar la decisión de compra",
    "urgency_level": "low"
  }
]
```

---

### 4.12 Texto en Pantalla OCR (onScreenText)

```json
[
  {
    "id": "a3ed72d8-ab9e-4c8a-ae14-a571ed3d0ba3",
    "product_analysis_id": "561b7ab4-ff57-4071-bbf3-08285465f70d",
    "text": "AIR",
    "t_start_s": 0.03,
    "t_end_s": 0.04,
    "x": 712,
    "y": 687,
    "width": 63,
    "height": 39
  }
]
```

---

### 4.13 Modal de Analytics por Anuncio

```http
GET https://app.dropkiller.com/dashboard/adskiller?analytics={ad_id}
```

**Ejemplo:**
```
https://app.dropkiller.com/dashboard/adskiller?analytics=9777dcba-3225-4807-acf8-0a34cf796133
```

**Muestra:**
- Información del advertiser
- Rango de fechas del anuncio
- País y plataformas
- Demografía (edad, ingresos, estilo de vida)
- Intereses de la audiencia
- Pain points (generados por IA)
- Ángulos de venta (generados por IA)
- Likes y duplicados
- Video descargable del creativo

---

## 5. Flujo de Integración Recomendado

### Opción A: Usando Dashboard DropKiller (Productos)

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

### Opción C: Research de Creativos con Adskiller

```
1. Ir a app.dropkiller.com/dashboard/adskiller
2. Seleccionar país y plataforma (facebook/tiktok)
3. Buscar por keyword (ej: "contraentrega", "envío gratis")
4. Analizar:
   - productAnalysis → Qué producto están vendiendo
   - marketingIntelligence → Nicho, propuestas de valor
   - salesAngles → Cómo lo están vendiendo
   - targetDemographics → A quién le venden
5. Click en modal de analytics para ver detalles completos
6. Descargar video creativo para inspiración
```

---

## 6. Cálculos Clave

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

## 7. Notas Importantes

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

### Adskiller
- ✅ **11,780+ anuncios** indexados (y creciendo)
- ✅ Análisis completo con IA (producto, marketing, demografía)
- ✅ 12 países soportados (LATAM + España)
- ✅ Facebook + TikTok
- ✅ Videos descargables
- ✅ OCR de texto en pantalla con timestamps
- ⚠️ Requiere suscripción DropKiller
- ⚠️ Next.js RSC hace difícil capturar algunos endpoints via network

### Dropi API
- ✅ Datos de catálogo completos
- ❌ **NO expone ventas** - solo stock y precios
- ⚠️ Requiere sesión activa en Dropi

---

## 8. Autenticación

### DropKiller Dashboard/Adskiller

Usa Clerk para autenticación OAuth con Google:

```
Clerk Domain: clerk.dropkiller.com
Session Cookie: __session
JWT Header: Authorization: Bearer {jwt}
```

El JWT se puede obtener del response de sesión:
```json
{
  "response": {
    "object": "session",
    "id": "sess_...",
    "status": "active",
    "last_active_token": {
      "jwt": "eyJhbGciOiJSUzI1NiIs..."
    }
  }
}
```

**Nota:** Los endpoints del dashboard usan Server-Side Rendering (RSC) de Next.js, lo que hace que muchas respuestas vengan pre-renderizadas en lugar de como JSON puro.
