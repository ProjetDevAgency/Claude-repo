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


def maire(d, x, base, t, sc=1.0, **pose):
    """Le maire : costume, écharpe tricolore, moustache. sc : échelle (gros plan > 1)."""
    bob, blink = idle(t, 0.2)
    p = {**MAIRE, "blink": blink, "mouth": "smile", **pose}
    character(d, x, base + bob * sc, sc=sc, **p)
    X = lambda v: x * SS + v * SS * sc  # noqa: E731
    Y = lambda v: (base + bob * sc) * SS + v * SS * sc  # noqa: E731
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


# ───────────── épisode 1 en fausse 3D (vue isométrique du village) ─────────────
import iso  # noqa: E402

BASE_ETAT = dict(maire=(0.6, -1.2))
PROJETS = {"1": (iso.RIVIERE_I + 1.0, iso.ROUTE_J + 0.5), "2": (2.8, 1.8), "3": (-2.0, -2.0)}


def vue(etat, z=1.0, center=(540, 960)):
    return iso.camera(iso.carte_cache(etat), z, center)


def pin(img, xy, n, label=None, k=1.0):
    """Repère numéroté planté sur la carte (au-dessus d'un projet)."""
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    x, y = xy
    s = 0.6 + 0.4 * back(k)
    d.line([x, y, x, y - 130 * s], fill=INK, width=8)
    d.ellipse([x - 66 * s, y - 262 * s, x + 66 * s, y - 130 * s], fill=YEL, outline=INK, width=8)
    d.text((x, y - 196 * s), n, font=FA(int(90 * s)), fill=INK, anchor="mm")
    if label:
        tag(img, min(max(x, 250), 830), y + 45, label, 42, WHITE, INK, rot=0, k=k)


def e1_jour(lt, dur):
    img, _ = vue(BASE_ETAT, push(lt, dur, 1.0, 1.12), (560, 930))
    big_number(img, (540, 300), "JOUR 1", 210, YEL, k=1.0)
    tag(img, 540, 520, "FAUCHÉ-LES-OIES", 70, WHITE, ROUGE, rot=-3, k=(lt + 0.3) / 0.3)
    return shake(img, lt)


def e1_fauche(lt, dur):
    bx, by = iso.iso(iso.RIVIERE_I + 1, iso.ROUTE_J + 0.5)
    img, _ = vue(BASE_ETAT, push(lt, dur, 1.9, 2.1), (bx + 40, by - 40))
    tag(img, 540, 260, "LE VILLAGE LE PLUS", 66, WHITE, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 400, "FAUCHÉ DE FRANCE", 80, ROUGE, WHITE, rot=3, k=(lt - 0.4) / 0.25)
    tag(img, 540, 1250, "PONT CASSÉ", 56, YEL, INK, rot=-4, k=(lt - 0.8) / 0.25)
    return flash(img, lt)


def e1_un(lt, dur):
    mx, my = iso.iso(1.1, -0.7)
    img, to = vue(BASE_ETAT, push(lt, dur, 2.1, 2.3), (mx, my - 60))
    big_number(img, (540, 320), "1 HABITANT", 180, WHITE, k=lt / 0.25)
    if lt > 0.9:
        x, y = to(1.1, -0.7, 60)
        tag(img, x, y - 40, "MOI", 64, YEL, INK, rot=-6, k=(lt - 0.9) / 0.25)
    return flash(img, lt)


def e1_regles(lt, dur):
    t_ab, t_co, t_de, t_pa = (T[k] - T["e1_regles"] for k in ("abonne", "comment", "decision", "palier"))
    etat = dict(BASE_ETAT)
    if lt > t_ab:
        n = min(6, int((lt - t_ab) / 0.25) + 1)
        etat["habitants"] = [(0.0, 1.5 + 0.9 * q, (200, 60, 60)) if q % 2 else (1.5 + 0.9 * q, 0.0, (60, 120, 200))
                             for q in range(n)]
    if lt > t_co:
        etat["maisons"] = [round(min(1.0, (lt - t_co) / 0.6), 1)]
    if lt > t_pa:
        etat["mystere"] = round(min(1.0, (lt - t_pa) / 0.5), 1)
    img, to = vue(etat, 1.25, (560, 700))
    if lt > t_co + 0.5:
        x, y = to(*iso.TERRAINS["maisons"][0], 75)
        tag(img, x + 20, y - 30, "@TON_PSEUDO", 36, WHITE, INK, rot=0, k=(lt - t_co - 0.5) / 0.25)
    regles_panel(img, lt, [t_ab, t_co, t_de, t_pa], y0=430)
    return img


def e1_caisse(lt, dur):
    mx, my = iso.iso(1.6, -2.0)
    img, _ = vue(BASE_ETAT, push(lt, dur, 1.6, 1.75), (mx, my + 40))
    tag(img, 540, 260, "CAISSE DE LA MAIRIE", 60, WHITE, INK, rot=-3, k=lt / 0.25)
    big_number(img, (540, 520), counter(0, 1000, lt, 0.7, "{:,} €"), 210, GREEN, k=1.0)
    return flash(img, lt)


def pins(img, to, lt, t0s, labels=True):
    for q, ((n, lab, prix), t0) in enumerate(zip(CHOIX, t0s)):
        i, j = PROJETS[n]
        pin(img, to(i, j), n, None, (lt - t0) / 0.25)
        if labels:   # légende sous la carte, une ligne par choix
            tag(img, 540, 1265 + q * 98, f"{n}  ·  {lab}  ·  {prix}", 44, WHITE, INK, rot=0, k=(lt - t0) / 0.25)


def e1_choix(lt, dur):
    t0s = [0.0, T["deux"] - T["un"], T["trois"] - T["un"]]
    img, to = vue(BASE_ETAT, 1.15, (420, 1010))
    tag(img, 540, 230, "ON FAIT QUOI ?", 80, YEL, INK, rot=-4, k=lt / 0.25)
    pins(img, to, lt, t0s)
    return img


def e1_vote(lt, dur):
    img, to = vue(BASE_ETAT, push(lt, dur, 1.1, 1.18), (420, 800))
    pins(img, to, 9.0, [0, 0, 0], labels=False)
    tag(img, 540, 200, "LE PLUS VOTÉ GAGNE", 64, WHITE, INK, rot=-3, k=lt / 0.25)
    tag(img, 540, 330, "RÉSULTAT DEMAIN", 58, ROUGE, WHITE, rot=3, k=(lt - 0.8) / 0.25)
    big_number(img, (540, 540), "1, 2 OU 3 ?", 180, YEL, "VOTE EN COMMENTAIRE", k=(lt - 1.6) / 0.25)
    tf = T["abo_fin"] - T["e1_vote"]
    tag(img, 540, 1330, "ABONNE-TOI POUR VOIR LE VILLAGE GRANDIR", 44, ROUGE, WHITE, rot=-2, k=(lt - tf) / 0.25)
    return shake(img, lt - 1.6)



# ───────────── épisode 1 : plans repris des comptes qui marchent (sonigz37, paum.les.bains) ─────────────
# Titre en deux lignes en haut (petite ligne blanche + grosse ligne jaune), comme chez eux.

def titre2(img, petit, gros, k=1.0, y=170):
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    s = 0.7 + 0.3 * back(k)
    for txt, size, col, yy in ((petit, int(54 * s), WHITE, y), (gros, int(104 * s), YEL, y + 95 * s)):
        f = FA(size)
        for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5), (-4, -4), (4, 4), (-4, 4), (4, -4)]:
            d.text((540 + dx, yy + dy), txt, font=f, fill=INK, anchor="mm")
        d.text((540, yy), txt, font=f, fill=col, anchor="mm")


def gros_plan_maire(img, lt, **pose):
    """Le maire en très gros plan (buste), posé sur le décor, comme le « mais maintenant il t'a toi »."""
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    maire(d, 540, 2350, lt, sc=2.1, **pose)
    lay = lay.resize((W, H), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)


def foule(lt, n=14):
    """Habitants qui marchent sur les routes."""
    out = []
    for q in range(n):
        v = ((q * 0.37 + lt * 0.5) % 1.0)
        if q % 2:
            out.append((-0.4, -6 + 12 * v, [(200, 60, 60), (60, 120, 200), (240, 180, 40), (120, 200, 120)][q % 4]))
        else:
            out.append((-6 + 12 * v, -0.4, [(60, 120, 200), (200, 60, 60), (120, 200, 120), (240, 180, 40)][q % 4]))
    return [(round(i, 2), round(j, 2), c) for i, j, c in out]


def bouton_abonner(img, x, y, k=1.0):
    if k <= 0:
        return
    s = 0.6 + 0.4 * back(k)
    d = ImageDraw.Draw(img)
    w, h = 300 * s, 80 * s
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=int(h / 2), fill=(235, 40, 60))
    d.text((x, y), "S'ABONNER", font=FA(int(48 * s)), fill=WHITE, anchor="mm")


def p_jour(lt, dur):                     # sonigz : la carte vide, le maire tout petit au carrefour
    img, _ = vue(dict(maire=(0.6, 0.6)), push(lt, dur, 1.0, 1.12), (540, 1020))
    titre2(img, "JOUR 1", "FAUCHÉ-LES-OIES", k=1.0)
    return shake(img, lt)


def p_fauche(lt, dur):                   # paum : un lieu du village avec son étiquette moqueuse
    bx, by = iso.iso(iso.RIVIERE_I + 1, iso.ROUTE_J + 0.5)
    img, to = vue(BASE_ETAT, push(lt, dur, 1.9, 2.1), (bx + 40, by - 60))
    titre2(img, "LE VILLAGE LE PLUS", "FAUCHÉ DE FRANCE", k=lt / 0.25)
    x, y = to(iso.RIVIERE_I + 1, iso.ROUTE_J + 0.5, 30)
    tag(img, x, y - 60, "PONT CASSÉ", 52, ROUGE, WHITE, rot=-4, k=(lt - 0.6) / 0.25)
    return flash(img, lt)


def p_un(lt, dur):                       # sonigz : gros plan du maire
    img, _ = vue(BASE_ETAT, 1.4, (600, 900))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.9, mouth="grin" if lt < 1.0 else "smile")
    titre2(img, "POUR L'INSTANT", "1 SEUL HABITANT", k=lt / 0.25)
    if lt > 0.9:
        tag(img, 820, 760, "MOI", 80, YEL, INK, rot=-8, k=(lt - 0.9) / 0.25)
    return flash(img, lt)


def p_regles(lt, dur):                   # « les règles sont simples » : le maire face caméra
    img, _ = vue(BASE_ETAT, 1.4, (600, 900))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.5, mouth="o" if int(lt * 7) % 2 else "smile")
    titre2(img, "LES RÈGLES", "SONT SIMPLES", k=lt / 0.25)
    return flash(img, lt)


def p_abonne(lt, dur):                   # sonigz : la foule qui arrive sur les routes
    img, _ = iso.camera(iso.carte(dict(BASE_ETAT, habitants=foule(lt))), push(lt, dur, 1.25, 1.35), (500, 980))
    titre2(img, "1 ABONNÉ", "= 1 HABITANT", k=lt / 0.25)
    return flash(img, lt)


def p_commente(lt, dur):                 # sonigz : les maisons qui poussent, une avec ton pseudo
    n = len(iso.TERRAINS["maisons"])
    mk = [round(min(1.0, max(0.0, (lt - 0.25 * q) / 0.5)), 1) for q in range(n)]
    img, to = vue(dict(BASE_ETAT, maisons=mk), push(lt, dur, 1.3, 1.4), (420, 1080))
    titre2(img, "1 COMMENTAIRE", "= TA MAISON", k=lt / 0.25)
    if lt > 0.6:
        x, y = to(*iso.TERRAINS["maisons"][0], 80)
        tag(img, x + 30, y - 40, "@TON_PSEUDO", 46, WHITE, INK, rot=-3, k=(lt - 0.6) / 0.25)
    return flash(img, lt)


def p_decide(lt, dur):                   # sonigz : « toi qui décides », le maire montre la caméra
    img, _ = vue(BASE_ETAT, 1.4, (600, 900))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.75, mouth="o" if int(lt * 7) % 2 else "grin")
    titre2(img, "C'EST TOI", "QUI DÉCIDES", k=lt / 0.25)
    tag(img, 540, 520, "VOTE EN COMMENTAIRE", 56, WHITE, INK, rot=-3, k=(lt - 0.8) / 0.25)
    return flash(img, lt)


def p_surprise(lt, dur):                 # sonigz : le monolithe noir mystère
    big = iso.carte_cache(BASE_ETAT).copy()
    d = ImageDraw.Draw(big)
    mi, mj = iso.TERRAINS["mystere"]
    k = ease(lt / 1.0)
    iso.box(d, mi - 0.3, mj - 0.3, 1.6, 1.6, 300 * k + 2, (24, 24, 30))
    x, y = iso.iso(mi + 0.5, mj + 0.5, 300 * k + 2)
    d.text((x * SS, (y + 6) * SS), "?", font=FA(int(90 * SS)), fill=WHITE, anchor="mm")
    cx, cy = iso.iso(mi + 0.5, mj + 0.5, 120)
    img, _ = iso.camera(big, 1.7, (cx, cy))
    titre2(img, "100 ABONNÉS", "UNE SURPRISE", k=lt / 0.25)
    return shake(img, lt, dur=0.6, amp=10)


def p_caisse(lt, dur):                   # paum : le budget de la mairie, billets qui volent
    mx, my = iso.iso(1.6, -2.0)
    img, _ = vue(BASE_ETAT, push(lt, dur, 1.6, 1.75), (mx, my + 40))
    img = dim(img, 0.3, blur=6, dark=0.9)
    d = ImageDraw.Draw(img)
    for q in range(8):
        a = q * 0.8 + lt * 2
        x = 540 + math.cos(a) * (180 + 60 * q % 3) * ease(lt / 0.6)
        y = 760 + math.sin(a) * 140 * ease(lt / 0.6)
        d.rounded_rectangle([x - 50, y - 26, x + 50, y + 26], radius=6, fill=(90, 180, 110), outline=(40, 110, 60), width=4)
    titre2(img, "PREMIER VOTE", "CAISSE DE LA MAIRIE", k=lt / 0.25)
    big_number(img, (540, 760), counter(0, 1000, lt, 0.7, "{:,} €"), 220, GREEN, k=1.0)
    return flash(img, lt)


def p_choix(lt, dur):                    # sonigz : les projets apparaissent sur leurs terrains, numérotés
    t2, t3 = T["deux"] - T["un"], T["trois"] - T["un"]
    etat = dict(BASE_ETAT, pont=lt > 0.3,
                epicerie=round(min(1.0, max(0.0, (lt - t2) / 0.6)), 1),
                fete=round(min(1.0, max(0.0, (lt - t3) / 0.6)), 1))
    img, to = vue(etat, 1.15, (420, 1010))
    titre2(img, "ON CONSTRUIT QUOI", "EN PREMIER ?", k=lt / 0.25)
    pins(img, to, lt, [0.0, t2, t3])
    return img


def p_gagne(lt, dur):                    # sonigz : le plus voté gagne
    etat = dict(BASE_ETAT, pont=True, epicerie=1.0, fete=1.0)
    img, to = vue(etat, push(lt, dur, 1.15, 1.22), (420, 1010))
    pins(img, to, 9.0, [0, 0, 0], labels=False)
    titre2(img, "LE CHOIX LE PLUS VOTÉ", "GAGNE", k=lt / 0.25)
    tag(img, 540, 1300, "RÉSULTAT DEMAIN", 70, ROUGE, WHITE, rot=-3, k=(lt - 0.9) / 0.25)
    return flash(img, lt)


def p_fin(lt, dur):                      # sonigz : gros plan maire + bouton S'abonner
    img, _ = vue(dict(BASE_ETAT, pont=True, epicerie=1.0, fete=1.0), 1.4, (500, 950))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.95, mouth="grin")
    titre2(img, "1, 2 OU 3 ?", "VOTE EN COMMENTAIRE", k=lt / 0.25)
    tf = T["abo_fin"] - T["p_fin"]
    if lt > tf:
        titre2(img, "ABONNE-TOI POUR VOIR", "LE VILLAGE GRANDIR", k=(lt - tf) / 0.25, y=560)
        bouton_abonner(img, 540, 1250, (lt - tf - 0.3) / 0.25)
    return shake(img, lt)


def episode1(voice_file=None):
    v = CartoonVideo("village_ep01", "scripts/village/ep01.txt", "", "", corner="")
    v.length = (29.0, 30.0, 31.0)
    v.hook_head_start = 0.0
    v.voice(voice_file or "output/_work_village_ep01/voice_raw.mp3")
    sc = [("Jour un", p_jour), ("le village le plus fauché", p_fauche), ("Pour l'instant", p_un),
          ("Les règles sont simples", p_regles), ("Tu t'abonnes", p_abonne), ("Tu commentes", p_commente),
          ("Et chaque décision", p_decide), ("À cent abonnés", p_surprise), ("Premier vote", p_caisse),
          ("Un, réparer", p_choix), ("Le choix le plus voté", p_gagne), ("Vote un, deux", p_fin)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["un"], T["deux"], T["trois"] = v.at("Un, réparer"), v.at("Deux, ouvrir"), v.at("Trois, la fête")
    T["abo_fin"] = v.at("et abonne-toi")
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["p_fauche"], "whoosh", 0.5)
    v.sfx(T["p_un"], "pop", 0.8)
    v.sfx(T["p_abonne"], "pop", 0.8)
    v.sfx(T["p_commente"], "pop", 0.8)
    v.sfx(T["p_surprise"], "impact", 0.9)
    v.sfx(T["p_caisse"], "ticks", 0.7)
    for k in ("un", "deux", "trois"):
        v.sfx(T[k], "pop", 0.8)
    v.sfx(T["p_gagne"], "whoosh", 0.5)
    v.sfx(T["abo_fin"], "succes", 0.8)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()



# ───────────── épisode 2 : résultat, les maisons des habitants, deuxième vote ─────────────

HAB = [  # pseudo, case, couleur, drapeau, rôle
    ("@Amine.6919", (1.3, 3.0), (245, 215, 150), None, "1ER HABITANT"),
    ("@Nelio", (2.5, 3.0), (90, 140, 230), None, None),
    ("@Mskoww_91", (3.7, 3.0), (60, 110, 210), None, None),
    ("@Maël", (2.5, 4.2), (250, 190, 190), None, "ADJOINT ?"),
    ("@Alexis", (1.3, 4.2), (210, 240, 200), None, "CONSEILLER"),
    ("@T_0", (3.7, 4.3), (240, 200, 60), None, "LE RICHE"),
    ("@You", (-2.0, 2.6), (248, 248, 248), "maroc", None),
    ("@ghb_s91", (-3.2, 2.6), (245, 225, 190), "tunisie", None),
    ("@S'", (-2.0, 1.4), (110, 200, 110), None, "FILLE DU MAIRE"),
    ("@rph.49", (-3.2, 1.4), (200, 225, 250), None, None),
    ("@Michael", (-2.0, 3.8), (230, 210, 250), None, "ADJOINT ?"),
    ("@Waillox", (-3.2, 3.8), (250, 230, 200), None, "LE PLUS MALIN"),
]
VILLA = ("@oumar dansoko", (4.6, 5.8))
GROTTE = ("@pkmoi", (5.6, 1.6))
PS5 = ("@ps5", (0.8, 6.2))
VOITURE = ("@kova.zfr", (4.9, 3.0))
FOOT = (-2.8, -2.8)          # terrain de foot à la place de la fête
BOULANGERIE = (3.6, -1.6)


def drapeau(d, i, j, kind):
    x, y = iso.iso(i + 0.5, j + 0.5, 95)
    s, q = SS, iso.HK
    d.line([x * s, y * s, x * s, (y - 50 * q) * s], fill=INK, width=int(3 * q * s))
    w, h = 34 * q, 22 * q
    d.rectangle([x * s, (y - 50 * q) * s, (x + w) * s, (y - 50 * q + h) * s], fill=(200, 30, 40))
    if kind == "maroc":
        d.text(((x + w / 2) * s, (y - 50 * q + h / 2) * s), "★", font=F(int(16 * q * s)), fill=(20, 120, 50), anchor="mm")
    else:
        cx, cy, r = (x + w / 2), (y - 50 * q + h / 2), 7 * q
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=WHITE)


def villa(d, i, j, k):
    iso.box(d, i, j, 1.4, 1.1, 42 * k, (250, 250, 245))
    if k > 0.6:
        iso.box(d, i + 0.15, j + 0.15, 1.1, 0.8, 4, (60, 60, 70), z0=42 * k)
    iso.tile(d, i + 1.55, j + 0.1, (80, 190, 240), 0.9, 0.9)


def grotte(d, i, j, k):
    pts = [iso.iso(i + 0.2, j + 0.9), iso.iso(i + 0.1, j + 0.3, 30 * k), iso.iso(i + 0.6, j + 0.1, 70 * k),
           iso.iso(i + 1.1, j + 0.2, 40 * k), iso.iso(i + 1.2, j + 0.9)]
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=(130, 125, 120))
    ex, ey = iso.iso(i + 0.7, j + 0.95)
    q = iso.HK * k
    d.chord([(ex - 22 * q) * SS, (ey - 40 * q) * SS, (ex + 22 * q) * SS, (ey + 10 * q) * SS], 180, 360, fill=(40, 35, 32))


def ps5(d, i, j, k):
    h = 95 * k
    iso.box(d, i, j, 0.28, 0.8, h, (245, 245, 250))
    iso.box(d, i + 0.28, j, 0.14, 0.8, h * 0.96, (25, 25, 30))
    iso.box(d, i + 0.42, j, 0.28, 0.8, h, (245, 245, 250))


def voiture(d, i, j, k):
    iso.box(d, i, j, 1.0, 0.7, 26 * k, (215, 40, 50))
    if k > 0.5:
        iso.box(d, i + 0.2, j + 0.1, 0.55, 0.5, 20, (190, 225, 245), z0=26 * k)
    for (a, b) in ((0.15, 0.7), (0.75, 0.7)):
        x, y = iso.iso(i + a, j + b, 4)
        r = 10 * iso.HK
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=INK)


def ep2_village(d, kh=None, kspec=1.0, extra_terrains=False):
    """Dessine les maisons des habitants (kh : liste de facteurs de croissance) + bâtiments spéciaux."""
    objs = []
    for n, (pseudo, (i, j), col, flag, role) in enumerate(HAB):
        k = 1.0 if kh is None else (kh[n] if n < len(kh) else 0.0)
        if k <= 0:
            iso.terrain(d, i, j)
            continue
        roof_col = (205, 160, 40) if pseudo == "@T_0" else (205, 75, 60)
        objs.append((i + j, lambda i=i, j=j, k=k, c=col, rc=roof_col, f=flag: (
            iso.maison(d, i, j, k, c, rc), f and k >= 1 and drapeau(d, i, j, f))))
    kv = 1.0 if kh is None else (kh[11] if len(kh) > 11 else 0.0)
    if kv > 0:
        objs.append((VOITURE[1][0] + VOITURE[1][1], lambda: voiture(d, *VOITURE[1], kv)))
    else:
        iso.terrain(d, *VOITURE[1])
    for (_, (i, j)), fn in ((VILLA, villa), (GROTTE, grotte), (PS5, ps5)):
        if kspec > 0:
            objs.append((i + j + 1, lambda i=i, j=j, fn=fn: fn(d, i, j, kspec)))
        else:
            iso.terrain(d, i, j, 1.4, 1.0)
    if extra_terrains:
        iso.terrain(d, *BOULANGERIE, 1.2, 1.2)
    for _, fn in sorted(objs, key=lambda o: o[0]):
        fn()


def vue2(etat, z, center, **kw):
    big = iso.carte_cache(etat).copy()
    ep2_village(ImageDraw.Draw(big), **kw)
    return iso.camera(big, z, center)


E2 = dict(maire=(0.6, -1.2), epicerie=1.0, maisons=[], terrains=False)


def label(img, to, i, j, txt, k=1.0, col=WHITE, fg=INK, z=110):
    x, y = to(i + 0.5, j + 0.5, z)
    tag(img, x, y, txt, 30, col, fg, rot=0, k=k)


def e2_jour(lt, dur):
    """Ouverture : le panneau d'entrée de ville, en grand, comme les vidéos qui marchent."""
    img, _ = vue2(dict(E2, epicerie=0), push(lt, dur, 1.0, 1.1), (540, 1020), kh=[0] * 12, kspec=0)
    img = dim(img, 0.25, blur=5, dark=0.9)
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    panneau(ImageDraw.Draw(lay), 540, 820, "FAUCHÉ-LES-OIES")
    lay = lay.resize((W, H), Image.LANCZOS)
    sc = 0.7 + 0.3 * back(lt / 0.35) if lt < 0.35 else 1.0
    lay = lay.resize((int(W * 1.25 * sc), int(H * 1.25 * sc)), Image.LANCZOS)
    img.paste(lay, (int(540 - 540 * 1.25 * sc), int(820 - 820 * 1.25 * sc)), lay)
    titre2(img, "JOUR 2", "VOUS AVEZ VOTÉ", k=1.0, y=230)
    return shake(img, lt)


def e2_votes(lt, dur):
    img, _ = vue2(dict(E2, epicerie=0), 1.0, (540, 1020), kh=[0] * 12, kspec=0)
    img = dim(img, 0.8)
    titre2(img, "RÉSULTAT", "64 VOTES", k=lt / 0.25)
    d = ImageDraw.Draw(img)
    rows = [("1 · RÉPARER LE PONT", 26, (120, 120, 132)), ("2 · OUVRIR UNE ÉPICERIE", 66, GREEN),
            ("3 · LA FÊTE DU VILLAGE", 8, (120, 120, 132))]
    for q, (lab, pct, col) in enumerate(rows):
        y = 620 + q * 210
        k = ease((lt - 0.3 - 0.25 * q) / 0.8)
        d.rounded_rectangle([90, y, 990, y + 120], radius=24, fill=(250, 250, 252))
        if k > 0:
            d.rounded_rectangle([90, y, 90 + max(48, 900 * pct / 100 * k), y + 120], radius=24, fill=col)
        d.text((120, y + 60), lab, font=FA(52), fill=INK, anchor="lm")
        d.text((960, y + 60), f"{int(pct * k)} %", font=FA(60), fill=INK, anchor="rm")
    return img


def e2_epicerie(lt, dur):
    k = round(min(1.0, ease(lt / 1.0)), 2)
    ex, ey = iso.iso(2.8, 1.8)
    img, to = vue2(dict(E2, epicerie=max(0.01, k), habitants=foule(lt, 8)), push(lt, dur, 1.9, 2.1), (ex, ey - 60),
                   kh=[0] * 12, kspec=0)
    titre2(img, "L'ÉPICERIE", "GAGNE !", k=lt / 0.25)
    if lt > 1.0:
        tag(img, 540, 1250, "OUVERTE AUJOURD'HUI", 64, GREEN, INK, rot=-3, k=(lt - 1.0) / 0.25)
    return shake(flash(img, lt), lt, dur=0.4, amp=10)


def e2_caisse(lt, dur):
    mx, my = iso.iso(1.6, -2.0)
    img, _ = vue2(E2, push(lt, dur, 1.6, 1.75), (mx, my + 40), kh=[0] * 12, kspec=0)
    img = dim(img, 0.3, blur=6, dark=0.9)
    titre2(img, "CAISSE DE LA MAIRIE", "−700 €", k=lt / 0.25)
    big_number(img, (540, 760), counter(1000, 300, lt - 0.3, 0.9, "{:,} €"), 220, GREEN, k=1.0)
    return flash(img, lt)


def e2_revenu(lt, dur):
    """L'épicerie rapporte 5 € par habitant et par jour : la caisse remonte."""
    ex, ey = iso.iso(2.8, 1.8)
    img, _ = iso.camera(iso.carte(dict(E2, habitants=foule(lt, 18))), push(lt, dur, 1.45, 1.6), (ex, ey - 40))
    img = dim(img, 0.25, blur=4, dark=0.92)
    titre2(img, "L'ÉPICERIE RAPPORTE", "5 € / HABITANT / JOUR", k=lt / 0.25)
    t1, t2, t3 = (T[k] - T["e2_revenu"] for k in ("vous50", "caisse550", "riche"))
    if lt > t1:
        big_number(img, (540, 640), "50 × 5 € = +250 €", 120, GREEN, "PAR JOUR", k=(lt - t1) / 0.25)
    if lt > t2:
        big_number(img, (540, 980), counter(300, 550, lt - t2, 0.8, "{:,} €"), 200, YEL, "DANS LA CAISSE", k=1.0, rot=-3)
    if lt > t3:
        tag(img, 540, 1330, "PLUS D'HABITANTS = PLUS D'ARGENT", 54, ROUGE, WHITE, rot=-3, k=(lt - t3) / 0.25)
    return flash(img, lt)


def e2_remplit(lt, dur):
    img, _ = iso.camera(iso.carte(dict(E2, habitants=foule(lt, 18))), push(lt, dur, 1.1, 1.2), (520, 1060))
    titre2(img, "LE VILLAGE SE REMPLIT", "+50 HABITANTS", k=lt / 0.25)
    return flash(img, lt)


def e2_maisons(lt, dur):
    third = dur / 3
    kh = [round(min(1.0, max(0.0, (lt - (n // 4) * third - 0.2 * (n % 4)) / 0.45)), 1) for n in range(12)]
    g = min(2, int(lt / third))
    idx = range(g * 4, g * 4 + 4)
    pts = [HAB[n][1] for n in idx]
    ci = sum(p[0] for p in pts) / 4 + 0.5
    cj = sum(p[1] for p in pts) / 4 + 0.5
    cx, cy = iso.iso(ci, cj)
    img, to = vue2(E2, 2.0, (cx, cy - 30), kh=kh, kspec=0)
    titre2(img, "LES MAISONS POUSSENT", "AVEC VOS PSEUDOS", k=lt / 0.25)
    if g == 0 and kh[11] >= 1 and False:
        label(img, to, *VOITURE[1], VOITURE[0], k=(lt - 2.5) / 0.2, z=70)
        x, y = to(VOITURE[1][0] + 0.5, VOITURE[1][1] + 0.5, 70)
        tag(img, x, y + 48, "MAISON-VOITURE", 24, YEL, INK, rot=0, k=(lt - 2.6) / 0.2)
    for n in idx:
        pseudo, (i, j), _, _, role = HAB[n]
        if kh[n] >= 1:
            x, y = to(i + 0.5, j + 0.5, 110)
            tn = (n // 4) * third + 0.2 * (n % 4) + 0.45
            tag(img, x, y, pseudo, 34, WHITE, INK, rot=0, k=(lt - tn) / 0.2)
            if role:
                x, y = to(i + 0.5, j + 0.5, 110)
                tag(img, x, y + 56, role, 28, YEL, INK, rot=0, k=(lt - tn - 0.15) / 0.2)
    return flash(img, lt - g * third)


def e2_speciaux(lt, dur):
    T0, T1, T2 = (T[k] - T["e2_speciaux"] for k in ("villa", "grotte", "ps5"))
    if lt < T1:
        (pseudo, (i, j)), title = VILLA, ("LA VILLA", "AVEC PISCINE")
        t0 = 0.0
    elif lt < T2:
        (pseudo, (i, j)), title = GROTTE, ("LA GROTTE", "DE L'HOMME DES CAVERNES")
        t0 = T1
    else:
        (pseudo, (i, j)), title = PS5, ("ET MÊME", "LA MAISON PS5")
        t0 = T2
    k = round(min(1.0, ease((lt - t0) / 0.6)), 2)
    cx, cy = iso.iso(i + 0.7, j + 0.6)
    img, to = vue2(E2, 2.2, (cx, cy - 60), kspec=max(0.01, k))
    titre2(img, *title, k=(lt - t0) / 0.25)
    if k >= 1:
        label(img, to, i + 0.2, j, pseudo, k=(lt - t0 - 0.6) / 0.2, z=130)
    return shake(flash(img, lt - t0), lt - t0, dur=0.3, amp=8)


CHOIX2 = [("1", "TERRAIN DE FOOT", "250 €", FOOT), ("2", "BOULANGERIE", "300 €", BOULANGERIE),
          ("3", "GARDER L'ARGENT POUR LE PONT", "0 €", (iso.RIVIERE_I + 1.0, iso.ROUTE_J + 0.5))]


def e2_vote(lt, dur):
    t0s = [T["c1"] - T["e2_vote"], T["c2"] - T["e2_vote"], T["c3"] - T["e2_vote"]]
    img, to = vue2(E2, 1.0, (540, 1000), extra_terrains=True)
    titre2(img, "DEUXIÈME VOTE", "550 € DANS LA CAISSE", k=lt / 0.25)
    for q, ((n, lab, prix, (i, j)), t0) in enumerate(zip(CHOIX2, t0s)):
        pin(img, to(i + 0.6, j + 0.6), n, None, (lt - t0) / 0.25)
        tag(img, 540, 1400 + q * 98, f"{n}  ·  {lab}  ·  {prix}", 42, WHITE, INK, rot=0, k=(lt - t0) / 0.25)
    return img


def e2_fin(lt, dur):
    img, _ = vue2(E2, 1.4, (500, 950))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.95, mouth="o" if int(lt * 7) % 2 else "grin")
    titre2(img, "PLUS QUE 50 HABITANTS", "AVANT LA SURPRISE", k=lt / 0.25)
    tv = T["vote_fin"] - T["e2_fin"]
    if lt > tv:
        titre2(img, "1, 2 OU 3 ?", "VOTE EN COMMENTAIRE", k=(lt - tv) / 0.25, y=560)
        bouton_abonner(img, 540, 1250, (lt - tv - 0.4) / 0.25)
    return shake(img, lt)


def episode2(voice_file=None):
    v = CartoonVideo("village_ep02", "scripts/village/ep02.txt", "", "", corner="")
    v.length = (33.0, 34.0, 35.0)
    v.hook_head_start = 0.0
    v.voice(voice_file or "output/_work_village_ep02/voice_raw.mp3")
    sc = [("Jour deux", e2_jour), ("Soixante-quatre votes", e2_votes), ("c'est l'épicerie qui gagne", e2_epicerie),
          ("Dans la caisse", e2_caisse), ("Mais l'épicerie rapporte", e2_revenu),
          ("Et les maisons poussent", e2_maisons), ("La villa avec piscine", e2_speciaux),
          ("Deuxième vote", e2_vote), ("Plus que cinquante", e2_fin)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["vous50"], T["caisse550"], T["riche"] = v.at("Vous êtes cinquante"), v.at("La caisse remonte"), v.at("Plus vous êtes")
    T["villa"], T["grotte"], T["ps5"] = v.at("La villa"), v.at("la grotte"), v.at("et même la maison")
    T["c1"], T["c2"], T["c3"] = v.at("Un, un terrain"), v.at("Deux, une boulangerie"), v.at("Trois, on garde")
    T["vote_fin"] = v.at("Vote un, deux")
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["e2_votes"] + 0.3, "ticks", 0.6)
    v.sfx(T["e2_epicerie"], "succes", 1.0)
    v.sfx(T["e2_caisse"] + 0.3, "ticks", 0.6)
    v.sfx(T["vous50"], "pop", 0.8)
    v.sfx(T["caisse550"], "ticks", 0.7)
    v.sfx(T["caisse550"] + 0.8, "succes", 0.8)
    v.sfx(T["e2_maisons"], "pop", 0.8)
    for k in ("villa", "grotte", "ps5"):
        v.sfx(T[k], "pop", 0.8)
    for k in ("c1", "c2", "c3"):
        v.sfx(T[k], "pop", 0.7)
    v.sfx(T["vote_fin"], "impact", 0.9)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()



if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ep", type=int, default=1)
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    {1: episode1, 2: episode2}[a.ep](a.voice_file)
