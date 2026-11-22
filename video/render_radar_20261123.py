#!/usr/bin/env python3
"""Marea Pública · Radar de la semana del 15 al 22 de noviembre de 2026 (pieza MP-20261123-IG).

Guion aprobado por Juan Camilo el 22-nov-2026. Motor de render_semana.py (voz de mujer).
Las cifras se leen de site/data.json (bloque "sem") y se comprueban contra el guion aprobado.

Uso: python video/render_radar_20261123.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
import escenas_20261123 as ec
from render_semana import SEA, EMBER

CORTE = "Datos de SECOP II al 22-nov-2026"


def guion(data):
    s, deps = data["sem"], data["deps"]
    assert s["desde"] == "2026-11-15", "El guion aprobado es de la semana del 15 al 22 de noviembre"
    tot = [x[0] for x in s["total"]]
    dirn = [x[0] for x in s["directa"]]
    vt = sum(x[1] for x in s["total"])
    vd = sum(x[1] for x in s["directa"])
    i_at, i_lg = deps.index("Atlántico"), deps.index("La Guajira")
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    assert (dirn[i_at], tot[i_at]) == (437, 516), (dirn[i_at], tot[i_at])
    assert round(100 * dirn[i_lg] / tot[i_lg]) == 29
    assert round(10 * sum(dirn) / sum(tot)) == 7 and round(100 * vd / vt) == 27

    filas = sorted(((rs.CORTO.get(d, d), 100 * dirn[i] / tot[i], "") for i, d in enumerate(deps) if tot[i] >= 30),
                   key=lambda r: -r[1])
    assert filas[0][0] == "Atlántico" and filas[-1][0] == "La Guajira"
    escenas = [
        ("intro", "[seriously] 85 de cada 100. Así contrató Atlántico esta semana: casi todo por contratación directa.",
         {"rango": "15 NOV – 22 NOV",
          "banda": {"arriba": ["85 de 100", "en Atlántico"], "abajo": ["contratos directos"]}}),
        ("cien", "[short pause] Del 15 al 22 de noviembre, Atlántico firmó 437 de sus 516 contratos de forma directa. "
                 "Es el porcentaje más alto del Caribe.",
         {"n": 85, "grande": "437 de 516", "sub": "el % más alto del Caribe"}),
        ("barras", "En el otro extremo está La Guajira, con 29 de cada 100.",
         {"titulo": "% de contratos directos", "sub": "15 al 22 de noviembre", "filas": filas,
          "hi": {"Atlántico"}, "lo": {"La Guajira"},
          "nota": "Departamentos con 30 contratos o más en la semana"}),
        ("dos", "Y un detalle que casi nadie mira: en todo el Caribe, 7 de cada 10 contratos fueron directos, "
                "pero solo 27 de cada 100 pesos. Son muchos contratos pequeños, sobre todo de servicios profesionales.",
         {"titulo": "Caribe", "sub": "contratación directa de la semana",
          "barras": [("de los contratos", 100 * sum(dirn) / sum(tot), EMBER), ("del valor", 100 * vd / vt, SEA)],
          "remate": "Muchos contratos pequeños"}),
        ("legal", "[calmly] La contratación directa es legal en varios casos. No es una falla por sí sola; "
                  "es una señal para revisar.", {}),
        ("cierre", "[warmly] Busca tu municipio gratis en mareapublica.com y envíale este video a alguien de Atlántico.",
         {"linea": "Envíaselo a alguien de Atlántico", "corte": CORTE}),
    ]
    return escenas, ""  # el caption aprobado va en bot/cola/2026-11-23_radar.json


rs.guion = guion
rs.VOZ = rs.VOZ_MUJER
rs.PERFIL = "veeduria"
rs.DIBUJA.update(ec.COMUNES)
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "ciudades", "barranquilla-rio-1.mp4")

if __name__ == "__main__":
    rs.main()
