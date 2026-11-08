"""Tes droits : l'auto-école qui fait payer le dossier. Héros récurrent Kévin, gestes et caméra fixes."""
import argparse

from PIL import Image, ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, room, shake, shock_lines, shot, tag)
from engine import H, W

GERANTE = dict(shirt=(140, 40, 70), pants=(30, 30, 40), hair=(90, 50, 30), long_hair=True, glasses=True)
MONITEUR = dict(shirt=(70, 120, 200), pants=(40, 40, 50), hair=(30, 30, 30))
PROCHE = dict(shirt=(200, 110, 40), pants=(40, 40, 60), hair=(30, 20, 15))
BASE = 1560

_bg = {}


def voiture_bg():
    if "v" in _bg:
        return _bg["v"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), (28, 30, 40))
    d = ImageDraw.Draw(im)
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
    d.rounded_rectangle([700 * s, 1330 * s, 900 * s, 1390 * s], radius=10 * s, fill=(60, 62, 76))


def bureau_fg(d):
    s = SS
    d.rectangle([520 * s, 1180 * s, W * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([520 * s, 1180 * s, W * s, 1210 * s], fill=(150, 104, 74))
    for j in range(4):
        d.rectangle([600 * s, (1150 - j * 26) * s, 760 * s, (1176 - j * 26) * s], fill=[(240, 200, 90), (200, 220, 250)][j % 2])


def other(d, x, base, look, t, seed, **pose):
    bob, blink = idle(t, seed)
    character(d, x, base + bob, **{**look, "blink": blink, **pose})


def car(t, kpose=None, moniteur=None, proche=None, z=1.0, center=None):
    big = voiture_bg().copy()
    d = ImageDraw.Draw(big)
    if kpose:
        kevin(d, 330, BASE, kpose, t)
    if moniteur is not None:
        other(d, 760, BASE, MONITEUR, t, 1.3, **moniteur)
    if proche is not None:
        other(d, 760, BASE, PROCHE, t, 2.1, **proche)
    voiture_fg(d)
    return shot(big, z, center=center)


def office(t, kpose=None, gerante=None, z=1.0, center=None, kx=280):
    big = room("vide").copy()
    d = ImageDraw.Draw(big)
    if gerante is not None:
        other(d, 800, BASE - 40, GERANTE, t, 0.7, **gerante)
    bureau_fg(d)
    if kpose:
        kevin(d, kx, BASE, kpose, t)
    return shot(big, z, center=center)


KHEAD = (280, BASE - 700)
GHEAD = (800, BASE - 740)


# Grammaire fixe : gros plan choc -> plan large -> gros plan adversaire -> plan moyen qui pousse.

def s_hook(lt, dur):
    if lt < 1.0:
        img = office(lt, "choc", z=2.3, center=(KHEAD[0], KHEAD[1] - 60))
        shock_lines(img, 540, 900, 300, lt)
        big_number(img, (540, 300), counter(0, 150, lt, 0.6), 230, YEL, "POUR SON PROPRE DOSSIER", k=1.0)
        return shake(flash(img, lt), lt)
    if lt < 2.0:
        img = office(lt, "neutre", gerante=dict(mouth="grin", arm=0.55), z=push(lt - 1, 1, 1.0, 1.06), center=(540, 1000))
        big_number(img, (540, 300), "150 €", 200, YEL, "LE TRANSFERT DU DOSSIER", k=1.0)
        return flash(img, lt - 1.0)
    if lt < 2.9:
        img = office(lt, gerante=dict(mouth="grin", arm=0.55), z=push(lt - 2, 0.9, 2.1, 2.3),
                     center=(GHEAD[0], GHEAD[1] - 40))
        tag(img, 540, 330, "PAYABLE AUJOURD'HUI", 64, RED, WHITE, rot=-4, k=(lt - 2.0) / 0.25)
        return flash(img, lt - 2.0)
    img = office(lt, "triste", gerante=dict(mouth="grin"), z=push(lt - 2.9, dur - 2.9, 1.2, 1.35), center=(540, 960))
    big_number(img, (540, 300), "150 €", 200, YEL, "LE TRANSFERT DU DOSSIER", k=1.0)
    return flash(img, lt - 2.9)


def s_douze(lt, dur):
    img = dim(office(lt, "neutre", gerante=dict(mouth="grin")), 0.8)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kévin", 0.2, False), ("N° NEPH", "???? ???? ????", 0.4, False)], lt, rot=-2)
    tag(img, 540, 330, "12 CHIFFRES", 70, YEL, INK, rot=-4, k=(lt - 0.6) / 0.3)
    return img


def s_paye(lt, dur):
    img = car(lt, "neutre", moniteur=dict(mouth="flat"), z=push(lt, dur, 1.0, 1.12))
    big_number(img, (540, 330), counter(0, 2500, lt, 0.8), 200, YEL, "DÉJÀ PAYÉS", k=1.0)
    tag(img, 540, 620, "30 H × 45 €", 60, WHITE, INK, rot=-4, k=(lt - 1.6) / 0.3)
    return shake(flash(img, lt), lt - 0.8)


def s_pas_pret(lt, dur):
    if lt < 1.4:
        img = car(lt, "neutre", moniteur=dict(mouth="o" if int(lt * 7) % 2 else "smile"), z=2.0, center=(760, 860))
        bubble(img, 540, 420, ["T'ES PAS", "ENCORE PRÊT"], 70, lt / 0.3, tail_x=600)
        return flash(img, lt)
    img = car(lt, "triste", moniteur=dict(mouth="smile"), z=push(lt - 1.4, dur - 1.4, 1.0, 1.15))
    big_number(img, (540, 330), "30E FOIS", 170, WHITE, "LA MÊME PHRASE", k=(lt - 1.4) / 0.3)
    tag(img, 540, 640, "EXAMEN : DANS 8 MOIS", 56, RED, WHITE, rot=-3, k=(lt - 2.6) / 0.3)
    return flash(img, lt - 1.4)


def s_partir(lt, dur):
    kx = 280 - 420 * (1 - ease(lt / 1.0))
    img = office(lt, "marche" if lt < 1.0 else "neutre", gerante=dict(mouth="grin", arm=0.55),
                 z=push(lt, dur, 1.05, 1.15), center=(540, 980), kx=kx)
    bubble(img, 640, 400, ["LE TRANSFERT, C'EST", "150 €. AUJOURD'HUI."], 54, (lt - 1.2) / 0.3, tail_x=780)
    return flash(img, lt)


def s_zero(lt, dur):
    img = office(lt, gerante=dict(mouth="o" if int(lt * 7) % 2 else "grin", clipboard=True),
                 z=push(lt, dur, 1.9, 2.15), center=(GHEAD[0], GHEAD[1] + 20))
    bubble(img, 540, 380, ["SINON TU REPARS", "DE ZÉRO"], 66, lt / 0.3, tail_x=700)
    if lt > 1.6:
        tag(img, 540, 640, "COMME TOUT LE MONDE", 50, WHITE, INK, rot=3, k=(lt - 1.6) / 0.3)
    return flash(img, lt)


def s_carte(lt, dur):
    img = office(lt, "carte", z=push(lt, dur, 1.9, 2.1), center=(KHEAD[0] + 150, KHEAD[1] + 120))
    tag(img, 540, 330, "IL HÉSITE", 64, YEL, INK, rot=-4, k=lt / 0.3)
    if lt > 1.2:
        tag(img, 540, 520, "2 ÉLÈVES ATTENDENT DERRIÈRE", 46, RED, WHITE, rot=3, k=(lt - 1.2) / 0.3)
    return flash(img, lt)


def s_echo(lt, dur):
    img = dim(office(lt, "triste", z=1.4, center=(KHEAD[0] + 100, KHEAD[1] + 100)), 0.65)
    tag(img, 540, 700, "« REPARTIR DE ZÉRO »", 86, YEL, INK, rot=-4, k=lt / 0.3)
    return img


def s_neph(lt, dur):
    img = dim(office(lt, "choc" if lt < 0.8 else "neutre", gerante=dict(mouth="flat")), 0.8)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kévin", 0.0, False), ("N° NEPH", "1204 5582 9917", 0.6, True)], lt + 0.5, rot=-2)
    big_number(img, (540, 280), "À LUI", 170, GREEN, "PAS À L'AUTO-ÉCOLE", k=(lt - 3.2) / 0.3, rot=-3)
    return shake(img, lt - 3.2)


def s_code(lt, dur):
    img = dim(office(lt, gerante=dict(mouth="flat")), 0.8)
    if lt < 4.8:
        card(img, 540, 800, "CODE DE LA ROUTE", "RESTITUTION DU DOSSIER", [
            ("Rendre le dossier", "gratuit", 1.6, True), ("Le facturer", "interdit", 3.0, True)], lt, rot=2)
        big_number(img, (540, 300), "LA LOI", 140, YEL, k=lt / 0.3)
        return img
    big_number(img, (540, 640), counter(0, 15000, lt - 4.8, 0.7), 210, RED, "D'AMENDE MAXIMUM", k=1.0)
    return shake(img, lt - 5.5)


def s_silence(lt, dur):
    img = office(lt, gerante=dict(mouth="flat", brows="triste"), z=push(lt, dur, 2.1, 2.3),
                 center=(GHEAD[0], GHEAD[1] - 40))
    tag(img, 540, 380, "…", 120, WHITE, INK, rot=0, k=lt / 0.3)
    return flash(img, lt)


def s_plateforme(lt, dur):
    if lt < 2.2:
        img = office(lt, "telephone", z=push(lt, 2.2, 1.6, 1.9), center=(KHEAD[0] + 100, KHEAD[1] + 200))
        big_number(img, (540, 330), "SANS AUTO-ÉCOLE ?", 120, WHITE, k=lt / 0.3)
        return flash(img, lt)
    img = dim(office(lt, "telephone"), 0.75)
    phone_big(img, 540, 860, lt - 2.2, "21:04", [
        ("État", "Candidat libre", "Inscription validée", (60, 110, 230)),
        ("État", "Examen réservé", "Date choisie par Kévin", GREEN)])
    if lt > 5.0:
        tag(img, 540, 260, "EXAMEN PRATIQUE : 0 €", 64, YEL, INK, rot=-4, k=(lt - 5.0) / 0.3)
    return img


def s_location(lt, dur):
    img = car(lt, "neutre", proche=dict(mouth="grin"), z=push(lt, dur, 1.0, 1.12))
    tag(img, 540, 300, "VOITURE À DOUBLE COMMANDE", 52, YEL, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 450, "EN LOCATION", 46, WHITE, INK, rot=3, k=(lt - 0.8) / 0.3)
    tag(img, 760, 640, "+ UN PROCHE", 52, GREEN, INK, rot=-3, k=(lt - 2.2) / 0.3)
    return flash(img, lt)


def s_demi(lt, dur):
    img = car(lt, "neutre", moniteur=dict(mouth="smile", arm=0.4), z=push(lt, dur, 1.9, 2.1), center=(760, 860))
    tag(img, 540, 380, "UN MONITEUR, ÇA RASSURE", 56, WHITE, INK, rot=-3, k=lt / 0.3)
    return flash(img, lt)


def s_permis(lt, dur):
    big = room("vide").copy()
    d = ImageDraw.Draw(big)
    kevin(d, 540, BASE, "permis", lt)
    img = shot(big, push(lt, dur, 1.15, 1.3), center=(540, 1000))
    shock_lines(img, 540, 760, 260, lt)
    big_number(img, (540, 300), "3 SEMAINES", 150, WHITE, "PLUS TARD", k=lt / 0.3)
    tag(img, 540, 1300, "PERMIS EN POCHE", 60, GREEN, INK, rot=-4, k=(lt - 0.8) / 0.3)
    return flash(img, lt)


def s_chute(lt, dur):
    img = dim(office(lt, "victoire", gerante=dict(mouth="flat")), 0.75)
    card(img, 540, 760, "PERMIS DE CONDUIRE", "DOSSIER DU CANDIDAT", [
        ("Candidat", "Kévin", 0.0, False), ("N° NEPH", "1204 5582 9917", 0.0, True)], lt + 1.0, rot=-2)
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
    v.scene("Kévin a déjà payé", s_paye)
    v.scene("Et à chaque leçon", s_pas_pret)
    v.scene("Alors Kévin veut partir", s_partir)
    v.scene("Et en rangeant le classeur", s_zero)
    v.scene("Kévin sort sa carte", s_carte)
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
