#!/usr/bin/env python3
"""Marea Pública · video del lunes (resumen semanal).

Lee site/data.json (bloque "sem"), escribe el guion, genera la voz con
ElevenLabs (si hay ELEVENLABS_API_KEY) y renderiza un MP4 vertical 1080x1920.
Sin clave usa audio en silencio y tiempos estimados (sirve para probar el diseño).

Uso: python video/render_semana.py [salida.mp4]
"""
import base64, json, math, os, re, subprocess, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTES = os.path.join(RAIZ, "video", "fonts")
W, H, FPS = 1080, 1920, 30

VOZ_MUJER = "Ut5x3LuSfExdBqv3rEz7"   # Marea Pública · Voz mujer (veeduría)
VOZ_HOMBRE = "vY4YbSJxUDECdZsKPrF6"  # Marea Pública · Voz hombre (MiPymes)

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
        ("intro", f"Semana del {rango} al {d2} de {m2}. Así contrataron las entidades públicas del Caribe colombiano.",
         {"rango": f"{d1} {m1[:3].upper()} – {d2} {m2[:3].upper()}"}),
        ("conteo", f"Firmaron {letras(T)} contratos en SECOP.", {"n": T}),
        ("grilla", f"{letras(D).capitalize()} fueron por contratación directa. "
                   f"{letras(de10).capitalize()} de cada diez, sin competencia entre empresas.",
         {"pct": pct, "de10": de10, "D": D}),
        ("barras", f"En {con_art(alto1[0])} llegó al {letras(alto1[1])} por ciento. "
                   f"En {con_art(alto2[0])}, al {letras(alto2[1])}. "
                   f"La excepción fue {con_art(bajo[0])}: {letras(bajo[1])} por ciento.",
         {"filas": filas, "hi": {alto1[0], alto2[0]}, "lo": {bajo[0]}}),
        ("idea", "La contratación directa es legal, y a veces se justifica. "
                 "Pero cuando se vuelve la regla, menos empresas pueden competir.", {}),
        ("cierre", "Busca tu municipio en marea pública punto com. Esto es Marea Pública.", {}),
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


# ---------- voz ----------
def tts(texto, voz, salida_mp3):
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        return None
    ultimo = None
    for modelo in ("eleven_v3", "eleven_multilingual_v2"):
        body = {"text": texto, "model_id": modelo}
        if modelo == "eleven_multilingual_v2":
            body["voice_settings"] = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.15}
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(body).encode(), method="POST",
            headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                j = json.load(r)
            with open(salida_mp3, "wb") as f:
                f.write(base64.b64decode(j["audio_base64"]))
            al = j.get("alignment") or j.get("normalized_alignment")
            print(f"Voz generada con {modelo}")
            return al
        except Exception as e:
            ultimo = e
            print(f"TTS con {modelo} falló: {e}")
    raise SystemExit(f"No se pudo generar la voz: {ultimo}")

def duracion(mp3):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", mp3], capture_output=True, text=True).stdout
    return float(out.strip())

def tiempos(texto, al, total):
    """Tiempo de inicio de cada carácter del texto."""
    if al and len(al.get("characters", [])) == len(texto):
        return al["character_start_times_seconds"], al["character_end_times_seconds"]
    # Estimación: reparte el tiempo por caracteres, con pausa extra en puntos.
    pesos = [3.5 if c in ".:" else 2.0 if c == "," else 1.0 for c in texto]
    k = total / sum(pesos)
    ini, fin, t = [], [], 0.15
    for p in pesos:
        ini.append(t); t += p * k * 0.95; fin.append(t)
    return ini, fin


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


# ---------- principal ----------
def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "video", "salida", "semana.mp4")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    data = json.load(open(os.path.join(RAIZ, "site", "data.json"), encoding="utf-8"))
    if not data.get("sem"):
        raise SystemExit("data.json no trae el bloque 'sem'")
    escenas, caption = guion(data)
    texto = " ".join(e[1] for e in escenas)
    mp3 = os.path.join(os.path.dirname(salida), "voz.mp3")
    al = tts(texto, VOZ_MUJER, mp3)
    if al is None:
        est = len(texto) / 14.5
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=mono", "-t", f"{est:.2f}", mp3], check=True)
        print("Sin ELEVENLABS_API_KEY: audio en silencio y tiempos estimados")
    dur_audio = duracion(mp3)
    ini, fin = tiempos(texto, al, dur_audio)

    # Límites de cada escena según el carácter donde empieza su frase
    pos, limites = 0, []
    for _, frase, _ in escenas:
        limites.append(pos)
        pos += len(frase) + 1
    t_esc = [ini[c] for c in limites] + [dur_audio + 1.0]
    t_esc[0] = 0.0

    # Palabras con tiempos, agrupadas en bloques para subtítulos
    bloques = []
    for k, (_, frase, _) in enumerate(escenas):
        actual = []
        for m in re.finditer(r"\S+", frase):
            c0, c1 = limites[k] + m.start(), limites[k] + m.end() - 1
            actual.append((m.group(), ini[c0], fin[c1]))
            if len(actual) == 4 or m.group()[-1] in ".,:":
                bloques.append(actual); actual = []
        if actual: bloques.append(actual)

    global FONDO
    FONDO = fondo()
    total = t_esc[-1]
    nframes = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", mp3]
    musica = os.path.join(RAIZ, "video", "musica.mp3")
    if os.path.exists(musica):
        cmd += ["-stream_loop", "-1", "-i", musica, "-filter_complex",
                "[2:a]volume=0.10[m];[1:a][m]amix=inputs=2:duration=first[a]", "-map", "0:v", "-map", "[a]"]
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
        f.write(texto)
    print(f"Listo: {salida} ({total:.1f} s)")


if __name__ == "__main__":
    main()
