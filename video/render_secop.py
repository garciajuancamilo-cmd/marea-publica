#!/usr/bin/env python3
"""Marea Pública · Cómo leer SECOP: qué es un oferente único (pieza MP-20261118-IG).

Guion aprobado por Juan Camilo el 18-nov-2026. Reutiliza el motor de render_semana.py
(voz ElevenLabs de mujer, subtítulos, música de veeduría, banda de cine) con escenas propias.
Las cifras se leen de site/data.json (bloque "comp") y se comprueban contra el guion aprobado.

Uso: python video/render_secop.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, F_DISP, F_BODY, F_MONO)

CAPTION = """En La Guajira, 65 de cada 100 procesos abiertos a competencia terminaron con un solo oferente.

Eso es un oferente único: la entidad abre el proceso para que cualquier empresa compita y solo llega una propuesta. No es ilegal (el Decreto 1082 de 2015 permite adjudicar con una sola oferta) y en mercados pequeños es común. Pero sí es una señal para mirar con calma.

En SECOP II revisa tres cosas:
1. Cuántos días hubo entre la publicación y el cierre.
2. Qué tan exigentes eran los requisitos habilitantes.
3. Cuántas empresas mostraron interés o hicieron observaciones.

El promedio del Caribe es 42 de cada 100. Cesar llega a 57 y San Andrés tiene el más bajo, 29.

¿Cuántos oferentes tuvo el último proceso que viste en tu municipio? Guárdalo para cuando revises uno y envíaselo a alguien de La Guajira.

El dato de tu municipio: link en la bio (mareapublica.com).

Fuente: SECOP II vía mareapublica.com, datos al 18 de noviembre de 2026. Procesos de licitación, selección abreviada, concurso de méritos y mínima cuantía adjudicados desde enero de 2024.
Voz generada con IA.

#MareaPública #ContrataciónPública #SECOP #LaGuajira #Cesar #VeeduríaCiudadana"""


def guion(data):
    c, deps = data["comp"], data["deps"]
    pct = {deps[int(k)]: 100 * u / t for k, (t, u) in c["dep"].items()}
    caribe = 100 * c["uno"] / c["tot"]
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    assert round(pct["La Guajira"]) == 65, pct["La Guajira"]
    assert round(pct["Cesar"]) == 57, pct["Cesar"]
    assert round(caribe) == 42, caribe
    assert max(pct, key=pct.get) == "La Guajira"

    filas = sorted(((rs.CORTO.get(d, d), round(v, 1)) for d, v in pct.items()), key=lambda r: -r[1])
    escenas = [
        ("intro", "[seriously] En La Guajira, 65 de cada 100 procesos abiertos a competencia "
                  "terminaron con un solo oferente.",
         {"rango": "ENE 2024 – NOV 2026",
          "banda": {"arriba": ["65 de cada 100", "en La Guajira"], "abajo": ["con un solo oferente"]}}),
        ("cien", "[short pause] ¿Qué significa eso?", {"n": 65}),
        ("def", "[warmly] Un oferente único es cuando la entidad abre el proceso para que cualquier "
                "empresa compita, y solo llega una propuesta.", {}),
        ("legal", "No es ilegal: la norma permite adjudicar con una sola oferta si cumple los requisitos. "
                  "Y en mercados pequeños pasa.", {}),
        ("revisa", "Pero sí vale la pena mirarlo. En SECOP revisa tres cosas: cuántos días hubo para ofertar, "
                   "qué tan exigentes eran los requisitos y cuántas empresas mostraron interés.", {}),
        ("barras", "En el Caribe el promedio es 42 de cada 100. En Cesar, 57.",
         {"filas": filas, "hi": {"La Guajira", "Cesar"}, "prom": caribe}),
        ("cierre", "Guárdalo para cuando revises un proceso de tu municipio.", {}),
    ]
    return escenas, CAPTION


def escena_cien(d, p, prm):
    lado, gap = 62, 14
    x0 = (W - (10 * lado + 9 * gap)) / 2
    y0 = 300
    for i in range(100):
        r, c = divmod(i, 10)
        x, y = x0 + c * (lado + gap), y0 + r * (lado + gap)
        ap = ease(p * 3 - i * 0.012)
        on = i < prm["n"] and p > 0.10 + i * 0.004
        d.rounded_rectangle((x, y, x + lado, y + lado), 12,
                            fill=mezcla(NIGHT, EMBER if on else NIGHT2, ap),
                            outline=mezcla(NIGHT, SEA, ap * 0.5), width=2)
    a = ease((p - 0.25) * 2.5)
    texto_c(d, 1080, "¿Qué significa?", F_DISP(100, 850), mezcla(NIGHT, SALT, a))


def sobre(d, cx, cy, a, lleno):
    w, h = 170, 116
    col = mezcla(NIGHT, EMBER if lleno else NIGHT2, a)
    borde = mezcla(NIGHT, SALT if lleno else SEA, a * (1 if lleno else 0.5))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 14, fill=col, outline=borde, width=4)
    d.line([(cx - w / 2 + 8, cy - h / 2 + 8), (cx, cy + 6), (cx + w / 2 - 8, cy - h / 2 + 8)], fill=borde, width=4)


def escena_def(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 290, "Oferente único", F_DISP(110), mezcla(NIGHT, SALT, a))
    # Puerta abierta: el proceso está abierto a cualquier empresa
    d.rounded_rectangle((W / 2 - 330, 470, W / 2 + 330, 980), 30, outline=mezcla(NIGHT, SEA, a), width=5)
    texto_c(d, 500, "PROCESO ABIERTO", F_MONO(40), mezcla(NIGHT, SEA, a))
    pos = [(W / 2 - 200, 650), (W / 2, 650), (W / 2 + 200, 650),
           (W / 2 - 200, 820), (W / 2, 820), (W / 2 + 200, 820)]
    for k, (x, y) in enumerate(pos):
        lleno = k == 1
        g = ease((p - 0.25 - (0.15 if lleno else 0)) * 3)
        sobre(d, x, y + (40 * (1 - g) if lleno else 0), g, lleno)
    b = ease((p - 0.55) * 3)
    texto_c(d, 1040, "Llega una sola propuesta", F_DISP(72, 750), mezcla(NIGHT, EMBER, b))


def escena_legal(d, p, prm):
    a = ease(p * 2.5)
    b = ease((p - 0.45) * 2.5)
    texto_c(d, 400, "No es ilegal", F_DISP(120), mezcla(NIGHT, SALT, a))
    texto_c(d, 550, "La norma permite adjudicar", F_DISP(64, 650), mezcla(NIGHT, MUTED, a))
    texto_c(d, 630, "con una sola oferta", F_DISP(64, 650), mezcla(NIGHT, MUTED, a))
    texto_c(d, 730, "Decreto 1082 de 2015", F_MONO(38), mezcla(NIGHT, SEA, a))
    d.line([(W / 2 - 60, 850), (W / 2 + 60, 850)], fill=mezcla(NIGHT, EMBER, b), width=6)
    texto_c(d, 910, "En mercados pequeños,", F_DISP(76, 700), mezcla(NIGHT, SALT, b))
    texto_c(d, 1010, "pasa.", F_DISP(110), mezcla(NIGHT, EMBER, b))


def escena_revisa(d, p, prm):
    a = ease(p * 3)
    texto_c(d, 280, "En SECOP, revisa:", F_DISP(96), mezcla(NIGHT, SALT, a))
    items = [("1", "Días para ofertar"), ("2", "Requisitos exigidos"), ("3", "Empresas interesadas")]
    for k, (n, t) in enumerate(items):
        g = ease((p - 0.22 - k * 0.2) * 3.5)
        y = 470 + k * 210
        d.rounded_rectangle((100, y, W - 100, y + 160), 30, fill=mezcla(NIGHT, NIGHT2, g),
                            outline=mezcla(NIGHT, SEA, g * 0.7), width=3)
        d.ellipse((160, y + 30, 260, y + 130), fill=mezcla(NIGHT, EMBER, g))
        fn = F_DISP(64, 850)
        wn = d.textlength(n, font=fn)
        d.text((210 - wn / 2, y + 40), n, font=fn, fill=mezcla(NIGHT, SALT, g))
        d.text((290 + 30 * (1 - g), y + 48), t, font=F_DISP(56, 700), fill=mezcla(NIGHT, SALT, g))


def escena_barras(d, p, prm):
    filas = prm["filas"]
    texto_c(d, 250, "Procesos con un solo oferente", F_DISP(54, 750), SALT)
    texto_c(d, 320, "% desde enero de 2024", F_BODY(34, 400), MUTED)
    y, alto, gap = 410, 74, 22
    x0, xmax = 330, W - 150
    for i, (dep, pc) in enumerate(filas):
        g = ease(p * 2.2 - i * 0.1)
        col = EMBER if dep in prm["hi"] else (90, 120, 126)
        yy = y + i * (alto + gap)
        f = F_BODY(38, 600)
        w = d.textlength(dep, font=f)
        d.text((x0 - 24 - w, yy + 14), dep, font=f, fill=mezcla(NIGHT, SALT, g))
        d.rounded_rectangle((x0, yy, xmax, yy + alto), 16, fill=NIGHT2)
        largo = (xmax - x0) * pc / 100 * g
        if largo > 20:
            d.rounded_rectangle((x0, yy, x0 + largo, yy + alto), 16, fill=col)
        d.text((x0 + largo + 16, yy + 12), f"{round(pc * g)} %", font=F_MONO(40), fill=SALT)
    # Línea del promedio del Caribe
    a = ease((p - 0.35) * 3)
    xp = x0 + (xmax - x0) * prm["prom"] / 100
    yb = y + len(filas) * (alto + gap)
    for yy in range(y - 16, yb - 6, 22):
        d.line([(xp, yy), (xp, yy + 12)], fill=mezcla(NIGHT, SALT, a), width=4)
    texto_c(d, yb + 10, f"Caribe: {round(prm['prom'])} %", F_MONO(38), mezcla(NIGHT, SALT, a), cx=xp)


def escena_cierre(d, p, prm):
    rs.escena_cierre(d, p, prm)
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1200, "Guárdalo para revisar tu municipio", F_DISP(52, 700), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1290, "Datos de SECOP II al 18-nov-2026", F_BODY(30, 400), mezcla(NIGHT, MUTED, b))


rs.guion = guion
rs.VOZ = rs.VOZ_MUJER
rs.PERFIL = "veeduria"
rs.DIBUJA.update({"cien": escena_cien, "def": escena_def, "legal": escena_legal,
                  "revisa": escena_revisa, "barras": escena_barras, "cierre": escena_cierre})
# Sin toma de La Guajira en la biblioteca: se usa la toma de marca (olas), neutra.
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "marca", "olas-1.mp4")

if __name__ == "__main__":
    rs.main()
