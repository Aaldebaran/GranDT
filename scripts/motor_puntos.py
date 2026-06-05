# -*- coding: utf-8 -*-
"""Motor de puntos - modelo gratis. Importable por daily.py."""
GOL       = {"ARQ":12, "DEF":9, "MED":6, "DEL":4}
RESULTADO = {"win":2, "draw":1, "loss":0}
VALLA     = {"ARQ":4, "DEF":2}

RONDAS = [
 ("R1", {"label":"Grupos j1+2", "stages":["GROUP_STAGE"], "matchdays":[1,2], "mult":1.0}),
 ("R2", {"label":"Grupos j3",   "stages":["GROUP_STAGE"], "matchdays":[3],   "mult":1.0}),
 ("R3", {"label":"Ronda de 32", "stages":["LAST_32"],     "matchdays":None,  "mult":1.25}),
 ("R4", {"label":"Octavos",     "stages":["LAST_16"],     "matchdays":None,  "mult":1.5}),
 ("R5", {"label":"Cuartos",     "stages":["QUARTER_FINALS"],"matchdays":None,"mult":1.75}),
 ("R6", {"label":"Semis+Final", "stages":["SEMI_FINALS","THIRD_PLACE","FINAL"],"matchdays":None,"mult":2.0}),
]
RONDA = dict(RONDAS)
ORDEN = [rid for rid,_ in RONDAS]

def pos_bucket(api_pos):
    p=(api_pos or "").lower()
    if "goal" in p: return "ARQ"
    if "def" in p or "back" in p: return "DEF"
    if "mid" in p: return "MED"
    return "DEL"

def matches_de_ronda(matches, r):
    out=[]
    for m in matches:
        if m.get("status")!="FINISHED": continue
        if m["stage"] not in r["stages"]: continue
        if r["matchdays"] and m.get("matchday") not in r["matchdays"]: continue
        out.append(m)
    return out

def round_completa(matches, r):
    rel=[m for m in matches if m["stage"] in r["stages"] and (not r["matchdays"] or m.get("matchday") in r["matchdays"])]
    return bool(rel) and all(m.get("status")=="FINISHED" for m in rel)

def goles_delta(scorers_prev, scorers_now):
    prev={s["player"]["id"]: s["goals"] for s in scorers_prev}
    return {s["player"]["id"]: s["goals"]-prev.get(s["player"]["id"],0) for s in scorers_now}

def resultados_por_nacion(ms):
    out={}
    for m in ms:
        h=m["homeTeam"]["name"]; a=m["awayTeam"]["name"]
        gh=m["score"]["fullTime"]["home"]; ga=m["score"]["fullTime"]["away"]
        if gh is None or ga is None: continue
        oh="win" if gh>ga else "draw" if gh==ga else "loss"
        oa="win" if ga>gh else "draw" if gh==ga else "loss"
        out.setdefault(h,[]).append((oh,ga)); out.setdefault(a,[]).append((oa,gh))
    return out

def puntos_ronda(rid, matches, scorers_prev, scorers_now, pool, equipos):
    r=RONDA[rid]; ms=matches_de_ronda(matches,r)
    delta=goles_delta(scorers_prev,scorers_now); resn=resultados_por_nacion(ms)
    res={}
    for dt,eq in equipos.items():
        total=0; lineas=[]
        for pid in eq["ids"]:
            pl=pool.get(str(pid))
            if not pl: continue
            pos=pl["pos"]; nat=pl["nat"]; pts=0; det=[]
            g=delta.get(int(pid),0)
            if g>0: pts+=g*GOL[pos]; det.append(f"{g} gol {pos} +{g*GOL[pos]}")
            for outcome,gc in resn.get(nat,[]):
                if RESULTADO[outcome]: pts+=RESULTADO[outcome]; det.append(f"{outcome} +{RESULTADO[outcome]}")
                if pos in VALLA and gc==0: pts+=VALLA[pos]; det.append(f"valla +{VALLA[pos]}")
            if str(eq.get("cap"))==str(pid) and pts: pts*=2; det.append("CAPITAN x2")
            if pts: total+=pts; lineas.append({"name":pl["name"],"nat":nat,"pos":pos,"pts":pts,"det":" / ".join(det)})
        res[dt]={"raw":total,"total":round(total*r["mult"]),"mult":r["mult"],"lineas":sorted(lineas,key=lambda x:-x["pts"])}
    return res, ms
