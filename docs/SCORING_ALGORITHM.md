# Algoritmo de Scoring - Product Intelligence

## Objetivo

Identificar productos ganadores en Dropi usando un sistema de puntuación de 12 factores.

---

## Criterios Mínimos (Filtros Duros)

Antes de aplicar scoring, los productos deben cumplir:

| Criterio | Valor Mínimo | Fuente |
|----------|--------------|--------|
| Ventas últimos 8 días | ≥ 3 | DropKiller API |
| Stock disponible | ≥ 50 unidades | Dropi API |
| Margen bruto | ≥ 40% | Calculado |
| Precio de venta | $25,000 - $150,000 COP | Dropi API |
| Antigüedad en catálogo | ≥ 14 días | Dropi API |

---

## Sistema de Scoring (100 puntos máximo)

### Factores de Demanda (40 puntos)

| Factor | Peso | Cálculo |
|--------|------|--------|
| Ventas 8d | 20 pts | Escala logarítmica, max en 50+ ventas |
| Tendencia ventas | 10 pts | Comparar días 1-4 vs 5-8 |
| Consistencia | 10 pts | Días con ventas / 8 días |

### Factores Financieros (30 puntos)

| Factor | Peso | Cálculo |
|--------|------|--------|
| Margen % | 15 pts | >60% = 15pts, 40-60% escala lineal |
| Precio óptimo | 10 pts | $50k-$100k = max, degradar fuera |
| ROI estimado | 5 pts | (margen * ventas) / inversión |

### Factores Operativos (20 puntos)

| Factor | Peso | Cálculo |
|--------|------|--------|
| Stock saludable | 10 pts | 100-500 = max, menos de 50 = 0 |
| Proveedor verificado | 5 pts | VERIFICADO/PREMIUM = 5pts |
| Múltiples bodegas | 5 pts | más de 1 bodega = 5pts |

### Factores de Competencia (10 puntos)

| Factor | Peso | Cálculo |
|--------|------|--------|
| Competencia Meta Ads | 10 pts | menos de 40 anunciantes = 10pts (requiere API externa) |

---

## Fórmula Final

```
SCORE = (Demanda * 0.4) + (Financiero * 0.3) + (Operativo * 0.2) + (Competencia * 0.1)
```

---

## Categorías de Resultado

| Score | Categoría | Recomendación |
|-------|-----------|---------------|
| 80-100 | 🏆 Ganador | Lanzar inmediatamente |
| 60-79 | ✅ Prometedor | Probar con presupuesto bajo |
| 40-59 | ⚠️ Riesgoso | Solo si tienes experiencia en el nicho |
| 0-39 | ❌ Evitar | No vale la pena |

---

## Notas de Implementación

1. **Sin datos de Meta Ads:** Si no hay API de competencia, asignar 5/10 puntos por defecto
2. **Productos nuevos:** Si tienen menos de 8 días de historial, extrapolar ventas
3. **Stock adjustment:** Ignorar días donde `stockAdjustment = true` para cálculo de ventas
