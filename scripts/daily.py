# -*- coding: utf-8 -*-
"""
Corre 1 vez por dia (lo dispara la GitHub Action).
1) baja partidos + tabla de goleadores
2) congela snapshots de cierre por ronda (para los goles por diferencia)
3) calcula puntos de cada ronda y escribe data/standings.json
Token: variable de entorno FOOTBALL_DATA_TOKEN.
"""
import os, sys, json, base64, datetime, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import motor_puntos as mp

TOKEN=os.environ.get("FOOTBALL_DATA_TOKEN")
if not TOKEN: sys.exit("Falta FOOTBALL_DATA_TOKEN")
BASE="https://api.football-data.org/v4"
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data"); SNAP=os.path.join(DATA,"snapshots")
os.makedirs(SNAP, exist_ok=True)

def get(path):
    req=urllib.request.Request(BASE+path, headers={"X-Auth-Token":TOKEN})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def decode_code(code):
    """code (base64 de 'id-id-...-id~capId') -> {'ids':[...],'cap':id}"""
    raw=base64.b64decode(code.strip()).decode()
    body,_,cap=raw.partition("~")
    ids=[int(x) for x in body.split("-") if x.strip().isdigit()]
    return {"ids":ids, "cap":int(cap) if cap.strip().isdigit() else None}

def equipos_para_ronda(teams_json, rid):
    """forward-fill: usa el ultimo codigo definido en o antes de rid."""
    out={}
    for dt, porronda in teams_json.items():
        code=None
        for r in mp.ORDEN:
            if r in porronda and porronda[r]: code=porronda[r]
            if r==rid: break
        if code:
            try: out[dt]=decode_code(code)
            except Exception as e: print(f"  codigo invalido de {dt} en {rid}: {e}")
    return out

def main():
    hoy=datetime.date.today().isoformat()
    matches=get("/competitions/WC/matches?season=2026")["matches"]
    scorers=get("/competitions/WC/scorers?season=2026&limit=100")["scorers"]
    json.dump(matches, open(f"{SNAP}/matches_{hoy}.json","w"), ensure_ascii=False)
    json.dump(scorers, open(f"{SNAP}/scorers_{hoy}.json","w"), ensure_ascii=False)

    pool_path=os.path.join(DATA,"players.json")
    teams_path=os.path.join(DATA,"teams.json")
    if not os.path.exists(pool_path):
        print("Falta data/players.json (corre build_pool.py). Salgo."); return
    if not os.path.exists(teams_path):
        print("Falta data/teams.json. Salgo."); return
    pool=json.load(open(pool_path)); teams=json.load(open(teams_path))
    teams={k:v for k,v in teams.items() if not k.startswith("_")}  # ignorar comentarios _

    standings={"updated":hoy, "dts":{dt:{"total":0,"rondas":{}} for dt in teams}, "rondas":{}, "ultimo_detalle":{}}
    prev_close=[]  # tabla de goleadores al cierre de la ronda anterior
    for rid in mp.ORDEN:
        r=mp.RONDA[rid]
        finished=mp.matches_de_ronda(matches, r)
        if not finished: continue
        completa=mp.round_completa(matches, r)
        close_file=f"{SNAP}/close_{rid}.json"
        if completa and not os.path.exists(close_file):
            json.dump(scorers, open(close_file,"w"), ensure_ascii=False)  # congelar
        scorers_now=json.load(open(close_file)) if os.path.exists(close_file) else scorers
        equipos=equipos_para_ronda(teams, rid)
        res,_=mp.puntos_ronda(rid, matches, prev_close, scorers_now, pool, equipos)
        standings["rondas"][rid]={"label":r["label"],"mult":r["mult"],"completa":completa}
        for dt,info in res.items():
            standings["dts"][dt]["rondas"][rid]=info["total"]
            standings["dts"][dt]["total"]+=info["total"]
            standings["ultimo_detalle"][dt]=info["lineas"][:8]
        if os.path.exists(close_file): prev_close=scorers_now
    standings["tabla"]=sorted(([dt,d["total"]] for dt,d in standings["dts"].items()), key=lambda x:-x[1])
    json.dump(standings, open(os.path.join(DATA,"standings.json"),"w"), ensure_ascii=False, indent=1)
    print(f"[{hoy}] standings.json actualizado. Partidos finalizados: {sum(1 for m in matches if m['status']=='FINISHED')}")
    print("Tabla:", standings["tabla"])

if __name__=="__main__": main()
