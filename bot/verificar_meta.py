#!/usr/bin/env python3
"""Verifica la conexión con Meta sin publicar nada. Escribe bot/estado/meta.json (sin la llave)."""
import json, os, urllib.request, urllib.parse

TOKEN = os.environ["META_TOKEN"].strip()
G = "https://graph.facebook.com"

def get(path, **params):
    params["access_token"] = TOKEN
    url = f"{G}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": json.loads(e.read().decode() or "{}").get("error", str(e))}

out = {}
out["yo"] = get("me", fields="id,name")
out["permisos"] = get("me/permissions")
out["paginas"] = get("me/accounts", fields="id,name,instagram_business_account{id,username,followers_count}")
# Lo que importa para publicar
res = {"pagina_id": None, "ig_id": None, "ig_usuario": None}
for p in out["paginas"].get("data", []):
    if "marea" in p.get("name", "").lower():
        res["pagina_id"] = p["id"]
        ig = p.get("instagram_business_account") or {}
        res["ig_id"] = ig.get("id")
        res["ig_usuario"] = ig.get("username")
out["resumen"] = res
if res["ig_id"]:
    out["ig_publicacion_limite"] = get(f"{res['ig_id']}/content_publishing_limit", fields="config,quota_usage")
    out["ig_recientes"] = get(f"{res['ig_id']}/media", fields="id,caption,media_type,timestamp,permalink", limit=10)
os.makedirs("estado", exist_ok=True)
json.dump(out, open("estado/meta.json", "w"), ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False))
