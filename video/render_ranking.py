#!/usr/bin/env python3
"""Marea Pública · Ranking: capitales del Caribe por % del valor en contratación directa
(pieza MP-20261119-IG).

Guion aprobado por Juan Camilo el 19-nov-2026. Reutiliza el motor de render_semana.py
(voz ElevenLabs de mujer, subtítulos, música de veeduría, banda de cine) con escenas propias.
Las cifras se leen de site/data.json (bloque "E": valor directo / valor total por entidad)
y se comprueban contra el guion aprobado.

Uso: python video/render_ranking.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, F_DISP, F_BODY, F_MONO)

# Alcaldías de las capitales (San Andrés no tiene alcaldía: queda por fuera)
CAPITALES = {
    "891780009": "Santa Marta", "892115007": "Riohacha", "890102018": "Barranquilla",
    "800098911": "Valledupar", "800096734": "Montería", "890480184": "Cartagena",
    "800104062": "Sincelejo",
}
APROBADO = {"Santa Marta": 80, "Riohacha": 58, "Barranquilla": 55, "Valledupar": 38,
            "Montería": 37, "Cartagena": 33, "Sincelejo": 15}

CAPTION = """En Santa Marta, 80 de cada 100 pesos que contrató la alcaldía desde 2024 fueron por contratación directa. En Sincelejo, 15.

Este es el ranking de las alcaldías de las capitales del Caribe según el valor contratado de forma directa (enero de 2024 a noviembre de 2026):
1. Santa Marta: 80 %
2. Riohacha: 58 %
3. Barranquilla: 55 %
4. Valledupar: 38 %
5. Montería: 37 % (incluye créditos de deuda pública, que son directos por ley)
6. Cartagena: 33 %
7. Sincelejo: 15 %

La contratación directa es legal en varios casos. En Santa Marta, la mayor parte de ese valor va a la empresa distrital de desarrollo urbano, que es una entidad pública, y la ley permite contratar directamente entre entidades públicas. La pregunta útil es cómo contrata después esa empresa, y eso también se puede revisar en SECOP.

Guárdalo y envíaselo a alguien de Santa Marta o de Sincelejo. ¿Qué te sorprende de tu ciudad?

Busca la ficha de tu municipio en mareapublica.com (link en la bio).

Fuente: mareapublica.com, con datos de SECOP II al 19 de noviembre de 2026.
Voz generada con IA.

#MareaPública #ContrataciónPública #SECOP #SantaMarta #Sincelejo #CaribeColombiano"""


def guion(data):
    por_nit = {e[0]: e for e in data["E"] if len(e) > 8}
    pct = {}
    for nit, ciudad in CAPITALES.items():
        e = por_nit[nit]
        pct[ciudad] = 100 * e[8] / e[6]
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    for c, v in APROBADO.items():
        assert round(pct[c]) == v, (c, pct[c])
    sm = por_nit["891780009"]
    assert sm[20].startswith("Empresa Distrital de Desarrollo"), sm[20]
    assert round(sm[19] / 10) == 56, sm[19]

    filas = sorted(((c, round(v, 1)) for c, v in pct.items()), key=lambda r: -r[1])
    escenas = [
        ("intro", "[seriously] En Santa Marta, 80 de cada 100 pesos que contrató la alcaldía desde 2024 "
                  "fueron por contratación directa. En Sincelejo, solo 15. [short pause]",
         {"rango": "ENE 2024 – NOV 2026",
          "banda": {"arriba": ["Santa Marta: 80", "de cada 100 pesos"], "abajo": ["Sincelejo: 15"]}}),
        ("barras", "Este es el ranking de las capitales del Caribe, por valor contratado de forma directa: "
                   "Santa Marta, 80 por ciento. Riohacha, 58. Barranquilla, 55. Valledupar, 38. "
                   "Montería, 37. Cartagena, 33. Y Sincelejo, 15.",
         {"filas": filas, "hi": {"Santa Marta"}, "lo": {"Sincelejo"}}),
        ("empresa", "[calmly] Ojo: en Santa Marta, la mayor parte va a su empresa distrital de desarrollo "
                    "urbano, que es pública. La ley permite contratar directo entre entidades públicas.",
         {"n": round(sm[19] / 10)}),
        ("pregunta", "La pregunta útil es otra: cómo contrata después esa empresa.", {}),
        ("cierre", "[warmly] Busca tu ciudad en mareapublica.com, y envíaselo a alguien de Santa Marta.", {}),
    ]
    return escenas, CAPTION


def escena_barras(d, p, prm):
    filas = prm["filas"]
    texto_c(d, 250, "% del valor por contratación directa", F_DISP(52, 750), SALT)
    texto_c(d, 320, "Alcaldías de capitales · desde enero de 2024", F_BODY(34, 400), MUTED)
    y, alto, gap = 420, 82, 26
    x0, xmax = 330, W - 150
    for i, (ciudad, pc) in enumerate(filas):
        g = ease(p * 2.6 - i * 0.1)
        col = EMBER if ciudad in prm["hi"] else SEA if ciudad in prm["lo"] else (90, 120, 126)
        yy = y + i * (alto + gap)
        f = F_BODY(38, 600)
        w = d.textlength(ciudad, font=f)
        d.text((x0 - 24 - w, yy + 18), ciudad, font=f, fill=mezcla(NIGHT, SALT, g))
        d.rounded_rectangle((x0, yy, xmax, yy + alto), 16, fill=NIGHT2)
        largo = (xmax - x0) * pc / 100 * g
        if largo > 20:
            d.rounded_rectangle((x0, yy, x0 + largo, yy + alto), 16, fill=col)
        etiqueta = f"{round(pc * g)} %" + ("*" if ciudad == "Montería" else "")
        d.text((x0 + largo + 16, yy + 16), etiqueta, font=F_MONO(40), fill=SALT)
    a = ease((p - 0.5) * 3)
    texto_c(d, y + len(filas) * (alto + gap) + 10, "* Montería incluye créditos de deuda pública",
            F_BODY(28, 400), mezcla(NIGHT, MUTED, a))


def escena_empresa(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 250, "Santa Marta", F_DISP(96), mezcla(NIGHT, SALT, a))
    # Dona: 56 de cada 100 pesos a la empresa distrital (entidad pública)
    cx, cy, r, grosor = W / 2, 640, 230, 70
    caja = (cx - r, cy - r, cx + r, cy + r)
    d.ellipse(caja, outline=mezcla(NIGHT, NIGHT2, a), width=grosor)
    g = ease((p - 0.1) * 2.2)
    fin = -90 + 360 * prm["n"] / 100 * g
    if g > 0.01:
        d.arc(caja, -90, fin, fill=EMBER, width=grosor)
    texto_c(d, cy - 90, f"{round(prm['n'] * g)}", F_DISP(150, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, cy + 70, "de cada 100 pesos", F_BODY(36, 500), mezcla(NIGHT, MUTED, a))
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 930, "Empresa distrital de desarrollo urbano", F_DISP(50, 750), mezcla(NIGHT, SALT, b))
    texto_c(d, 995, "Entidad pública", F_DISP(50, 750), mezcla(NIGHT, EMBER, b))
    c = ease((p - 0.6) * 3)
    f = F_MONO(34)
    s = "LEGAL · Ley 1150 de 2007"
    w = d.textlength(s, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 30, 1110, W / 2 + w / 2 + 30, 1170), 28,
                        outline=mezcla(NIGHT, SEA, c), width=3)
    texto_c(d, 1120, s, f, mezcla(NIGHT, SEA, c))


def escena_pregunta(d, p, prm):
    a = ease(p * 2.5)
    b = ease((p - 0.3) * 2.5)
    texto_c(d, 480, "La pregunta útil:", F_DISP(84, 750), mezcla(NIGHT, MUTED, a))
    d.line([(W / 2 - 60, 620), (W / 2 + 60, 620)], fill=mezcla(NIGHT, EMBER, b), width=6)
    texto_c(d, 690, "¿Cómo contrata", F_DISP(110), mezcla(NIGHT, SALT, b))
    texto_c(d, 820, "después", F_DISP(110), mezcla(NIGHT, EMBER, b))
    texto_c(d, 950, "esa empresa?", F_DISP(110), mezcla(NIGHT, SALT, b))


def escena_cierre(d, p, prm):
    rs.escena_cierre(d, p, prm)
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1200, "Envíaselo a alguien de Santa Marta", F_DISP(52, 700), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1290, "Datos de SECOP II al 19-nov-2026", F_BODY(30, 400), mezcla(NIGHT, MUTED, b))


rs.guion = guion
rs.VOZ = rs.VOZ_MUJER
rs.PERFIL = "veeduria"
rs.DIBUJA.update({"barras": escena_barras, "empresa": escena_empresa,
                  "pregunta": escena_pregunta, "cierre": escena_cierre})
# Toma de apertura: bahía de Santa Marta (paisaje, sin edificios públicos).
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "ciudades", "santa-marta-bahia-1.mp4")

if __name__ == "__main__":
    rs.main()
