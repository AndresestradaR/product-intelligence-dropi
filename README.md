# Product Intelligence Dropi

🎯 Sistema de inteligencia de productos para identificar ganadores en dropshipping usando Dropi.

## ⚠️ IMPORTANTE PARA CLAUDE

**Antes de implementar cualquier integración con Dropi, LEE:**

1. **[🔐 DROPI_AUTH.md](docs/DROPI_AUTH.md)** - Autenticación que funciona desde servidores (headers críticos)
2. **[📡 API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - Todos los endpoints disponibles

---

## ¿Qué hace?

1. **Escanea** el catálogo completo de Dropi
2. **Filtra** por criterios objetivos (stock, margen, precio)
3. **Obtiene ventas reales** via DropKiller API
4. **Calcula scoring** con algoritmo de 12 factores
5. **Retorna** los TOP productos listos para vender

## Fuentes de Datos

| API | Datos | Auth |
|-----|-------|------|
| [Dropi](https://api.dropi.co) | Catálogo, stock, precios, órdenes | **JWT** (ver DROPI_AUTH.md) |
| [DropKiller](https://extension-api.dropkiller.com) | Ventas históricas (8d) | No |

## Documentación

| Doc | Descripción |
|-----|-------------|
| [🔐 DROPI_AUTH.md](docs/DROPI_AUTH.md) | **Login con email/password desde servidores** - Headers críticos, código Python/FastAPI completo |
| [📡 API_ENDPOINTS.md](docs/API_ENDPOINTS.md) | Todos los endpoints de Dropi, DropKiller y Adskiller |
| [🧮 SCORING_ALGORITHM.md](docs/SCORING_ALGORITHM.md) | Algoritmo de 12 factores para scoring de productos |

## Quick Start - Login Dropi

```python
import httpx

def get_dropi_headers(country="co"):
    """Headers OBLIGATORIOS para evitar 403"""
    origin = f"https://app.dropi.{country}"
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": origin,
        "Referer": f"{origin}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        # --- CRÍTICOS ---
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

# Login
response = httpx.post(
    "https://api.dropi.co/api/login",
    json={
        "email": "tu@email.com",
        "password": "tu_password",
        "white_brand_id": 1,  # Siempre 1
        "brand": "",
        "otp": None,
        "with_cdc": False
    },
    headers=get_dropi_headers()
)
data = response.json()
token = data["token"]  # JWT para usar en requests autenticados
```

## Países Soportados

| País | Código | API URL |
|------|--------|---------|
| 🇨🇴 Colombia | CO | api.dropi.co |
| 🇬🇹 Guatemala | GT | api.dropi.gt |
| 🇲🇽 México | MX | api.dropi.mx |
| 🇵🇪 Perú | PE | api.dropi.pe |
| 🇪🇨 Ecuador | EC | api.dropi.ec |
| 🇨🇱 Chile | CL | api.dropi.cl |

## Apps que Usan Esta Documentación

- **Lucid Analytics** - BI para dropshipping
- **SOC Hub** - Gestión multi-canal
- **MCP Dropi** - Servidor MCP para Claude

---

**Autor:** Andrés Estrada  
**Comunidad:** Trucos Ecomm & Drop
