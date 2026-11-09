"""Tes droits : la CAF réclame un trop perçu dont la moitié est prescrite. Kévin + bruitages."""
import argparse

from PIL import ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, notif, phone_big, push, room, shake, shock_lines, shot, tag)
from prime_ct import salon_bg

BASE = 1560
CAF = (30, 110, 200)
CONSEILLERE = dict(shirt=(60, 90, 160), pants=(30, 30, 40), hair=(50, 30, 20), long_hair=True)
CX = 760
CHEAD = (CX, BASE - 740)

_bg = {}


def guichet_bg():
    if "g" in _bg:
        return _bg["g"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60 * s, 420 * s, 420 * s, 640 * s], radius=16 * s, fill=CAF)
    d.text((240 * s, 530 * s), "CAF", fill=WHITE, anchor="mm",
           font=__import__("cartoon").FA(110 * s))
    _bg["g"] = im
    return im


def headset(d, x, base):
    s = SS
    y = base - 700
    d.arc([(x - 112) * s, (y - 120) * s, (x + 112) * s, (y + 60) * s], 190, 350, fill=INK, width=12 * s)
    d.rounded_rectangle([(x - 124) * s, (y - 30) * s, (x - 96) * s, (y + 34) * s], radius=8 * s, fill=INK)
    d.line([(x - 110) * s, (y + 30) * s, (x - 40) * s, (y + 62) * s], fill=INK, width=7 * s)
    d.ellipse([(x - 48) * s, (y + 52) * s, (x - 28) * s, (y + 72) * s], fill=INK)


def guichet(t, kpose=None, conseillere=None, z=1.0, center=None):
    big = guichet_bg().copy()
    d = ImageDraw.Draw(big)
    if conseillere is not None:
        bob, blink = idle(t, 0.5)
        character(d, CX, BASE - 40 + bob, **{**CONSEILLERE, "blink": blink, **conseillere})
        headset(d, CX, BASE - 40 + bob)
    s = SS
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1210 * s], fill=(150, 104, 74))
    d.rounded_rectangle([600 * s, 1120 * s, 860 * s, 1170 * s], radius=8 * s, fill=(40, 40, 50))   # clavier
    if kpose:
        kevin(d, 280, BASE, kpose, t)
    return shot(big, z, center=center)


def salon(t, kpose="telephone", z=1.0, center=None):
    big = salon_bg().copy()
    d = ImageDraw.Draw(big)
    kevin(d, 540, BASE, kpose, t)
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "smile"


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    if lt < 1.0:      # gros plan choc + compteur
        img = salon(lt, "choc", z=2.3, center=(540, BASE - 760))
        shock_lines(img, 540, 900, 300, lt)
        big_number(img, (540, 300), counter(0, 3000, lt, 0.6), 220, RED, "RÉCLAMÉS PAR LA CAF", k=1.0)
        return shake(flash(img, lt), lt)
    if lt < 2.1:      # l'écran du téléphone
        img = dim(salon(lt, "telephone"), 0.8)
        phone_big(img, 540, 860, lt - 1.0, "08:12", [("CAF", "Trop perçu", "3 000 € à rembourser", CAF)])
        return flash(img, lt - 1.0)
    img = salon(lt, "triste", z=push(lt - 2.1, dur - 2.1, 1.3, 1.5), center=(540, BASE - 640))
    big_number(img, (540, 300), "3 000 €", 200, RED, "À REMBOURSER", k=1.0)
    return flash(img, lt - 2.1)


def s_moitie(lt, dur):
    img = dim(salon(lt, "triste"), 0.75)
    big_number(img, (540, 360), "3 000 €", 210, RED, k=1.0)
    k = ease((lt - 0.8) / 0.5)
    if k > 0:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([140, 640, 940, 760], radius=20, fill=(60, 60, 70))
        d.rounded_rectangle([140, 640, 140 + 800 * 0.5, 760], radius=20, fill=RED)
        d.line([140 + 400, 620, 140 + 400 + 400 * k, 780], fill=YEL, width=14)
        d.line([140 + 400, 780, 140 + 400 + 400 * k, 620], fill=YEL, width=14)
    tag(img, 540, 920, "LA MOITIÉ N'EXISTE PLUS", 60, GREEN, INK, rot=-4, k=(lt - 1.3) / 0.3)
    return img


def s_appli(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    rows = [("CAF", "APL de novembre", "40 € au lieu de 300 €", CAF)]
    if lt > 2.6:
        rows.append(("CAF", "Message", "Trop perçu, à rembourser", RED))
    phone_big(img, 540, 860, lt, "08:12", rows)
    return img


def s_attente(lt, dur):
    img = salon(lt, "telephone", z=push(lt, dur, 1.5, 1.7), center=(540, BASE - 620))
    big_number(img, (540, 300), "40 MIN", 190, WHITE, "DE MUSIQUE D'ATTENTE", k=lt / 0.3)
    return flash(img, lt)


def s_conseillere(lt, dur):
    img = guichet(lt, conseillere=dict(mouth=talk(lt), arm=0.3), z=push(lt, dur, 1.9, 2.1),
                  center=(CHEAD[0] - 60, CHEAD[1] + 60))
    bubble(img, 520, 380, ["C'EST LA RÈGLE,", "VOUS DEVEZ", "REMBOURSER"], 60, (lt - 0.6) / 0.3, tail_x=680)
    return flash(img, lt)


def s_echeance(lt, dur):
    img = guichet(lt, "triste", conseillere=dict(mouth=talk(lt)), z=push(lt, dur, 1.1, 1.2), center=(540, 980))
    bubble(img, 660, 380, ["ON PEUT FAIRE", "3 × 1 000 €"], 64, lt / 0.3, tail_x=760)
    return flash(img, lt)


def s_compte(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    phone_big(img, 540, 860, lt, "12:40", [("Banque", "Solde", "412,00 €", (60, 110, 230))])
    return img


def s_mille(lt, dur):
    img = dim(salon(lt, "triste"), 0.8)
    big_number(img, (540, 520), "1 000 € / MOIS", 170, RED, k=lt / 0.25)
    tag(img, 540, 820, "AVEC 412 € SUR LE COMPTE", 52, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return shake(img, lt)


def s_raccroche(lt, dur):
    img = salon(lt, "neutre" if lt < 1.4 else "telephone", z=push(lt, dur, 1.2, 1.4), center=(540, 1000))
    tag(img, 540, 300, "IL DIT PAS OUI", 66, YEL, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 470, "IL RELIT TOUT", 56, WHITE, INK, rot=3, k=(lt - 1.6) / 0.3)
    return flash(img, lt)


def s_dates(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    card(img, 540, 820, "CAF · TROP PERÇU", "DÉTAIL DES SOMMES", [
        ("Aides de 2023 à 2024", "1 500 €", 0.6, lt > 2.0),
        ("Aides de 2025 à 2026", "1 500 €", 1.0, False)], lt, rot=-2)
    tag(img, 540, 330, "LE DÉTAIL : LES DATES", 60, YEL, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 1180, "PLUS DE 2 ANS", 60, RED, WHITE, rot=3, k=(lt - 2.6) / 0.3)
    return img


def s_prescrit(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    big_number(img, (540, 330), "2 ANS", 230, YEL, "POUR RÉCLAMER, SAUF FRAUDE", k=lt / 0.3)
    if lt > 4.2:
        tag(img, 540, 820, "AU-DELÀ : PRESCRIT", 90, RED, WHITE, rot=-5, k=(lt - 4.2) / 0.2)
        return shake(img, lt - 4.2)
    if lt > 2.2:
        tag(img, 540, 720, "PAS UN JOUR DE PLUS", 60, WHITE, INK, rot=3, k=(lt - 2.2) / 0.3)
    return img


def s_calcul(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    tag(img, 540, 240, "FAIS LE CALCUL", 60, YEL, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 470), "3 000 €", 140, WHITE, "RÉCLAMÉS", k=(lt - 0.5) / 0.3)
    big_number(img, (540, 760), "− 1 500 €", 140, RED, "PRESCRITS", k=(lt - 1.6) / 0.3)
    if lt > 3.2:
        big_number(img, (540, 1080), counter(3000, 1500, lt - 3.2, 0.6), 170, GREEN, "LA DETTE COUPÉE EN 2",
                   k=1.0, rot=-3)
    return img


def s_lettre(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    card(img, 540, 800, "LETTRE RECOMMANDÉE AR", "COMMISSION DE RECOURS AMIABLE", [
        ("Dans les 2 mois", "", 0.6, False),
        ("Sommes de plus de 2 ans", "prescrites", 1.2, True),
        ("Pour le reste", "remise de dette", 2.4, True),
        ("Motif", "bonne foi", 3.4, False)], lt, stamp="ENVOYÉ", stamp_t=4.4)
    return img


def s_demi(lt, dur):
    img = guichet(lt, conseillere=dict(mouth="smile"), z=push(lt, dur, 1.9, 2.1), center=(CHEAD[0], CHEAD[1] - 40))
    tag(img, 540, 330, "LA CAF A PAS TOUT FAUX", 60, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 510, "L'ARGENT A ÉTÉ VERSÉ EN TROP", 48, RED, WHITE, rot=3, k=(lt - 1.2) / 0.3)
    return flash(img, lt)


def s_echeancier(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    if lt < 3.0:
        tag(img, 540, 360, "+ UN ÉCHÉANCIER", 70, YEL, INK, rot=-4, k=lt / 0.3)
        tag(img, 540, 560, "CALÉ SUR SES REVENUS", 56, WHITE, INK, rot=3, k=(lt - 0.8) / 0.3)
        return img
    phone_big(img, 540, 860, lt - 3.0, "18:03", [("CAF", "Réponse à votre recours", "Nouveau courrier", CAF)])
    tag(img, 540, 240, "QUELQUES SEMAINES PLUS TARD", 50, WHITE, INK, rot=-3, k=(lt - 3.0) / 0.3)
    return img


def s_annule(lt, dur):
    img = salon(lt, "victoire", z=push(lt, dur, 1.1, 1.2), center=(540, 1000))
    big_number(img, (540, 300), "1 500 €", 210, GREEN, "ANNULÉS", k=lt / 0.25, strike=ease((lt - 0.4) / 0.3))
    tag(img, 540, 620, "LE RESTE, ÉTALÉ SUR DES MOIS", 52, WHITE, INK, rot=-3, k=(lt - 1.4) / 0.3)
    return flash(img, lt)


def s_chute(lt, dur):
    img = salon(lt, "victoire", z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    tag(img, 540, 300, "PAYER SANS LIRE = PERDRE", 60, RED, WHITE, rot=-4, k=lt / 0.3)
    big_number(img, (540, 560), "IL A LU LES DATES", 120, YEL, k=(lt - 1.0) / 0.3)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · MONTANTS INDICATIFS · CECI N'EST PAS UN CONSEIL", 24, (40, 40, 50), WHITE,
            rot=0, k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_trop_percu", "scripts/modele/4_caf_trop_percu.txt", "", "", corner="CAF")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    sc = [("Kévin ouvre son appli", s_hook), ("Il le sait pas encore", s_moitie), ("Au lieu de ses", s_appli),
          ("Kévin appelle", s_attente), ("La conseillère soupire", s_conseillere),
          ("Et en tapant sur son clavier", s_echeance), ("Kévin regarde son compte", s_compte),
          ("Mille euros par mois", s_mille), ("Et pourtant, Kévin dit pas oui", s_raccroche),
          ("Le détail, c'est les dates", s_dates), ("Ce que peu de gens savent", s_prescrit),
          ("Fais le calcul", s_calcul), ("Mais alors, le reste", s_lettre), ("Honnêtement, la CAF", s_demi),
          ("Sauf que Kévin demande aussi", s_echeancier), ("Mille cinq cents euros annulés", s_annule),
          ("Ceux qui paient sans lire", s_chute)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
    T = {fn.__name__: v.at(phrase) for phrase, fn in sc}
    # une douzaine de bruitages, sur les moments forts seulement
    v.sfx(0.0, "impact", 1.0)
    v.sfx(1.0, "notif", 0.9)
    v.sfx(T["s_moitie"] + 0.8, "whoosh", 0.6)
    v.sfx(T["s_appli"] + 2.6, "notif", 0.9)
    v.sfx(T["s_attente"], "attente", 0.8)
    v.sfx(T["s_mille"], "rate", 0.9)
    v.sfx(T["s_raccroche"], "whoosh", 0.6)
    v.sfx(T["s_prescrit"] + 4.2, "impact", 1.0)
    v.sfx(T["s_calcul"] + 3.2, "ticks", 0.7)
    v.sfx(T["s_lettre"] + 4.4, "tampon", 1.0)
    v.sfx(T["s_echeancier"] + 3.0, "notif", 0.9)
    v.sfx(T["s_annule"], "succes", 1.0)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
