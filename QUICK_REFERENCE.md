# Product Intelligence Dropi - Quick Reference

## APIs

### Dropi (Catálogo)
```
GET https://api.dropi.co/api/products/productlist/v1/index
```
→ Lista productos con stock, precios, proveedores

### DropKiller (Ventas)
```
GET https://extension-api.dropkiller.com/api/v3/history?ids={ids}&country={code}
```
→ Historial de ventas últimos 8 días

**Parámetros:**
- `ids`: Separados por coma (ej: `1645891,2017300`)
- `country`: `CO`, `EC`, `MX`, `PA`

---

## Campos Clave

### Dropi Response
```json
{
  "id": 1645891,
  "sale_price": 30000,
  "suggested_price": 99900,
  "warehouse_product": [{"stock": 82}],
  "user": {"category_user": {"name": "VERIFICADO"}}
}
```

### DropKiller Response
```json
{
  "externalId": "1645891",
  "history": [{
    "date": "2025-12-24",
    "soldUnits": 5,
    "billing": 150000,
    "stock": 82
  }]
}
```

---

## Filtros Mínimos

| Criterio | Valor |
|----------|-------|
| Stock | ≥ 50 |
| Margen | ≥ 40% |
| Precio | $25k-$150k |
| Ventas 8d | ≥ 3 |

---

## Fórmulas

```python
margen = ((suggested_price - sale_price) / suggested_price) * 100
ventas_8d = sum(h["soldUnits"] for h in history)
```
