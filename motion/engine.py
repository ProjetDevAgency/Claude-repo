"""Moteur de motion design 2D pour les vidéos éco (1080x1920, 30 i/s).

Une vidéo = une voix off + une liste de scènes. Chaque scène démarre sur un
mot du script (trouvé dans le timing Whisper) et se dessine avec Pillow.
Tout est dessiné par le code : aucune image reprise.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import audio, subtitles, tts  # noqa: E402
from pipeline.common import load_config  # noqa: E402

W, H, FPS = 1080, 1920, 30
BG = (16, 16, 18)
PANEL = (32, 32, 36)
GREY = (120, 120, 128)
RED = (214, 40, 48)
YELLOW = (255, 210, 0)
WHITE = (242, 242, 242)
GREEN = (60, 190, 110)
BLUE = (60, 150, 230)
F_BOLD = str(ROOT / "assets/fonts/Montserrat-ExtraBold.ttf")
_fonts = {}


def F(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(F_BOLD, size)
    return _fonts[size]


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def back(t):
    """Petit dépassement à l'arrivée (effet « pop »)."""
    t = max(0.0, min(1.0, t))
    c = 1.7
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def fmt(n, dec=0):
    s = f"{n:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s


def text(d, xy, s, size, fill=WHITE, anchor="mm", alpha=1.0):
    if alpha <= 0:
        return
    col = mix(BG, fill, alpha) if alpha < 1 else fill
    d.text(xy, s, font=F(size), fill=col, anchor=anchor)


def pop_text(d, xy, s, size, fill, lt, dur=0.35):
    """Texte qui apparaît en grossissant légèrement."""
    k = back(lt / dur)
    if lt <= 0:
        return
    text(d, xy, s, max(8, int(size * (0.6 + 0.4 * k))), fill, alpha=min(1, lt / 0.15))


def tag(d, x, y, s, size, bg, fg=WHITE, anchor="mm"):
    f = F(size)
    w = f.getlength(s)
    pad = size * 0.45
    if anchor == "mm":
        x0 = x - w / 2 - pad
    else:
        x0 = x
    d.rounded_rectangle([x0, y - size * 0.75, x0 + w + 2 * pad, y + size * 0.75], radius=int(size * 0.3), fill=bg)
    d.text((x0 + pad + w / 2, y), s, font=f, fill=fg, anchor="mm")


def person(d, x, y, s, col):
    """Petit personnage en aplat (tête + corps)."""
    d.ellipse([x - 0.28 * s, y - s, x + 0.28 * s, y - 0.44 * s], fill=col)
    d.rounded_rectangle([x - 0.42 * s, y - 0.36 * s, x + 0.42 * s, y + 0.5 * s], radius=int(0.3 * s), fill=col)


def bar(d, x, y, w, h, frac, col, bgcol=PANEL):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(h / 2), fill=bgcol)
    if frac > 0.01:
        d.rounded_rectangle([x, y, x + max(h, w * frac), y + h], radius=int(h / 2), fill=col)


def load_country(code):
    g = json.load(open(ROOT / f"assets/geo/{code}.geo.json"))["features"][0]["geometry"]
    return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]


def header(d, date_label, topic):
    d.rectangle([0, 0, W, 150], fill=(8, 8, 10))
    text(d, (50, 75), date_label, 34, WHITE, anchor="lm")
    tag(d, W - 60 - F(34).getlength(topic) / 2 - 15, 75, topic, 34, RED)


class Video:
    """Assemble voix + scènes + sous-titres en un MP4."""

    def __init__(self, name, script_path, date_label, topic):
        self.name, self.date_label, self.topic = name, date_label, topic
        self.text = " ".join(Path(script_path).read_text(encoding="utf-8").split())
        self.work = ROOT / "output" / f"_work_{name}"
        self.work.mkdir(parents=True, exist_ok=True)
        self.scenes = []
        self.hook_head_start = 3.0  # secondes « d'avance » de la 1re scène à l'image 0

    def voice(self, voice_file=None):
        cfg = load_config()
        if voice_file:
            raw = Path(voice_file)
        else:
            raw = self.work / "voice_raw.mp3"
            if not raw.exists():
                el = cfg["voice"].get("elevenlabs", {})
                tts.synthesize_elevenlabs(self.text, raw, None, el.get("model", "eleven_v4"))
        v = cfg["voice"]
        s = audio.remove_silences(audio.load(raw), v["silence_threshold_db"], v["min_silence"], v["keep_silence"])
        audio.save(s, self.work / "voice_tight.wav")
        dur = len(s) / audio.SR
        target = 61.6
        src = self.work / "voice_tight.wav"
        if dur > target or dur < 60.5:
            f = max(0.94, min(1.25, dur / target))
            audio.speed_up(src, self.work / "voice_fit.wav", f)
            src = self.work / "voice_fit.wav"
            print(f"   vitesse voix x{f:.3f}")
        self.voice_path = audio.normalize(src, self.work / "voice.wav")
        self.vdur = len(audio.load(self.voice_path)) / audio.SR
        self.dur = min(63.0, max(61.0, self.vdur + 0.4))
        self.words = subtitles.align(self.text, subtitles.transcribe_words(self.voice_path))
        print(f"   voix {self.vdur:.1f}s → vidéo {self.dur:.1f}s")

    def at(self, phrase, after=0.0):
        """Instant où commence la suite de mots `phrase` (première occurrence après `after`)."""
        target = [subtitles._norm(w) for w in phrase.split()]
        norm = [subtitles._norm(w["text"]) for w in self.words]
        for i in range(len(norm) - len(target) + 1):
            if norm[i:i + len(target)] == target and self.words[i]["start"] >= after:
                return self.words[i]["start"]
        raise ValueError(f"phrase introuvable dans le script : {phrase!r}")

    def scene(self, phrase, fn, after=0.0):
        self.scenes.append((self.at(phrase, after), fn))

    def render(self):
        self.scenes.sort(key=lambda s: s[0])
        cfg = load_config()
        sub_cfg = dict(cfg["subtitles"], position_y=0.80, size=84)
        ass = subtitles.write_ass(self.words, self.work / "subs.ass", sub_cfg, W, H, self.dur)
        out = ROOT / "output" / f"{self.name}.mp4"
        fonts = str(ROOT / "assets" / "fonts")
        ff = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-i", str(self.voice_path), "-af", "apad", "-t", f"{self.dur:.2f}",
             "-vf", f"ass='{ass}':fontsdir='{fonts}'", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-maxrate", "2M", "-bufsize", "4M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
        n = int(self.dur * FPS)
        for i in range(n):
            t = i / FPS
            img = Image.new("RGB", (W, H), BG)
            d = ImageDraw.Draw(img)
            # trame de fond discrète
            for gx in range(27, W, 54):
                for gy in range(180, H, 54):
                    d.point((gx, gy), fill=(40, 40, 46))
            # scène active (la dernière commencée), avec fondu d'entrée
            cur = [(t0, fn) for t0, fn in self.scenes if t0 <= t]
            if cur:
                t0, fn = cur[-1]
                nxt = [s0 for s0, _ in self.scenes if s0 > t0]
                end = nxt[0] if nxt else self.dur
                lt = t - t0
                # 1re scène : déjà construite dès la 1re image (pas d'écran vide = pas de swipe)
                if t0 == self.scenes[0][0]:
                    lt += self.hook_head_start
                fn(d, img, lt, end - t0)
            elif self.scenes:
                self.scenes[0][1](d, img, self.hook_head_start, 1.0)
            header(d, self.date_label, self.topic)
            # coup de zoom sur la 1re seconde : mouvement immédiat dans le feed
            if t < 0.9:
                z = 1 + 0.10 * (1 - ease(t / 0.9))
                w2, h2 = int(W * z), int(H * z)
                big = img.resize((w2, h2))
                img = big.crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
            ff.stdin.write(img.tobytes())
        ff.stdin.close()
        ff.wait()
        print("✅", out)
        return out
