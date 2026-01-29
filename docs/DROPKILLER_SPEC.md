# 🔍 Buscador de Productos - Especificación DropKiller

## Objetivo
Crear un buscador de productos ganadores que se conecte a DropKiller para obtener datos de ventas, stock y métricas de productos de dropshipping en LATAM.

---

## API de DropKiller (Dashboard)

### Endpoint Principal - Búsqueda de Productos
```http
GET https://app.dropkiller.com/dashboard/products?{params}
```

**Requiere autenticación:** Cookie de sesión de DropKiller (usuario debe tener suscripción activa)

### Query Parameters

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `platform` | string | Plataforma de dropshipping | `dropi`, `easydrop`, `aliclick` |
| `country` | UUID | ID del país | `65c75a5f-0c4a-45fb-8c90-5b538805a15a` |
| `limit` | number | Productos por página | `50` |
| `page` | number | Número de página | `1` |
| `s7min` | number | Ventas 7 días mínimo | `10` |
| `s7max` | number | Ventas 7 días máximo | `100` |
| `s30min` | number | Ventas 30 días mínimo | `50` |
| `s30max` | number | Ventas 30 días máximo | `500` |
| `f7min` | number | Facturación 7 días mínimo (COP) | `100000` |
| `f7max` | number | Facturación 7 días máximo (COP) | `5000000` |
| `f30min` | number | Facturación 30 días mínimo | `500000` |
| `f30max` | number | Facturación 30 días máximo | `20000000` |
| `stock-min` | number | Stock mínimo | `50` |
| `stock-max` | number | Stock máximo | `1000` |
| `price-min` | number | Precio mínimo | `25000` |
| `price-max` | number | Precio máximo | `150000` |
| `creation-date` | string | Rango de fechas | `2025-12-01/2025-12-30` |

**Ejemplo de URL completa:**
```
https://app.dropkiller.com/dashboard/products?platform=dropi&country=65c75a5f-0c4a-45fb-8c90-5b538805a15a&limit=50&page=1&s7min=10&stock-min=50&price-min=25000&price-max=150000
```

---

### IDs de Países (UUIDs)

```typescript
const COUNTRY_IDS = {
  colombia: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
  ecuador: '82811e8b-d17d-4ab9-847a-fa925785d566',
  mexico: '98993bd0-955a-4fa3-9612-c9d4389c44d0',
  chile: 'ad63080c-908d-4757-9548-30decb082b7e',
  spain: '3f18ae66-2f98-4af1-860e-53ed93e5cde0',
  peru: '6acfee32-9c25-4f95-b030-a005e488f3fb',
  panama: 'c1f01c6a-99c7-4253-b67f-4e2607efae9e',
  paraguay: 'f2594db9-caee-4221-b4a6-9b6267730a2d',
  argentina: 'de93b0dd-d9d3-468d-8c44-e9780799a29f',
  guatemala: '77c15189-b3b9-4f55-9226-e56c231f87ac',
} as const;
```

---

### Plataformas Soportadas

| Plataforma | Valor | Países Disponibles |
|------------|-------|-------------------|
| Dropi | `dropi` | AR, CL, CO, EC, ES, GT, MX, PA, PY, PE |
| Easydrop | `easydrop` | CL, EC, MX, PE |
| Aliclick | `aliclick` | PE |
| Dropea | `dropea` | ES |
| Droplatam | `droplatam` | CL, CO, EC, ES, MX, PA, PY, PE |
| Seventy Block | `seventy block` | CO |
| Wimpy | `wimpy` | CO, MX |
| Mastershop | `mastershop` | CO |

---

### Endpoint de Detalle de Producto

```http
GET https://app.dropkiller.com/dashboard/tracking/detail/{product_uuid}?platform=dropi
```

**Respuesta incluye:**
- Gráfico de ventas diarias (30 días)
- Total de ventas
- Promedio diario
- Facturación total
- Historial de stock
- URL del producto en la plataforma origen

---

## Implementación Sugerida

### Opción 1: Web Scraping con Puppeteer/Playwright
Como DropKiller requiere autenticación por cookies, se puede hacer scraping:

```typescript
// Pseudocódigo
import { chromium } from 'playwright';

async function scrapeDropKiller(filters: ProductFilters) {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  
  // Cargar cookies de sesión del usuario
  await context.addCookies(userCookies);
  
  const page = await context.newPage();
  const url = buildDropKillerUrl(filters);
  await page.goto(url);
  
  // Extraer datos de la tabla de productos
  const products = await page.evaluate(() => {
    // Parsear la tabla de productos
  });
  
  return products;
}
```

### Opción 2: Interceptar API calls
DropKiller hace llamadas a su backend. Se puede interceptar:

```typescript
page.on('response', async (response) => {
  if (response.url().includes('/api/products')) {
    const data = await response.json();
    // Procesar datos
  }
});
```

---

## Estructura de Datos Esperada

```typescript
interface Product {
  id: string;
  externalId: string;          // ID en Dropi/plataforma
  name: string;
  image: string;
  price: number;
  stock: number;
  sales7d: number;             // Ventas últimos 7 días
  sales30d: number;            // Ventas últimos 30 días
  revenue7d: number;           // Facturación 7 días
  revenue30d: number;          // Facturación 30 días
  platform: string;            // dropi, easydrop, etc.
  country: string;
  url: string;                 // Link al producto
  createdAt: Date;
  dailySales?: number[];       // Array de ventas por día (30 días)
}

interface ProductFilters {
  platform?: string;
  country?: string;
  minSales7d?: number;
  maxSales7d?: number;
  minSales30d?: number;
  maxSales30d?: number;
  minStock?: number;
  maxStock?: number;
  minPrice?: number;
  maxPrice?: number;
  dateRange?: { from: string; to: string };
  page?: number;
  limit?: number;
}
```

---

## UI Requerida

Crear una interfaz con:

1. **Filtros:**
   - Selector de país (dropdown)
   - Selector de plataforma (dropdown)
   - Rango de ventas 7d (slider o inputs)
   - Rango de ventas 30d (slider o inputs)
   - Rango de precio (slider o inputs)
   - Rango de stock (slider o inputs)

2. **Tabla de resultados:**
   - Imagen del producto
   - Nombre
   - Precio
   - Ventas 7d / 30d
   - Stock
   - Link a producto

3. **Acciones:**
   - Ver detalle (gráfico de ventas)
   - Copiar link
   - Agregar a favoritos

---

## Notas de Autenticación

- El usuario debe tener suscripción activa en DropKiller
- Se necesita manejar las cookies de sesión
- Opciones:
  1. Usuario pega sus cookies manualmente
  2. OAuth si DropKiller lo soporta (investigar)
  3. Extension de Chrome que capture las cookies

---

## Stack Sugerido

- **Backend:** Node.js/TypeScript con Playwright para scraping
- **Frontend:** Next.js o React
- **Base de datos:** PostgreSQL para cachear productos
- **Cache:** Redis para rate limiting y cache de búsquedas
