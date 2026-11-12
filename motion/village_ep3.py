"""Fauché-les-Oies, jour 3 : Maël adjoint, le foot gagne, 11 000 € de dons, on construit tout, et une lueur verte…"""
import math

from PIL import Image, ImageDraw, ImageFilter

import facades
import rue
import iso
import village_ep2 as v2
from cartoon import (FA, GREEN, INK, RED, WHITE, YEL, CartoonVideo, big_number, counter, dim, ease, flash, push, shake,
                     shock_lines, tag)
from village import ROUGE, bouton_abonner, gros_plan_maire, pin, titre2

T = {}
P = v2.PERSOS
P.update({
    "Maël": (dict(shirt=(250, 170, 200), pants=(240, 240, 240), hair=(60, 40, 30), mouth="grin", arm=0.95), ["rosette"],
             "ÉLU ADJOINT · 82 %"),
    "al_bsc": (dict(shirt=(250, 250, 250), pants=(40, 40, 50), hair=(30, 25, 20), mouth="grin"), ["toque"],
               "LE RESTAURANT D'AL"),
    "rph.49": (dict(shirt=(120, 40, 60), pants=(40, 30, 40), hair=(70, 50, 30), mouth="grin", brows="colere", arm=0.9),
               ["couronne"], "VEUT DÉFIER LE MAIRE"),
    "Louane_": (dict(shirt=(250, 210, 230), pants=(60, 160, 220), hair=(140, 80, 40), long_hair=True, mouth="grin",
                     arm=0.95), ["lunettes_soleil"], "VILLA 8 CHAMBRES · SPA · GYM"),
    "Mskoww_91": (dict(shirt=(30, 30, 36), pants=(60, 110, 210), hair=(25, 20, 18), mouth="grin"), [],
                  "CONCESSION MOTOCROSS"),
})
CONSTRUCTIONS = [  # pseudo, façade, rôle
    ("Kuromi", "boulangerie", "LA BOULANGERIE"),
    ("SKR junior", "boxe", "LE CLUB DE BOXE"),
    ("al_bsc", "restaurant", None),
    ("Louane_", "villa_spa", None),
    ("Mskoww_91", "motocross", None),
    ("Waillox", "usine", "L'USINE WAITROLLOX"),
]


# ───────────── compteurs permanents : habitants + caisse ─────────────

def caisse(t):
    v = 315
    if "don1" in T and t >= T["don1"]:
        v += int(1000 * ease((t - T["don1"]) / 0.5))
    if "don2" in T and t >= T["don2"]:
        v += int(10000 * ease((t - T["don2"]) / 0.7))
    if "boul" in T and t >= T["boul"]:
        v -= int(300 * ease((t - T["boul"]) / 0.5))
    if "boxe" in T and t >= T["boxe"]:
        v -= int(400 * ease((t - T["boxe"]) / 0.5))
    return v


def habitants(t):
    return 68 if "68e" in T and t >= T["68e"] + 0.3 else 67


def compteur(img, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 40, 330, 210], radius=20, fill=(20, 20, 26))
    d.text((52, 66), "HABITANTS", font=FA(26), fill=(200, 200, 210), anchor="lm")
    h = habitants(t)
    d.text((52, 112), f"{h}", font=FA(64), fill=YEL if h > 67 else WHITE, anchor="lm")
    d.text((150, 118), "/ 100", font=FA(32), fill=(150, 150, 160), anchor="lm")
    d.text((52, 178), f"CAISSE {caisse(t):,} €".replace(",", " "), font=FA(30), fill=GREEN, anchor="lm")


def avec_caisse(fn):
    def g(lt, dur):
        img = fn(lt, dur)
        compteur(img, T.get(fn.__name__, 0) + lt)
        return img
    g.__name__ = fn.__name__
    return g


# ───────────── nuit ─────────────

def nuit(img, to, lt, force=1.0):
    bleu = Image.new("RGB", img.size, (15, 25, 70))
    img = Image.blend(img, bleu, 0.55 * force)
    gi, gj = v2.GROTTE
    x, y = to(gi + 1.0, gj + 1.0, 30)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pul = 1 + 0.15 * math.sin(lt * 6)
    for r, a in ((260, 50), (170, 90), (90, 150)):
        rr = r * pul * force
        d.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], fill=(90, 255, 120, a))
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    img.paste(lay, (0, 0), lay)
    return img


# ───────────── scènes ─────────────

def s_froid(lt, dur):
    """Ouverture : la nuit, l'oie disparue, la lueur verte."""
    img, to = v2.vue(push(lt, dur, 1.6, 1.9), iso.iso(v2.GROTTE[0] + 1, v2.GROTTE[1] + 1))
    img = nuit(img, to, lt)
    titre2(img, "CETTE NUIT, À FAUCHÉ-LES-OIES", "UNE OIE A DISPARU", k=1.0, y=300)
    tl = T["lueur"] - T["s_froid"]
    if lt > tl:
        tag(img, 540, 1300, "UNE LUEUR VERTE PRÈS DE LA GROTTE", 48, (40, 200, 90), INK, rot=-3, k=(lt - tl) / 0.25)
        return shake(img, lt - tl, dur=0.5, amp=10)
    return shake(img, lt)


def s_hier(lt, dur):
    img = facades.decor().copy()
    lay = rue.panneau_ville("FAUCHÉ-LES-OIES", 67, y=640, s=1.0).resize((1080, 1920), Image.LANCZOS)
    img.paste(lay, (0, 0), lay)
    titre2(img, "POURTANT, HIER", "TOUT ALLAIT BIEN", k=lt / 0.25, y=260)
    return flash(img, lt)


def s_mael(lt, dur):
    img = v2.fiche(lt + 0.9, dur, "Maël", nom="@MAËL · ADJOINT", role="ÉLU AVEC 82 % DES VOIX")
    if lt > 0.2:
        d = ImageDraw.Draw(img)
        for k in range(40):
            x = (k * 97 + 40) % 1080
            y = ((k * 53) % 700 + lt * 420 * (0.6 + (k % 5) / 5)) % 1920
            d.rectangle([x, y, x + 16, y + 26], fill=[(250, 80, 80), (255, 210, 40), (60, 150, 230), (80, 200, 120)][k % 4])
    return img


def s_foot(lt, dur):
    fi, fj = v2.FOOT
    x, y = iso.iso(fi + 0.8, fj + 0.8)
    img, to = iso.camera(v2.carte_j2("foot", extra=("foot",)), push(lt, dur, 2.4, 2.7), (x, y - 20))
    v2.perso(img, "S2Z", lt, x=800, sc=0.9, base=1950)
    titre2(img, "LE TERRAIN DE FOOT", "DE @S2Z · CONSTRUIT", k=lt / 0.25, y=260)
    tag(img, 330, 560, "61 %", 90, GREEN, INK, rot=-6, k=(lt - 0.4) / 0.25)
    return shake(flash(img, lt), lt, dur=0.3, amp=10)


def s_dons(lt, dur):
    img, _ = v2.vue(1.0, (540, 960))
    img = dim(img, 0.85)
    titre2(img, "LES DONS", "ONT EXPLOSÉ", k=lt / 0.25, y=290)
    d = ImageDraw.Draw(img)
    rows = [("@T_0", "+1 000 €", T["don1"] - T["s_dons"]), ("LE SECRÉTAIRE DE MAIRIE", "+10 000 €", T["don2"] - T["s_dons"])]
    for k, (qui, combien, t0) in enumerate(rows):
        if lt < t0:
            continue
        y = 640 + k * 190
        d.rounded_rectangle([90, y, 990, y + 150], radius=26, fill=(250, 250, 252))
        d.text((130, y + 75), qui, font=FA(46), fill=INK, anchor="lm")
        d.text((950, y + 75), combien, font=FA(62), fill=GREEN, anchor="rm")
    tt = T["onze"] - T["s_dons"]
    if lt > tt:
        big_number(img, (540, 1180), "11 000 €", 190, YEL, "DANS LA CAISSE", k=(lt - tt) / 0.25, rot=-3)
        return shake(img, lt - tt)
    return img


def s_construit(lt, dur):
    t0s = [T[k] - T["s_construit"] for k in ("c0", "c1", "c2", "c3", "c4", "c5")]
    n = max(i for i, t in enumerate(t0s) if lt >= t) if lt >= t0s[0] else -1
    if n < 0:
        img, _ = v2.vue(1.0, (540, 960))
        titre2(img, "ALORS", "ON A TOUT CONSTRUIT", k=lt / 0.25, y=290)
        return shake(img, lt)
    pseudo, kind, role = CONSTRUCTIONS[n]
    l = lt - t0s[n]
    img = facades.decor().copy()
    facades.poser(img, facades.calque(kind), v2.pop_k(l, t0=0.0, duree=0.35))
    v2.poussiere(img, l, t0=0.0, duree=0.35)
    if l > 0.35:
        v2.perso(img, pseudo, l - 0.35, x=800, sc=0.85, base=1920)
        v2.etiquette(img, 800, 1920 - 765 - 40, "@" + pseudo.rstrip("_"))
    titre2(img, "ON A TOUT CONSTRUIT", "@" + pseudo.rstrip("_").upper(), k=1.0, y=290)
    tag(img, 540, 480, role or P[pseudo][2], 46, ROUGE, WHITE, rot=-3, k=(l - 0.2) / 0.2)
    return shake(img, l - 0.3, dur=0.2, amp=12)


def s_chateau(lt, dur):
    img = facades.decor().copy()
    facades.poser(img, facades.calque("chateau"), v2.pop_k(lt, t0=0.0, duree=0.4))
    v2.poussiere(img, lt, t0=0.0, duree=0.4)
    if lt > 0.4:
        v2.perso(img, "rph.49", lt - 0.4, x=800, sc=0.85, base=1920)
        v2.etiquette(img, 800, 1920 - 765 - 40, "@rph.49")
    titre2(img, "MAIS @RPH.49", "S'EST CONSTRUIT UN CHÂTEAU", k=lt / 0.25, y=290)
    tv = T["place"] - T["s_chateau"]
    if lt > tv:
        tag(img, 540, 500, "IL VEUT PRENDRE LA PLACE DU MAIRE", 50, RED, WHITE, rot=-3, k=(lt - tv) / 0.25)
        return shake(img, lt - tv, dur=0.4, amp=12)
    return img


def s_vote(lt, dur):
    img, to = v2.vue(1.15, iso.iso(v2.GROTTE[0], v2.GROTTE[1] + 2))
    img = nuit(img, to, lt)
    titre2(img, "ET MAINTENANT, LA GROTTE", "ON FAIT QUOI ?", k=lt / 0.25, y=290)
    t1, t2 = T["v1"] - T["s_vote"], T["v2"] - T["s_vote"]
    tag(img, 540, 1250, "1 · ON ENVOIE @PKMOI VOIR", 54, YEL, INK, rot=-2, k=(lt - t1) / 0.25)
    tag(img, 540, 1380, "2 · DES CAMÉRAS (500 €)", 54, WHITE, INK, rot=2, k=(lt - t2) / 0.25)
    if lt > t1:
        v2.perso(img, "pkmoi", lt - t1, x=850, sc=0.7, base=1150)
    return img


def s_fin(lt, dur):
    img, _ = v2.vue(1.4, (500, 950))
    img = dim(img, 0.35, blur=8, dark=0.85)
    gros_plan_maire(img, lt, arm=0.95, mouth="o" if int(lt * 7) % 2 else "grin")
    titre2(img, "ABONNE-TOI", "TU DEVIENS LE 68E HABITANT", k=lt / 0.25, y=290)
    bouton_abonner(img, 540, 470, (lt - 0.4) / 0.25)
    tp = T["pote"] - T["s_fin"]
    if lt > tp:
        tag(img, 540, 590, "ENVOIE ÇA À TON POTE", 60, YEL, INK, rot=-3, k=(lt - tp) / 0.25)
        tag(img, 540, 700, "SA MAISON SERA À CÔTÉ DE LA TIENNE", 42, WHITE, INK, rot=2, k=(lt - tp - 0.6) / 0.25)
    return shake(img, lt)


def main():
    v = CartoonVideo("village_ep03", "scripts/village/ep03.txt", "", "", corner="")
    v.length = (45.0, 47.0, 50.0)
    v.hook_head_start = 0.0
    v.voice("output/_work_village_ep03/voice_raw.mp3")
    sc = [("Cette nuit", s_froid), ("Pourtant, hier", s_hier), ("Maël élu", s_mael), ("Le terrain de foot", s_foot),
          ("Et les dons", s_dons), ("Alors on a tout", s_construit), ("Mais R P H", s_chateau),
          ("Et maintenant, la grotte", s_vote), ("Abonne-toi", s_fin)]
    for phrase, fn in sc:
        T[fn.__name__] = v.at(phrase)
    T["lueur"] = v.at("Et près de la grotte")
    T["don1"], T["don2"], T["onze"] = v.at("Mille euros de"), v.at("Dix mille du"), v.at("Onze mille euros")
    for k, ph in enumerate(("La boulangerie", "La boxe", "Le restaurant", "La villa spa", "La boutique", "L'usine")):
        T[f"c{k}"] = v.at(ph)
    T["boul"], T["boxe"] = T["c0"] + 0.4, T["c1"] + 0.4
    T["place"] = v.at("Et il veut prendre")
    T["v1"], T["v2"] = v.at("Un, on envoie"), v.at("Deux, on installe")
    T["68e"], T["pote"] = v.at("tu deviens le soixante-huitième"), v.at("Et envoie ça")
    for phrase, fn in sc:
        v.scene(phrase, avec_caisse(fn))
    v.sfx(0.0, "impact", 1.0)
    v.sfx(0.1, "rate", 0.7)
    v.sfx(T["lueur"], "impact", 0.9)
    v.sfx(T["s_hier"], "whoosh", 0.6)
    v.sfx(T["s_mael"], "succes", 0.8)
    v.sfx(T["s_foot"], "pop", 0.8)
    v.sfx(T["don1"], "ticks", 0.6)
    v.sfx(T["don2"], "ticks", 0.7)
    v.sfx(T["onze"], "succes", 1.0)
    for k in range(6):
        v.sfx(T[f"c{k}"], "marteau", 0.55)
        v.sfx(T[f"c{k}"] + 0.3, "impact", 0.5)
    v.sfx(T["s_chateau"], "marteau", 0.6)
    v.sfx(T["place"], "impact", 1.0)
    v.sfx(T["s_vote"], "rate", 0.7)
    v.sfx(T["v1"], "pop", 0.8)
    v.sfx(T["v2"], "pop", 0.8)
    v.sfx(T["68e"], "succes", 0.9)
    v.sfx(T["pote"], "notif", 0.8)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
