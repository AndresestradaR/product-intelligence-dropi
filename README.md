# Product Intelligence Dropi

🎯 Sistema de inteligencia de productos para identificar ganadores en dropshipping usando Dropi.

## ¿Qué hace?

1. **Escanea** el catálogo completo de Dropi
2. **Filtra** por criterios objetivos (stock, margen, precio)
3. **Obtiene ventas reales** via DropKiller API
4. **Calcula scoring** con algoritmo de 12 factores
5. **Retorna** los TOP productos listos para vender

## Fuentes de Datos

| API | Datos | Auth |
|-----|-------|------|
| [Dropi](https://api.dropi.co) | Catálogo, stock, precios | No |
| [DropKiller](https://extension-api.dropkiller.com) | Ventas históricas (8d) | No |

## Documentación

- [📡 API Endpoints](docs/API_ENDPOINTS.md)
- [🧮 Algoritmo de Scoring](docs/SCORING_ALGORITHM.md)

## Quick Start

```python
# Obtener productos con ventas
import requests

# 1. Catálogo de Dropi
products = requests.get("https://api.dropi.co/api/products/productlist/v1/index").json()["objects"]

# 2. Ventas de DropKiller
ids = ",".join([str(p["id"]) for p in products[:50]])
sales = requests.get(f"https://extension-api.dropkiller.com/api/v3/history?ids={ids}&country=CO").json()
```

## Países Soportados

- 🇨🇴 Colombia (CO)
- 🇪🇨 Ecuador (EC)
- 🇲🇽 México (MX)
- 🇵🇦 Panamá (PA)

## Roadmap

- [ ] Script de escaneo automatizado
- [ ] Integración Meta Ads Library API
- [ ] Dashboard web para visualización
- [ ] Alertas de productos trending

---

**Autor:** Andrés Estrada  
**Comunidad:** Trucos Ecomm &amp; Drop
