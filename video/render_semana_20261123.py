#!/usr/bin/env python3
"""Marea Pública · renderiza en una sola corrida los 5 reels aprobados para el 23 al 27 de noviembre de 2026.

Cada video se genera en un proceso aparte (cada script ajusta el motor de render_semana.py a su manera)
y queda en salida/<pieza>/<pieza>-AAAAMMDD.mp4, con su voz, guion y caption de control.

Uso (workflow "Video de prueba", script=render_semana_20261123): python video/render_semana_20261123.py salida/x.mp4
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PIEZAS = [("radar", "20261123"), ("licitaciones", "20261124"), ("secop", "20261125"),
          ("ranking", "20261126"), ("consejo", "20261127")]

base = os.path.dirname(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
fallos = []
for nombre, fecha in PIEZAS:
    out = os.path.join(base, nombre, f"{nombre}-{fecha}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print(f"=== {nombre} ===", flush=True)
    r = subprocess.run([sys.executable, os.path.join(AQUI, f"render_{nombre}_20261123.py"), out])
    if r.returncode:
        fallos.append(nombre)
if fallos:
    sys.exit(f"Fallaron: {', '.join(fallos)}")
