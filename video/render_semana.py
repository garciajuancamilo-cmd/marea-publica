#!/usr/bin/env python3
"""Marea Pública · video del lunes (resumen semanal).

Lee site/data.json (bloque "sem"), escribe el guion, genera la voz con
ElevenLabs (si hay ELEVENLABS_API_KEY) y renderiza un MP4 vertical 1080x1920.
Sin clave usa audio en silencio y tiempos estimados (sirve para probar el diseño).

Uso: python video/render_semana.py [salida.mp4]
"""
import base64, json, math, os, re, subprocess, sys, unicodedata, urllib.request
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "video", "fonts")
W, H, FPS = 1080, 1920, 30

VOZ_MUJER = "Ut5x3LuSfExdBqv3rEz7"   # Marea Pública · Voz mujer (veeduría)
VOZ_HOMBRE = "vY4YbSJxUDECdZsKPrF6"  # Marea Pública · Voz hombre (MiPymes)
VOZ = VOZ_MUJER
MODELO_USADO = "ninguno"

# Paleta de la página (modo oscuro)
NIGHT = (11, 42, 51)
NIGHT2 = (16, 56, 66)
SALT = (238, 243, 242)
MUTED = (150, 178, 182)
SEA = (92, 188, 192)
EMBER = (226, 92, 44)

MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
CORTO = {"San Andrés, Providencia y Santa Catalina": "San Andrés"}
ART = {"Atlántico": "el Atlántico", "Cesar": "el Cesar", "La Guajira": "La Guajira"}
def con_art(dep): return ART.get(dep, dep)


# ---------- utilidades de texto ----------
def font(nombre, size, peso=None):
    f = ImageFont.truetype(os.path.join(FUENTES, nombre), size)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f

def F_DISP(s, w=800): return font("SchibstedGrotesk.ttf", s, w)
def F_BODY(s, w=500): return font("PublicSans.ttf", s, w)
def F_MONO(s): return font("IBMPlexMono-Medium.ttf", s)

UNI = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
       "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete",
       "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós", "veintitrés",
       "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
DEC = ["", "", "", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]
CEN = ["", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
       "seiscientos", "setecientos", "ochocientos", "novecientos"]

def letras(n):
    n = int(n)
    if n < 30: return UNI[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEC[d] + ("" if u == 0 else " y " + UNI[u])
    if n == 100: return "cien"
    if n < 1000:
        c, r = divmod(n, 100)
        return CEN[c] + ("" if r == 0 else " " + letras(r))
    if n < 1_000_000:
        m, r = divmod(n, 1000)
        base = "mil" if m == 1 else letras(m).replace("uno", "un") + " mil"
        return base + ("" if r == 0 else " " + letras(r))
    return str(n)

def miles(n): return f"{int(n):,}".replace(",", ".")

def fecha_larga(iso):
    a, m, d = iso.split("-")
    return int(d), MESES[int(m)]


# ---------- guion ----------
def guion(data):
    s = data["sem"]
    deps = data["deps"]
    tot = [x[0] for x in s["total"]]
    dirn = [x[0] for x in s["directa"]]
    T, D = sum(tot), sum(dirn)
    pct = round(100 * D / T)
    de10 = round(10 * D / T)
    d1, m1 = fecha_larga(s["desde"])
    d2, m2 = fecha_larga(s["hasta"])
    rango = f"{d1} de {m1}" if m1 != m2 else f"{d1}"
    filas = []
    for i, dep in enumerate(deps):
        if tot[i] >= 30:
            filas.append((CORTO.get(dep, dep), round(100 * dirn[i] / tot[i]), tot[i]))
    filas.sort(key=lambda r: -r[1])
    grandes = [f for f in filas if f[2] >= 100]
    alto1, alto2 = grandes[0], grandes[1]
    bajo = grandes[-1]

    escenas = [
        ("intro", f"[warmly] Semana del {rango} al {d2} de {m2}. Así contrataron las entidades públicas del Caribe colombiano.",
         {"rango": f"{d1} {m1[:3].upper()} – {d2} {m2[:3].upper()}"}),
        ("conteo", f"Firmaron… [short pause] {miles(T)} contratos en SECOP.", {"n": T}),
        ("grilla", f"{miles(D)} fueron por contratación directa. "
                   f"[seriously] {('Casi ' + letras(de10)) if de10 * 10 > pct + 1 else letras(de10).capitalize()} de cada diez, SIN competencia entre empresas.",
         {"pct": pct, "de10": de10, "D": D}),
        ("barras", f"[pause] En {con_art(alto1[0])} llegó al {alto1[1]} %. "
                   f"En {con_art(alto2[0])}, al {alto2[1]} %. "
                   f"La excepción fue {con_art(bajo[0])}: {bajo[1]} %.",
         {"filas": filas, "hi": {alto1[0], alto2[0]}, "lo": {bajo[0]}}),
        ("idea", "[calmly] La contratación directa es legal, y a veces se justifica… "
                 "pero cuando se vuelve la regla, menos empresas pueden competir.", {}),
        ("cierre", "[warmly] Busca tu municipio en mareapublica.com. [short pause] Esto es Marea Pública.", {}),
    ]
    caption = (
        f"📊 Semana del {d1} de {m1} al {d2} de {m2} en el Caribe colombiano\n\n"
        f"Las entidades públicas firmaron {miles(T)} contratos en SECOP II. "
        f"{miles(D)} ({pct} %) fueron por contratación directa, sin competencia entre empresas.\n\n"
        f"Más alto: {alto1[0]} ({alto1[1]} %) y {alto2[0]} ({alto2[1]} %). Más bajo: {bajo[0]} ({bajo[1]} %).\n\n"
        "La contratación directa es legal y en muchos casos se justifica. Pero cuando se vuelve la regla, "
        "menos empresas pueden competir.\n\n"
        "🔎 Busca tu municipio en mareapublica.com (link en la bio)\n\n"
        "Fuente: SECOP II, datos abiertos. Cifras preliminares: SECOP publica con rezago. "
        "Son indicadores para revisar, no acusaciones.\n"
        "🎙️ Voz generada con IA.\n\n"
        "#ContrataciónPública #SECOP #Transparencia #CaribeColombiano #Veeduría #MiPymes "
        "#Barranquilla #Cartagena #Colombia"
    )
    return escenas, caption


# ---------- pronunciación ----------
# La voz recibe la forma "hablada"; los subtítulos muestran la forma escrita.
PRONUNCIACION = {
    "MiPymes": "/mi ˈpimes/", "MiPyme": "/mi ˈpime/", "mipymes": "/mi ˈpimes/",
    "SECOP": "/ˈsekop/", "NIT": "/nit/", "UNSPSC": "U N S P S C",
    "Magangué": "/maɣaŋˈɡe/", "Ciénaga": "/ˈsjenaɣa/", "Riohacha": "/rioˈat͡ʃa/",
    "Mompós": "/momˈpos/", "Uribia": "/uˈɾiβja/",
}
ETIQUETA = re.compile(r"\[[^\]]+\]\s*")

def escrito(t):
    """Texto para subtítulos: sin marcas de interpretación."""
    return re.sub(r"\s+", " ", ETIQUETA.sub("", t)).strip()

def hablado(t, con_marcas=True):
    """Texto para la voz: con pronunciación fonética y sin separador de miles."""
    if not con_marcas:
        t = ETIQUETA.sub("", t)
    for k, v in PRONUNCIACION.items():
        t = re.sub(rf"(?<!\w){re.escape(k)}(?!\w)", v, t)
    t = re.sub(r"(\d)\.(\d{3})(?!\d)", r"\1\2", t)
    t = re.sub(r"(\d)\.(\d{3})(?!\d)", r"\1\2", t)
    return t

def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


# ---------- voz ----------
def tts(texto_marcado, voz, salida_mp3):
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        return None
    ultimo = None
    for modelo in ("eleven_v4", "eleven_v3", "eleven_multilingual_v2"):
        con_marcas = modelo != "eleven_multilingual_v2"
        body = {"text": hablado(texto_marcado, con_marcas), "model_id": modelo}
        if not con_marcas:
            body["voice_settings"] = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2}
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), method="POST",
            headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                j = json.load(r)
            al = j.get("alignment") or j.get("normalized_alignment")
            if not al or not al.get("characters"):
                raise RuntimeError("sin marcas de tiempo")
            with open(salida_mp3, "wb") as f:
                f.write(base64.b64decode(j["audio_base64"]))
            print(f"Voz generada con {modelo}")
            global MODELO_USADO
            MODELO_USADO = modelo
            return al
        except Exception as e:
            ultimo = e
            print(f"TTS con {modelo} falló: {e}")
    raise SystemExit(f"No se pudo generar la voz: {ultimo}")

def duracion(mp3):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", mp3], capture_output=True, text=True).stdout
    return float(out.strip())

def tiempos_palabras(palabras, al, total):
    """(inicio, fin) de cada palabra escrita, buscándola en el audio en orden.
    Las palabras con pronunciación fonética o no encontradas se interpolan."""
    n = len(palabras)
    res = [None] * n
    if al:
        chars = al["characters"]; ini = al["character_start_times_seconds"]; fin = al["character_end_times_seconds"]
        # palabras del audio con sus tiempos (sin marcas)
        aw, cur, t0, t1, dentro = [], "", None, None, 0
        for c, a, b in zip(chars, ini, fin):
            if c == "[":
                dentro += 1
            if dentro:
                if c == "]":
                    dentro -= 1
                continue
            if c.isspace():
                if cur: aw.append((_norm(cur), t0, t1)); cur = ""
            else:
                if not cur: t0 = a
                cur += c; t1 = b
        if cur: aw.append((_norm(cur), t0, t1))
        j = 0
        for i, w in enumerate(palabras):
            nw = _norm(w)
            if not nw:
                continue
            for k in range(j, min(j + 6, len(aw))):
                if aw[k][0] == nw or (nw and aw[k][0].startswith(nw)) or (aw[k][0] and nw.startswith(aw[k][0])):
                    res[i] = (aw[k][1], aw[k][2]); j = k + 1
                    break
    if not any(res):
        # estimación por longitud
        pesos = [len(w) + (6 if w[-1:] in ".:" else 3 if w[-1:] == "," else 1) for w in palabras]
        k = (total - 0.3) / sum(pesos); t = 0.15
        for i, p in enumerate(pesos):
            res[i] = (t, t + p * k * 0.9); t += p * k
        return res
    # interpolar huecos
    for i in range(n):
        if res[i] is None:
            prev = next((res[k][1] for k in range(i - 1, -1, -1) if res[k]), 0.0)
            nxt = next((res[k][0] for k in range(i + 1, n) if res[k]), total)
            res[i] = (prev, max(prev + 0.15, (prev + nxt) / 2))
    return res


# ---------- dibujo ----------
def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3

def mezcla(c1, c2, a):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

def fondo():
    img = Image.new("RGB", (W, H), NIGHT)
    d = ImageDraw.Draw(img)
    for y in range(H):  # degradado vertical sutil
        d.line([(0, y), (W, y)], fill=mezcla(NIGHT2, NIGHT, y / H))
    return img

FONDO = None

def olas(d, t):
    for k in range(4):
        y0 = 1540 + k * 46
        pts = [(x, y0 + 12 * math.sin(x / 140 + t * 0.9 + k)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=mezcla(NIGHT, SEA, 0.10 + 0.05 * k), width=3)

def texto_c(d, y, s, f, fill, cx=W // 2):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)

def envolver(d, s, f, ancho):
    lineas, actual = [], ""
    for p in s.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=f) <= ancho:
            actual = prueba
        else:
            lineas.append(actual); actual = p
    if actual: lineas.append(actual)
    return lineas

def cabecera(d, rango):
    d.rounded_rectangle((72, 120, 112, 160), 10, fill=EMBER)
    d.text((128, 118), "MAREA PÚBLICA", font=F_MONO(34), fill=SALT)
    f = F_MONO(28)
    w = d.textlength(rango, font=f)
    d.rounded_rectangle((W - 72 - w - 36, 116, W - 72, 164), 24, outline=SEA, width=2)
    d.text((W - 72 - w - 18, 124), rango, font=f, fill=SEA)
    d.text((72, 190), "Fuente: SECOP II · datos preliminares", font=F_BODY(26, 400), fill=MUTED)

def subtitulos(d, palabras, t):
    # palabras: [(texto, ini, fin)] agrupadas en bloques de ~4
    activo = None
    for bloque in palabras:
        if bloque[0][1] - 0.05 <= t <= bloque[-1][2] + 0.25:
            activo = bloque
    if not activo:
        return
    f = F_DISP(58, 750)
    linea = " ".join(p[0] for p in activo)
    ancho = d.textlength(linea, font=f)
    x = (W - ancho) / 2
    y = 1330
    d.rounded_rectangle((x - 28, y - 18, x + ancho + 28, y + 84), 22, fill=(6, 24, 30))
    for p in activo:
        col = EMBER if p[1] <= t <= p[2] + 0.08 else SALT
        d.text((x, y), p[0], font=f, fill=col)
        x += d.textlength(p[0] + " ", font=f)

def escena_intro(d, p, prm):
    a = ease(p * 2.2)
    y = 560 + 60 * (1 - a)
    col = mezcla(NIGHT, SALT, a)
    texto_c(d, y, "¿Cómo contrató", F_DISP(104), col)
    texto_c(d, y + 120, "el Caribe", F_DISP(104), col)
    texto_c(d, y + 240, "esta semana?", F_DISP(104), mezcla(NIGHT, EMBER, a))
    b = ease((p - 0.25) * 2)
    deps = "Atlántico · Bolívar · Cesar · Córdoba"
    deps2 = "La Guajira · Magdalena · Sucre · San Andrés"
    texto_c(d, y + 420, deps, F_BODY(36), mezcla(NIGHT, MUTED, b))
    texto_c(d, y + 472, deps2, F_BODY(36), mezcla(NIGHT, MUTED, b))

def escena_conteo(d, p, prm):
    n = int(prm["n"] * ease(p * 1.6))
    a = ease(p * 3)
    texto_c(d, 600, miles(n), F_DISP(250, 850), mezcla(NIGHT, SALT, a))
    texto_c(d, 900, "contratos firmados", F_BODY(54, 600), mezcla(NIGHT, SEA, a))
    texto_c(d, 970, "en una semana", F_BODY(54, 400), mezcla(NIGHT, MUTED, a))

def escena_grilla(d, p, prm):
    de10 = prm["de10"]
    lado, gap = 150, 30
    x0 = (W - (5 * lado + 4 * gap)) / 2
    y0 = 470
    for i in range(10):
        r, c = divmod(i, 5)
        x, y = x0 + c * (lado + gap), y0 + r * (lado + gap)
        on = i < de10 and p > 0.12 + i * 0.06
        aparece = ease(p * 4 - i * 0.15)
        base = mezcla(NIGHT, NIGHT2 if not on else EMBER, aparece)
        d.rounded_rectangle((x, y, x + lado, y + lado), 28, fill=base,
                            outline=mezcla(NIGHT, SEA, aparece * 0.6), width=3)
    a = ease((p - 0.35) * 2.5)
    texto_c(d, 860, f"{prm['pct']} %", F_DISP(200, 850), mezcla(NIGHT, EMBER, a))
    texto_c(d, 1080, "por contratación directa", F_BODY(50, 600), mezcla(NIGHT, SALT, a))
    texto_c(d, 1145, f"{miles(prm['D'])} contratos sin competencia", F_BODY(40, 400), mezcla(NIGHT, MUTED, a))

def escena_barras(d, p, prm):
    filas = prm["filas"]
    texto_c(d, 300, "% de contratos directos", F_DISP(56, 750), SALT)
    y, alto, gap = 420, 74, 24
    x0, xmax = 330, W - 190
    for i, (dep, pc, n) in enumerate(filas):
        g = ease(p * 2.2 - i * 0.12)
        col = EMBER if dep in prm["hi"] else SEA if dep in prm["lo"] else (90, 120, 126)
        yy = y + i * (alto + gap)
        f = F_BODY(38, 600)
        w = d.textlength(dep, font=f)
        d.text((x0 - 24 - w, yy + 14), dep, font=f, fill=mezcla(NIGHT, SALT, g))
        d.rounded_rectangle((x0, yy, xmax, yy + alto), 16, fill=NIGHT2)
        largo = (xmax - x0) * pc / 100 * g
        if largo > 20:
            d.rounded_rectangle((x0, yy, x0 + largo, yy + alto), 16, fill=col)
        d.text((x0 + largo + 16 if largo < (xmax - x0) - 150 else x0 + largo - 120, yy + 12),
               f"{round(pc * g)} %", font=F_MONO(40), fill=SALT)
    a = ease((p - 0.5) * 3)
    texto_c(d, y + len(filas) * (alto + gap) + 20, "Departamentos con 30 contratos o más en la semana",
            F_BODY(28, 400), mezcla(NIGHT, MUTED, a))

def escena_idea(d, p, prm):
    a = ease(p * 2.5)
    b = ease((p - 0.35) * 2.5)
    texto_c(d, 470, "Es legal.", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, 600, "A veces se justifica.", F_DISP(76, 700), mezcla(NIGHT, MUTED, a))
    d.line([(W / 2 - 60, 760), (W / 2 + 60, 760)], fill=mezcla(NIGHT, EMBER, b), width=6)
    texto_c(d, 820, "Pero cuando es la regla,", F_DISP(76, 700), mezcla(NIGHT, SALT, b))
    texto_c(d, 920, "menos empresas", F_DISP(110), mezcla(NIGHT, EMBER, b))
    texto_c(d, 1050, "compiten.", F_DISP(110), mezcla(NIGHT, EMBER, b))

def escena_cierre(d, p, prm):
    a = ease(p * 2.5)
    s = 150
    x, y = W / 2 - s / 2, 440
    d.rounded_rectangle((x, y, x + s, y + s), 36, fill=mezcla(NIGHT, EMBER, a))
    for k in range(3):
        yy = y + 50 + k * 26
        pts = [(x + 22 + j * 6, yy + 8 * math.sin(j / 3.2)) for j in range(19)]
        d.line(pts, fill=mezcla(EMBER, SALT, a), width=6)
    texto_c(d, 640, "Marea Pública", F_DISP(110), mezcla(NIGHT, SALT, a))
    texto_c(d, 780, "Busca tu municipio en", F_BODY(48, 400), mezcla(NIGHT, MUTED, a))
    b = ease((p - 0.15) * 2.5)
    f = F_DISP(84, 800)
    w = d.textlength("mareapublica.com", font=f)
    d.rounded_rectangle((W / 2 - w / 2 - 40, 860, W / 2 + w / 2 + 40, 990), 30, fill=mezcla(NIGHT, SEA, b))
    texto_c(d, 878, "mareapublica.com", f, mezcla(SEA, NIGHT, b))
    texto_c(d, 1080, "Veeduría ciudadana y licitaciones para MiPymes", F_BODY(34, 400), mezcla(NIGHT, MUTED, b))
    texto_c(d, 1130, "Voz generada con IA", F_BODY(28, 400), mezcla(NIGHT, MUTED, b * 0.8))

DIBUJA = {"intro": escena_intro, "conteo": escena_conteo, "grilla": escena_grilla,
          "barras": escena_barras, "idea": escena_idea, "cierre": escena_cierre}


# ---------- música ----------
PERFIL = "veeduria"   # veeduria | mipymes | institucional

def elegir_musica(perfil):
    """Rota las pistas del perfil según el día del año (misma pista todo el día)."""
    import datetime as _dt, glob as _glob
    pistas = sorted(_glob.glob(os.path.join(RAIZ, "video", "musica", perfil, "*.mp3")))
    if not pistas:
        return None
    return pistas[_dt.date.today().timetuple().tm_yday % len(pistas)]

def punto_de_inicio(musica, total, t_cierre):
    """Segundo de la pista donde arranca el video, para que su momento fuerte (climax)
    coincida con el cierre del video. Nunca antes de que la pista 'entre' y siempre
    al inicio de un compás, para que no suene cortada."""
    try:
        cat = json.load(open(os.path.join(RAIZ, "video", "musica", "catalogo.json"), encoding="utf-8"))
        info = next(c for c in cat if os.path.basename(c["archivo"]) == os.path.basename(musica)
                    and os.path.basename(os.path.dirname(c["archivo"])) == os.path.basename(os.path.dirname(musica)))
    except Exception:
        return 0.0
    dur = duracion(musica)
    ideal = info.get("climax", 0) - t_cierre
    tope = max(0.0, dur - total - 0.5)
    ofs = min(max(ideal, info.get("entrada", 0)), tope)
    previos = [b for b in info.get("compases", []) if b <= ofs + 0.05]
    return round(previos[-1] if previos else ofs, 2)


# ---------- principal ----------
def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "video", "salida", "semana.mp4")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    data = json.load(open(os.path.join(RAIZ, "site", "data.json"), encoding="utf-8"))
    if not data.get("sem"):
        raise SystemExit("data.json no trae el bloque 'sem'")
    escenas, caption = guion(data)
    texto = " ".join(e[1] for e in escenas)          # con marcas
    mp3 = os.path.join(os.path.dirname(salida), "voz.mp3")
    al = tts(texto, VOZ, mp3)
    if al is None:
        est = len(escrito(texto)) / 14.5
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=mono", "-t", f"{est:.2f}", mp3], check=True)
        print("Sin ELEVENLABS_API_KEY: audio en silencio y tiempos estimados")
    dur_audio = duracion(mp3)

    # Palabras escritas de cada escena, con sus tiempos en el audio
    por_escena = [escrito(e[1]).split() for e in escenas]
    planas = [w for ws in por_escena for w in ws]
    tw = tiempos_palabras(planas, al, dur_audio)
    t_esc, bloques, i = [], [], 0
    for ws in por_escena:
        t_esc.append(tw[i][0] if ws else (t_esc[-1] if t_esc else 0.0))
        actual = []
        for w in ws:
            actual.append((w, tw[i][0], tw[i][1])); i += 1
            if len(actual) == 4 or w[-1] in ".,:…":
                bloques.append(actual); actual = []
        if actual: bloques.append(actual)
    t_esc.append(dur_audio + 1.0)
    t_esc[0] = 0.0
    for k in range(1, len(t_esc)):              # nunca hacia atrás
        t_esc[k] = max(t_esc[k], t_esc[k - 1] + 0.5)
    texto_escrito = " ".join(escrito(e[1]) for e in escenas)

    global FONDO
    FONDO = fondo()
    total = t_esc[-1]
    nframes = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", mp3]
    musica = elegir_musica(PERFIL)
    if musica:
        ofs = punto_de_inicio(musica, total, t_esc[-2])
        print(f"Música: {os.path.basename(musica)} desde el segundo {ofs}")
        fin_m = max(0.5, total - 1.5)
        cmd += ["-ss", f"{ofs:.2f}", "-i", musica, "-filter_complex",
                f"[2:a]atrim=0:{total:.2f},volume=0.30,afade=t=in:d=1.0,afade=t=out:st={fin_m:.2f}:d=1.5[m];"
                "[m][1:a]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=400[md];"
                "[1:a]apad[v];[v][md]amix=inputs=2:duration=shortest:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", salida]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rango = escenas[0][2]["rango"]
    for fr in range(nframes):
        t = fr / FPS
        k = max(i for i in range(len(escenas)) if t_esc[i] <= t)
        p = (t - t_esc[k]) / max(0.5, t_esc[k + 1] - t_esc[k])
        img = FONDO.copy()
        d = ImageDraw.Draw(img)
        olas(d, t)
        cabecera(d, rango)
        nombre, _, prm = escenas[k]
        DIBUJA[nombre](d, p, prm)
        if nombre != "cierre":
            subtitulos(d, bloques, t)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    with open(os.path.join(os.path.dirname(salida), "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)
    with open(os.path.join(os.path.dirname(salida), "guion.txt"), "w", encoding="utf-8") as f:
        f.write(texto_escrito + f"\n\n--- enviado a la voz ({MODELO_USADO}) ---\n" + hablado(texto))
    print(f"Listo: {salida} ({total:.1f} s)")


if __name__ == "__main__":
    main()
