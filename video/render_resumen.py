#!/usr/bin/env python3
"""Carrusel 'Resumen de la semana' (sábado) · 1080x1350 · estilo de los posts de lanzamiento.

Uso: python video/render_resumen.py  -> site/redes/resumen/resumen-20261121_N.jpg
"""
import math, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_semana import RAIZ, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER, F_DISP, F_BODY, F_MONO

W, H, M = 1080, 1350, 80
ID = "resumen-20261121"
CORTE = "corte 21-nov-2026"

LAMINAS = [
    dict(kicker="RESUMEN DE LA SEMANA · CARIBE", pre="Santa Marta:", big="80 de cada 100",
         label="pesos, por contratación directa",
         body="Eso contrató de forma directa su alcaldía desde 2024. Y hay 4 cifras más de la semana. Desliza."),
    dict(kicker="ALCALDÍAS DE CAPITALES · DESDE 2024", big="80 % · 15 %", label="Santa Marta · Sincelejo",
         body="Es la distancia en contratación directa. En Santa Marta, el 56 % del valor fue a su empresa "
              "distrital de desarrollo urbano (EDUS), una entidad pública: la ley permite contratarla así."),
    dict(kicker="LA GUAJIRA · DESDE 2024", big="65 de 100", label="procesos con un solo oferente",
         body="1.167 de 1.792 procesos abiertos a competencia recibieron una sola oferta. "
              "En el Caribe son 42 de cada 100."),
    dict(kicker="SAN ANDRÉS · 7 AL 14 DE NOVIEMBRE", big="89 de 92", label="contratos directos",
         body="El 97 %: el porcentaje más alto del Caribe esa semana."),
    dict(kicker="MÍNIMA CUANTÍA · CARIBE", big="5 días", label="o menos para ofertar",
         body="Así pasa en la mitad de los procesos. Ten lista tu carpeta: RUT, Cámara de Comercio, "
              "seguridad social y una cotización base."),
    dict(kicker="PARA MIPYMES · ABIERTOS HOY", big="75", label="procesos abiertos",
         body="Mínima cuantía o selección abreviada hasta $500 millones, con cierre desde el "
              "24 de noviembre. Suman $18.498 millones."),
    dict(kicker="PIVIJAY · MAGDALENA", big="6 obras", label="abiertas por $1.236 millones",
         body="Acueducto de Las Canoas, vía a San José de la Montaña, alcantarillado, colegios rurales "
              "y parques. Todas cierran el 30 de noviembre."),
    dict(kicker="TE LEEMOS", cierre="¿Qué municipio revisamos la próxima semana?",
         body="Guárdalo y envíaselo a alguien de tu municipio. Busca el tuyo en mareapublica.com."),
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
    out = os.path.join(RAIZ, "site", "redes", "resumen")
    os.makedirs(out, exist_ok=True)
    for i, L in enumerate(LAMINAS):
        p = os.path.join(out, f"{ID}_{i + 1}.jpg")
        lamina(i, L).save(p, quality=92)
        print(p)


if __name__ == "__main__":
    main()
