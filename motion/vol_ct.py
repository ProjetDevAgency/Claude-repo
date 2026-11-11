"""Tes droits : vol en retard, la compagnie doit indemniser. Format Kévin v2 (audit laficelle)."""
import math

from PIL import Image, ImageDraw

from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, notif, phone_big, push, shake, shock_lines, shot, tag)
from engine import H, W
import rue

BASE = 1560
AGENTE = dict(shirt=(30, 60, 140), pants=(30, 40, 80), hair=(60, 35, 25), long_hair=True)
SARAH = dict(shirt=(230, 120, 160), pants=(40, 50, 80), hair=(150, 90, 40), long_hair=True)
KX, AX = 300, 780
AHEAD = (AX, BASE - 40 - 700)
KHEAD = (KX, BASE - 700)
T = {}
_bg = {}


# ───────────── décors ─────────────

def hall():
    """Hall d'aéroport : grandes baies avec un avion, tableau des départs, carrelage."""
    if "h" in _bg:
        return _bg["h"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), (215, 225, 235))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 200 * s, W * s, 1050 * s], fill=(150, 200, 240))                 # baies vitrées
    for x in range(0, W, 180):
        d.rectangle([x * s, 200 * s, (x + 14) * s, 1050 * s], fill=(110, 120, 135))
    d.rectangle([0, 190 * s, W * s, 215 * s], fill=(110, 120, 135))
    d.polygon([(200 * s, 760 * s), (760 * s, 700 * s), (860 * s, 720 * s), (240 * s, 800 * s)], fill=(245, 245, 250))
    d.polygon([(470 * s, 730 * s), (560 * s, 600 * s), (620 * s, 600 * s), (560 * s, 725 * s)], fill=(230, 230, 238))
    d.polygon([(250 * s, 770 * s), (220 * s, 680 * s), (260 * s, 680 * s), (300 * s, 765 * s)], fill=(230, 60, 60))
    d.rectangle([0, 1050 * s, W * s, H * s], fill=(200, 205, 212))                    # carrelage
    for y in range(1050, H, 90):
        d.line([0, y * s, W * s, y * s], fill=(185, 190, 198), width=3 * s)
    _bg["h"] = im
    return im


def tableau(d, y0=260, rows=(("LISBONNE", "07:00", "RETARDÉ"), ("MADRID", "07:20", "À L'HEURE"),
                             ("ROME", "07:45", "À L'HEURE"))):
    s = SS
    d.rounded_rectangle([90 * s, y0 * s, 990 * s, (y0 + 330) * s], radius=18 * s, fill=(25, 25, 32))
    d.text((540 * s, (y0 + 45) * s), "DÉPARTS", font=FA(int(52 * s)), fill=YEL, anchor="mm")
    for k, (dest, h, st) in enumerate(rows):
        y = y0 + 120 + k * 75
        d.text((130 * s, y * s), dest, font=FA(int(46 * s)), fill=WHITE, anchor="lm")
        d.text((560 * s, y * s), h, font=FA(int(46 * s)), fill=YEL, anchor="mm")
        d.text((950 * s, y * s), st, font=FA(int(42 * s)), fill=(240, 70, 70) if st == "RETARDÉ" else GREEN,
               anchor="rm")


def comptoir(d):
    s = SS
    d.rectangle([520 * s, 1180 * s, W * s, 1500 * s], fill=(70, 80, 100))
    d.rectangle([520 * s, 1170 * s, W * s, 1200 * s], fill=(230, 230, 236))
    d.rounded_rectangle([640 * s, 1240 * s, 960 * s, 1300 * s], radius=10 * s, fill=(30, 60, 140))
    d.text((800 * s, 1270 * s), "ENREGISTREMENT", font=FA(int(30 * s)), fill=WHITE, anchor="mm")


def scene(t, kpose=None, agente=None, sarah=None, z=1.0, center=None, board=True, banc=False, kx=KX):
    big = hall().copy()
    d = ImageDraw.Draw(big)
    if board:
        tableau(d)
    if banc:
        s = SS
        d.rounded_rectangle([140 * s, 1330 * s, 940 * s, 1380 * s], radius=10 * s, fill=(90, 100, 120))
        for x in (180, 880):
            d.rectangle([x * s, 1380 * s, (x + 20) * s, 1480 * s], fill=(70, 80, 95))
    if agente is not None:
        bob, blink = idle(t, 0.4)
        character(d, AX, BASE - 40 + bob, **{**AGENTE, "blink": blink, **agente})
        x, y = AX * SS, (BASE - 40 + bob - 540) * SS                                    # foulard de la compagnie
        d.polygon([(x - 50 * SS, y), (x + 50 * SS, y), (x, y + 60 * SS)], fill=(230, 60, 60))
        comptoir(d)
    if sarah is not None:
        bob, blink = idle(t, 1.7)
        character(d, 560 if banc else 560, BASE + bob, **{**SARAH, "blink": blink, **sarah})
    if kpose:
        kevin(d, kx, BASE, kpose, t)
    img = shot(big, z, center=center)
    return rue.contour_aretes(img, seuil=90, w=3)


def badge(img, x, y, txt):
    tag(img, x, y, txt, 30, RED, WHITE, rot=0, k=1.0)


def carte_sombre(img, titre, rows, lt, y0=560, sous=None):
    """Carte d'explication sur fond sombre : titre jaune, lignes qui s'allument, surlignage."""
    d = ImageDraw.Draw(img)
    h = 170 + 120 * len(rows)
    d.rounded_rectangle([70, y0, 1010, y0 + h], radius=34, fill=(28, 28, 36))
    d.text((540, y0 + 70), titre, font=FA(58), fill=YEL, anchor="mm")
    if sous:
        d.text((540, y0 + 125), sous, font=FA(32), fill=(170, 170, 185), anchor="mm")
    for k, (txt, t0, hl) in enumerate(rows):
        if lt < t0:
            continue
        y = y0 + 190 + k * 120
        if hl:
            w = 860 * ease((lt - t0) / 0.4)
            d.rounded_rectangle([110, y - 44, 110 + w, y + 44], radius=14, fill=(255, 210, 50))
        d.text((130, y), txt, font=FA(46), fill=INK if hl else WHITE, anchor="lm")


# ───────────── compteur permanent ─────────────

def valeur(t):
    if "c250" not in T or t < T["c250"]:
        return 0
    if t < T["c500"]:
        return int(250 * ease((t - T["c250"]) / 0.6))
    return int(250 + 250 * ease((t - T["c500"]) / 0.6))


def compteur(img, v):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([30, 40, 420, 150], radius=18, fill=(20, 20, 26))
    d.text((52, 66), "DÛ PAR LA COMPAGNIE", font=FA(26), fill=(200, 200, 210), anchor="lm")
    d.text((52, 116), f"{v:,} €".replace(",", " "), font=FA(56), fill=GREEN if v else (240, 80, 80), anchor="lm")


def avec_compteur(fn):
    def g(lt, dur):
        img = fn(lt, dur)
        compteur(img, valeur(T.get(fn.__name__, 0) + lt))
        return img
    g.__name__ = fn.__name__
    return g


def talk(t):
    return "o" if int(t * 7) % 2 else "smile"


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    img = scene(lt, agente=dict(mouth=talk(lt), arm=0.35), z=push(lt, dur, 2.1, 2.25), center=(AHEAD[0], AHEAD[1] - 60),
                board=False)
    card(img, 540, 1330, "BON D'ACHAT", "COMPAGNIE AÉRIENNE", [("Valeur", "50 €", 0.0, True)], 1.0, w=700, rot=-3)
    badge(img, 540, 640, "LA COMPAGNIE")
    tag(img, 540, 320, "« 4 H DE RETARD ?", 80, WHITE, INK, rot=-4, k=1.0)
    tag(img, 540, 470, "UN BON DE 50 €, C'EST TOUT »", 62, RED, WHITE, rot=3, k=(lt + 0.3) / 0.3)
    return shake(img, lt)


def s_faux(lt, dur):
    img = dim(scene(lt, agente=dict(mouth="grin"), board=False), 0.85)
    big_number(img, (540, 600), "FAUX", 260, RED, k=lt / 0.2)
    tag(img, 540, 900, "LA PREUVE OFFICIELLE · À LA FIN", 48, YEL, INK, rot=-3, k=(lt - 0.6) / 0.25)
    return shake(img, lt)


def s_tease(lt, dur):
    img = scene(lt, "choc", z=2.2, center=(KHEAD[0] + 40, KHEAD[1] - 40), board=False)
    shock_lines(img, 540, 900, 300, lt)
    big_number(img, (540, 330), counter(0, 500, lt, 0.7, "{:,} €"), 220, GREEN, "QUE LA COMPAGNIE VA LUI DEVOIR", k=1.0)
    return shake(flash(img, lt), lt)


def s_truc(lt, dur):
    img = scene(lt, "neutre", agente=dict(mouth="grin"), z=push(lt, dur, 1.1, 1.2), center=(540, 1000), board=False)
    tag(img, 540, 330, "UN SEUL PETIT TRUC", 70, YEL, INK, rot=-4, k=lt / 0.25)
    tn = T["non3"] - T["s_truc"]
    if lt > tn:
        for k in range(3):
            tag(img, 270 + k * 270, 560, "NON", 64, RED, WHITE, rot=(-8, 4, -3)[k], k=(lt - tn - 0.35 * k) / 0.2)
    return flash(img, lt)


def s_aeroport(lt, dur):
    img = scene(lt, "marche" if lt < 1.5 else "neutre", sarah=dict(mouth="grin"), z=push(lt, dur, 1.0, 1.12),
                center=(540, 900), kx=300 - 300 * (1 - ease(lt / 1.5)))
    tag(img, 540, 140, "JUILLET · LYON → LISBONNE", 54, WHITE, INK, rot=-3, k=lt / 0.25)
    return flash(img, lt)


def s_banc(lt, dur):
    img = scene(lt, "triste", sarah=dict(mouth="sad", brows="triste"), banc=True, z=1.05, center=(540, 1000), board=False)
    big_number(img, (540, 420), counter(0, 4, lt, 1.2, "{} H"), 200, RED, "DE VACANCES PERDUES", k=1.0)
    return flash(img, lt)


def s_ag1(lt, dur):
    img = scene(lt, agente=dict(mouth=talk(lt), arm=0.3), z=push(lt, dur, 1.9, 2.1), center=(AHEAD[0] - 60, AHEAD[1] + 60),
                board=False)
    badge(img, AX - 90, 560, "LA COMPAGNIE")
    bubble(img, 520, 330, ["PROBLÈME TECHNIQUE,", "C'EST PAS DE", "NOTRE FAUTE"], 58, (lt - 0.4) / 0.3, tail_x=680)
    return flash(img, lt)


def s_ag2(lt, dur):
    img = scene(lt, "neutre", agente=dict(mouth=talk(lt), arm=0.55), z=push(lt, dur, 1.1, 1.2), center=(540, 980),
                board=False)
    bubble(img, 640, 330, ["SIGNEZ ICI, ON VOUS", "OFFRE UN BON DE 50 €"], 52, lt / 0.3, tail_x=760)
    card(img, 640, 1150, "BON D'ACHAT · 50 €", "SIGNATURE DU PASSAGER", [("..............", "", 0.0, False)], 1.0,
         w=560, rot=4)
    return flash(img, lt)


def s_non(lt, dur):
    img = scene(lt, "parle", agente=dict(mouth="flat"), z=push(lt, dur, 1.15, 1.25), center=(540, 980), board=False)
    tag(img, 540, 300, "IL A DROIT À AUTRE CHOSE ?", 52, WHITE, INK, rot=-3, k=lt / 0.25)
    t1, t2 = T["non_a"] - T["s_non"], T["non_b"] - T["s_non"]
    if lt > t1:
        tag(img, 330, 520, "NON", 90, RED, WHITE, rot=-8, k=(lt - t1) / 0.2)
    if lt > t2:
        tag(img, 740, 560, "NON, C'EST LE RÈGLEMENT", 50, RED, WHITE, rot=5, k=(lt - t2) / 0.2)
        return shake(img, lt - t2)
    return flash(img, lt)


def s_sarah(lt, dur):
    img = scene(lt, "carte", sarah=dict(mouth="o" if int(lt * 7) % 2 else "flat"), z=push(lt, dur, 1.6, 1.75),
                center=(450, BASE - 650), board=False)
    bubble(img, 560, 330, ["PRENDS LE BON", "ET OUBLIE"], 64, lt / 0.3, tail_x=600)
    if lt > 1.8:
        tag(img, 540, 560, "LE STYLO DANS LA MAIN", 52, YEL, INK, rot=3, k=(lt - 1.8) / 0.25)
    return flash(img, lt)


def s_echo(lt, dur):
    img = dim(scene(lt, agente=dict(mouth="grin"), board=False, z=1.5, center=(AX - 100, AHEAD[1] + 200)), 0.7)
    tag(img, 540, 700, "« C'EST PAS DE NOTRE FAUTE »", 70, RED, WHITE, rot=-4, k=lt / 0.25)
    return img


def s_abonne(lt, dur):
    img = dim(scene(lt, "telephone", board=False), 0.75)
    phone_big(img, 540, 900, lt, "11:32", [("Où va ton argent", "Où va ton argent", "Vol en retard : tes droits", (40, 160, 90))])
    tag(img, 540, 260, "HEUREUSEMENT…", 64, YEL, INK, rot=-3, k=lt / 0.25)
    return img


def s_reglement(lt, dur):
    img = dim(scene(lt, "neutre", board=False), 0.9)
    carte_sombre(img, "RÈGLEMENT EUROPÉEN 261", [("Retard de 3 h ou plus", 0.6, False), ("à l'arrivée", 1.0, False),
                                                 ("= indemnisation par passager", 2.0, True)], lt, y0=520,
                 sous="DROITS DES PASSAGERS AÉRIENS")
    return img


def s_seuil(lt, dur):
    img = dim(scene(lt, "neutre", board=False), 0.9)
    big_number(img, (540, 560), "4 H ?", 220, (240, 80, 80), "CE QUE CERTAINS PAYS VOULAIENT", k=lt / 0.25,
               strike=ease((lt - 2.2) / 0.3))
    if lt > 2.6:
        big_number(img, (540, 1000), "3 H", 240, GREEN, "ÇA RESTE 3 HEURES", k=(lt - 2.6) / 0.25, rot=-3)
    return img


def s_pieges(lt, dur):
    img = dim(scene(lt, "neutre", board=False), 0.92)
    t1, t2, t3 = (T[k] - T["s_pieges"] for k in ("p1", "p2", "p3"))
    rows = [("1 · LA PANNE = SON PROBLÈME", t1, lt < t2), ("2 · LA DISTANCE", t2, t2 <= lt < t3),
            ("3 · LE BON, SEULEMENT SI TU SIGNES", t3, lt >= t3)]
    carte_sombre(img, "LES 3 PIÈGES", rows, lt, y0=300)
    if t2 <= lt < t3:
        carte_sombre(img, "MONTANT PAR PASSAGER", [("MOINS DE 1 500 KM · 250 €", t2 + 0.8, True),
                                                    ("JUSQU'À 3 500 KM · 400 €", t2 + 1.6, False),
                                                    ("AU-DELÀ · 600 €", t2 + 2.2, False)], lt, y0=1000)
    elif lt < t2 and lt > t1 + 1.0:
        tag(img, 540, 1050, "SAUF TEMPÊTE, GRÈVE DU CONTRÔLE AÉRIEN…", 40, WHITE, INK, rot=-2, k=(lt - t1 - 1.0) / 0.25)
    return img


def s_calcul(lt, dur):
    img = dim(scene(lt, "neutre", sarah=dict(mouth="grin"), board=False), 0.9)
    tag(img, 540, 260, "FAIS LE CALCUL AVEC KÉVIN", 56, YEL, INK, rot=-3, k=lt / 0.25)
    carte_sombre(img, "LYON → LISBONNE", [("1 400 KM · MOINS DE 1 500", 0.6, False),
                                          ("250 € × 2 PASSAGERS", T["c250"] - T["s_calcul"], False),
                                          ("= 500 €", T["c500"] - T["s_calcul"], True)], lt, y0=520)
    return img


def s_partage(lt, dur):
    img = dim(scene(lt, "telephone", board=False), 0.85)
    d = ImageDraw.Draw(img)
    cols = [(214, 120, 40), (230, 120, 160), (60, 120, 220), (90, 180, 100)]
    noms = ["KÉVIN", "SARAH", "YANIS", "LÉA"]
    tp = T["envoie"] - T["s_partage"]
    if lt < tp:
        card(img, 540, 900, "TES BILLETS DE CET ÉTÉ", "REGARDE BIEN", [("Retard à l'arrivée ?", "3 h ou plus", 0.3, True)],
             lt, w=800, rot=-2)
        return img
    for k in range(4):                                         # visio à 4 cases
        x0, y0 = 90 + (k % 2) * 460, 500 + (k // 2) * 520
        d.rounded_rectangle([x0, y0, x0 + 440, y0 + 500], radius=24, fill=(40, 44, 60))
        lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        character(ImageDraw.Draw(lay), (x0 + 220), y0 + 640, sc=0.55, shirt=cols[k], pants=(40, 40, 60),
                  hair=(40, 30, 25), long_hair=k % 2 == 1, mouth="o" if k else "grin", arms_up=k > 0 and lt - tp > 0.5 + k * 0.3)
        lay = lay.resize((W, H), Image.LANCZOS).crop((x0, y0, x0 + 440, y0 + 500))
        img.paste(lay, (x0, y0), lay)
        d.text((x0 + 24, y0 + 470), noms[k], font=FA(34), fill=WHITE, anchor="lm")
    tag(img, 540, 330, "ON EN A TOUS UN", 70, YEL, INK, rot=-3, k=(lt - T["tous"] + T["s_partage"]) / 0.25)
    return img


def s_lettre(lt, dur):
    img = dim(scene(lt, "neutre", board=False), 0.85)
    card(img, 540, 840, "RÉCLAMATION", "À LA COMPAGNIE", [
        ("1 · Vol retardé de 4 h", "", 0.6, False), ("2 · Règlement européen 261", "", 1.6, False),
        ("3 · 500 € en virement", "", 2.6, True)], lt, stamp="ENVOYÉ", stamp_t=3.6)
    return img


def s_paie(lt, dur):
    img = scene(lt, "victoire", sarah=dict(mouth="grin", arm=0.9), z=push(lt, dur, 1.05, 1.15), center=(540, 1000),
                board=False)
    phone_big(img, 540, 760, lt, "10:05", [("Banque", "Virement reçu", "COMPAGNIE · +500 €", (60, 110, 230))], k=None)
    tag(img, 540, 260, "2 SEMAINES PLUS TARD", 56, WHITE, INK, rot=-3, k=lt / 0.25)
    return flash(img, lt)


def s_chute(lt, dur):
    img = scene(lt, "neutre", agente=dict(mouth="sad", brows="triste"), z=push(lt, dur, 1.5, 1.7),
                center=(KHEAD[0] + 160, KHEAD[1] + 260), board=False)
    card(img, 600, 1180, "BON D'ACHAT · 50 €", "SIGNATURE DU PASSAGER", [("(rien)", "", 0.0, False)], 1.0, w=560, rot=4,
         stamp="PAS SIGNÉ", stamp_t=0.6)
    tag(img, 540, 300, "LE PETIT TRUC DE KÉVIN", 60, YEL, INK, rot=-3, k=lt / 0.25)
    tag(img, 540, 1780, "CAS TYPE · RÈGLEMENT (CE) 261/2004 · CECI N'EST PAS UN CONSEIL JURIDIQUE", 20, (40, 40, 50),
        WHITE, rot=0, k=(lt - 0.5) / 0.3)
    return img


def main():
    v = CartoonVideo("droits_vol_retard", "scripts/modele/9_vol_retard.txt", "", "", corner="")
    v.length = (84.0, 88.0, 92.0)
    v.hook_head_start = 0.0
    v.voice("output/_work_droits_vol/voice_raw.mp3")
    sc = [("Ton vol a quatre heures", s_hook), ("Faux, et la preuve", s_faux), ("Kévin le sait pas encore", s_tease),
          ("Parce qu'au comptoir", s_truc), ("Juillet, aéroport", s_aeroport), ("Ils atterrissent", s_banc),
          ("Au comptoir, l'agente", s_ag1), ("Et en poussant", s_ag2), ("Kévin demande", s_non),
          ("Sarah lui dit", s_sarah)]
    for phrase, fn in sc:
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("C'est pas de notre faute", after=T["s_sarah"])
    sc += [("C'est pas de notre faute", s_echo)]
    sc2 = [("Et pourtant, heureusement", s_abonne), ("Le règlement européen", s_reglement),
           ("Cette année, certains", s_seuil), ("Retiens bien les trois", s_pieges), ("Fais le calcul", s_calcul),
           ("Regarde bien tes billets", s_partage), ("Kévin écrit à la compagnie", s_lettre),
           ("Deux semaines plus tard", s_paie), ("Et le petit truc", s_chute)]
    for phrase, fn in sc2:
        T[fn.__name__] = v.at(phrase)
    T["non3"] = v.at("L'agente va lui dire non")
    T["non_a"] = v.at("Non. Il insiste")
    T["non_b"] = v.at("Non, c'est le règlement")
    T["p1"], T["p2"], T["p3"] = v.at("Le premier, la panne"), v.at("Le deuxième, la distance"), v.at("Le troisième, le bon")
    T["c250"], T["c500"] = v.at("Deux cent cinquante euros chacun"), v.at("cinq cents euros pour le couple")
    T["envoie"], T["tous"] = v.at("Et c'est là que Kévin envoie"), v.at("On en a tous un")
    for phrase, fn in sc + sc2:
        after = T["s_sarah"] if fn is s_echo else 0.0
        v.scene(phrase, avec_compteur(fn), after=after)
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["s_faux"], "impact", 0.9)
    v.sfx(T["s_tease"], "ticks", 0.6)
    for k in range(3):
        v.sfx(T["non3"] + 0.35 * k + 0.1, "tampon", 0.7)
    v.sfx(T["s_aeroport"], "whoosh", 0.5)
    v.sfx(T["s_banc"], "rate", 0.8)
    v.sfx(T["non_a"], "tampon", 0.8)
    v.sfx(T["non_b"], "tampon", 0.9)
    v.sfx(T["s_echo"], "impact", 0.8)
    v.sfx(T["s_abonne"], "notif", 0.9)
    for k in ("p1", "p2", "p3"):
        v.sfx(T[k], "pop", 0.8)
    v.sfx(T["c250"], "ticks", 0.6)
    v.sfx(T["c500"], "succes", 0.9)
    v.sfx(T["envoie"], "notif", 0.8)
    v.sfx(T["s_lettre"] + 3.6, "tampon", 1.0)
    v.sfx(T["s_paie"], "notif", 1.0)
    v.sfx(T["s_chute"] + 0.6, "tampon", 0.9)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
