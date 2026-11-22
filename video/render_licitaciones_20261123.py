#!/usr/bin/env python3
"""Marea Pública · Licitaciones abiertas del martes 24 de noviembre de 2026 (pieza MP-20261124-IG).

Guion aprobado por Juan Camilo el 22-nov-2026. Motor de render_semana.py (voz de hombre, música MiPymes).
Las cifras se leen de site/data.json (bloque "lic") y se comprueban contra el guion aprobado.

Uso: python video/render_licitaciones_20261123.py [salida.mp4]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_semana as rs
import escenas_20261123 as ec
from render_semana import (W, NIGHT, NIGHT2, SALT, MUTED, SEA, EMBER, ease, mezcla, texto_c,
                           F_DISP, F_BODY, F_MONO)

CORTE = "Datos de SECOP II al 22-nov-2026"
# noticeUID, municipio, departamento, objeto corto, entidad corta, valor (millones), cierre
PROCESOS = [
    ("CO1.NTC.11241237", "Fundación", "Magdalena", "Alcantarillado del barrio La Esperanza",
     "Alcaldía de Fundación", 427.0, "2026-12-01"),
    ("CO1.NTC.11240280", "Riohacha", "La Guajira", "Demolición de tanques elevados en Cotoprix",
     "Alcaldía de Riohacha", 176.6, "2026-12-02"),
    ("CO1.NTC.11246926", "El Carmen de Bolívar", "Bolívar", "Mobiliario para instituciones educativas",
     "Alcaldía de El Carmen de Bolívar", 231.8, "2026-12-03"),
    ("CO1.NTC.11240976", "Barranquilla", "Atlántico", "Uniformes y elementos de protección",
     "Instituto de Tránsito del Atlántico", 173.4, "2026-12-04"),
]


def escena_total(d, p, prm):
    n = int(prm["n"] * ease(p * 2.2))
    a = ease(p * 3)
    texto_c(d, 330, "Caribe colombiano", F_BODY(48, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 430, str(n), F_DISP(330, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 820, "procesos abiertos", F_DISP(76, 750), mezcla(NIGHT, SALT, a))
    texto_c(d, 910, "a la medida de una MiPyme", F_DISP(60, 650), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 1030, "Selección abreviada", F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    texto_c(d, 1082, "hasta $500 millones", F_BODY(38, 500), mezcla(NIGHT, MUTED, b))
    ec.pastilla(d, 1170, "CIERRAN DESDE EL 27 DE NOVIEMBRE", F_MONO(34), mezcla(NIGHT, EMBER, b))


def escena_aviso(d, p, prm):
    a = ease(p * 2.5)
    ec.pastilla(d, 290, "OJO", F_MONO(34), mezcla(NIGHT, EMBER, a), True, mezcla(EMBER, SALT, a))
    texto_c(d, 410, "Selección abreviada", F_DISP(84), mezcla(NIGHT, SALT, a))
    texto_c(d, 510, "de menor cuantía", F_DISP(84), mezcla(NIGHT, SALT, a))
    for i, (num, t1) in enumerate((("1", "Manifiesta interés"), ("2", "Presenta tu oferta"))):
        b = ease(p * 2.8 - 0.5 - i * 0.45)
        y = 660 + i * 190
        d.rounded_rectangle((130, y, W - 130, y + 150), 36, fill=mezcla(NIGHT, NIGHT2, b),
                            outline=mezcla(NIGHT, SEA if i == 0 else EMBER, b), width=4)
        d.ellipse((170, y + 30, 260, y + 120), fill=mezcla(NIGHT, SEA if i == 0 else EMBER, b))
        texto_c(d, y + 36, num, F_DISP(64), NIGHT, cx=215)
        d.text((300, y + 40), t1, font=F_DISP(64, 750), fill=mezcla(NIGHT, SALT, b))
    c = ease((p - 0.45) * 2.5)
    texto_c(d, 1080, "Revisa hoy el cronograma", F_BODY(44, 600), mezcla(NIGHT, SEA, c))
    texto_c(d, 1140, "en SECOP II", F_BODY(44, 500), mezcla(NIGHT, MUTED, c))


def guion(data):
    lic, deps = data["lic"], data["deps"]
    assert data["meta"]["lic_fecha"] == "2026-11-22", "El guion aprobado usa las licitaciones del 22-nov-2026"
    aptos = [l for l in lic if str(l[7])[:10] >= "2026-11-27" and l[4] in ("S", "M") and l[5] and l[5] <= 500]
    assert len(aptos) == 43, len(aptos)
    por_uid = {l[8]: l for l in lic}
    for uid, mun, dep, _, _, val, cierre in PROCESOS:
        l = por_uid[uid]
        assert deps[l[1]] == dep and abs(l[5] - val) < 0.05 and str(l[7])[:10] == cierre, (uid, l)

    t = [
        "En Fundación, Magdalena: alcantarillado para el barrio La Esperanza, 427 millones. Cierra el 1 de diciembre.",
        "En Riohacha: demolición de tanques elevados en Cotoprix, 176 millones. Cierra el 2.",
        "En El Carmen de Bolívar: mobiliario para los colegios, 231 millones. Cierra el 3.",
        "Y el Tránsito del Atlántico compra uniformes por 173 millones. Cierra el 4.",
    ]
    escenas = [
        ("intro", "[confident] 43 procesos públicos abiertos en el Caribe a la medida de una MiPyme.",
         {"rango": "LICITACIONES · 24 NOV",
          "banda": {"arriba": ["43 procesos", "abiertos"], "abajo": ["para MiPymes"]}}),
        ("total", "Y todavía hay tiempo. [short pause] Te muestro cuatro.", {"n": 43}),
    ]
    for k, (pr, txt) in enumerate(zip(PROCESOS, t)):
        uid, mun, dep, obj, ent, val, cierre = pr
        escenas.append(("tarjeta", txt, {"k": k, "n": 4, "mun": mun, "dep": dep, "obj": obj, "ent": ent,
                                         "val": val, "cierre": cierre}))
    escenas += [
        ("aviso", "[seriously] Ojo: en la selección abreviada de menor cuantía primero hay que manifestar interés. "
                  "Revisa el cronograma hoy.", {}),
        ("alertas", "[warmly] ¿Quieres que te avisemos cuando abra algo de tu sector? "
                    "Inscríbete gratis en las alertas: enlace en la bio.", {"corte": CORTE}),
    ]
    return escenas, ""  # el caption aprobado va en bot/cola/2026-11-24_licitaciones.json


rs.guion = guion
rs.VOZ = rs.VOZ_HOMBRE
rs.PERFIL = "mipymes"
rs.DIBUJA.update(ec.COMUNES)
rs.DIBUJA.update({"total": escena_total, "aviso": escena_aviso})
rs.elegir_toma = lambda perfil: os.path.join(rs.RAIZ, "video", "tomas", "temas", "portatil-datos-1.mp4")

if __name__ == "__main__":
    rs.main()
