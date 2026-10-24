
import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
API_URL = "https://fc27-market.val.run/latest"

app = FastAPI(title="FUT Trader IA FC27")


def get_market():
    request = Request(
        API_URL,
        headers={"User-Agent": "FUT-Trader-IA-FC27/1.0"}
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def get_players(data):
    players = []
    for group, items in data.get("groups", {}).items():
        for player in items:
            player["group"] = group
            players.append(player)
    return players


@app.get("/")
async def home():
    return FileResponse(ROOT / "index.html")


@app.get("/api/health")
async def health():
    try:
        data = get_market()
        return {
            "ok": True,
            "source": "FC27 community market",
            "platform": "PlayStation",
            "year": 27,
            "updated": data.get("updated")
        }
    except Exception as exc:
        return {
            "ok": False,
            "message": "No se pudo consultar el mercado",
            "detail": str(exc)[:200]
        }


@app.get("/api/search")
async def search(q: str = Query(min_length=2, max_length=80)):
    try:
        data = get_market()
        players = get_players(data)
        query = q.strip().casefold()

        matches = [
            p for p in players
            if query in str(p.get("name", "")).casefold()
        ]

        results = []
        for p in matches[:15]:
            results.append({
                "id": str(p.get("eaId", "")),
                "name": p.get("name", "Desconocido"),
                "rating": p.get("rating"),
                "position": p.get("position"),
                "version": p.get("group"),
                "price": p.get("price"),
                "updated": data.get("updated", "Hora no disponible"),
                "signal": p.get("signal"),
                "forecast": p.get("forecast"),
                "pct_7d": p.get("pct_7d")
            })

        return {
            "results": results,
            "count": len(results),
            "updated": data.get("updated"),
            "message": (
                "Sin resultados en los jugadores disponibles"
                if not results else None
            )
        }
    except Exception as exc:
        raise HTTPException(
            502,
            f"No se pudo consultar la fuente de precios: {str(exc)[:180]}"
        )


@app.get("/api/price")
async def price(id: str = Query(min_length=1, max_length=30)):
    try:
        player_id = int(id)
    except ValueError:
        raise HTTPException(400, "ID de carta inválido.")

    try:
        data = get_market()
        for player in get_players(data):
            if player.get("eaId") == player_id:
                return {
                    "id": id,
                    "name": player.get("name"),
                    "price": player.get("price"),
                    "updated": data.get("updated"),
                    "signal": player.get("signal"),
                    "forecast": player.get("forecast"),
                    "pct_7d": player.get("pct_7d")
                }

        return {
            "id": id,
            "price": None,
            "updated": data.get("updated"),
            "message": "Esta carta no está en los jugadores disponibles"
        }

    except Exception as exc:
        raise HTTPException(
            502,
            f"No se pudo actualizar el precio: {str(exc)[:180]}"
        )

