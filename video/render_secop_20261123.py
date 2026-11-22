#!/usr/bin/env python3
"""Marea Pública · Cómo leer SECOP: el supervisor del contrato (pieza MP-20261125-IG).

Guion aprobado por Juan Camilo el 22-nov-2026. Motor de render_semana.py (voz de mujer).
Las cifras se leen de site/data.json (bloque "E": contratos con supervisor "No definido",
entidades no nacionales con 15 o más contratos) y se comprueban contra el guion aprobado.

Uso: python video/render_secop_20261123.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
import escenas_20261123 as ec
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER, ease, mezcla, texto_c,
                           F_DISP, F_BODY, F_MONO)

CORTE = "Datos de SECOP II al 22-nov-2026"


def escena_ficha(d, p, prm):
    a = ease(p * 2.5)
    x0, x1, y0 = 110, W - 110, 300
    d.rounded_rectangle((x0, y0, x1, y0 + 760), 32, fill=mezcla(NIGHT, NIGHT2, a),
                        outline=mezcla(NIGHT, SEA, a * 0.6), width=3)
    d.text((x0 + 50, y0 + 40), "CONTRATO · SECOP II", font=F_MONO(32), fill=mezcla(NIGHT, SEA, a))
    campos = [("Entidad", "Alcaldía de ……"), ("Objeto", "Prestación de servicios ……"),
              ("Valor", "$ ……"), ("Fecha de firma", "…… de 2026"), ("Supervisor", "No definido")]
    for i, (k, v) in enumerate(campos):
        b = ease(p * 2.8 - 0.2 - i * 0.12)
        y = y0 + 120 + i * 120
        ultimo = i == len(campos) - 1
        if ultimo:
            c = ease((p - 0.45) * 3)
            d.rounded_rectangle((x0 + 30, y - 16, x1 - 30, y + 100), 20, outline=mezcla(NIGHT, EMBER, c), width=5)
        d.text((x0 + 60, y), k, font=F_BODY(32, 500), fill=mezcla(NIGHT, MUTED, b))
        d.text((x0 + 60, y + 40), v, font=F_DISP(46, 750),
               fill=mezcla(NIGHT, EMBER if ultimo else SALT, b))
    c = ease((p - 0.5) * 3)
    texto_c(d, 1110, "Ficha de ejemplo, sin datos reales", F_BODY(30, 400), mezcla(NIGHT, MUTED, c))


def escena_rol(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 300, "El supervisor", F_DISP(100), mezcla(NIGHT, SALT, a))
    texto_c(d, 420, "vigila que el contrato se cumpla", F_BODY(44, 600), mezcla(NIGHT, MUTED, a))
    for i, (t1, t2) in enumerate((("Lo pactado", "se entrega"), ("A tiempo", "según el plazo"),
                                  ("Al precio", "acordado"))):
        b = ease(p * 2.8 - 0.4 - i * 0.3)
        y = 560 + i * 200
        d.rounded_rectangle((150, y, W - 150, y + 160), 36, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, SEA, b), width=3)
        d.ellipse((190, y + 40, 270, y + 120), fill=mezcla(NIGHT, EMBER, b))
        d.line([(210, y + 82), (226, y + 98), (252, y + 62)], fill=NIGHT, width=8)
        d.text((310, y + 30), t1, font=F_DISP(60, 800), fill=mezcla(NIGHT, SALT, b))
        d.text((310, y + 100), t2, font=F_BODY(36, 500), fill=mezcla(NIGHT, MUTED, b))


def escena_pasos(d, p, prm):
    a = ease(p * 2.5)
    texto_c(d, 300, "Cómo revisarlo", F_DISP(96), mezcla(NIGHT, SALT, a))
    for i, t1 in enumerate(("Abre el contrato en SECOP II", "Entra a los documentos",
                            "Busca la designación de supervisión")):
        b = ease(p * 2.8 - 0.3 - i * 0.35)
        y = 470 + i * 200
        d.rounded_rectangle((110, y, W - 110, y + 160), 36, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, SEA if i < 2 else EMBER, b), width=4)
        d.ellipse((150, y + 35, 240, y + 125), fill=mezcla(NIGHT, SEA if i < 2 else EMBER, b))
        texto_c(d, y + 42, str(i + 1), F_DISP(64), NIGHT, cx=195)
        d.text((275, y + 50), t1, font=F_DISP(48, 750), fill=mezcla(NIGHT, SALT, b))


def guion(data):
    deps = data["deps"]
    F = [r for r in data["E"] if len(r) > 11 and r[4] != "N"]
    n = {i: sum(r[5] for r in F if r[2] == i) for i in range(len(deps))}
    s = {i: sum(r[11] for r in F if r[2] == i) for i in range(len(deps))}
    pct = {rs.CORTO.get(deps[i], deps[i]): 100 * s[i] / n[i] for i in n}
    caribe = 100 * sum(s.values()) / sum(n.values())
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    assert round(pct["Bolívar"] / 10) == 3 and round(caribe) == 16 and round(pct["Córdoba"]) == 1, (pct, caribe)
    assert max(pct, key=pct.get) == "Bolívar" and min(pct, key=pct.get) == "Córdoba"

    filas = sorted(((k, v, "") for k, v in pct.items()), key=lambda r: -r[1])
    escenas = [
        ("intro", "[curious] En Bolívar, 3 de cada 10 contratos aparecen en SECOP sin supervisor definido.",
         {"rango": "CÓMO LEER SECOP",
          "banda": {"arriba": ["3 de cada 10", "sin supervisor"], "abajo": ["en Bolívar"]}}),
        ("ficha", "¿Qué quiere decir eso?", {}),
        ("rol", "[short pause] El supervisor es la persona de la entidad que vigila que el contrato se cumpla: "
                "que se entregue lo pactado, a tiempo y por el precio acordado.", {}),
        ("barras", "En los datos abiertos de SECOP II ese campo debería tener un nombre. "
                   "En el Caribe, 16 de cada 100 contratos dicen \"No definido\". En Córdoba, apenas 1.",
         {"titulo": "% de contratos con supervisor", "sub": "\"No definido\" · desde enero de 2024",
          "filas": filas, "hi": {"Bolívar"}, "lo": {"Córdoba"},
          "nota": "Entidades territoriales con 15 contratos o más"}),
        ("frases", "[calmly] Ojo: no quiere decir que nadie lo vigile. Muchas veces el supervisor se designa "
                   "en un documento aparte y no se actualiza en la plataforma. Pero es un dato público y debería estar.",
         {"lineas": [("No quiere decir", 84, SALT), ("que nadie lo vigile.", 84, SALT), ("", 40, SALT),
                     ("Puede estar en", 70, MUTED), ("un documento aparte.", 70, MUTED), ("", 40, SALT),
                     ("Pero debería estar.", 100, EMBER)]}),
        ("pasos", "Para revisarlo, abre el contrato en SECOP II y busca la designación de supervisión en los documentos.",
         {}),
        ("cierre", "[warmly] Guárdalo para cuando revises un contrato de tu municipio.",
         {"linea": "Guárdalo para revisar tu municipio", "corte": CORTE}),
    ]
    return escenas, ""  # el caption aprobado va en bot/cola/2026-11-25_secop.json


rs.guion = guion
rs.VOZ = rs.VOZ_MUJER
rs.PERFIL = "veeduria"
rs.DIBUJA.update(ec.COMUNES)
rs.DIBUJA.update({"ficha": escena_ficha, "rol": escena_rol, "pasos": escena_pasos})
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "temas", "documentos-1.mp4")

if __name__ == "__main__":
    rs.main()
