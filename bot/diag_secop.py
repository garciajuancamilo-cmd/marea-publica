import json, os, urllib.request, urllib.parse
B="https://www.datos.gov.co/resource/p6dx-8zbt.json"
T=os.environ.get("SOCRATA_APP_TOKEN","")
def q(p):
    u=B+"?"+urllib.parse.urlencode(p)
    h={"X-App-Token":T} if T else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=120) as r: return json.load(r)
    except urllib.error.HTTPError as e: return {"error":e.code,"body":e.read().decode()[:600]}
    except Exception as e: return {"error":str(e)}
out={}
out["total"]=q({"$select":"count(*)"})
out["max_pub"]=q({"$select":"max(fecha_de_publicacion_del) as m, max(fecha_de_recepcion_de) as r"})
out["dep_values"]=q({"$select":"departamento_entidad, count(*) as n","$group":"departamento_entidad","$order":"n desc","$limit":40})
out["estados_recientes"]=q({"$select":"estado_del_procedimiento, count(*) as n","$where":"fecha_de_publicacion_del >= '2026-11-01'","$group":"estado_del_procedimiento","$order":"n desc"})
out["muestra"]=q({"$where":"fecha_de_publicacion_del >= '2026-11-10'","$limit":2})
out["recepcion_futura"]=q({"$select":"count(*)","$where":"fecha_de_recepcion_de >= '2026-11-16'"})
os.makedirs("diag",exist_ok=True)
json.dump(out,open("diag/secop.json","w"),ensure_ascii=False,indent=1)
