"""
Marea Pública — motor de datos (fase 1)

Descarga de SECOP II (datos.gov.co) los agregados de contratación de la región
Caribe y genera site/data.json, el único archivo que la página necesita.

Uso:
    python etl/build_data.py                # escribe site/data.json
    SOCRATA_APP_TOKEN=xxxx python etl/build_data.py   # con token (recomendado)

No requiere librerías externas. Corre en GitHub Actions cada noche.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import defaultdict

BASE_URL = "https://www.datos.gov.co/resource/"
CONTRATOS = "jbjy-vk9h"
PROCESOS = "p6dx-8zbt"
DESDE = "2024-01-01"

DEPS = [
    "Atlántico", "Bolívar", "Cesar", "Córdoba", "La Guajira",
    "Magdalena", "Sucre", "San Andrés, Providencia y Santa Catalina",
]
DEPS_SQL = "(" + ",".join("'" + d + "'" for d in DEPS) + ")"
BASE = (f"departamento in {DEPS_SQL} AND fecha_de_firma >= '{DESDE}' "
        "AND valor_del_contrato between 1 and 1000000000000")
DIRECTA = (" AND modalidad_de_contratacion in "
           "('Contratación directa','Contratación Directa (con ofertas)')")
TRIANG = (" AND (upper(objeto_del_contrato) like '%GERENCIA INTEGRAL%' "
          "OR upper(objeto_del_contrato) like '%INTERADMINISTRATIVO%' "
          "OR upper(objeto_del_contrato) like '%AUNAR ESFUERZOS%')")

TOKEN = os.environ.get("SOCRATA_APP_TOKEN", "")
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "data.json")


# ---------------------------------------------------------------- utilidades
def q(dataset: str, params: dict, retries: int = 4) -> list:
    url = BASE_URL + dataset + ".json?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json"}
    if TOKEN:
        headers["X-App-Token"] = TOKEN
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # red inestable: reintenta con espera creciente
            if i == retries - 1:
                raise RuntimeError(f"Fallo consultando {dataset}: {e}") from e
            time.sleep(5 * (i + 1))
    return []


def q_all(dataset: str, params: dict, page: int = 50000) -> list:
    out, off = [], 0
    while True:
        rows = q(dataset, {**params, "$limit": page, "$offset": off})
        out.extend(rows)
        if len(rows) < page:
            return out
        off += page


def by_entity(select: str, extra: str = "") -> dict:
    rows = q(CONTRATOS, {"$select": "nit_entidad as k, " + select,
                         "$where": BASE + extra, "$group": "nit_entidad", "$limit": 20000})
    return {r["k"]: r for r in rows}


SMALL = r"\b(De|Del|La|Las|Los|Y|E|En|Para|Por|El|A|Al)\b"
UPPER = r"\b(Ese|E\.s\.e|Sas|S\.a\.s|Esp|E\.s\.p|Ltda|S\.a|Icbf|Sena|Edubar|Iub|Inpec|Dane|Ut)\b\.?"


def tc(s) -> str:
    s = re.sub(r"\*+", "", str(s or ""))
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"(^|[\s\-\(\./])([a-záéíóúñü])", lambda m: m.group(1) + m.group(2).upper(), s)
    s = re.sub(SMALL, lambda m: m.group(0).lower(), s)
    s = s[:1].upper() + s[1:]
    return re.sub(UPPER, lambda m: m.group(0).upper(), s, flags=re.I)


def uid(u) -> str:
    url = (u or {}).get("url", "") if isinstance(u, dict) else ""
    m = re.search(r"noticeUID=([^&]+)", url)
    return m.group(1) if m else ""


def grp(mod: str) -> str:
    m = mod.lower()
    if "directa" in m: return "D"
    if "especial" in m: return "R"
    if "licitaci" in m: return "L"
    if "selecci" in m or "subasta" in m: return "S"
    if "mínima" in m or "minima" in m: return "M"
    if "concurso" in m: return "C"
    return "O"


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------- clasificador UNSPSC
# SECOP II casi nunca publica el código UNSPSC de los procesos abiertos en datos abiertos.
# Si viene, se usa el oficial; si no, se estima el segmento a partir del objeto.
SEGMENTOS = {
 "10":"Material vivo vegetal y animal, accesorios y suministros","14":"Materiales y productos de papel",
 "15":"Combustibles, aditivos, lubricantes y anticorrosivos","25":"Vehículos comerciales, militares y particulares, accesorios y componentes",
 "26":"Maquinaria y accesorios para generación y distribución de energía","30":"Componentes y suministros para estructuras, edificación, construcción y obras civiles",
 "39":"Componentes, accesorios y suministros de sistemas eléctricos e iluminación","40":"Componentes y equipos para distribución y sistemas de acondicionamiento",
 "42":"Equipo médico, accesorios y suministros","43":"Tecnologías de la información y telecomunicaciones",
 "44":"Equipos de oficina, accesorios y suministros","46":"Equipos y suministros de defensa, orden público, protección, vigilancia y seguridad",
 "47":"Equipos de limpieza y suministros","49":"Equipos, suministros y accesorios para deportes y recreación",
 "50":"Alimentos, bebidas y tabaco","51":"Medicamentos y productos farmacéuticos","53":"Ropa, maletas y productos de aseo personal",
 "56":"Muebles, mobiliario y decoración","60":"Instrumentos musicales, juegos, artes, artesanías y equipo educativo",
 "72":"Servicios de edificación, construcción de instalaciones y mantenimiento","76":"Servicios de limpieza industrial",
 "77":"Servicios medioambientales","78":"Servicios de transporte, almacenaje y correo",
 "80":"Servicios de gestión, servicios profesionales de empresa y servicios administrativos",
 "81":"Servicios basados en ingeniería, investigación y tecnología","82":"Servicios editoriales, de diseño, de artes gráficas y bellas artes",
 "84":"Servicios financieros y de seguros","85":"Servicios de salud","86":"Servicios educativos y de formación",
 "90":"Servicios de viajes, alimentación, alojamiento y entretenimiento","92":"Servicios de defensa nacional, orden público, seguridad y vigilancia",
 "93":"Servicios políticos y de asuntos cívicos",
}
COMPRA = r"(suministro|adquisicion|adquirir|compra|compraventa|dotacion de elementos|elementos)"
REGLAS = [  # (segmento, patron) — el orden importa: la primera que coincide gana
 ("81", r"interventor|consultor|estudios y disenos|disenos|estudio tecnico|estudios tecnicos|topograf|diagnostico|formulacion de alternativas"),
 ("84", r"\bseguro|soat|poliza"),
 ("50", r"agua potable|alimentacion escolar|\bpae\b|complementos? alimentari|raciones|refrigerio|alimentos|viveres|aceites y grasas|mercados"),
 ("51", r"medicament|farmac"),
 ("42", r"dotacion hospitalaria|ayudas tecnicas|equipos? (biomedic|medic)|insumos medic|lentes|monturas|oftalm|odontolog"),
 ("85", r"hospitalari|servicios? (de salud|medic|integrales medic)|terapias|consulta externa|imagenes diagnosticas|laboratorio clinico|atencion integral de pacientes|alergolog"),
 ("15", r"combustible|gasolina|acpm|diesel|lubricante"),
 ("25", r"vehicul|camioneta|llantas|parque automotor|motocicleta|repuestos"),
 ("92", r"vigilancia|seguridad privada"),
 ("47", COMPRA + r".{0,60}(aseo|limpieza|desinfeccion)"),
 ("76", r"aseo|limpieza|desinfeccion|cafeteria|fumigacion"),
 ("53", r"calzado|vestido|uniforme|dotacion"),
 ("40", r"aires? acondicionad|refrigeracion|neveras"),
 ("39", r"transformador|alumbrado|iluminacion|electric"),
 ("46", r"cctv|camaras de seguridad|circuito cerrado|equipos de seguridad"),
 ("43", r"switch|swicth|elementos de red|lectores|dispositivos de lectura|software|licencia|computo|computador|tecnologic|conectividad|internet|telecomunicacion|apropiacion digital|redes de datos"),
 ("82", r"plan de medios|medios de comunicacion|difusion|impresion|fotocopiado|publicidad|avisos|piezas graficas|editorial"),
 ("78", r"tecnico-mecanica|tecnicomecanica|transporte|traslado|grua|mensajeria|acarreo"),
 ("90", r"tiquetes|festividad|turistic|cultural|recreativ|logistic|evento|feria|hospedaje|alojamiento|festival|celebracion|conmemoracion"),
 ("49", COMPRA + r".{0,60}deport"),
 ("86", r"capacitacion|formacion|curso|diplomado|educativ|pedagog"),
 ("77", r"conservacion|ambiental|reforestacion|residuos|arborizacion|poda|cesped|maleza|hidrolog"),
 ("56", r"estanteria|mobiliario|muebles|enseres"),
 ("44", r"papeleria|utiles de oficina|insumos de oficina"),
 ("10", r"material vegetal|semillas|plantulas|insumos agricolas|agropecuari|pecuari"),
 ("93", r"victima|sensibilizacion|tenencia responsable|participacion ciudadana|convivencia"),
 ("72", r"construccion|obra|pavimento|adecuacion|rehabilitacion|mejoramiento|optimizacion de red|mitigacion|mantenimiento|reparacion|cerramiento|acueducto|alcantarillado"),
 ("30", COMPRA + r".{0,60}(ferreteria|materiales de construccion|cemento)"),
 ("80", r"apoyo a la gestion|asesoria|administrativ|servicios profesionales|fortalecimiento|acompanamiento|operador|aunar esfuerzos"),
]
def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")
def clasificar(codigo, objeto):
    """Devuelve (codigo8, segmento, estimado)."""
    m = re.match(r"V1\.(\d{8})", codigo or "")
    if m:
        return m.group(1), m.group(1)[:2], False
    t = norm(objeto)
    for seg, pat in REGLAS:
        if re.search(pat, t):
            return "", seg, True
    if re.search(COMPRA, t):
        return "", "B", True   # bien sin categoría precisa
    return "", "", True
def tipo(seg):
    if seg == "72": return "obra"
    if seg == "B" or (seg.isdigit() and int(seg) < 70): return "bien"
    if seg: return "servicio"
    return ""


# ---------------------------------------------------------------- consultas
def main() -> None:
    hoy = dt.date.today()
    log = lambda m: print(f"[{dt.datetime.now():%H:%M:%S}] {m}", flush=True)

    log("Totales por departamento")
    dep = q(CONTRATOS, {"$select": "departamento, count(*) as n, sum(valor_del_contrato) as v",
                        "$where": BASE, "$group": "departamento"})
    dep_tot = {r["departamento"]: (int(r["n"]), round(num(r["v"]) / 1e6)) for r in dep}

    log("Entidades")
    ent = q(CONTRATOS, {"$select": "nit_entidad as k, max(nombre_entidad) as nm, max(departamento) as dp, "
                                   "max(ciudad) as c, max(orden) as o, count(*) as n, sum(valor_del_contrato) as v",
                        "$where": BASE, "$group": "nit_entidad", "$limit": 20000})
    S = {
        "dir": by_entity("count(*) as n, sum(valor_del_contrato) as v", DIRECTA),
        "pn": by_entity("count(*) as n", " AND tipodocproveedor='Cédula de Ciudadanía'"),
        "pro": by_entity("count(*) as n", " AND dias_adicionados != '0'"),
        "sup": by_entity("count(*) as n", " AND upper(nombre_supervisor) like 'NO DEFINID%'"),
        "dic": by_entity("count(*) as n", f" AND fecha_de_firma < '{hoy.year}-01-01' AND date_extract_m(fecha_de_firma)=12"),
        "pre": by_entity("count(*) as n", f" AND fecha_de_firma < '{hoy.year}-01-01'"),
        "gi": by_entity("count(*) as n, sum(valor_del_contrato) as v", TRIANG),
        "jan": by_entity("count(*) as n", DIRECTA + " AND ((fecha_de_firma >= '2024-01-01' AND fecha_de_firma < '2024-02-01') "
                                                  "OR (fecha_de_firma >= '2025-01-01' AND fecha_de_firma < '2025-02-01'))"),
        "j26": by_entity("count(*) as n", DIRECTA + " AND fecha_de_firma >= '2026-01-01' AND fecha_de_firma < '2026-02-01'"),
        "veda": by_entity("count(*) as n", DIRECTA + " AND fecha_de_firma >= '2026-02-01' AND fecha_de_firma < '2026-07-01'"),
    }
    g = lambda key, k, f="n": num((S[key].get(k) or {}).get(f))

    log("Proveedores por entidad (concentración)")
    prov = q_all(CONTRATOS, {"$select": "nit_entidad as k, documento_proveedor as p, max(tipodocproveedor) as t, "
                                        "max(proveedor_adjudicado) as nm, sum(valor_del_contrato) as v",
                             "$where": BASE, "$group": "nit_entidad, documento_proveedor",
                             "$order": "nit_entidad, documento_proveedor"})
    P = defaultdict(list)
    for p in prov:
        P[p["k"]].append(p)

    log("Armando filas de entidades")
    munis, mi, E = [], {}, []
    for e in ent:
        n, v = int(e["n"]), num(e["v"])
        d = DEPS.index(e["dp"]) if e["dp"] in DEPS else 0
        city = tc(e.get("c"))
        key = f"{d}|{city}"
        if key not in mi:
            mi[key] = len(munis)
            munis.append([city, d])
        row = [e["k"], tc(e["nm"])[:90].strip(), d, mi[key], (e.get("o") or "")[:1], n, round(v / 1e6)]
        if n >= 15:
            ps = sorted(P.get(e["k"], []), key=lambda x: -num(x["v"]))
            hhi = sum((num(x["v"]) / v) ** 2 for x in ps) if v else 0
            t = ps[0] if ps else {"v": 0, "t": "", "nm": ""}
            k = e["k"]
            row += [int(g("dir", k)), round(g("dir", k, "v") / 1e6), int(g("pn", k)), int(g("pro", k)),
                    int(g("sup", k)), int(g("dic", k)), int(g("pre", k)), int(g("gi", k)),
                    round(g("gi", k, "v") / 1e6), int(g("jan", k)), int(g("j26", k)), int(g("veda", k)),
                    round(num(t["v"]) / v * 1000) if v else 0,
                    tc(t["nm"])[:60].strip() if t.get("t") == "NIT" else "",
                    round(hhi * 1000)]
        E.append(row)

    log("Series mensuales y modalidades")
    dm = {}
    for x in q(CONTRATOS, {"$select": "departamento as d, date_extract_y(fecha_de_firma) as y, "
                                      "date_extract_m(fecha_de_firma) as m, count(*) as n",
                           "$where": BASE + DIRECTA, "$group": "d,y,m", "$limit": 5000}):
        if x["d"] not in DEPS:
            continue
        i = (int(x["y"]) - 2024) * 12 + int(x["m"]) - 1
        months = (hoy.year - 2024) * 12 + hoy.month
        dm.setdefault(str(DEPS.index(x["d"])), [0] * months)
        if 0 <= i < months:
            dm[str(DEPS.index(x["d"]))][i] = int(x["n"])
    mod = {}
    for x in q(CONTRATOS, {"$select": "departamento as d, modalidad_de_contratacion as mo, count(*) as n, "
                                      "sum(valor_del_contrato) as v",
                           "$where": BASE, "$group": "d,mo", "$limit": 5000}):
        if x["d"] not in DEPS:
            continue
        m = mod.setdefault(str(DEPS.index(x["d"])), {})
        c = m.setdefault(grp(x["mo"]), [0, 0])
        c[0] += int(x["n"])
        c[1] += round(num(x["v"]) / 1e6)

    log("Intermediarias (triangulación)")
    gi = [[tc(x["p"])[:80], x["d"], int(x["n"]), round(num(x["v"]) / 1e6), int(x["ne"])]
          for x in q(CONTRATOS, {"$select": "documento_proveedor as d, max(proveedor_adjudicado) as p, "
                                            "max(tipodocproveedor) as t, count(*) as n, sum(valor_del_contrato) as v, "
                                            "count(distinct nit_entidad) as ne",
                                 "$where": BASE + TRIANG, "$group": "documento_proveedor",
                                 "$order": "v desc", "$limit": 15})
          if x.get("t") == "NIT"]

    log("Contrato directo más grande por entidad")
    full = [r for r in E if len(r) > 7 and r[7] > 0]
    full.sort(key=lambda r: -r[8])
    big = {}
    for r in full[:140]:
        rows = q(CONTRATOS, {"$select": "proveedor_adjudicado as p, documento_proveedor as d, valor_del_contrato as v, "
                                        "fecha_de_firma as f, objeto_del_contrato as o, id_contrato as id, urlproceso as u",
                             "$where": BASE + DIRECTA + f" AND nit_entidad='{r[0]}' AND tipodocproveedor='NIT'",
                             "$order": "valor_del_contrato desc", "$limit": 1})
        if rows:
            b = rows[0]
            big[r[0]] = [tc(b["p"])[:80], b["d"], round(num(b["v"]) / 1e5) / 10, str(b.get("f", ""))[:10],
                         tc(b.get("o")).replace(";", ",")[:90].strip(), b["id"], uid(b.get("u"))]

    log("Licitaciones abiertas")
    manana = (hoy + dt.timedelta(days=1)).isoformat()
    hasta = (hoy + dt.timedelta(days=30)).isoformat()
    lic_raw = q(PROCESOS, {
        "$select": "entidad, departamento_entidad, ciudad_entidad, id_del_proceso, referencia_del_proceso, "
                   "descripci_n_del_procedimiento, modalidad_de_contratacion, precio_base, "
                   "fecha_de_publicacion_del, fecha_de_recepcion_de, estado_del_procedimiento, urlproceso, "
                   "codigo_principal_de_categoria, nit_entidad, visualizaciones_del, proveedores_que_manifestaron",
        "$where": f"departamento_entidad in {DEPS_SQL} AND fecha_de_recepcion_de >= '{manana}' "
                  f"AND fecha_de_recepcion_de <= '{hasta}' AND estado_del_procedimiento = 'Publicado' "
                  "AND modalidad_de_contratacion not in ('Contratación directa','Contratación Directa (con ofertas)',"
                  "'Contratación régimen especial','Solicitud de información a los Proveedores')",
        "$order": "fecha_de_recepcion_de", "$limit": 5000})
    seen, lic = set(), []
    for x in lic_raw:
        if x["id_del_proceso"] in seen:
            continue
        seen.add(x["id_del_proceso"])
        cod, seg, est = clasificar(x.get("codigo_principal_de_categoria"), x.get("descripci_n_del_procedimiento"))
        lic.append([tc(x["entidad"])[:90].strip(), DEPS.index(x["departamento_entidad"]), tc(x.get("ciudad_entidad")),
                    tc(x.get("descripci_n_del_procedimiento"))[:80].strip(), grp(x["modalidad_de_contratacion"]),
                    round(num(x.get("precio_base")) / 1e5) / 10, (x.get("fecha_de_publicacion_del") or "")[:10],
                    str(x["fecha_de_recepcion_de"])[:10], uid(x.get("urlproceso")),
                    str(x.get("referencia_del_proceso", ""))[:28], cod, seg, 1 if est else 0, "",
                    x.get("nit_entidad", ""), int(num(x.get("visualizaciones_del"))),
                    int(num(x.get("proveedores_que_manifestaron")))])

    familias = sorted({r[10][:4] for r in lic if r[10]})
    if familias:
        log("Nombres de familias UNSPSC oficiales")
        lista = ",".join("'" + f + "'" for f in familias)
        nombres = {r["id_familia"]: r["nf"] for r in q("f789-7hwg", {
            "$select": "id_familia, max(nombre_familia) as nf",
            "$where": f"id_familia in ({lista})", "$group": "id_familia", "$limit": 500})}
        for r in lic:
            if r[10]:
                r[13] = nombres.get(r[10][:4], "")

    log("Historial de competencia (oferente único, plazos y topes)")
    hist = q_all(PROCESOS, {
        "$select": "nit_entidad as k, departamento_entidad as dp, modalidad_de_contratacion as m, "
                   "proveedores_unicos_con as u, precio_base as p, fecha_de_publicacion_del as fp, "
                   "fecha_de_recepcion_de as fr, descripci_n_del_procedimiento as o",
        "$where": f"departamento_entidad in {DEPS_SQL} AND adjudicado='Si' AND fecha_de_publicacion_del >= '{DESDE}' "
                  "AND modalidad_de_contratacion in ('Licitación pública','Licitación pública Obra Publica',"
                  "'Mínima cuantía','Selección Abreviada de Menor Cuantía','Selección abreviada subasta inversa',"
                  "'Concurso de méritos abierto','Seleccion Abreviada Menor Cuantia Sin Manifestacion Interes')",
        "$order": "id_del_proceso"}, page=20000)
    c_ent, c_seg, c_dep, dias, mc = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), defaultdict(list), defaultdict(list)
    tot = uno = 0
    for h in hist:
        u = int(num(h.get("u")))
        if u < 1:
            continue
        g = grp(h.get("m", ""))
        sg = clasificar("", h.get("o"))[1] or "-"
        d = str(DEPS.index(h["dp"])) if h.get("dp") in DEPS else None
        one = 1 if u == 1 else 0
        tot += 1; uno += one
        for bucket, key in ((c_ent, h.get("k")), (c_seg, sg), (c_dep, d)):
            if key is not None:
                bucket[key][0] += 1; bucket[key][1] += one
        try:
            dd = (dt.date.fromisoformat(h["fr"][:10]) - dt.date.fromisoformat(h["fp"][:10])).days
            if 0 <= dd < 200:
                dias[g].append(dd)
        except (KeyError, TypeError, ValueError):
            pass
        if g == "M" and num(h.get("p")) > 0:
            mc[h.get("k")].append(num(h.get("p")))
    plazo = {g: sorted(v)[len(v) // 2] for g, v in dias.items() if v}
    tope = {}
    for k, v in mc.items():
        if len(v) >= 10:
            v.sort()
            tope[k] = round(v[int(0.97 * (len(v) - 1))] / 1e5) / 10
    comp = {"tot": tot, "uno": uno, "ent": dict(c_ent), "seg": dict(c_seg), "dep": dict(c_dep),
            "plazo": plazo, "tope": tope}

    data = {
        "meta": {"fecha": hoy.isoformat(), "desde": DESDE,
                 "fuente": f"SECOP II · datos.gov.co ({CONTRATOS}, {PROCESOS})"},
        "deps": DEPS,
        "depTot": [list(dep_tot.get(d, (0, 0))) for d in DEPS],
        "E": E, "lic": lic,
        "seg": {k: v for k, v in SEGMENTOS.items() if any(r[11] == k for r in lic) or k in comp["seg"]},
        "comp": comp, "munis": munis, "dm": dm, "mod": mod, "gi": gi, "big": big,
    }

    # control de calidad: la suma por entidad debe coincidir con los totales oficiales
    n_ent = sum(r[5] for r in E)
    n_dep = sum(v[0] for v in dep_tot.values())
    if n_ent != n_dep:
        log(f"ADVERTENCIA: entidades suman {n_ent} y departamentos {n_dep}")
    if n_dep < 1000:
        sys.exit("Muy pocos contratos: la fuente pudo fallar. No se reemplaza data.json.")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    log(f"Listo: {len(E)} entidades, {n_dep} contratos, {len(lic)} licitaciones → {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
