"""Escenas compartidas por los videos de la semana del 23 al 28 de noviembre de 2026.

Las usan render_{radar,licitaciones,secop,ranking,consejo}_20261123.py, que a su vez
reutilizan el motor de render_semana.py (voz ElevenLabs, subtítulos, música, banda de cine).
"""
import math
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, envolver, F_DISP, F_BODY, F_MONO)

GRIS = (90, 120, 126)
MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def millones(v):
    s = f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "$" + (s[:-2] if s.endswith(",0") else s) + " millones"


def pastilla(d, y, s, f, col, relleno=False, texto=None):
    w = d.textlength(s, font=f)
    caja = (W / 2 - w / 2 - 34, y, W / 2 + w / 2 + 34, y + f.size + 34)
    if relleno:
        d.rounded_rectangle(caja, (f.size + 34) // 2, fill=col)
        texto_c(d, y + 15, s, f, texto or NIGHT)
    else:
        d.rounded_rectangle(caja, (f.size + 34) // 2, outline=col, width=3)
        texto_c(d, y + 15, s, f, col)


def escena_cien(d, p, prm):
    """Cuadrícula de 100 con n encendidos. prm: n, grande, sub."""
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
    texto_c(d, 1100, prm["grande"], F_DISP(110, 850), mezcla(NIGHT, EMBER, a))
    texto_c(d, 1235, prm["sub"], F_BODY(46, 600), mezcla(NIGHT, SALT, a))


def escena_barras(d, p, prm):
    """Barras horizontales. prm: titulo, sub, filas [(etiqueta, pct, marca)], hi, lo, nota."""
    filas = prm["filas"]
    texto_c(d, 250, prm["titulo"], F_DISP(52, 750), SALT)
    if prm.get("sub"):
        texto_c(d, 320, prm["sub"], F_BODY(34, 400), MUTED)
    n = len(filas)
    alto = 82 if n <= 7 else 70
    gap = 26 if n <= 7 else 20
    y = 410
    x0, xmax = 330, W - 150
    for i, (lab, pc, marca) in enumerate(filas):
        g = ease(p * 2.6 - i * 0.1)
        col = EMBER if lab in prm.get("hi", ()) else SEA if lab in prm.get("lo", ()) else GRIS
        yy = y + i * (alto + gap)
        f = F_BODY(38, 600)
        w = d.textlength(lab, font=f)
        d.text((x0 - 24 - w, yy + (alto - 44) / 2), lab, font=f, fill=mezcla(NIGHT, SALT, g))
        d.rounded_rectangle((x0, yy, xmax, yy + alto), 16, fill=NIGHT2)
        largo = (xmax - x0) * pc / 100 * g
        if largo > 20:
            d.rounded_rectangle((x0, yy, x0 + largo, yy + alto), 16, fill=col)
        d.text((x0 + largo + 16, yy + (alto - 48) / 2), f"{round(pc * g)} %{marca}", font=F_MONO(40), fill=SALT)
    a = ease((p - 0.5) * 3)
    if prm.get("nota"):
        texto_c(d, y + n * (alto + gap) + 10, prm["nota"], F_BODY(28, 400), mezcla(NIGHT, MUTED, a))


def escena_dos(d, p, prm):
    """Dos barras verticales para contrastar. prm: titulo, sub, barras [(etq, pct, col)], remate."""
    texto_c(d, 250, prm["titulo"], F_DISP(84), SALT)
    texto_c(d, 360, prm["sub"], F_BODY(42, 500), MUTED)
    base, alto_max, ancho = 1130, 560, 280
    for k, (lab, v, col) in enumerate(prm["barras"]):
        g = ease(p * 2.2 - k * 0.35)
        cx = W / 2 + (-210 if k == 0 else 210)
        h = alto_max * v / 100 * g
        d.rounded_rectangle((cx - ancho / 2, base - alto_max, cx + ancho / 2, base), 22, fill=NIGHT2)
        if h > 4:
            d.rounded_rectangle((cx - ancho / 2, base - h, cx + ancho / 2, base), 22, fill=col)
        texto_c(d, base - h - 100, f"{round(v * g)} %", F_DISP(80, 850), mezcla(NIGHT, SALT, g), cx=cx)
        texto_c(d, base + 24, lab, F_BODY(42, 600), mezcla(NIGHT, SALT, g), cx=cx)
    a = ease((p - 0.5) * 3)
    if prm.get("remate"):
        texto_c(d, 1240, prm["remate"], F_DISP(54, 750), mezcla(NIGHT, EMBER, a))


def escena_legal(d, p, prm):
    a = ease(p * 2.5)
    b = ease((p - 0.4) * 2.5)
    texto_c(d, 430, "Es legal", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, 560, "en varios casos,", F_DISP(76, 700), mezcla(NIGHT, MUTED, a))
    texto_c(d, 650, prm.get("caso", "como servicios profesionales."), F_DISP(60, 600), mezcla(NIGHT, MUTED, a))
    texto_c(d, 740, "Ley 1150 de 2007", F_MONO(36), mezcla(NIGHT, SEA, a))
    d.line([(W / 2 - 60, 840), (W / 2 + 60, 840)], fill=mezcla(NIGHT, EMBER, b), width=6)
    texto_c(d, 900, "No es una falla.", F_DISP(76, 700), mezcla(NIGHT, SALT, b))
    texto_c(d, 1010, "Es una señal", F_DISP(110), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1140, "para revisar.", F_DISP(110), mezcla(NIGHT, EMBER, b))


def escena_frases(d, p, prm):
    """Líneas centradas que aparecen en orden. prm: lineas [(texto, tam, color)]."""
    y = prm.get("y", 420)
    for i, (t, tam, col) in enumerate(prm["lineas"]):
        a = ease(p * 2.6 - i * 0.18)
        texto_c(d, y, t, F_DISP(tam, 800 if tam >= 90 else 700), mezcla(NIGHT, col, a))
        y += int(tam * 1.25)


def escena_tarjeta(d, p, prm):
    """Proceso abierto. prm: k, n, mun, dep, obj, ent, val, cierre (AAAA-MM-DD)."""
    a = ease(p * 2.6)
    dx = 80 * (1 - a)
    if prm.get("n"):
        texto_c(d, 290, f"{prm['k'] + 1} DE {prm['n']}", F_MONO(34), mezcla(NIGHT, SEA, a))
    else:
        texto_c(d, 290, prm.get("kicker", "EJEMPLO ABIERTO"), F_MONO(34), mezcla(NIGHT, SEA, a))
    mun = prm["mun"]
    texto_c(d, 350, mun, F_DISP(128 if len(mun) < 11 else 96 if len(mun) < 20 else 80),
            mezcla(NIGHT, SALT, a), cx=W / 2 + dx)
    texto_c(d, 505, prm["dep"], F_BODY(50, 500), mezcla(NIGHT, MUTED, a), cx=W / 2 + dx)
    b = ease((p - 0.08) * 2.6)
    x0, x1, y0, y1 = 110, W - 110, 620, 930
    d.rounded_rectangle((x0, y0, x1, y1), 36, fill=mezcla(NIGHT, NIGHT2, b),
                        outline=mezcla(NIGHT, SEA, b * 0.7), width=3)
    f = F_DISP(58, 750)
    lineas = envolver(d, prm["obj"], f, x1 - x0 - 100)[:2]
    for i, ln in enumerate(lineas):
        texto_c(d, y0 + 55 + i * 72, ln, f, mezcla(NIGHT, SALT, b))
    texto_c(d, y0 + 70 + len(lineas) * 72, prm["ent"], F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    c = ease((p - 0.2) * 2.6)
    texto_c(d, 975, millones(prm["val"]), F_DISP(96, 850), mezcla(NIGHT, EMBER, c))
    _, m, dd = prm["cierre"].split("-")
    pastilla(d, 1140, f"Cierra el {int(dd)} de {MESES[int(m)]}", F_DISP(48, 700), mezcla(NIGHT, SEA, c), True,
             mezcla(SEA, NIGHT, c))


def escena_cierre(d, p, prm):
    """Cierre de marca con dos líneas propias. prm: linea, corte."""
    rs.escena_cierre(d, p, prm)
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1200, prm["linea"], F_DISP(52, 700), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1290, prm["corte"], F_BODY(30, 400), mezcla(NIGHT, MUTED, b))


def escena_alertas(d, p, prm):
    """Cierre MiPyme: invitación a las alertas gratis. prm: corte."""
    a = ease(p * 2.5)
    s = 150
    x, y = W / 2 - s / 2, 360
    d.rounded_rectangle((x, y, x + s, y + s), 36, fill=mezcla(NIGHT, EMBER, a))
    for k in range(3):
        yy = y + 50 + k * 26
        pts = [(x + 22 + j * 6, yy + 8 * math.sin(j / 3.2)) for j in range(19)]
        d.line(pts, fill=mezcla(EMBER, SALT, a), width=6)
    texto_c(d, 560, "Alertas gratis", F_DISP(104), mezcla(NIGHT, SALT, a))
    texto_c(d, 680, "de tu sector", F_DISP(104), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.15) * 2.5)
    f = F_DISP(66, 800)
    t = "mareapublica.com/alertas"
    w = d.textlength(t, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 36, 860, W / 2 + w / 2 + 36, 970), 28, fill=mezcla(NIGHT, SEA, b))
    texto_c(d, 875, t, f, mezcla(SEA, NIGHT, b))
    texto_c(d, 1010, "Enlace en la bio", F_DISP(56, 750), mezcla(NIGHT, SALT, b))
    c = ease((p - 0.35) * 2.5)
    texto_c(d, 1120, "Guárdalo y envíaselo a quien tenga empresa", F_BODY(38, 600), mezcla(NIGHT, MUTED, c))
    texto_c(d, 1210, prm["corte"], F_BODY(30, 400), mezcla(NIGHT, MUTED, c))
    texto_c(d, 1255, "Voz generada con IA", F_BODY(28, 400), mezcla(NIGHT, MUTED, c * 0.8))


COMUNES = {"cien": escena_cien, "barras": escena_barras, "dos": escena_dos, "legal": escena_legal,
           "frases": escena_frases, "tarjeta": escena_tarjeta, "cierre": escena_cierre,
           "alertas": escena_alertas}
