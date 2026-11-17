#!/usr/bin/env python3
"""Marea Pública · Licitaciones abiertas del 17 de noviembre de 2026 (pieza MP-20261117-IG).

Guion aprobado por Juan Camilo el 17-nov-2026. Reutiliza el motor de render_semana.py
(voz ElevenLabs de hombre, subtítulos, música MiPymes, banda de cine) con escenas propias.
Las cifras se leen de site/data.json (bloque "lic") y se comprueban contra el guion aprobado.

Uso: python video/render_licitaciones.py [salida.mp4]
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, envolver, F_DISP, F_BODY, F_MONO)

URL = "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID="

# noticeUID, municipio, departamento, objeto corto, entidad corta, valor (millones), cierre
PROCESOS = [
    ("CO1.NTC.11191064", "Corozal", "Sucre", "Reposición de redes de alcantarillado",
     "Alcaldía de Corozal", 490.2, "2026-11-23"),
    ("CO1.NTC.11215240", "El Paso", "Cesar", "Suministro de materiales de construcción",
     "Alcaldía de El Paso", 180.0, "2026-11-24"),
    ("CO1.NTC.11163832", "Cartagena", "Bolívar", "Reparaciones locativas en un colegio",
     "I.E. Pedro Romero", 60.0, "2026-11-25"),
    ("CO1.NTC.11208491", "Barranquilla", "Atlántico", "Compra e instalación de mobiliario",
     "Personería Distrital", 490.0, "2026-11-27"),
]

CAPTION = """77 procesos públicos abiertos en el Caribe a la medida de una MiPyme, y todos cierran antes de diciembre.

Te mostramos cuatro:
📍 Corozal (Sucre): reposición de alcantarillado, $490,2 millones. Cierra el 23 de noviembre.
📍 El Paso (Cesar): materiales de construcción, $180 millones. Cierra el 24.
📍 Cartagena: reparaciones locativas en la I.E. Pedro Romero, $60 millones. Cierra el 25.
📍 Barranquilla: mobiliario para la Personería Distrital, $490 millones. Cierra el 27.

Son de mínima cuantía o selección abreviada hasta $500 millones. Ojo: en la selección abreviada de menor cuantía primero se manifiesta interés. Revisa el cronograma de cada proceso en SECOP II.

¿En qué sector está tu empresa? Cuéntanos y te decimos qué hay abierto. Guárdalo y envíaselo a quien tenga una MiPyme.

Los 77 procesos, con enlace directo a SECOP: link en la bio (mareapublica.com › Licitaciones).

Fuente: SECOP II vía mareapublica.com, datos al 17 de noviembre de 2026. Fechas de cierre según SECOP; pueden cambiar por adenda.
Voz generada con IA.

#MareaPública #ContrataciónPública #SECOP #Licitaciones #MiPymes #CaribeColombiano"""


def millones(v):
    s = f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "$" + (s[:-2] if s.endswith(",0") else s) + " millones"


def guion(data):
    lic, deps = data["lic"], data["deps"]
    assert data["meta"]["lic_fecha"] == "2026-11-17", "El guion aprobado usa las licitaciones del 17-nov-2026"
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    aptos = [l for l in lic if str(l[7])[:10] >= "2026-11-20" and l[4] in ("S", "M") and l[5] and l[5] <= 500]
    assert len(aptos) == 77, len(aptos)
    assert all(str(l[7])[:10] <= "2026-12-03" for l in aptos)
    por_uid = {l[8]: l for l in lic}
    for uid, mun, dep, _, _, val, cierre in PROCESOS:
        l = por_uid[uid]
        assert deps[l[1]] == dep and abs(l[5] - val) < 0.05 and str(l[7])[:10] == cierre, (uid, l)

    t = [
        "Hay 77 procesos públicos abiertos a tu medida, y todos cierran antes de diciembre. [short pause] Te traigo cuatro.",
        "En Corozal, Sucre: reposición de alcantarillado por 490 millones. Cierra el 23 de noviembre.",
        "En El Paso, Cesar: materiales de construcción por 180 millones. Cierra el 24.",
        "En Cartagena, un colegio busca reparaciones locativas por 60 millones. Cierra el 25.",
        "Y en Barranquilla, la Personería Distrital compra mobiliario por 490 millones. Cierra el 27.",
    ]
    escenas = [
        ("intro", "[warmly] ¿Tienes una MiPyme en el Caribe?",
         {"rango": "LICITACIONES · 17 NOV",
          "banda": {"arriba": ["¿Tienes una", "MiPyme?"], "abajo": ["Esto es para ti"]}}),
        ("total", t[0], {"n": 77}),
    ]
    for k, (p, txt) in enumerate(zip(PROCESOS, t[1:])):
        escenas.append(("tarjeta", txt, {"k": k, "p": p}))
    escenas += [
        ("consejo", "[seriously] Un consejo: en la selección abreviada de menor cuantía primero hay que manifestar interés. "
                    "Revisa el cronograma en SECOP antes de que se te pase la fecha.", {}),
        ("cierre", "[calmly] Los 77 están en mareapublica.com, en Licitaciones. Guárdalo y envíaselo a quien tenga empresa.", {}),
    ]
    return escenas, CAPTION


def escena_total(d, p, prm):
    n = int(prm["n"] * ease(p * 2.2))
    a = ease(p * 3)
    texto_c(d, 330, "Caribe colombiano", F_BODY(48, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 430, str(n), F_DISP(330, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 820, "procesos abiertos", F_DISP(76, 750), mezcla(NIGHT, SALT, a))
    texto_c(d, 910, "a la medida de una MiPyme", F_DISP(60, 650), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1030, "Mínima cuantía o selección abreviada", F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    texto_c(d, 1082, "hasta $500 millones", F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    f = F_MONO(36)
    s = "CIERRAN ANTES DE DICIEMBRE"
    w = d.textlength(s, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 30, 1170, W / 2 + w / 2 + 30, 1240), 34,
                        outline=mezcla(NIGHT, EMBER, b), width=3)
    texto_c(d, 1184, s, f, mezcla(NIGHT, EMBER, b))


def escena_tarjeta(d, p, prm):
    uid, mun, dep, obj, ent, val, cierre = prm["p"]
    a = ease(p * 2.6)
    dx = 80 * (1 - a)
    texto_c(d, 290, f"{prm['k'] + 1} DE 4", F_MONO(34), mezcla(NIGHT, SEA, a))
    texto_c(d, 350, mun, F_DISP(128 if len(mun) < 11 else 112), mezcla(NIGHT, SALT, a), cx=W / 2 + dx)
    texto_c(d, 505, dep, F_BODY(50, 500), mezcla(NIGHT, MUTED, a), cx=W / 2 + dx)
    b = ease((p - 0.08) * 2.6)
    x0, x1, y0, y1 = 110, W - 110, 620, 930
    d.rounded_rectangle((x0, y0, x1, y1), 36, fill=mezcla(NIGHT, NIGHT2, b),
                        outline=mezcla(NIGHT, SEA, b * 0.7), width=3)
    f = F_DISP(58, 750)
    lineas = envolver(d, obj, f, x1 - x0 - 100)[:2]
    for i, ln in enumerate(lineas):
        texto_c(d, y0 + 55 + i * 72, ln, f, mezcla(NIGHT, SALT, b))
    texto_c(d, y0 + 70 + len(lineas) * 72, ent, F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    c = ease((p - 0.2) * 2.6)
    texto_c(d, 975, millones(val), F_DISP(96, 850), mezcla(NIGHT, EMBER, c))
    dia = int(cierre[-2:])
    s = f"Cierra el {dia} de noviembre"
    fm = F_DISP(48, 700)
    w = d.textlength(s, font=fm)
    d.rounded_rectangle((W / 2 - w / 2 - 36, 1140, W / 2 + w / 2 + 36, 1226), 43,
                        fill=mezcla(NIGHT, SEA, c))
    texto_c(d, 1154, s, fm, mezcla(SEA, NIGHT, c))


def escena_consejo(d, p, prm):
    a = ease(p * 2.5)
    f = F_MONO(34)
    s = "CONSEJO MIPYME"
    w = d.textlength(s, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 30, 290, W / 2 + w / 2 + 30, 356), 33, fill=mezcla(NIGHT, EMBER, a))
    texto_c(d, 302, s, f, mezcla(EMBER, SALT, a))
    texto_c(d, 410, "Selección abreviada", F_DISP(84), mezcla(NIGHT, SALT, a))
    texto_c(d, 510, "de menor cuantía", F_DISP(84), mezcla(NIGHT, SALT, a))
    for i, (num, t1) in enumerate((("1", "Manifiesta interés"), ("2", "Presenta tu oferta"))):
        b = ease(p * 2.8 - 0.5 - i * 0.45)
        y = 660 + i * 190
        d.rounded_rectangle((130, y, W - 130, y + 150), 36, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, SEA if i == 0 else EMBER, b), width=4)
        d.ellipse((170, y + 30, 260, y + 120), fill=mezcla(NIGHT, SEA if i == 0 else EMBER, b))
        texto_c(d, y + 36, num, F_DISP(64), mezcla(NIGHT, NIGHT, b), cx=215)
        d.text((300, y + 40), t1, font=F_DISP(64, 750), fill=mezcla(NIGHT, SALT, b))
    c = ease((p - 0.45) * 2.5)
    texto_c(d, 1080, "Revisa el cronograma en SECOP II", F_BODY(44, 600), mezcla(NIGHT, SEA, c))
    texto_c(d, 1140, "antes de que se pase la fecha", F_BODY(44, 500), mezcla(NIGHT, MUTED, c))


def escena_cierre(d, p, prm):
    a = ease(p * 2.5)
    s = 150
    x, y = W / 2 - s / 2, 380
    d.rounded_rectangle((x, y, x + s, y + s), 36, fill=mezcla(NIGHT, EMBER, a))
    for k in range(3):
        yy = y + 50 + k * 26
        pts = [(x + 22 + j * 6, yy + 8 * math.sin(j / 3.2)) for j in range(19)]
        d.line(pts, fill=mezcla(EMBER, SALT, a), width=6)
    texto_c(d, 580, "Los 77 procesos en", F_BODY(52, 500), mezcla(NIGHT, MUTED, a))
    b = ease((p - 0.15) * 2.5)
    f = F_DISP(84, 800)
    w = d.textlength("mareapublica.com", font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 40, 670, W / 2 + w / 2 + 40, 800), 30, fill=mezcla(NIGHT, SEA, b))
    texto_c(d, 688, "mareapublica.com", f, mezcla(SEA, NIGHT, b))
    texto_c(d, 830, "› Licitaciones", F_DISP(64, 750), mezcla(NIGHT, SALT, b))
    c = ease((p - 0.35) * 2.5)
    texto_c(d, 990, "Guárdalo y envíaselo", F_DISP(64, 750), mezcla(NIGHT, EMBER, c))
    texto_c(d, 1070, "a quien tenga empresa", F_DISP(64, 750), mezcla(NIGHT, EMBER, c))
    texto_c(d, 1210, "Datos de SECOP II al 17-nov-2026", F_BODY(30, 400), mezcla(NIGHT, MUTED, c))
    texto_c(d, 1255, "Voz generada con IA", F_BODY(28, 400), mezcla(NIGHT, MUTED, c * 0.8))


rs.guion = guion
rs.VOZ = rs.VOZ_HOMBRE
rs.PERFIL = "mipymes"
rs.DIBUJA.update({"total": escena_total, "tarjeta": escena_tarjeta,
                  "consejo": escena_consejo, "cierre": escena_cierre})
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "temas", "taller-mipyme-1.mp4")

if __name__ == "__main__":
    rs.main()
