import json, unicodedata
from pathlib import Path
from urllib.request import Request, urlopen
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parent
API_URL = "https://fc27-market.val.run/latest"
app = FastAPI(title="FUT Trader IA FC27")

def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "").casefold().strip())
    return "".join(c for c in s if not unicodedata.combining(c))

def market():
    req = Request(API_URL, headers={"User-Agent":"FUT-Trader-IA-FC27/2.0", "Accept":"application/json"})
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

def players(data):
    out=[]
    groups=data.get("groups", {})
    if isinstance(groups, dict):
        for group, items in groups.items():
            if isinstance(items, list):
                for p in items:
                    if isinstance(p, dict):
                        p=dict(p); p.setdefault("group", group); out.append(p)
    if not out and isinstance(data.get("players"), list):
        out=[p for p in data["players"] if isinstance(p,dict)]
    return out

@app.get("/")
async def home():
    return FileResponse(ROOT/"index.html")

@app.get("/api/health")
async def health():
    try:
        d=market()
        return {"ok":True,"source":"FC27 community market","platform":"PlayStation","year":27,"updated":d.get("updated"),"players_available":len(players(d))}
    except Exception as e:
        return {"ok":False,"message":"No se pudo consultar el mercado","detail":str(e)[:180]}

@app.get("/api/search")
async def search(q: str = Query(min_length=2,max_length=80)):
    try:
        d=market(); ps=players(d); query=norm(q)
        found=[p for p in ps if query in norm(p.get("name",""))]
        if not found:
            terms=query.split()
            found=[p for p in ps if terms and all(t in norm(p.get("name","")) for t in terms)]
        res=[]
        for p in found[:30]:
            res.append({"id":str(p.get("eaId",p.get("id",""))),"name":p.get("name","Desconocido"),
                "rating":p.get("rating"),"position":p.get("position"),"version":p.get("group",p.get("version","")),
                "price":p.get("price"),"updated":d.get("updated"),"signal":p.get("signal"),
                "forecast":p.get("forecast"),"pct_7d":p.get("pct_7d")})
        return {"results":res,"count":len(res),"updated":d.get("updated"),"message":None if res else "Sin resultados"}
    except Exception as e:
        raise HTTPException(502,f"No se pudo consultar la fuente de precios: {str(e)[:160]}")

@app.get("/api/price")
async def price(id: str = Query(min_length=1,max_length=40)):
    try:
        d=market()
        p=next((x for x in players(d) if str(x.get("eaId",x.get("id","")))==str(id)),None)
        if not p: return {"id":id,"price":None,"updated":d.get("updated"),"message":"Carta no disponible"}
        return {"id":id,"name":p.get("name"),"price":p.get("price"),"updated":d.get("updated"),
                "signal":p.get("signal"),"forecast":p.get("forecast"),"pct_7d":p.get("pct_7d")}
    except Exception as e:
        raise HTTPException(502,f"No se pudo actualizar el precio: {str(e)[:160]}")
