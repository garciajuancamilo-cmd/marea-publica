#!/usr/bin/env python3
"""Marea Pública · Ranking: gobernaciones del Caribe por % del valor en contratación directa
(pieza MP-20261126-IG).

Guion aprobado por Juan Camilo el 22-nov-2026. Motor de render_semana.py (voz de mujer).
Las cifras se leen de site/data.json (bloque "E") y se comprueban contra el guion aprobado.

Uso: python video/render_ranking_20261123.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
import escenas_20261123 as ec
from render_semana import SALT, MUTED, EMBER

CORTE = "Datos de SECOP II al 22-nov-2026"
GOBERNACIONES = {
    "892400038": "San Andrés", "8921150151": "La Guajira", "890102006": "Atlántico",
    "890480059": "Bolívar", "800103935": "Córdoba", "892280021": "Sucre",
    "800103920": "Magdalena", "892399999": "Cesar",
}
APROBADO = {"San Andrés": 55, "La Guajira": 46, "Atlántico": 40, "Bolívar": 40, "Córdoba": 36,
            "Sucre": 31, "Magdalena": 29, "Cesar": 17}
DEUDA = {"Bolívar", "Córdoba", "Sucre"}  # su mayor contrato directo es un empréstito (bloque "big")


def guion(data):
    por_nit = {e[0]: e for e in data["E"] if len(e) > 8}
    pv = {g: 100 * por_nit[n][8] / por_nit[n][6] for n, g in GOBERNACIONES.items()}
    pn = {g: 100 * por_nit[n][7] / por_nit[n][5] for n, g in GOBERNACIONES.items()}
    # Comprobación: las cifras del guion aprobado deben salir de los datos
    for g, v in APROBADO.items():
        assert round(pv[g]) == v, (g, pv[g])
    assert min(pn.values()) > 80, pn
    for n, g in GOBERNACIONES.items():
        if g in DEUDA:
            assert "mpr" in data["big"][n][4].lower(), (g, data["big"][n])

    filas = sorted(((g, v, "*" if g in DEUDA else "") for g, v in pv.items()), key=lambda r: -r[1])
    filas_n = sorted(((g, v, "") for g, v in pn.items()), key=lambda r: -r[1])
    escenas = [
        ("intro", "[seriously] La Gobernación del Cesar contrata 17 de cada 100 pesos de forma directa. "
                  "La de San Andrés, 55.",
         {"rango": "ENE 2024 – NOV 2026",
          "banda": {"arriba": ["Cesar: 17", "San Andrés: 55"], "abajo": ["de cada 100 pesos"]}}),
        ("barras", "[short pause] Este es el ranking de las 8 gobernaciones del Caribe desde 2024: San Andrés 55. "
                   "La Guajira 46. Atlántico 40. Bolívar 40. Córdoba 36. Sucre 31. Magdalena 29. Y Cesar 17.",
         {"titulo": "% del valor por contratación directa", "sub": "Gobernaciones · desde enero de 2024",
          "filas": filas, "hi": {"San Andrés"}, "lo": {"Cesar"},
          "nota": "* Incluye créditos de deuda pública, directos por ley"}),
        ("barras", "Pero mira esto: si cuentas contratos y no pesos, todas pasan de 80 de cada 100.",
         {"titulo": "% de contratos directos", "sub": "Gobernaciones · desde enero de 2024",
          "filas": filas_n, "hi": set(), "lo": set(), "nota": "Contando contratos, no pesos"}),
        ("frases", "[calmly] La mayoría son contratos pequeños de servicios profesionales, y en Bolívar, Córdoba y Sucre "
                   "la cifra incluye créditos de deuda pública, que por ley son directos.",
         {"lineas": [("Muchos contratos", 96, SALT), ("pequeños", 96, EMBER), ("", 40, SALT),
                     ("Bolívar, Córdoba y Sucre:", 60, MUTED), ("incluye deuda pública,", 60, MUTED),
                     ("directa por ley", 60, MUTED)]}),
        ("cierre", "[warmly] Guárdalo, envíaselo a alguien de tu departamento y cuéntanos: ¿te sorprende el tuyo?",
         {"linea": "¿Te sorprende el tuyo?", "corte": CORTE}),
    ]
    return escenas, ""  # el caption aprobado va en bot/cola/2026-11-26_ranking.json


rs.guion = guion
rs.VOZ = rs.VOZ_MUJER
rs.PERFIL = "veeduria"
rs.DIBUJA.update(ec.COMUNES)
# Toma de apertura: río (paisaje, sin edificios públicos).
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "ciudades", "monteria-rio-1.mp4")

if __name__ == "__main__":
    rs.main()
