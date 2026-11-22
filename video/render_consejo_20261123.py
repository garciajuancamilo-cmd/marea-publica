#!/usr/bin/env python3
"""Marea Pública · Consejo MiPyme: oferta donde compiten pocos (pieza MP-20261127-IG).

Guion aprobado por Juan Camilo el 22-nov-2026. Motor de render_semana.py (voz de hombre, música MiPymes).
Las cifras se leen de site/data.json (bloques "comp.seg" y "lic") y se comprueban contra el guion aprobado.

Uso: python video/render_consejo_20261123.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
import escenas_20261123 as ec
from render_semana import SALT, MUTED, EMBER, SEA

CORTE = "Datos de SECOP II al 22-nov-2026"
UID = "CO1.NTC.11246952"


def guion(data):
    seg, deps = data["comp"]["seg"], data["deps"]
    pct = {k: 100 * u / t for k, (t, u) in seg.items()}
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    assert round(pct["90"]) == 46, seg["90"]
    assert round(pct["78"]) == 62 and round(pct["56"]) == 20, (pct["78"], pct["56"])
    l = {x[8]: x for x in data["lic"]}[UID]
    assert deps[l[1]] == "Córdoba" and abs(l[5] - 150) < 0.05 and l[7] == "2026-12-03", l

    filas = [("Transporte", pct["78"], ""), ("Eventos", pct["90"], ""), ("Muebles", pct["56"], "")]
    escenas = [
        ("intro", "[confident] En logística y eventos, casi la mitad de los procesos públicos del Caribe "
                  "llegó con una sola oferta.",
         {"rango": "CONSEJO MIPYME",
          "banda": {"arriba": ["46 de 100", "en eventos"], "abajo": ["con una sola oferta"]}}),
        ("frases", "[short pause] El consejo de hoy: antes de decidir dónde ofertar, mira cuánta competencia hay en tu sector.",
         {"y": 470, "lineas": [("CONSEJO MIPYME", 44, SEA), ("", 30, SALT), ("Antes de ofertar,", 90, SALT),
                               ("mira cuánta", 90, SALT), ("competencia", 110, EMBER), ("hay en tu sector", 90, SALT)]}),
        ("barras", "En eventos, alimentación y alojamiento, 46 de cada 100 procesos tuvieron un solo oferente. "
                   "En transporte, 62. En muebles, apenas 20: ahí la pelea es dura.",
         {"titulo": "% de procesos con un solo oferente", "sub": "Caribe · desde enero de 2024",
          "filas": filas, "hi": {"Transporte", "Eventos"}, "lo": {"Muebles"},
          "nota": "Sector estimado según el objeto del proceso"}),
        ("tarjeta", "Ejemplo de esta semana: Cereté, en Córdoba, busca operador logístico para las actividades "
                    "de Navidad con los niños. 150 millones. Cierra el 3 de diciembre.",
         {"k": 0, "kicker": "EJEMPLO ABIERTO", "mun": "Cereté", "dep": "Córdoba",
          "obj": "Operador logístico para actividades de Navidad", "ent": "Municipio de Cereté",
          "val": 150.0, "cierre": "2026-12-03"}),
        ("alertas", "[warmly] Te avisamos cuando abra algo de tu sector: alertas gratis, enlace en la bio.",
         {"corte": CORTE}),
    ]
    return escenas, ""  # el caption aprobado va en bot/cola/2026-11-27_consejo.json


rs.guion = guion
rs.VOZ = rs.VOZ_HOMBRE
rs.PERFIL = "mipymes"
rs.DIBUJA.update(ec.COMUNES)
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "temas", "taller-mipyme-1.mp4")

if __name__ == "__main__":
    rs.main()
