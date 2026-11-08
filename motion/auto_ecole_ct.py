"""Tes droits : l'auto-école qui fait payer le dossier (style cartoon plat, hook en gros plans)."""
import argparse

from PIL import Image, ImageDraw

from cartoon import (GREEN, GREY, INK, RED, SS, WHITE, YEL, CartoonVideo, FA, back, big_number, bubble, card,
                     character, counter, dim, ease, flash, notif, phone_big, room, shock_lines, shot, tag)
from engine import H, W

KEVIN = dict(shirt=(214, 120, 40), pants=(40, 60, 120), hair=(70, 44, 30))
GERANTE = dict(shirt=(140, 40, 70), pants=(30, 30, 40), hair=(90, 50, 30), long_hair=True, glasses=True)
MONITEUR = dict(shirt=(70, 120, 200), pants=(40, 40, 50), hair=(30, 30, 30))
PROCHE = dict(shirt=(60, 160, 110), pants=(40, 40, 60), hair=(30, 20, 15))
BASE = 1560

_bg = {}


def voiture_bg():
    if "v" in _bg:
        return _bg["v"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), (28, 30, 40))
    d = ImageDraw.Draw(im)
    # pare-brise : rue de nuit
    d.polygon([(90 * s, 160 * s), (990 * s, 160 * s), (1060 * s, 880 * s), (20 * s, 880 * s)], fill=(40, 52, 100))
    d.polygon([(400 * s, 880 * s), (680 * s, 880 * s), (560 * s, 420 * s), (520 * s, 420 * s)], fill=(60, 62, 72))
    for j in range(4):
        y = 460 + j * 110
        d.rectangle([536 * s, y * s, 544 * s, (y + 50) * s], fill=(230, 230, 230))
    for x, y in [(200, 360), (880, 380), (320, 520), (760, 540)]:
        d.line([x * s, y * s, x * s, (y + 260) * s], fill=(20, 20, 30), width=8 * s)
        d.ellipse([(x - 22) * s, (y - 22) * s, (x + 22) * s, (y + 22) * s], fill=(255, 220, 140))
    d.rectangle([0, 0, W * s, 170 * s], fill=(22, 24, 32))
    d.rounded_rectangle([440 * s, 175 * s, 640 * s, 240 * s], radius=12 * s, fill=(20, 20, 26))
    # sièges
    for x in (330, 760):
        d.rounded_rectangle([(x - 170) * s, 820 * s, (x + 170) * s, 1500 * s], radius=80 * s, fill=(50, 52, 62))
    _bg["v"] = im
    return im


def voiture_fg(d):
    s = SS
    d.rectangle([0, 1250 * s, W * s, H * s], fill=(36, 38, 48))
    d.rectangle([0, 1250 * s, W * s, 1280 * s], fill=(56, 58, 70))
    d.ellipse([170 * s, 1050 * s, 490 * s, 1370 * s], outline=(15, 15, 20), width=34 * s)
    d.line([330 * s, 1210 * s, 330 * s, 1370 * s], fill=(15, 15, 20), width=30 * s)
    tag_y = 1330
    d.rounded_rectangle([700 * s, tag_y * s, 900 * s, (tag_y + 60) * s], radius=10 * s, fill=(60, 62, 76))


def bureau_fg(d):
    s = SS
    d.rectangle([520 * s, 1180 * s, W * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([520 * s, 1180 * s, W * s, 1210 * s], fill=(150, 104, 74))
    # pile de dossiers
    for j in range(4):
        d.rectangle([600 * s, (1150 - j * 26) * s, 760 * s, (1176 - j * 26) * s], fill=[(240, 200, 90), (200, 220, 250)][j % 2])


def car(kevin=None, moniteur=None, proche=None, z=1.0, center=None):
    big = voiture_bg().copy()
    d = ImageDraw.Draw(big)
    if kevin is not None:
        character(d, 330, BASE, **{**KEVIN, **kevin})
    if moniteur is not None:
        character(d, 760, BASE, **{**MONITEUR, **moniteur})
    if proche is not None:
        character(d, 760, BASE, **{**PROCHE, **proche})
    voiture_fg(d)
    return shot(big, z, center=center)


def office(kevin=None, gerante=None, z=1.0, center=None):
    big = room("vide").copy()
    d = ImageDraw.Draw(big)
    if gerante is not None:
        character(d, 800, BASE - 40, **{**GERANTE, **gerante})
    bureau_fg(d)
    if kevin is not None:
        character(d, 280, BASE, **{**KEVIN, **kevin})
    return shot(big, z, center=center)


KHEAD = (280, BASE - 700)     # tête de Kevin dans le bureau
GHEAD = (800, BASE - 740)     # tête de la gérante


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    """Gros plan choc, plan large, gros plan gérante, plan moyen : un plan par seconde environ."""
    if lt < 1.0:      # gros plan sur Kevin, choqué, bras levés
        img = office(kevin=dict(mouth="o", arms_up=True, brows="triste"), z=2.3, center=(KHEAD[0], KHEAD[1] - 60))
        shock_lines(img, 540, 900, 300, lt)
        big_number(img, (540, 300), counter(0, 150, lt, 0.6), 230, YEL, "POUR SON PROPRE DOSSIER", k=1.0)
        return flash(img, lt)
    if lt < 2.0:      # plan large : la gérante tend la main derrière son bureau
        img = office(kevin=dict(mouth="o"), gerante=dict(mouth="grin", arm=0.55), z=1.05, center=(540, 1000))
        big_number(img, (540, 300), "150 €", 200, YEL, "LE TRANSFERT DU DOSSIER", k=1.0)
        return flash(img, lt - 1.0)
    if lt < 2.9:      # gros plan sur la gérante qui sourit
        img = office(gerante=dict(mouth="grin", arm=0.55), z=2.2, center=(GHEAD[0], GHEAD[1] - 40))
        tag(img, 540, 330, "PAYABLE AUJOURD'HUI", 64, RED, WHITE, rot=-4, k=(lt - 2.0) / 0.25)
        return flash(img, lt - 2.0)
    img = office(kevin=dict(mouth="flat", brows="triste"), gerante=dict(mouth="grin"), z=1.25, center=(540, 960))
    big_number(img, (540, 300), "150 €", 200, YEL, "LE TRANSFERT DU DOSSIER", k=1.0, strike=0.0)
    return flash(img, lt - 2.9)


def s_douze(lt, dur):
    img = dim(office(kevin=dict(mouth="flat"), gerante=dict(mouth="grin")), 0.8)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kevin", 0.2, False), ("N° NEPH", "???? ???? ????", 0.4, False)], lt, rot=-2)
    tag(img, 540, 330, "12 CHIFFRES", 70, YEL, INK, rot=-4, k=(lt - 0.6) / 0.3)
    return img


def s_paye(lt, dur):
    img = car(kevin=dict(mouth="flat"), moniteur=dict(mouth="flat"), z=1.05)
    big_number(img, (540, 330), counter(0, 2500, lt, 0.8), 200, YEL, "DÉJÀ PAYÉS", k=1.0)
    tag(img, 540, 620, "30 H × 45 €", 60, WHITE, INK, rot=-4, k=(lt - 1.6) / 0.3)
    return flash(img, lt)


def s_pas_pret(lt, dur):
    if lt < 1.4:
        img = car(kevin=dict(mouth="flat"), moniteur=dict(mouth="smile"), z=2.0, center=(760, 860))
        bubble(img, 540, 420, ["T'ES PAS", "ENCORE PRÊT"], 70, lt / 0.3, tail_x=600)
        return flash(img, lt)
    img = car(kevin=dict(mouth="sad", brows="triste"), moniteur=dict(mouth="smile"), z=1.05)
    big_number(img, (540, 330), "30E FOIS", 170, WHITE, "LA MÊME PHRASE", k=(lt - 1.4) / 0.3)
    tag(img, 540, 640, "EXAMEN : DANS 8 MOIS", 56, RED, WHITE, rot=-3, k=(lt - 2.6) / 0.3)
    return flash(img, lt - 1.4)


def s_partir(lt, dur):
    img = office(kevin=dict(mouth="flat"), gerante=dict(mouth="grin", arm=0.55), z=1.1, center=(540, 980))
    bubble(img, 640, 400, ["LE TRANSFERT, C'EST", "150 €. AUJOURD'HUI."], 54, (lt - 1.2) / 0.3, tail_x=780)
    return flash(img, lt)


def s_zero(lt, dur):
    img = office(gerante=dict(mouth="grin", clipboard=True), z=2.0, center=(GHEAD[0], GHEAD[1] + 20))
    bubble(img, 540, 380, ["SINON TU REPARS", "DE ZÉRO"], 66, lt / 0.3, tail_x=700)
    if lt > 1.6:
        tag(img, 540, 640, "COMME TOUT LE MONDE", 50, WHITE, INK, rot=3, k=(lt - 1.6) / 0.3)
    return flash(img, lt)


def s_carte(lt, dur):
    img = office(kevin=dict(mouth="flat", brows="triste", arm=0.45, hold="carte"), z=2.0,
                 center=(KHEAD[0] + 150, KHEAD[1] + 120))
    tag(img, 540, 330, "IL HÉSITE", 64, YEL, INK, rot=-4, k=lt / 0.3)
    if lt > 1.2:
        tag(img, 540, 520, "2 ÉLÈVES ATTENDENT DERRIÈRE", 46, RED, WHITE, rot=3, k=(lt - 1.2) / 0.3)
    return flash(img, lt)


def s_echo(lt, dur):
    img = dim(office(kevin=dict(mouth="sad", brows="triste"), z=1.4, center=(KHEAD[0] + 100, KHEAD[1] + 100)), 0.65)
    tag(img, 540, 700, "« REPARTIR DE ZÉRO »", 86, YEL, INK, rot=-4, k=lt / 0.3)
    return img


def s_neph(lt, dur):
    img = dim(office(kevin=dict(mouth="o"), gerante=dict(mouth="flat")), 0.8)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kevin", 0.0, False), ("N° NEPH", "1204 5582 9917", 0.6, True)], lt + 0.5, rot=-2)
    big_number(img, (540, 280), "À LUI", 170, GREEN, "PAS À L'AUTO-ÉCOLE", k=(lt - 3.2) / 0.3, rot=-3)
    return img


def s_code(lt, dur):
    img = dim(office(gerante=dict(mouth="flat")), 0.8)
    if lt < 4.8:
        card(img, 540, 800, "CODE DE LA ROUTE", "RESTITUTION DU DOSSIER", [
            ("Rendre le dossier", "gratuit", 1.6, True), ("Le facturer", "interdit", 3.0, True)], lt, rot=2)
        big_number(img, (540, 300), "LA LOI", 140, YEL, k=lt / 0.3)
    else:
        big_number(img, (540, 640), counter(0, 15000, lt - 4.8, 0.7), 210, RED, "D'AMENDE MAXIMUM", k=1.0)
    return img


def s_silence(lt, dur):
    img = office(gerante=dict(mouth="flat", brows="triste"), z=2.2, center=(GHEAD[0], GHEAD[1] - 40))
    tag(img, 540, 380, "…", 120, WHITE, INK, rot=0, k=lt / 0.3)
    return flash(img, lt)


def s_plateforme(lt, dur):
    img = dim(office(kevin=dict(mouth="smile", phone=True)), 0.75)
    if lt < 2.2:
        big_number(img, (540, 640), "SANS AUTO-ÉCOLE ?", 130, WHITE, k=lt / 0.3)
        return img
    phone_big(img, 540, 860, lt - 2.2, "21:04", [
        ("État", "Candidat libre", "Inscription validée", (60, 110, 230)),
        ("État", "Examen réservé", "Date choisie par Kevin", GREEN)])
    if lt > 5.0:
        tag(img, 540, 260, "EXAMEN PRATIQUE : 0 €", 64, YEL, INK, rot=-4, k=(lt - 5.0) / 0.3)
    return img


def s_location(lt, dur):
    img = car(kevin=dict(mouth="smile"), proche=dict(mouth="grin"), z=1.05)
    tag(img, 540, 300, "VOITURE À DOUBLE COMMANDE", 52, YEL, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 450, "EN LOCATION", 46, WHITE, INK, rot=3, k=(lt - 0.8) / 0.3)
    tag(img, 760, 640, "+ UN PROCHE", 52, GREEN, INK, rot=-3, k=(lt - 2.2) / 0.3)
    return flash(img, lt)


def s_demi(lt, dur):
    img = car(kevin=dict(mouth="flat"), moniteur=dict(mouth="smile", arm=0.4), z=2.0, center=(760, 860))
    tag(img, 540, 380, "UN MONITEUR, ÇA RASSURE", 56, WHITE, INK, rot=-3, k=lt / 0.3)
    return flash(img, lt)


def s_permis(lt, dur):
    big = room("vide").copy()
    d = ImageDraw.Draw(big)
    character(d, 540, BASE, **{**KEVIN, "mouth": "grin", "arm": 0.95, "hold": "permis"})
    img = shot(big, 1.2, center=(540, 1000))
    shock_lines(img, 540, 760, 260, lt)
    big_number(img, (540, 300), "3 SEMAINES", 150, WHITE, "PLUS TARD", k=lt / 0.3)
    tag(img, 540, 1300, "PERMIS EN POCHE", 60, GREEN, INK, rot=-4, k=(lt - 0.8) / 0.3)
    return flash(img, lt)


def s_chute(lt, dur):
    img = dim(office(kevin=dict(mouth="grin"), gerante=dict(mouth="flat")), 0.75)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kevin", 0.0, False), ("N° NEPH", "1204 5582 9917", 0.0, True)], lt + 1.0, rot=-2)
    big_number(img, (540, 280), "À LUI", 170, GREEN, "DEPUIS LE DÉBUT", k=(lt - 0.6) / 0.3, rot=-3)
    if lt > 1.0:
        tag(img, 540, 1760, "CAS TYPE · CECI N'EST PAS UN CONSEIL JURIDIQUE", 26, (40, 40, 50), WHITE, rot=0,
            k=(lt - 1.0) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_auto_ecole", "scripts/modele/1_auto_ecole.txt", "", "", corner="PERMIS")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    v.scene("Cent cinquante euros pour récupérer", s_hook)
    v.scene("Il le sait pas encore", s_douze)
    v.scene("Kevin a déjà payé", s_paye)
    v.scene("Et à chaque leçon", s_pas_pret)
    v.scene("Alors Kevin veut partir", s_partir)
    v.scene("Et en rangeant le classeur", s_zero)
    v.scene("Kevin sort sa carte", s_carte)
    v.scene("Repartir de zéro", s_echo)
    v.scene("Et pourtant, en haut", s_neph)
    v.scene("Ce que peu de gens savent", s_code)
    v.scene("La gérante dit plus rien", s_silence)
    v.scene("Mais alors, sans auto-école", s_plateforme)
    v.scene("Sur le papier", s_location)
    v.scene("Honnêtement, l'auto-école", s_demi)
    v.scene("Trois semaines plus tard", s_permis)
    v.scene("Le dossier était à lui", s_chute)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
