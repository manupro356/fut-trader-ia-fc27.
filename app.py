import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Uses an unofficial community SDK which reads FUTBIN's public web endpoints.
# FUTBIN does not provide a public API; upstream changes may break this integration.
try:
    from futbin_sdk import FutbinClient, Platform
except Exception as exc:
    FutbinClient = None
    Platform = None
    SDK_IMPORT_ERROR = str(exc)
else:
    SDK_IMPORT_ERROR = ""

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="FUT Trader IA FC27")

@app.get("/")
async def home():
    return FileResponse(ROOT / "index.html")

@app.get("/api/health")
async def health():
    if FutbinClient is None:
        return {"ok": False, "message": "No se pudo cargar futbin-sdk", "detail": SDK_IMPORT_ERROR}
    return {"ok": True, "source": "FUTBIN community endpoints", "platform": "PlayStation/console", "year": 27}

@app.get("/api/search")
async def search(q: str = Query(min_length=2, max_length=80)):
    if FutbinClient is None:
        raise HTTPException(503, "No se pudo cargar el SDK. Revisá el log de instalación.")
    try:
        async with FutbinClient(year=27, timeout=25) as client:
            hits = await client.search_players(query=q)
        results = []
        for p in hits[:15]:
            pid = getattr(p, "futbin_id", None) or getattr(p, "id", None)
            name = getattr(p, "name", None)
            if pid is None or not name:
                continue
            price = getattr(p, "price_ps", None)
            try:
                price = int(price) if price not in (None, "", 0, "0") else None
            except (TypeError, ValueError):
                price = None
            results.append({
                "id": str(pid),
                "name": str(name),
                "rating": getattr(p, "rating", None),
                "position": getattr(p, "position", None),
                "version": getattr(p, "version", None),
                "price": price,
                "updated": "Precio consultado al buscar"
            })
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(502, f"La fuente de precios no respondió: {str(e)[:220]}")

@app.get("/api/price")
async def price(id: str = Query(min_length=1, max_length=30)):
    if FutbinClient is None:
        raise HTTPException(503, "No se pudo cargar el SDK. Revisá el log de instalación.")
    try:
        player_id = int(id)
    except ValueError:
        raise HTTPException(400, "ID de carta inválido.")
    try:
        async with FutbinClient(year=27, timeout=25) as client:
            result = await client.get_player_price(player_id, Platform.PS)
        value = getattr(result, "price", None)
        if value is None:
            return {"id": id, "price": None, "updated": "Precio no disponible"}
        return {"id": id, "price": int(value), "updated": "Consulta reciente"}
    except Exception as e:
        raise HTTPException(502, f"No se pudo actualizar el precio: {str(e)[:220]}")

# Keep the app self-contained and serve the frontend from the same origin.
