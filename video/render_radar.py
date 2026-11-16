#!/usr/bin/env python3
"""Marea Pública · Radar de la semana del 9 al 16 de noviembre de 2026 (pieza MP-20261116-IG).

Guion aprobado por Juan Camilo el 16-nov-2026. Reutiliza el motor de render_semana.py
(voz ElevenLabs, subtítulos, música, banda de cine) con escenas propias.
Las cifras se leen de site/data.json (bloque "sem") y se comprueban contra el guion aprobado.

Uso: python video/render_radar.py [salida.mp4]
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, miles, F_DISP, F_BODY, F_MONO)

SA = "San Andrés, Providencia y Santa Catalina"

CAPTION = """87 de 90: así contrató San Andrés esta semana 🏝️

Del 9 al 16 de noviembre, San Andrés firmó 87 de sus 90 contratos por contratación directa (97%), el porcentaje más alto del Caribe. Magdalena fue el más bajo (46%). Atlántico fue el que más cambió: 1.138 contratos directos, 314 más que la semana anterior.

La contratación directa es legal en varios casos, como los servicios profesionales y de apoyo a la gestión. No es una falla por sí sola, pero sí una señal para revisar.

Ojo: SECOP II publica con rezago, así que la semana puede crecer en los próximos días.

¿Cómo va tu municipio? Búscalo gratis en mareapublica.com (link en la bio) y envíale este video a alguien de San Andrés.

Fuente: mareapublica.com, con datos de SECOP II al 16 de noviembre de 2026.
Voz generada con IA.

#MareaPública #ContrataciónPública #SECOP #SanAndrés #Atlántico #Magdalena"""


def guion(data):
    s, deps = data["sem"], data["deps"]
    assert s["desde"] == "2026-11-09", "El guion aprobado es de la semana del 9 al 16 de noviembre"
    tot = [x[0] for x in s["total"]]
    dirn = [x[0] for x in s["directa"]]
    prev = [x[0] for x in s["directa_previa"]]
    i_sa, i_mg, i_at = deps.index(SA), deps.index("Magdalena"), deps.index("Atlántico")
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    assert (dirn[i_sa], tot[i_sa]) == (87, 90), (dirn[i_sa], tot[i_sa])
    assert round(100 * dirn[i_mg] / tot[i_mg]) == 46
    assert (dirn[i_at], dirn[i_at] - prev[i_at]) == (1138, 314)

    filas = sorted(((rs.CORTO.get(d, d), round(100 * dirn[i] / tot[i]), tot[i])
                    for i, d in enumerate(deps)), key=lambda r: -r[1])
    escenas = [
        ("intro", "[seriously] 87 de 90. Así contrató San Andrés esta semana: casi todo por contratación directa.",
         {"rango": "9 NOV – 16 NOV",
          "banda": {"arriba": ["87 de 90", "en San Andrés"], "abajo": ["contratos directos"]}}),
        ("cien", "[short pause] Es el porcentaje más alto del Caribe: 97 de cada 100 contratos.", {"n": 97}),
        ("barras", "En el otro extremo está Magdalena, con 46 de cada 100.",
         {"filas": filas, "hi": {"San Andrés"}, "lo": {"Magdalena"}}),
        ("cambio", "Y el que más se movió fue Atlántico: 1.138 contratos directos, 314 más que la semana anterior.",
         {"antes": prev[i_at], "ahora": dirn[i_at]}),
        ("idea", "[calmly] Ojo: la contratación directa es legal en varios casos, como los servicios profesionales. "
                 "No es una falla por sí sola; es una señal para mirar con lupa.", {}),
        ("cierre", "[warmly] Busca tu municipio gratis en mareapublica.com y envíale este video a alguien de San Andrés.", {}),
    ]
    return escenas, CAPTION


def escena_cien(d, p, prm):
    lado, gap = 62, 14
    x0 = (W - (10 * lado + 9 * gap)) / 2
    y0 = 330
    for i in range(100):
        r, c = divmod(i, 10)
        x, y = x0 + c * (lado + gap), y0 + r * (lado + gap)
        ap = ease(p * 3 - i * 0.012)
        on = i < prm["n"] and p > 0.10 + i * 0.004
        d.rounded_rectangle((x, y, x + lado, y + lado), 12,
                            fill=mezcla(NIGHT, EMBER if on else NIGHT2, ap),
                            outline=mezcla(NIGHT, SEA, ap * 0.5), width=2)
    a = ease((p - 0.3) * 2.5)
    texto_c(d, 1110, "97 de cada 100", F_DISP(110, 850), mezcla(NIGHT, EMBER, a))
    texto_c(d, 1240, "el % más alto del Caribe", F_BODY(48, 600), mezcla(NIGHT, SALT, a))


def escena_cambio(d, p, prm):
    texto_c(d, 260, "Atlántico", F_DISP(110), SALT)
    texto_c(d, 385, "contratos directos por semana", F_BODY(44, 500), MUTED)
    base, alto_max, ancho = 1180, 470, 260
    mx = max(prm["antes"], prm["ahora"])
    for k, (lab, v, col) in enumerate((("2 a 8 nov", prm["antes"], (90, 120, 126)),
                                       ("9 a 16 nov", prm["ahora"], EMBER))):
        g = ease(p * 2.2 - k * 0.35)
        cx = W / 2 + (-200 if k == 0 else 200)
        h = alto_max * v / mx * g
        if h > 4:
            d.rounded_rectangle((cx - ancho / 2, base - h, cx + ancho / 2, base), 20, fill=col)
        texto_c(d, base - h - 90, miles(round(v * g)), F_MONO(64), mezcla(NIGHT, SALT, g), cx=cx)
        texto_c(d, base + 24, lab, F_BODY(40, 500), mezcla(NIGHT, MUTED, g), cx=cx)
    a = ease((p - 0.45) * 3)
    texto_c(d, 470, "+314 (+38 %)", F_DISP(76, 800), mezcla(NIGHT, EMBER, a))


def escena_idea(d, p, prm):
    a = ease(p * 2.5)
    b = ease((p - 0.4) * 2.5)
    texto_c(d, 430, "Es legal", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, 560, "en varios casos,", F_DISP(76, 700), mezcla(NIGHT, MUTED, a))
    texto_c(d, 650, "como servicios profesionales.", F_DISP(60, 600), mezcla(NIGHT, MUTED, a))
    texto_c(d, 740, "Ley 1150 de 2007", F_MONO(36), mezcla(NIGHT, SEA, a))
    d.line([(W / 2 - 60, 840), (W / 2 + 60, 840)], fill=mezcla(NIGHT, EMBER, b), width=6)
    texto_c(d, 900, "No es una falla.", F_DISP(76, 700), mezcla(NIGHT, SALT, b))
    texto_c(d, 1010, "Es una señal", F_DISP(110), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1140, "para revisar.", F_DISP(110), mezcla(NIGHT, EMBER, b))


def escena_cierre(d, p, prm):
    rs.escena_cierre(d, p, prm)
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1200, "Envíaselo a alguien de San Andrés", F_DISP(52, 700), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1290, "Datos de SECOP II al 16-nov-2026", F_BODY(30, 400), mezcla(NIGHT, MUTED, b))


rs.guion = guion
rs.DIBUJA.update({"cien": escena_cien, "cambio": escena_cambio, "idea": escena_idea, "cierre": escena_cierre})
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "ciudades", "san-andres-mar-1.mp4")

if __name__ == "__main__":
    rs.main()
