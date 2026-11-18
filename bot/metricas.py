#!/usr/bin/env python3
"""Lee métricas de lo publicado (bot/publicado/) en Instagram y Facebook. No publica nada.
Escribe estado/metricas.json."""
import datetime as dt, glob, json, os, urllib.parse, urllib.request

TOKEN = os.environ["META_TOKEN"].strip()
G = "https://graph.facebook.com/v21.0"

def get(path, token=TOKEN, **params):
    params["access_token"] = token
    try:
        with urllib.request.urlopen(f"{G}/{path}?{urllib.parse.urlencode(params)}", timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try: return {"error": json.loads(e.read().decode()).get("error", {}).get("message")}
        except Exception: return {"error": str(e)}

pags = get("me/accounts", fields="id,name,access_token,instagram_business_account{id,username,followers_count}").get("data", [])
p = next(x for x in pags if "marea" in x["name"].lower())
pid, ptok, ig = p["id"], p["access_token"], p["instagram_business_account"]
out = {"fecha": dt.datetime.now(dt.timezone.utc).isoformat(), "ig_usuario": ig.get("username"),
       "ig_seguidores": ig.get("followers_count"), "fb_pagina": p["name"], "piezas": {}}
out["fb_seguidores"] = get(pid, token=ptok, fields="followers_count,fan_count")

IG_MET = ["reach", "views", "impressions", "likes", "comments", "saved", "shares", "total_interactions",
          "profile_visits", "follows", "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
FB_MET = ["post_impressions", "post_impressions_unique", "post_clicks", "post_video_views", "post_video_views_unique"]

for f in sorted(glob.glob("bot/publicado/*.json")):
    r = json.load(open(f))
    d = {"publicado": r.get("fecha")}
    m = (r.get("instagram") or {}).get("media_id")
    if m:
        d["ig"] = {"permalink": r["instagram"].get("permalink")}
        d["ig"].update({k: v for k, v in get(m, fields="like_count,comments_count,media_type,timestamp").items()})
        for met in IG_MET:  # una por una: si alguna no aplica al formato, no tumba las demás
            x = get(f"{m}/insights", metric=met)
            if "data" in x and x["data"]:
                d["ig"][met] = x["data"][0]["values"][0]["value"]
    fb = r.get("facebook") or {}
    fid = fb.get("post_id") or fb.get("video_id")
    if fid:
        d["fb"] = {"id": fid}
        base = get(fid, token=ptok, fields="shares,comments.summary(true).limit(0),reactions.summary(true).limit(0)")
        d["fb"]["compartidos"] = (base.get("shares") or {}).get("count", 0)
        d["fb"]["comentarios"] = ((base.get("comments") or {}).get("summary") or {}).get("total_count")
        d["fb"]["reacciones"] = ((base.get("reactions") or {}).get("summary") or {}).get("total_count")
        if "error" in base: d["fb"]["error"] = base["error"]
        for met in FB_MET:
            x = get(f"{fid}/insights", token=ptok, metric=met)
            if "data" in x and x["data"]:
                d["fb"][met] = x["data"][0]["values"][0]["value"]
    out["piezas"][r["id"]] = d

# Cuenta de Instagram, últimos días
for met in ["profile_views", "reach", "follower_count", "website_clicks", "accounts_engaged"]:
    x = get(f"{ig['id']}/insights", metric=met, period="day", metric_type="total_value")
    if "data" not in x:
        x = get(f"{ig['id']}/insights", metric=met, period="day")
    out.setdefault("ig_cuenta", {})[met] = x.get("data", x)

os.makedirs("estado", exist_ok=True)
json.dump(out, open("estado/metricas.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "ig_cuenta"}, ensure_ascii=False)[:3000])
