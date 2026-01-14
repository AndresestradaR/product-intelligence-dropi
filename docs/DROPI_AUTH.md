# Dropi Authentication - Guía Definitiva

## ⚠️ PROBLEMA CRÍTICO: Bloqueo de IPs

Dropi **bloquea requests desde IPs de datacenters** (AWS, Railway, Render, etc.) con error 403.

**Solución que SÍ funciona:** Usar headers completos que simulan un navegador real.

---

## URLs por País

```python
DROPI_API_URLS = {
    "co": "https://api.dropi.co",
    "gt": "https://api.dropi.gt",
    "mx": "https://api.dropi.mx",
    "cl": "https://api.dropi.cl",
    "pe": "https://api.dropi.pe",
    "ec": "https://api.dropi.ec",
}
```

---

## White Brand IDs

```python
WHITE_BRAND_IDS = {
    "co": 1,  # Colombia usa 1
    "gt": 1,
    "mx": 1,
    "cl": 1,
    "pe": 1,
    "ec": 1,
}
```

**Nota:** El hash largo `df3e6b0bb66ceaadca4f84cbc371fd66e04d20fe51fc414da8d1b84d31d178de` que aparece en algunos docs es para white labels específicos. Para Dropi estándar usar `1`.

---

## Headers Completos (CRÍTICO)

Estos headers son **obligatorios** para evitar el 403:

```python
def get_dropi_headers(token: str = None, country: str = "co"):
    """Headers completos - PROBADOS Y FUNCIONANDO"""
    origin = f"https://app.dropi.{country}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": origin,
        "Referer": f"{origin}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        # --- ESTOS SON CRÍTICOS ---
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
```

---

## Login Endpoint

```http
POST https://api.dropi.{country}/api/login
```

### Payload

```json
{
    "email": "usuario@ejemplo.com",
    "password": "contraseña",
    "white_brand_id": 1,
    "brand": "",
    "otp": null,
    "with_cdc": false
}
```

### Respuesta Exitosa

```json
{
    "isSuccess": true,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "objects": {
        "id": 668470,
        "name": "Juan",
        "surname": "Pérez",
        "email": "usuario@ejemplo.com",
        "walletId": 12345
    },
    "wallets": [
        {
            "id": 12345,
            "amount": 1234567.89,
            "currency": "COP"
        }
    ]
}
```

---

## Código Python Completo (Funciona en Railway)

```python
import asyncio
import httpx

DROPI_API_URLS = {
    "co": "https://api.dropi.co",
    "gt": "https://api.dropi.gt",
    "mx": "https://api.dropi.mx",
}

def get_dropi_headers(country: str = "co"):
    origin = f"https://app.dropi.{country}"
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": origin,
        "Referer": f"{origin}/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }


async def dropi_login(email: str, password: str, country: str = "co") -> dict:
    """
    Login en Dropi - FUNCIONA DESDE SERVIDORES
    
    Returns:
        {
            "success": True,
            "token": "jwt...",
            "user_id": "668470",
            "user_name": "Juan Pérez",
            "wallet_balance": 1234567.89
        }
    """
    api_url = DROPI_API_URLS.get(country, DROPI_API_URLS["co"])
    
    payload = {
        "email": email,
        "password": password,
        "white_brand_id": 1,
        "brand": "",
        "otp": None,
        "with_cdc": False
    }
    
    try:
        async with asyncio.timeout(15):
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
                response = await client.post(
                    f"{api_url}/api/login",
                    json=payload,
                    headers=get_dropi_headers(country=country)
                )
                
                data = response.json()
                
                if data.get("isSuccess") and data.get("token"):
                    user_data = data.get("objects", {})
                    
                    # Extraer wallet balance
                    wallet_balance = 0
                    wallets = data.get("wallets") or user_data.get("wallets")
                    if wallets and isinstance(wallets, list) and len(wallets) > 0:
                        first_wallet = wallets[0]
                        if isinstance(first_wallet, dict):
                            try:
                                wallet_balance = float(str(first_wallet.get("amount", 0)).replace(",", ""))
                            except:
                                pass
                    
                    return {
                        "success": True,
                        "token": data["token"],
                        "user_id": str(user_data.get("id", "")),
                        "user_name": f"{user_data.get('name', '')} {user_data.get('surname', '')}".strip(),
                        "user_email": user_data.get("email", email),
                        "wallet_balance": wallet_balance,
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Login failed"),
                        "status_code": response.status_code
                    }
                    
    except asyncio.TimeoutError:
        return {"success": False, "error": "Dropi no responde (timeout 15s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Endpoint FastAPI Completo

```python
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

router = APIRouter()

class DropiLoginRequest(BaseModel):
    email: str
    password: str
    country: str = "co"

@router.post("/login")
async def login_dropi(
    channel_id: int = Query(...),
    credentials: DropiLoginRequest = None,
    email: str = Query(None),
    password: str = Query(None),
    country: str = Query("co")
):
    """Login en Dropi con email/password"""
    user_email = credentials.email if credentials else email
    user_password = credentials.password if credentials else password
    user_country = credentials.country if credentials else country
    
    if not user_email or not user_password:
        raise HTTPException(status_code=400, detail="Email y password requeridos")
    
    result = await dropi_login(user_email, user_password, user_country)
    
    if not result.get("success"):
        return {"success": False, "error": result.get("error")}
    
    # Guardar token en BD...
    
    return {
        "success": True,
        "message": "✅ Dropi conectado",
        "user_id": result.get("user_id"),
        "user_name": result.get("user_name"),
        "wallet_balance": result.get("wallet_balance")
    }
```

---

## Frontend (JavaScript)

```javascript
async function connectDropi(email, password, country = 'co') {
    const response = await fetch(`${API_BASE}/dropi/auth/login?channel_id=4&country=${country}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, country })
    });
    
    const data = await response.json();
    
    if (data.success) {
        console.log('✅ Conectado:', data.user_name);
        return data;
    } else {
        console.error('❌ Error:', data.error);
        throw new Error(data.error);
    }
}
```

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 403 Forbidden | Faltan headers Sec-* | Usar `get_dropi_headers()` completo |
| 403 Forbidden | IP bloqueada | Verificar headers, NO hay solución de proxy |
| "Invalid credentials" | Email/password incorrectos | Verificar credenciales en app.dropi.co |
| Timeout | Dropi lento | Aumentar timeout a 15s |
| CORS error | Request desde frontend directo | Hacer request desde backend |

---

## Apps que Usan Esta Implementación

1. **Lucid Analytics** - `lucid-analytics/backend/routers/dropi.py`
2. **SOC Hub** - `soc-hub/app/api/v1/endpoints/dropi_auth.py`
3. **MCP Dropi** - Servidor MCP para Claude

---

## Checklist de Implementación

- [ ] Usar `white_brand_id: 1` (no el hash largo)
- [ ] Incluir TODOS los headers Sec-*
- [ ] Origin y Referer deben coincidir con el país
- [ ] Timeout mínimo de 10-15 segundos
- [ ] Extraer wallet de `wallets[0].amount`
- [ ] Manejar respuesta `isSuccess: true` + `token`

---

*Última actualización: Enero 2026*
*Probado en: Railway, Vercel, localhost*
