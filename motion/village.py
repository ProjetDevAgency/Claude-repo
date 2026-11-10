"""« Le village des abonnés » : feuilleton participatif. Le maire de Fauché-les-Oies, un budget, les abonnés votent.

Décor de jour en cartoon plat (même moteur que Kévin). Épisodes courts (27-30 s) en attendant la monétisation.
    python motion/village.py --ep 1
"""
import argparse
import math

from PIL import Image, ImageDraw

from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, F, back, big_number, character, counter, dim,
                     ease, flash, idle, push, shake, shot, tag)
from engine import H, W

SKY = (140, 205, 245)
GRASS = (112, 192, 92)
ROAD = (90, 92, 104)
BLEU, BLANC, ROUGE = (35, 70, 160), (245, 245, 245), (215, 40, 50)
MAIRE = dict(shirt=(40, 50, 90), pants=(40, 50, 90), hair=(70, 50, 40))
BASE = 1500
_bg = {}


# ───────────── décor ─────────────

def campagne():
    if "c" in _bg:
        return _bg["c"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), SKY)
    d = ImageDraw.Draw(im)
    for cx, cy, r in [(180, 260, 70), (260, 240, 90), (340, 270, 60), (800, 360, 80), (880, 330, 60)]:
        d.ellipse([(cx - r) * s, (cy - r * 0.6) * s, (cx + r) * s, (cy + r * 0.6) * s], fill=WHITE)
    d.polygon([(0, 1000 * s), (300 * s, 880 * s), (650 * s, 960 * s), (1080 * s, 860 * s), (1080 * s, H * s), (0, H * s)],
              fill=(96, 176, 80))
    d.rectangle([0, 1080 * s, W * s, H * s], fill=GRASS)
    d.polygon([(470 * s, 1080 * s), (610 * s, 1080 * s), (900 * s, H * s), (180 * s, H * s)], fill=ROAD)
    for j in range(5):
        y0 = 1120 + j * 170
        d.rectangle([536 * s, y0 * s, 544 * s, (y0 + 70 + j * 12) * s], fill=WHITE)
    for x, y in [(90, 1060), (980, 1050), (150, 1020)]:   # arbres
        d.rectangle([(x - 12) * s, y * s, (x + 12) * s, (y + 70) * s], fill=(110, 75, 50))
        d.ellipse([(x - 60) * s, (y - 110) * s, (x + 60) * s, (y + 20) * s], fill=(60, 150, 70))
    _bg["c"] = im
    return im


def panneau(d, x, y, nom, s=SS):
    d.rectangle([(x - 230) * s, (y + 60) * s, (x - 210) * s, (y + 330) * s], fill=(120, 120, 130))
    d.rectangle([(x + 210) * s, (y + 60) * s, (x + 230) * s, (y + 330) * s], fill=(120, 120, 130))
    d.rounded_rectangle([(x - 300) * s, (y - 70) * s, (x + 300) * s, (y + 90) * s], radius=20 * s, fill=WHITE,
                        outline=ROUGE, width=16 * s)
    d.text((x * s, (y + 10) * s), nom, font=FA(86 * s), fill=INK, anchor="mm")


def maire(d, x, base, t, **pose):
    """Le maire : costume, écharpe tricolore, moustache."""
    bob, blink = idle(t, 0.2)
    p = {**MAIRE, "blink": blink, "mouth": "smile", **pose}
    character(d, x, base + bob, **p)
    s = SS
    X = lambda v: x * s + v * s  # noqa: E731
    Y = lambda v: (base + bob) * s + v * s  # noqa: E731
    for k, col in enumerate((BLEU, BLANC, ROUGE)):   # écharpe en diagonale
        o = (k - 1) * 22
        d.polygon([(X(-80 + o), Y(-560)), (X(-50 + o), Y(-560)), (X(90 + o), Y(-300)), (X(60 + o), Y(-300))], fill=col)
    d.chord([X(-48), Y(-668), X(48), Y(-622)], 180, 360, fill=(70, 50, 40))       # moustache


def pigeon(d, x, y, t, k=2.2):
    s = SS * k
    x, y = x / k, y / k
    h = math.sin(t * 9) * 6
    d.ellipse([(x - 50) * s, (y - 40) * s, (x + 50) * s, (y + 30) * s], fill=(150, 155, 170))
    d.ellipse([(x + 20) * s, (y - 80 + h) * s, (x + 70) * s, (y - 30 + h) * s], fill=(130, 135, 150))
    d.polygon([(x + 70) * s, (y - 58 + h) * s, (x + 95) * s, (y - 52 + h) * s, (x + 70) * s, (y - 46 + h) * s], fill=YEL)
    d.ellipse([(x + 46) * s, (y - 66 + h) * s, (x + 56) * s, (y - 56 + h) * s], fill=INK)
    d.line([(x - 10) * s, (y + 28) * s, (x - 10) * s, (y + 50) * s], fill=(230, 140, 60), width=int(5 * s))
    d.line([(x + 15) * s, (y + 28) * s, (x + 15) * s, (y + 50) * s], fill=(230, 140, 60), width=int(5 * s))


def cabine(d, x, base):
    s = SS
    d.rectangle([(x - 90) * s, (base - 520) * s, (x + 90) * s, base * s], fill=(60, 110, 200))
    d.rectangle([(x - 70) * s, (base - 440) * s, (x + 70) * s, (base - 40) * s], fill=(190, 225, 245))
    d.rounded_rectangle([(x - 120) * s, (base - 610) * s, (x + 120) * s, (base - 520) * s], radius=12 * s, fill=WHITE,
                        outline=BLEU, width=8 * s)
    d.text((x * s, (base - 565) * s), "MAIRIE", font=FA(60 * s), fill=BLEU, anchor="mm")


def maison(d, x, base, w, col, roof=(200, 70, 60), plaque=None):
    s = SS
    d.rectangle([(x - w / 2) * s, (base - w * 0.8) * s, (x + w / 2) * s, base * s], fill=col)
    d.polygon([((x - w * 0.62) * s, (base - w * 0.8) * s), (x * s, (base - w * 1.35) * s),
               ((x + w * 0.62) * s, (base - w * 0.8) * s)], fill=roof)
    d.rectangle([(x - w * 0.12) * s, (base - w * 0.42) * s, (x + w * 0.12) * s, base * s], fill=(110, 75, 50))
    if plaque:
        d.rounded_rectangle([(x - w * 0.45) * s, (base - w * 0.75) * s, (x + w * 0.45) * s, (base - w * 0.55) * s],
                            radius=8 * s, fill=WHITE, outline=INK, width=4 * s)
        d.text((x * s, (base - w * 0.65) * s), plaque, font=FA(int(w * 0.11) * s), fill=INK, anchor="mm")


def scene(t, z=1.0, center=None, sign=True, mx=760, mpose=None, extra=None):
    big = campagne().copy()
    d = ImageDraw.Draw(big)
    if sign:
        panneau(d, 360, 860, "FAUCHÉ-LES-OIES")
    if extra:
        extra(d)
    maire(d, mx, BASE, t, **(mpose or {}))
    return shot(big, z, center=center)


# ───────────── épisode 1 ─────────────

CHOIX = [("1", "RÉPARER LE PONT", "900 €"), ("2", "OUVRIR UNE ÉPICERIE", "700 €"), ("3", "FÊTE DU VILLAGE", "200 €")]
T = {}


def e1_jour(lt, dur):
    img = scene(lt, z=push(lt, dur, 1.0, 1.08), center=(540, 1000), mpose=dict(arm=0.95, mouth="grin"))
    big_number(img, (540, 300), "JOUR 1", 200, YEL, k=1.0)
    return shake(img, lt)


def e1_fauche(lt, dur):
    img = scene(lt, z=push(lt, dur, 1.15, 1.3), center=(470, 1000), mpose=dict(mouth="smile"))
    tag(img, 540, 260, "LE VILLAGE LE PLUS", 66, WHITE, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 400, "FAUCHÉ DE FRANCE", 80, ROUGE, WHITE, rot=3, k=(lt - 0.4) / 0.25)
    return flash(img, lt)


def e1_un(lt, dur):
    img = scene(lt, sign=False, mx=540, mpose=dict(arm=0.95, mouth="grin"), z=1.1, center=(540, 1050))
    big_number(img, (540, 300), "1 HABITANT", 180, WHITE, k=lt / 0.25)
    if lt > 1.0:
        tag(img, 760, 700, "MOI", 70, YEL, INK, rot=-6, k=(lt - 1.0) / 0.25)
    return flash(img, lt)


REGLES = [("ABONNÉ", "= HABITANT"), ("COMMENTAIRE", "= TA MAISON À TON PSEUDO"),
          ("CHAQUE DÉCISION", "= TU VOTES EN COMMENTAIRE"), ("100 ABONNÉS", "= UNE SURPRISE")]


def regles_panel(img, lt, t0s, y0=480):
    tag(img, 540, y0 - 210, "LES RÈGLES", 90, YEL, INK, rot=-3, k=lt / 0.25)
    for j, ((a, b), t0) in enumerate(zip(REGLES, t0s)):
        on = lt >= t0
        y = y0 + j * 215
        lay = Image.new("RGBA", (960, 200), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle([0, 0, 959, 199], radius=30, fill=(WHITE if on else (215, 215, 222)) + (255,))
        dl.ellipse([24, 40, 144, 160], fill=(YEL if on else (180, 180, 188)) + (255,))
        dl.text((84, 100), str(j + 1), font=FA(80), fill=INK + (255,), anchor="mm")
        dl.text((176, 68), a, font=FA(62), fill=(INK if on else (150, 150, 160)) + (255,), anchor="lm")
        dl.text((176, 142), b, font=FA(50), fill=((40, 140, 70) if on else (160, 160, 170)) + (255,), anchor="lm")
        sc = 1.0 + 0.08 * max(0.0, 1 - (lt - t0) / 0.25) if on else 0.94
        lay = lay.resize((int(960 * sc), int(200 * sc)))
        img.paste(lay, (540 - lay.width // 2, y - lay.height // 2), lay)


def e1_regles(lt, dur):
    def maisons(d):
        if lt > T["comment"] - T["e1_regles"]:
            maison(d, 900, 1120, 150, (240, 200, 120), plaque="@TOI")
    img = dim(scene(lt, sign=False, mx=200, mpose=dict(arm=0.5, mouth="o" if int(lt * 7) % 2 else "smile"),
                    extra=maisons), 0.45, blur=6, dark=0.75)
    t0s = [T[k] - T["e1_regles"] for k in ("abonne", "comment", "decision", "palier")]
    regles_panel(img, lt, t0s)
    return img


def e1_caisse(lt, dur):
    def caisse(d):
        s = SS
        d.rounded_rectangle([300 * s, 1080 * s, 780 * s, 1420 * s], radius=30 * s, fill=(60, 140, 80))
        d.rectangle([300 * s, 1180 * s, 780 * s, 1200 * s], fill=(40, 100, 60))
        d.rounded_rectangle([480 * s, 1220 * s, 600 * s, 1300 * s], radius=12 * s, fill=YEL)
    img = scene(lt, sign=False, mx=880, mpose=dict(mouth="o"), z=1.0, center=(540, 960), extra=caisse)
    tag(img, 540, 260, "CAISSE DE LA MAIRIE", 60, WHITE, INK, rot=-3, k=lt / 0.25)
    big_number(img, (540, 520), counter(0, 1000, lt, 0.7, "{:,} €"), 200, GREEN, k=1.0)
    return flash(img, lt)


def e1_choix(lt, dur):
    img = dim(scene(lt), 0.75)
    tag(img, 540, 230, "ON FAIT QUOI ?", 80, YEL, INK, rot=-4, k=lt / 0.25)
    t0s = [0.0, T["deux"] - T["un"], T["trois"] - T["un"]]
    for j, ((n, lab, prix), t0) in enumerate(zip(CHOIX, t0s)):
        k = (lt - t0) / 0.25
        if k <= 0:
            continue
        y = 520 + j * 250
        sc = 0.6 + 0.4 * back(k)
        lay = Image.new("RGBA", (900, 200), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle([0, 0, 899, 199], radius=30, fill=WHITE + (255,))
        dl.ellipse([24, 40, 144, 160], fill=YEL + (255,))
        dl.text((84, 100), n, font=FA(80), fill=INK + (255,), anchor="mm")
        dl.text((180, 70), lab, font=FA(58), fill=INK + (255,), anchor="lm")
        dl.text((180, 145), prix, font=FA(62), fill=(40, 140, 70, 255), anchor="lm")
        lay = lay.resize((int(900 * sc), int(200 * sc)))
        img.paste(lay, (540 - lay.width // 2, y - lay.height // 2), lay)
    return img


def e1_vote(lt, dur):
    img = scene(lt, sign=False, mpose=dict(arm=0.95, mouth="o" if int(lt * 7) % 2 else "grin"), z=1.05,
                center=(600, 1000))
    tag(img, 540, 240, "LE PLUS VOTÉ GAGNE", 70, WHITE, INK, rot=-3, k=lt / 0.25)
    tag(img, 540, 380, "RÉSULTAT DEMAIN", 64, ROUGE, WHITE, rot=3, k=(lt - 0.8) / 0.25)
    big_number(img, (540, 600), "1, 2 OU 3 ?", 190, YEL, "VOTE EN COMMENTAIRE", k=(lt - 1.6) / 0.25)
    tf = T["abo_fin"] - T["e1_vote"]
    tag(img, 540, 1250, "ABONNE-TOI POUR VOIR LE VILLAGE GRANDIR", 44, ROUGE, WHITE, rot=-2, k=(lt - tf) / 0.25)
    return shake(img, lt - 1.6)


def episode1(voice_file=None):
    v = CartoonVideo("village_ep01", "scripts/village/ep01.txt", "", "", corner="LE VILLAGE DES ABONNÉS")
    v.length = (29.0, 30.0, 31.0)
    v.hook_head_start = 0.0
    v.voice(voice_file or "output/_work_village_ep01/voice_raw.mp3")
    sc = [("Jour un", e1_jour), ("le village le plus fauché", e1_fauche), ("Pour l'instant", e1_un),
          ("Les règles sont simples", e1_regles), ("Premier vote", e1_caisse), ("Un, réparer", e1_choix),
          ("Le choix le plus voté", e1_vote)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["abonne"], T["comment"], T["decision"] = v.at("Tu t'abonnes"), v.at("Tu commentes"), v.at("Et chaque décision")
    T["palier"], T["abo_fin"] = v.at("À cent abonnés"), v.at("et abonne-toi")
    T["un"], T["deux"], T["trois"] = v.at("Un, réparer"), v.at("Deux, ouvrir"), v.at("Trois, la fête")
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["e1_fauche"], "whoosh", 0.5)
    for k in ("abonne", "comment", "decision", "palier"):
        v.sfx(T[k], "pop", 0.8)
    v.sfx(T["e1_caisse"], "ticks", 0.7)
    for k in ("un", "deux", "trois"):
        v.sfx(T[k], "pop", 0.8)
    v.sfx(T["e1_vote"] + 1.6, "impact", 0.9)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, default=1)
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    {1: episode1}[a.ep](a.voice_file)
