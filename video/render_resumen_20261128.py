#!/usr/bin/env python3
"""Carrusel 'Resumen de la semana' del sábado 28 de noviembre de 2026 (pieza MP-20261128-IG) · 1080x1350.
Aprobado por Juan Camilo el 22-nov-2026. Motor de dibujo: render_resumen.py.

Uso: python video/render_resumen_20261128.py  -> site/redes/2026-11-28/resumen-20261128_N.jpg
"""
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_semana import RAIZ, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER, F_DISP, F_BODY, F_MONO

W, H, M = 1080, 1350, 80
ID = "resumen-20261128"
CORTE = "corte 22-nov-2026"

LAMINAS = [
    dict(kicker="RESUMEN DE LA SEMANA · CARIBE", pre="Cesar 17 · San Andrés 55", big="de cada 100",
         label="pesos, por contratación directa",
         body="Eso contrataron de forma directa sus gobernaciones desde 2024. Y hay 4 cifras más de la semana. Desliza."),
    dict(kicker="ATLÁNTICO · 15 AL 22 DE NOVIEMBRE", big="85 de 100", label="contratos directos",
         body="437 de 516 contratos firmados en la semana: el porcentaje más alto del Caribe. "
              "La Guajira fue el más bajo, con 29 de cada 100."),
    dict(kicker="CARIBE · 15 AL 22 DE NOVIEMBRE", big="7 de 10", label="contratos fueron directos",
         body="Pero solo 27 de cada 100 pesos. Son muchos contratos pequeños, sobre todo de servicios profesionales y de apoyo a la gestión."),
    dict(kicker="CÓMO LEER SECOP · BOLÍVAR", big="3 de 10", label="contratos sin supervisor definido",
         body="En el Caribe son 16 de cada 100; en Córdoba, 1. No quiere decir que nadie vigile el contrato: "
              "a veces se designa en un documento aparte. Pero debería estar."),
    dict(kicker="GOBERNACIONES · DESDE 2024", big="55 % · 17 %", label="San Andrés · Cesar",
         body="Valor contratado de forma directa: San Andrés 55, La Guajira 46, Atlántico 40, Bolívar 40*, "
              "Córdoba 36*, Sucre 31*, Magdalena 29, Cesar 17. *Incluye créditos de deuda pública, directos por ley."),
    dict(kicker="MIPYMES · EVENTOS Y LOGÍSTICA", big="46 de 100", label="procesos con una sola oferta",
         body="Desde 2024. Abiertos hoy: Fundación, alcantarillado, $427 M (1 dic). El Carmen de Bolívar, mobiliario, $231,8 M (3 dic). "
              "Cereté, logística, $150 M (3 dic). Tránsito del Atlántico, uniformes, $173,4 M (4 dic)."),
    dict(kicker="PARA LEER BIEN LOS DATOS", cierre="Es legal en varios casos. Es una señal para revisar.",
         body="La contratación directa y el oferente único no son una falla por sí solos. "
              "Alertas gratis de licitaciones de tu sector: mareapublica.com/alertas"),
    dict(kicker="TE LEEMOS", cierre="¿Qué revisamos la próxima semana?",
         body="Guárdalo y envíaselo a alguien de tu municipio. Busca el tuyo y las licitaciones abiertas en mareapublica.com."),
]


def mezcla(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def envolver(d, texto, f, ancho):
    lineas, act = [], ""
    for p in texto.split():
        prueba = (act + " " + p).strip()
        if d.textlength(prueba, font=f) <= ancho:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    return lineas


def ajustar(d, texto, tam, ancho, peso=850):
    while tam > 60 and d.textlength(texto, font=F_DISP(tam, peso)) > ancho:
        tam -= 4
    return F_DISP(tam, peso)


def espaciado(d, xy, s, f, fill, sep=4):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + sep


def lamina(i, L):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        d.line((0, y, W, y), fill=mezcla(NIGHT2, NIGHT, y / H))
    # olas al pie
    for k in range(4):
        base = 1200 + k * 36
        pts = [(x, base + 9 * math.sin(x / 95 + k * 1.3)) for x in range(0, W + 10, 10)]
        d.line(pts, fill=mezcla(NIGHT, SEA, 0.18), width=2)
    # cabecera
    d.rounded_rectangle((M, 66, M + 36, 102), 8, fill=EMBER)
    espaciado(d, (M + 52, 66), "MAREA PÚBLICA", F_MONO(32), SALT, 3)
    n = f"{i + 1}/{len(LAMINAS)}"
    f = F_MONO(30)
    d.text((W - M - d.textlength(n, font=f), 68), n, font=f, fill=SEA)
    # cuerpo
    ancho = W - 2 * M
    bloques = []  # (alto, fn)
    fk = F_MONO(30)
    bloques.append((60, lambda y: espaciado(d, (M, y), L["kicker"], fk, SEA, 4)))
    if "cierre" in L:
        fc = F_DISP(92, 800)
        ls = envolver(d, L["cierre"], fc, ancho)
        for ln in ls:
            bloques.append((108, lambda y, ln=ln: d.text((M, y), ln, font=fc, fill=SALT)))
        bloques.append((40, lambda y: None))
    else:
        if L.get("pre"):
            fp = F_DISP(72, 800)
            bloques.append((92, lambda y: d.text((M, y), L["pre"], font=fp, fill=SALT)))
        fb = ajustar(d, L["big"], 210, ancho)
        alto_big = int(fb.size * 1.08)
        bloques.append((alto_big, lambda y: d.text((M - 6, y), L["big"], font=fb, fill=EMBER)))
        fl = ajustar(d, L["label"], 70, ancho, 800)
        bloques.append((int(fl.size * 1.85), lambda y: d.text((M, y), L["label"], font=fl, fill=SALT)))
    fbody = F_BODY(42, 400)
    for ln in envolver(d, L["body"], fbody, ancho):
        bloques.append((58, lambda y, ln=ln: d.text((M, y), ln, font=fbody, fill=mezcla(MUTED, SALT, 0.45))))
    total = sum(a for a, _ in bloques)
    y = max(180, (H - total) // 2 - 30)
    for a, fn in bloques:
        fn(y)
        y += a
    # pie
    fp = F_MONO(26)
    d.text((M, 1258), f"Fuente: SECOP II · {CORTE}", font=fp, fill=MUTED)
    s = "mareapublica.com"
    d.text((W - M - d.textlength(s, font=fp), 1258), s, font=fp, fill=MUTED)
    return im


def main():
    out = os.path.join(RAIZ, "site", "redes", "2026-11-28")
    os.makedirs(out, exist_ok=True)
    for i, L in enumerate(LAMINAS):
        p = os.path.join(out, f"{ID}_{i + 1}.jpg")
        lamina(i, L).save(p, quality=92)
        print(p)


if __name__ == "__main__":
    main()
