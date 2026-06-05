# -*- coding: utf-8 -*-
"""
Construye data/players.json (el pool del armador) UNA vez, cuando esten las listas de 26.
Baja el plantel de cada seleccion del Mundial 2026 (posicion + id por jugador).
Precio: arranca con un valor por defecto + una tabla curada para los nombres conocidos.
Los precios son EDITABLES a mano en data/players.json (es la unica parte no automatica del modelo gratis).
Token: variable de entorno FOOTBALL_DATA_TOKEN.
Uso:   python scripts/build_pool.py            (todas las selecciones)
       python scripts/build_pool.py 8          (solo 8, para probar rapido)
"""
import os, sys, json, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from motor_puntos import pos_bucket

TOKEN=os.environ.get("FOOTBALL_DATA_TOKEN")
if not TOKEN: sys.exit("Falta FOOTBALL_DATA_TOKEN")
BASE="https://api.football-data.org/v4"
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data")

# Precios curados por nombre (editables). Lo que no figure: PRECIO_DEFAULT segun posicion.
PRECIO_DEFAULT={"ARQ":3.0,"DEF":3.0,"MED":3.5,"DEL":4.0}
CURADOS={
 "Kylian Mbappé":12.0,"Erling Haaland":11.0,"Lamine Yamal":10.5,"Vinícius Júnior":10.0,
 "Jude Bellingham":10.5,"Harry Kane":9.5,"Pedri":8.5,"Rodri":8.0,"Florian Wirtz":8.0,
 "Jamal Musiala":8.5,"Bukayo Saka":8.0,"Phil Foden":8.0,"Federico Valverde":7.0,
 "Rodrygo":7.5,"Bruno Fernandes":7.0,"Rafael Leão":7.0,"Julián Álvarez":8.0,
 "Lautaro Martínez":7.5,"Alexis Mac Allister":7.0,"Enzo Fernández":6.5,"Achraf Hakimi":7.0,
 "Virgil van Dijk":6.0,"William Saliba":6.5,"Antonio Rüdiger":5.5,"Rúben Dias":5.5,
 "Emiliano Martínez":6.5,"Alisson":6.0,"Thibaut Courtois":5.5,"Gianluigi Donnarumma":5.5,
 "Cody Gakpo":5.5,"Victor Osimhen":7.0,"Christian Pulisic":5.0,"Pau Cubarsí":6.0,
}

def get(path, tries=4):
    for i in range(tries):
        try:
            req=urllib.request.Request(BASE+path, headers={"X-Auth-Token":TOKEN})
            with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code==429:  # rate limit: esperar y reintentar
                time.sleep(12); continue
            raise
    raise SystemExit("Demasiados 429, reintentar mas tarde")

def team_ids():
    p=os.path.join(DATA,"matches_seed.json")
    matches=None
    if os.path.exists(p): matches=json.load(open(p))
    if not matches:
        matches=get("/competitions/WC/matches?season=2026")["matches"]
        json.dump(matches, open(p,"w"), ensure_ascii=False)
    ids={}
    for m in matches:
        for side in ("homeTeam","awayTeam"):
            t=m[side]
            if t.get("id"): ids[t["id"]]=t["name"]
    return ids

def main():
    limit=int(sys.argv[1]) if len(sys.argv)>1 else None
    ids=team_ids()
    items=list(ids.items())
    if limit: items=items[:limit]
    pool={}
    for n,(tid,tname) in enumerate(items,1):
        try: d=get(f"/teams/{tid}")
        except SystemExit as e: print(e); break
        squad=d.get("squad",[])
        for pl in squad:
            pos=pos_bucket(pl.get("position"))
            precio=CURADOS.get(pl["name"], PRECIO_DEFAULT[pos])
            pool[str(pl["id"])]={"id":pl["id"],"name":pl["name"],"nat":tname,"pos":pos,"price":precio}
        print(f"  [{n}/{len(items)}] {tname}: {len(squad)} jugadores")
        time.sleep(7)  # respetar 10 req/min
    json.dump(pool, open(os.path.join(DATA,"players.json"),"w"), ensure_ascii=False, indent=0)
    from collections import Counter
    print(f"\nPool guardado: {len(pool)} jugadores")
    print("Por posicion:", dict(Counter(p['pos'] for p in pool.values())))

if __name__=="__main__": main()
