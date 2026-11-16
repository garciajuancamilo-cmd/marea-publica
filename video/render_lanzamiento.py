#!/usr/bin/env python3
"""Reel de lanzamiento de Marea Pública (reutiliza el motor de render_semana)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import W, SALT, MUTED, SEA, EMBER, NIGHT, NIGHT2, F_DISP, F_BODY, ease, mezcla, texto_c

def datos_pagina():
    d = json.load(open(os.path.join(rs.RAIZ, "site", "data.json"), encoding="utf-8"))
    n = sum(x[0] for x in d["depTot"])
    v = sum(x[1] for x in d["depTot"])  # millones
    dirn = sum((m.get("D") or [0])[0] for m in d["mod"].values())
    return n, v, dirn

def guion(_data):
    n, v, dirn = datos_pagina()
    pct = round(100 * dirn / n)
    escenas = [
        ("hook", "¿Sabes cómo se contrata con la plata pública en el Caribe?", {"rango": "CARIBE · DESDE 2024"}),
        ("conteo", f"Desde enero de 2024, las entidades públicas firmaron {rs.letras(n)} contratos.", {"n": n}),
        ("grilla", "Siete de cada diez, por contratación directa. Sin competencia entre empresas.",
         {"pct": pct, "de10": round(pct / 10), "D": dirn}),
        ("leemos", "En Marea Pública leemos SECOP todos los días, y te lo mostramos claro: "
                   "por departamento, municipio y entidad.", {}),
        ("puertas", "Si quieres vigilar, o si tienes una empresa y quieres contratar con el Estado,", {}),
        ("cierre", "entra a marea pública punto com. Esto es Marea Pública.", {}),
    ]
    return escenas, ""

def escena_hook(d, p, prm):
    a = ease(p * 2.2)
    y = 600 + 60 * (1 - a)
    texto_c(d, y, "La plata pública", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, y + 125, "del Caribe,", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, y + 250, "a la vista.", F_DISP(110), mezcla(NIGHT, EMBER, a))

def escena_leemos(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 470, "Leemos SECOP II", F_DISP(96), mezcla(NIGHT, SALT, a))
    texto_c(d, 580, "todos los días", F_DISP(96), mezcla(NIGHT, SEA, a))
    for i, t in enumerate(["Departamento", "Municipio", "Entidad"]):
        b = ease(p * 3 - 0.6 - i * 0.35)
        y = 760 + i * 130
        f = F_DISP(60, 750)
        w = d.textlength(t, font=f)
        d.rounded_rectangle((W / 2 - w / 2 - 40, y, W / 2 + w / 2 + 40, y + 100), 28,
                            fill=mezcla(NIGHT, NIGHT2, b), outline=mezcla(NIGHT, SEA, b), width=3)
        texto_c(d, y + 16, t, f, mezcla(NIGHT, SALT, b))

def escena_puertas(d, p, prm):
    for i, (t1, t2, col) in enumerate([("Quiero vigilar", "Ciudadanos y veedurías", SEA),
                                       ("Tengo una empresa", "Licitaciones para MiPymes", EMBER)]):
        b = ease(p * 2.5 - i * 0.5)
        y = 520 + i * 300
        d.rounded_rectangle((110, y, W - 110, y + 240), 36, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, col, b), width=5)
        texto_c(d, y + 50, t1, F_DISP(76), mezcla(NIGHT, SALT, b))
        texto_c(d, y + 150, t2, F_BODY(42, 500), mezcla(NIGHT, MUTED, b))

def cabecera(d, rango):
    d.rounded_rectangle((72, 120, 112, 160), 10, fill=EMBER)
    d.text((128, 118), "MAREA PÚBLICA", font=rs.F_MONO(34), fill=SALT)
    f = rs.F_MONO(28)
    w = d.textlength(rango, font=f)
    d.rounded_rectangle((W - 72 - w - 36, 116, W - 72, 164), 24, outline=SEA, width=2)
    d.text((W - 72 - w - 18, 124), rango, font=f, fill=SEA)
    d.text((72, 190), "Fuente: SECOP II · datos abiertos", font=F_BODY(26, 400), fill=MUTED)
rs.cabecera = cabecera

rs.DIBUJA.update({"hook": escena_hook, "leemos": escena_leemos, "puertas": escena_puertas})
rs.guion = guion
rs.PERFIL = "institucional"
_orig_conteo = rs.escena_conteo
def conteo(d, p, prm):
    n = int(prm["n"] * ease(p * 1.6))
    a = ease(p * 3)
    texto_c(d, 600, rs.miles(n), F_DISP(230, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 880, "contratos firmados", F_BODY(54, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 950, "desde enero de 2024", F_BODY(54, 400), mezcla(NIGHT, MUTED, a))
rs.DIBUJA["conteo"] = conteo

if __name__ == "__main__":
    rs.main()
