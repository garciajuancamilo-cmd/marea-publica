#!/usr/bin/env python3
"""Publica en Instagram y Facebook lo que esté en bot/cola/ con aprobado=true y hora cumplida.

Modo prueba (PRUEBA=1): crea los contenedores de Instagram y valida las imágenes, pero NO publica.
Registra cada publicación en bot/publicado/<id>.json para no repetirla.
"""
import datetime as dt, glob, json, os, sys, time, urllib.parse, urllib.request

G = "https://graph.facebook.com/v21.0"
TOKEN = os.environ["META_TOKEN"].strip()
PRUEBA = os.environ.get("PRUEBA") == "1"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLA, HECHO = os.path.join(RAIZ, "bot", "cola"), os.path.join(RAIZ, "bot", "publicado")

def api(metodo, ruta, token=TOKEN, **params):
    params["access_token"] = token
    data = urllib.parse.urlencode(params, doseq=True).encode()
    url = f"{G}/{ruta}"
    req = urllib.request.Request(url if metodo == "POST" else url + "?" + data.decode(),
                                 data=data if metodo == "POST" else None, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{metodo} {ruta}: {e.read().decode()[:500]}")

def ids():
    pags = api("GET", "me/accounts", fields="id,name,access_token,instagram_business_account")["data"]
    p = next(x for x in pags if "marea" in x["name"].lower())
    return p["id"], p["access_token"], p["instagram_business_account"]["id"]

def esperar(cid):
    for _ in range(40):
        s = api("GET", cid, fields="status_code,status")
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Contenedor {cid}: {s}")
        time.sleep(5)
    raise RuntimeError(f"Contenedor {cid} no terminó")

def instagram(ig, e):
    if e["tipo"] == "carrusel":
        hijos = []
        for u in e["imagenes"]:
            hijos.append(api("POST", f"{ig}/media", image_url=u, is_carousel_item="true")["id"])
        for h in hijos:
            esperar(h)
        cid = api("POST", f"{ig}/media", media_type="CAROUSEL", children=",".join(hijos), caption=e["caption"])["id"]
    elif e["tipo"] == "reel":
        cid = api("POST", f"{ig}/media", media_type="REELS", video_url=e["video"], caption=e["caption"],
                  share_to_feed="true")["id"]
    else:
        cid = api("POST", f"{ig}/media", image_url=e["imagenes"][0], caption=e["caption"])["id"]
    esperar(cid)
    if PRUEBA:
        return {"contenedor": cid, "prueba": True}
    m = api("POST", f"{ig}/media_publish", creation_id=cid)
    link = api("GET", m["id"], fields="permalink").get("permalink")
    return {"media_id": m["id"], "permalink": link}

def facebook(pid, ptoken, e):
    if PRUEBA:  # sube una foto sin publicar para validar el permiso de la página
        if e["tipo"] == "reel":
            return {"prueba": True}
        f = api("POST", f"{pid}/photos", token=ptoken, url=e["imagenes"][0], published="false")["id"]
        return {"prueba": True, "foto_sin_publicar": f}
    if e["tipo"] == "reel":
        r = api("POST", f"{pid}/videos", token=ptoken, file_url=e["video"], description=e["caption"])
        return {"video_id": r.get("id")}
    fotos = [api("POST", f"{pid}/photos", token=ptoken, url=u, published="false")["id"] for u in e["imagenes"]]
    params = {f"attached_media[{i}]": json.dumps({"media_fbid": f}) for i, f in enumerate(fotos)}
    r = api("POST", f"{pid}/feed", token=ptoken, message=e["caption"], **params)
    return {"post_id": r.get("id")}

def main():
    os.makedirs(HECHO, exist_ok=True)
    ahora = dt.datetime.now(dt.timezone.utc)
    pendientes = []
    for f in sorted(glob.glob(os.path.join(COLA, "*.json"))):
        e = json.load(open(f, encoding="utf-8"))
        if os.path.exists(os.path.join(HECHO, e["id"] + ".json")) or not e.get("aprobado"):
            continue
        cuando = dt.datetime.fromisoformat(e["publicar_en"].replace("Z", "+00:00"))
        if PRUEBA or cuando <= ahora:
            pendientes.append((cuando, e))
    pendientes.sort(key=lambda x: x[0])
    if not pendientes:
        print("Nada para publicar"); return
    pid, ptoken, ig = ids()
    errores = 0
    for _, e in pendientes:
        res = {"id": e["id"], "fecha": ahora.isoformat()}
        for red in e["redes"]:
            try:
                res[red] = instagram(ig, e) if red == "instagram" else facebook(pid, ptoken, e)
                print(e["id"], red, "OK", res[red])
            except Exception as ex:
                errores += 1
                res[red] = {"error": str(ex)}
                print(e["id"], red, "ERROR", ex)
        if not PRUEBA:
            json.dump(res, open(os.path.join(HECHO, e["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
        else:
            os.makedirs(os.path.join(RAIZ, "estado"), exist_ok=True)
            json.dump(res, open(os.path.join(RAIZ, "estado", e["id"] + ".json"), "w"), ensure_ascii=False, indent=1)
        time.sleep(20)
    if errores:
        sys.exit(1)

if __name__ == "__main__":
    main()
