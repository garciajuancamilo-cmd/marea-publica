#!/usr/bin/env python3
"""Marea Pública · Consejo MiPyme del 20 de noviembre de 2026 (pieza MP-20261120-IG).

Guion aprobado por Juan Camilo el 20-nov-2026. Reutiliza el motor de render_semana.py
(voz ElevenLabs de hombre, subtítulos, música MiPymes, banda de cine) con escenas propias.
Las cifras se leen de site/data.json (bloques "comp" y "lic") y se comprueban contra el guion.

Uso: python video/render_consejo.py [salida.mp4]
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER,
                           ease, mezcla, texto_c, envolver, F_DISP, F_BODY, F_MONO)

EJEMPLO = "CO1.NTC.11240322"  # Rama Judicial Valledupar, MC-VA-18-2026

CAPTION = """En el Caribe, la mitad de los procesos de mínima cuantía da 5 días o menos para presentar tu oferta.

Si esperas a ver el proceso publicado para reunir los papeles, ya vas tarde. La ventaja: en mínima cuantía no te piden RUP y gana la oferta con el menor precio que cumpla los requisitos. Ten lista tu carpeta desde hoy: RUT, certificado de Cámara de Comercio, pagos de seguridad social, antecedentes y una cotización base.

Ejemplo de esta semana: la Rama Judicial en Valledupar contrata el mantenimiento de sedes judiciales en Chimichagua y Manaure (Cesar). $175 millones, cierra el martes 24 de noviembre. Hoy hay 22 procesos de mínima cuantía abiertos en el Caribe por $1.798 millones.

Guárdalo para tu próxima oferta y envíaselo a alguien que tenga una MiPyme. ¿Qué documento es el que más te cuesta conseguir?

Busca todas las licitaciones abiertas en mareapublica.com (link en la bio).

Fuente: mareapublica.com, con datos de SECOP II al 20 de noviembre de 2026.
Voz generada con IA.

#MareaPública #ContrataciónPública #SECOP #Licitaciones #Valledupar #MiPymes"""


def guion(data):
    lic, comp = data["lic"], data["comp"]
    assert data["meta"]["lic_fecha"] == "2026-11-20", "El guion aprobado usa los datos del 20-nov-2026"
    assert comp["plazo"]["M"] == 5, comp["plazo"]
    minimas = [l for l in lic if l[4] == "M"]
    assert len(minimas) == 22, len(minimas)
    assert abs(sum(l[5] for l in minimas) - 1797.7) < 1, sum(l[5] for l in minimas)
    ej = next(l for l in lic if l[8] == EJEMPLO)
    assert ej[4] == "M" and abs(ej[5] - 175.0) < 0.05 and str(ej[7])[:10] == "2026-11-24", ej

    escenas = [
        ("intro", "[warmly] En el Caribe, la mitad de los procesos de mínima cuantía te da cinco días o menos para presentar tu oferta.",
         {"rango": "CONSEJO MIPYME · 20 NOV",
          "banda": {"arriba": ["5 días o menos", "para ofertar"], "abajo": ["en mínima cuantía"]}}),
        ("plazo", "[short pause] Si esperas a ver el proceso para alistar papeles, ya vas tarde.", {"n": 5}),
        ("reglas", "[calmly] La buena noticia: en mínima cuantía no te piden RUP, y gana la oferta con el menor precio que cumpla los requisitos.", {}),
        ("carpeta", "Por eso, ten lista desde hoy tu carpeta: RUT, certificado de existencia y representación, "
                    "pagos de seguridad social, certificados de antecedentes y una cotización base.", {}),
        ("ejemplo", "[short pause] Un ejemplo de esta semana: la Rama Judicial en Valledupar busca quién haga mantenimiento "
                    "a sedes judiciales en Chimichagua y Manaure. Son 175 millones de pesos y cierra el martes 24 de noviembre.", {}),
        ("total", "Hoy hay 22 procesos de mínima cuantía abiertos en el Caribe. Búscalos en mareapublica.com, en Licitaciones.",
         {"n": 22}),
        ("cierre", "[warmly] Guarda este video para cuando armes tu próxima oferta.", {}),
    ]
    return escenas, CAPTION


def etiqueta(d, y, s, color, a):
    f = F_MONO(34)
    w = d.textlength(s, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 30, y, W / 2 + w / 2 + 30, y + 66), 33, fill=mezcla(NIGHT, color, a))
    texto_c(d, y + 12, s, f, mezcla(color, SALT, a))


def escena_plazo(d, p, prm):
    a = ease(p * 2.4)
    texto_c(d, 300, "Plazo típico para ofertar", F_BODY(48, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 380, str(prm["n"]), F_DISP(360, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 790, "días", F_DISP(110, 800), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.25) * 2.4)
    # cinco casillas de calendario que se van tachando
    x0, s, g = 175, 130, 22
    for i in range(5):
        x = x0 + i * (s + g)
        c = ease(p * 3 - 0.6 - i * 0.18)
        d.rounded_rectangle((x, 960, x + s, 960 + s), 22, outline=mezcla(NIGHT, SEA, b), width=4,
                            fill=mezcla(NIGHT, NIGHT2, b))
        if c > 0:
            d.line((x + 28, 960 + 28, x + 28 + (s - 56) * c, 960 + 28 + (s - 56) * c), fill=EMBER, width=8)
    texto_c(d, 1150, "Mediana en mínima cuantía · Caribe, desde 2024", F_BODY(32, 400), mezcla(NIGHT, MUTED, b))


def escena_reglas(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 290, "En mínima cuantía", F_DISP(84), mezcla(NIGHT, SALT, a))
    items = (("Sin RUP", "Ley 1150 de 2007, art. 6", SEA),
             ("Gana el menor precio", "que cumpla · Ley 1474 de 2011, art. 94", EMBER))
    for i, (t1, t2, col) in enumerate(items):
        b = ease(p * 2.8 - 0.4 - i * 0.5)
        y = 470 + i * 300
        d.rounded_rectangle((110, y, W - 110, y + 240), 40, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, col, b), width=5)
        texto_c(d, y + 50, t1, F_DISP(84 if len(t1) < 12 else 66, 800), mezcla(NIGHT, col, b))
        texto_c(d, y + 160, t2, F_BODY(36, 500), mezcla(NIGHT, MUTED, b))


def escena_carpeta(d, p, prm):
    a = ease(p * 2.5)
    etiqueta(d, 280, "TU CARPETA, LISTA DESDE HOY", EMBER, a)
    items = ["RUT", "Cámara de Comercio", "Seguridad social al día", "Antecedentes", "Cotización base"]
    for i, t in enumerate(items):
        b = ease(p * 3.2 - 0.3 - i * 0.38)
        y = 420 + i * 150
        d.rounded_rectangle((150, y, W - 150, y + 120), 30, fill=mezcla(NIGHT, NIGHT2, b))
        d.rounded_rectangle((185, y + 25, 255, y + 95), 16, outline=mezcla(NIGHT, SEA, b), width=5)
        if b > 0.6:
            d.line([(200, y + 60), (217, y + 78), (243, y + 40)], fill=SEA, width=8)
        d.text((290, y + 30), t, font=F_DISP(58, 750), fill=mezcla(NIGHT, SALT, b))


def escena_ejemplo(d, p, prm):
    a = ease(p * 2.6)
    texto_c(d, 290, "EJEMPLO DE ESTA SEMANA", F_MONO(34), mezcla(NIGHT, SEA, a))
    texto_c(d, 350, "Valledupar", F_DISP(128), mezcla(NIGHT, SALT, a), cx=W / 2 + 80 * (1 - a))
    texto_c(d, 505, "Rama Judicial · Cesar", F_BODY(50, 500), mezcla(NIGHT, MUTED, a))
    b = ease((p - 0.08) * 2.6)
    x0, x1, y0, y1 = 90, W - 90, 610, 940
    d.rounded_rectangle((x0, y0, x1, y1), 36, fill=mezcla(NIGHT, NIGHT2, b),
                        outline=mezcla(NIGHT, SEA, b * 0.7), width=3)
    f = F_DISP(52, 750)
    lineas = envolver(d, "Mantenimiento de sedes judiciales en Chimichagua y Manaure", f, x1 - x0 - 80)[:3]
    for i, ln in enumerate(lineas):
        texto_c(d, y0 + 40 + i * 66, ln, f, mezcla(NIGHT, SALT, b))
    texto_c(d, y0 + 70 + len(lineas) * 66, "Mínima cuantía · MC-VA-18-2026", F_BODY(36, 500), mezcla(NIGHT, MUTED, b))
    c = ease((p - 0.2) * 2.6)
    texto_c(d, 975, "$175 millones", F_DISP(96, 850), mezcla(NIGHT, EMBER, c))
    s = "Cierra el martes 24 de noviembre"
    fm = F_DISP(46, 700)
    w = d.textlength(s, font=fm)
    d.rounded_rectangle((W / 2 - w / 2 - 36, 1140, W / 2 + w / 2 + 36, 1226), 43, fill=mezcla(NIGHT, SEA, c))
    texto_c(d, 1156, s, fm, mezcla(SEA, NIGHT, c))


def escena_total(d, p, prm):
    n = int(prm["n"] * ease(p * 2.2))
    a = ease(p * 3)
    texto_c(d, 330, "Hoy, en el Caribe", F_BODY(48, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 430, str(n), F_DISP(330, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 820, "procesos de mínima", F_DISP(76, 750), mezcla(NIGHT, SALT, a))
    texto_c(d, 910, "cuantía abiertos", F_DISP(76, 750), mezcla(NIGHT, SALT, a))
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1030, "por $1.798 millones", F_DISP(60, 650), mezcla(NIGHT, EMBER, b))
    f = F_MONO(36)
    s = "MAREAPUBLICA.COM › LICITACIONES"
    w = d.textlength(s, font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 30, 1150, W / 2 + w / 2 + 30, 1220), 34,
                        outline=mezcla(NIGHT, SEA, b), width=3)
    texto_c(d, 1164, s, f, mezcla(NIGHT, SEA, b))


def escena_cierre(d, p, prm):
    a = ease(p * 2.5)
    s = 150
    x, y = W / 2 - s / 2, 380
    d.rounded_rectangle((x, y, x + s, y + s), 36, fill=mezcla(NIGHT, EMBER, a))
    for k in range(3):
        yy = y + 50 + k * 26
        pts = [(x + 22 + j * 6, yy + 8 * math.sin(j / 3.2)) for j in range(19)]
        d.line(pts, fill=mezcla(EMBER, SALT, a), width=6)
    texto_c(d, 600, "Guárdalo para tu", F_DISP(76, 750), mezcla(NIGHT, SALT, a))
    texto_c(d, 690, "próxima oferta", F_DISP(76, 750), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.15) * 2.5)
    f = F_DISP(84, 800)
    w = d.textlength("mareapublica.com", font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 40, 850, W / 2 + w / 2 + 40, 980), 30, fill=mezcla(NIGHT, SEA, b))
    texto_c(d, 868, "mareapublica.com", f, mezcla(SEA, NIGHT, b))
    c = ease((p - 0.35) * 2.5)
    texto_c(d, 1210, "Datos de SECOP II al 20-nov-2026", F_BODY(30, 400), mezcla(NIGHT, MUTED, c))
    texto_c(d, 1255, "Voz generada con IA", F_BODY(28, 400), mezcla(NIGHT, MUTED, c * 0.8))


rs.guion = guion
rs.VOZ = rs.VOZ_HOMBRE
rs.PERFIL = "mipymes"
rs.PRONUNCIACION.update({"RUP": "rup", "RUT": "rut"})
rs.DIBUJA.update({"plazo": escena_plazo, "reglas": escena_reglas, "carpeta": escena_carpeta,
                  "ejemplo": escena_ejemplo, "total": escena_total, "cierre": escena_cierre})
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "temas", "documentos-1.mp4")

if __name__ == "__main__":
    rs.main()
