"""Démo motion design 2D (style carte + infographie) : la migration des gnous.

    python motion/demo_gnous.py            # voix ElevenLabs (clé dans l'environnement)
    python motion/demo_gnous.py --voice-file voix.mp3

Toutes les images sont dessinées par le code : 100 % original.
"""
import argparse
import json
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import audio, subtitles, tts  # noqa: E402
from pipeline.common import load_config  # noqa: E402

W, H, FPS = 1080, 1920, 30
BG = (18, 18, 20)
LAND = (38, 38, 42)
EDGE = (92, 92, 100)
RED = (196, 32, 40)
YELLOW = (255, 214, 10)
WHITE = (240, 240, 240)
BLUE = (60, 150, 230)
F_BOLD = str(ROOT / "assets/fonts/Montserrat-ExtraBold.ttf")
F_REG = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

TEXT = ("Chaque année, un million et demi de gnous quittent le Serengeti. "
        "Deux cent cinquante mille ne reviendront jamais. "
        "Et le pire obstacle, c'est cette rivière. "
        "Dans son eau, des crocodiles attendent depuis des semaines. "
        "Et toi, tu traverserais en premier ?")

# carte : projection simple, cadrée sur la Tanzanie et le Kenya
LON0, LON1, LAT0, LAT1 = 29.0, 42.5, -12.0, 5.0
MX0, MX1 = 60, W - 60
SCALE = (MX1 - MX0) / (LON1 - LON0)
MY0 = 1080 - (LAT1 - LAT0) * SCALE / 2


def proj(lon, lat, zoom=1.0, cx=34.9, cy=-1.8):
    x = MX0 + (lon - LON0) * SCALE
    y = MY0 + (LAT1 - lat) * SCALE
    if zoom != 1.0:
        px, py = MX0 + (cx - LON0) * SCALE, MY0 + (LAT1 - cy) * SCALE
        x = W / 2 + (x - px) * zoom
        y = 1000 + (y - py) * zoom
    return x, y


def load_polys():
    polys = []
    for c in ["TZA", "KEN", "UGA", "RWA", "BDI"]:
        g = json.load(open(ROOT / f"assets/geo/{c}.geo.json"))["features"][0]["geometry"]
        rings = [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
        polys += [(c, r) for r in rings]
    return polys


SERENGETI = (34.83, -2.33)
MARA = (35.10, -1.45)
RIVER = [(35.70, -0.85), (35.45, -1.10), (35.20, -1.35), (34.95, -1.52), (34.60, -1.58), (34.25, -1.55), (33.95, -1.52)]


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def font(path, size):
    return ImageFont.truetype(path, size)


def text_c(d, y, s, f, fill, anchor="mm"):
    d.text((W / 2, y), s, font=f, fill=fill, anchor=anchor)


def fmt(n):
    return f"{int(n):,}".replace(",", " ")


def render(times, dur, out_pipe):
    polys = load_polys()
    random.seed(3)
    herd = []
    for _ in range(320):
        a, r = random.uniform(0, 2 * math.pi), random.gauss(0, 0.11)
        herd.append((SERENGETI[0] + r * math.cos(a) * 1.4, SERENGETI[1] + r * math.sin(a),
                     random.random(), random.uniform(0.6, 1.4)))
    t_million, t_deux, t_pire, t_riviere, t_croco, t_toi = times
    fb = {s: font(F_BOLD, s) for s in (34, 44, 64, 92, 130)}
    for i in range(int(dur * FPS)):
        t = i / FPS
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        # caméra : vue d'ensemble, zoom sur le Serengeti, puis gros plan sur la rivière
        k1, k2 = ease((t - 0.5) / 1.3), ease((t - t_pire) / 1.2)
        z = lerp(1.0, 3.2, k1) + (5.2 - 3.2) * k2
        cx = lerp(lerp(34.9, 34.95, k1), 34.95, k2)
        cy = lerp(lerp(-1.8, -2.0, k1), -1.62, k2)
        P = lambda lo, la: proj(lo, la, z, cx, cy)  # noqa: E731
        # trame de points façon carte
        for gx in range(0, W, 54):
            for gy in range(160, H, 54):
                d.point((gx, gy), fill=(48, 48, 54))
        # pays : apparition progressive du contour
        draw_in = ease(t / 1.0)
        dying = ease((t - t_deux) / 2.2)
        for c, ring in polys:
            pts = [P(lo, la) for lo, la in ring]
            fill = LAND
            if c == "TZA":
                k = 0.12 * dying
                fill = tuple(int(lerp(LAND[j], RED[j], k)) for j in range(3))
            d.polygon(pts, fill=fill)
            n = max(2, int(len(pts) * draw_in))
            d.line(pts[:n], fill=EDGE, width=3)
        # rivière Mara
        rv = [P(lo, la) for lo, la in RIVER]
        pulse = 0.5 + 0.5 * math.sin(t * 8)
        rc = BLUE if t < t_riviere else tuple(int(lerp(BLUE[j], RED[j], pulse)) for j in range(3))
        d.line(rv, fill=rc, width=int(4 + 3 * z), joint="curve")
        # troupeau : apparaît, migre vers le nord, une partie disparaît
        appear = ease((t - t_million + 0.3) / 1.0)
        move = ease((t - t_million - 0.8) / 4.5)
        for k, (lo, la, ph, sz) in enumerate(herd):
            if k / len(herd) > appear:
                continue
            dead = ph < 0.17 and dying > ph / 0.17 * 0.9
            # le troupeau monte jusqu'à la berge sud (lat -1.72) et s'y masse
            tlo = lerp(lo, lo + 0.12, move)
            tla = lerp(la, -1.80 + (la - SERENGETI[1]) * 0.6, move) + 0.006 * math.sin(t * 3 + k)
            x, y = P(tlo, tla)
            r = 4.2 * sz * min(z, 4) / 2.2
            col = RED if dead else WHITE
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        # repère Serengeti
        sx, sy = P(*SERENGETI)
        if 0.6 < t < t_pire:
            rr = 14 + 10 * (0.5 + 0.5 * math.sin(t * 5))
            d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=YELLOW, width=4)
            d.text((sx + 60, sy + 60), "SERENGETI", font=fb[34], fill=YELLOW, anchor="lm")
        if t_riviere - 0.2 < t < t_toi:
            mx, my = P(34.75, -1.56)
            d.text((mx, my - 80), "RIVIÈRE MARA", font=fb[44], fill=RED, anchor="mm")
        # bandeau du haut
        d.rectangle([0, 0, W, 150], fill=(10, 10, 12))
        d.text((50, 75), "SERENGETI · CHAQUE ANNÉE", font=fb[34], fill=WHITE, anchor="lm")
        d.rectangle([W - 240, 48, W - 50, 102], fill=RED)
        d.text((W - 145, 75), "MIGRATION", font=fb[34], fill=WHITE, anchor="mm")
        # compteur
        up = ease((t - t_million) / 1.4)
        down = ease((t - t_deux) / 2.0)
        if t > t_million - 0.1:
            n = 1_500_000 * up - 250_000 * down
            col = WHITE if down == 0 else tuple(int(lerp(WHITE[j], RED[j], down)) for j in range(3))
            text_c(d, 300, fmt(n), fb[130], col)
            text_c(d, 395, "GNOUS EN VIE" if down < 0.5 else "250 000 NE REVIENDRONT PAS", fb[44],
                   YELLOW if down < 0.5 else RED)
        if t > t_pire:
            box = ease((t - t_pire) / 0.4)
            y0 = 1560
            d.rectangle([W / 2 - 330 * box, y0 - 55, W / 2 + 330 * box, y0 + 55], fill=RED)
            if box > 0.9:
                text_c(d, y0, "OBSTACLE N°1", fb[64], WHITE)
        # crocodiles : petites marques rouges qui surgissent le long de la rivière
        if t > t_croco:
            for j, (lo, la) in enumerate(RIVER[1:-1]):
                k = ease((t - t_croco - 0.15 * j) / 0.3)
                if k <= 0:
                    continue
                x, y = P(lo, la)
                s_ = 24 * k
                for dx in (-1.6, 0, 1.6):
                    d.polygon([(x + dx * s_ - s_ * 0.7, y), (x + dx * s_, y - s_ * 1.6),
                               (x + dx * s_ + s_ * 0.7, y)], fill=RED)
        if t > t_toi:
            k = ease((t - t_toi) / 0.4)
            ov = Image.new("RGB", (W, H), (0, 0, 0))
            img = Image.blend(img, ov, 0.55 * k)
            d = ImageDraw.Draw(img)
            text_c(d, 720, "ET TOI ?", fb[130], tuple(int(255 * k) for _ in range(3)))
        out_pipe.write(img.tobytes())


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    args = ap.parse_args()
    work = ROOT / "output" / "_work_motion_demo"
    work.mkdir(parents=True, exist_ok=True)
    if args.voice_file:
        raw = Path(args.voice_file)
    else:
        el = cfg["voice"].get("elevenlabs", {})
        raw = tts.synthesize_elevenlabs(TEXT, work / "voice_raw.mp3", None, el.get("model", "eleven_v4"))
    s = audio.remove_silences(audio.load(raw), -38, 0.15, 0.09)
    audio.save(s, work / "voice_tight.wav")
    voice = audio.normalize(work / "voice_tight.wav", work / "voice.wav")
    words = subtitles.align(TEXT, subtitles.transcribe_words(voice))
    vdur = len(audio.load(voice)) / audio.SR
    dur = vdur + 1.8

    def at(word, default):
        for w in words:
            if subtitles._norm(w["text"]) == word:
                return w["start"]
        return default
    times = (at("million", 1.5), at("deux", 4.5), at("pire", 8.0), at("riviere", 9.0),
             at("crocodiles", 10.0), at("toi", 12.0))
    print("repères :", [round(x, 2) for x in times], "durée", round(dur, 2))
    sub_cfg = dict(cfg["subtitles"], position_y=0.74)
    ass = subtitles.write_ass(words, work / "subs.ass", sub_cfg, W, H, dur)
    out = ROOT / "output" / "demo_motion_gnous.mp4"
    fonts = str(ROOT / "assets" / "fonts")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(voice), "-t", f"{dur:.2f}", "-af", "apad",
                           "-vf", f"ass='{ass}':fontsdir='{fonts}'", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    render(times, dur, ff.stdin)
    ff.stdin.close()
    ff.wait()
    print("✅", out)


if __name__ == "__main__":
    main()
