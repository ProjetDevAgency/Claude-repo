"""Tes droits : résilier sa box avant la fin de l'engagement (au plus un quart du restant). Ouverture mépris."""
import argparse

from PIL import ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, room, shake, shock_lines, shot, tag)
from prime_ct import salon_bg
from trop_percu_ct import headset

BASE = 1560
CONSEILLER = dict(shirt=(120, 40, 160), pants=(30, 30, 40), hair=(40, 30, 25), glasses=True)
CX = 760
CHEAD = (CX, BASE - 740)
OPE = (230, 90, 30)
BANK = (60, 110, 230)

_bg = {}


def plateau_bg():
    if "p" in _bg:
        return _bg["p"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60 * s, 420 * s, 460 * s, 640 * s], radius=16 * s, fill=OPE)
    d.text((260 * s, 530 * s), "SERVICE CLIENT", fill=WHITE, anchor="mm", font=__import__("cartoon").FA(56 * s))
    _bg["p"] = im
    return im


def box(d, x, y, on=True):
    s = SS
    d.rounded_rectangle([(x - 90) * s, (y - 40) * s, (x + 90) * s, (y + 40) * s], radius=14 * s, fill=(240, 240, 245))
    for j in range(4):
        d.ellipse([(x - 60 + j * 26) * s, (y - 8) * s, (x - 46 + j * 26) * s, (y + 6) * s],
                  fill=GREEN if on else (150, 150, 160))


def plateau(t, conseiller=None, z=1.0, center=None):
    big = plateau_bg().copy()
    d = ImageDraw.Draw(big)
    if conseiller is not None:
        bob, blink = idle(t, 0.5)
        character(d, CX, BASE - 40 + bob, **{**CONSEILLER, "blink": blink, **conseiller})
        headset(d, CX, BASE - 40 + bob)
    s = SS
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1210 * s], fill=(150, 104, 74))
    d.rounded_rectangle([600 * s, 1120 * s, 860 * s, 1170 * s], radius=8 * s, fill=(40, 40, 50))
    return shot(big, z, center=center)


def salon(t, kpose="telephone", z=1.0, center=None, deux_box=False, kx=540):
    big = salon_bg().copy()
    d = ImageDraw.Draw(big)
    if deux_box:
        box(d, 220, 1040, True)
        box(d, 860, 1040, False)
    kevin(d, kx, BASE, kpose, t)
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


def s_hook(lt, dur):
    if lt < 1.8:
        img = plateau(lt, conseiller=dict(mouth=talk(lt), arm=0.3), z=push(lt, 1.8, 2.3, 2.45),
                      center=(CHEAD[0], CHEAD[1] + 110))
        tag(img, 540, 320, "« VOUS PARTEZ AVANT LA FIN ?", 72, WHITE, INK, rot=-4, k=1.0)
        tag(img, 540, 480, "CE SERA LES 9 MOIS RESTANTS »", 66, RED, WHITE, rot=3, k=(lt + 0.3) / 0.3)
        return shake(img, lt)
    img = salon(lt, "choc", z=push(lt - 1.8, dur - 1.8, 1.7, 1.9), center=(540, BASE - 760))
    shock_lines(img, 540, 900, 300, lt)
    big_number(img, (540, 330), "4 FOIS MOINS", 170, GREEN, "CE QU'IL VA VRAIMENT PAYER", k=(lt - 1.8) / 0.25)
    return flash(img, lt - 1.8)


def s_box(lt, dur):
    img = salon(lt, "neutre", z=push(lt, dur, 1.0, 1.1), center=(540, 1000))
    big_number(img, (540, 300), "40 € / MOIS", 150, YEL, k=lt / 0.25)
    tag(img, 540, 520, "ENGAGEMENT 24 MOIS", 60, WHITE, INK, rot=-3, k=(lt - 1.0) / 0.25)
    return flash(img, lt)


def s_demenage(lt, dur):
    img = salon(lt, "neutre", z=push(lt, dur, 1.0, 1.1), center=(540, 1000), deux_box=True)
    tag(img, 540, 280, "15 MOIS PLUS TARD", 66, WHITE, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 440, "IL DÉMÉNAGE CHEZ SA COPINE", 52, YEL, INK, rot=3, k=(lt - 0.8) / 0.25)
    if lt > 3.2:
        tag(img, 540, 700, "2 BOX POUR 1 SALON", 60, RED, WHITE, rot=-3, k=(lt - 3.2) / 0.25)
    return flash(img, lt)


def s_appel(lt, dur):
    img = salon(lt, "telephone", z=push(lt, dur, 1.5, 1.7), center=(540, BASE - 620))
    big_number(img, (540, 300), "20 MIN", 190, WHITE, "D'ATTENTE", k=lt / 0.3)
    return flash(img, lt)


def s_c1(lt, dur):
    img = plateau(lt, conseiller=dict(mouth=talk(lt), arm=0.3), z=push(lt, dur, 1.9, 2.1),
                  center=(CHEAD[0] - 60, CHEAD[1] + 60))
    bubble(img, 520, 380, ["VOUS ÊTES ENGAGÉ,", "VOUS PAYEZ", "JUSQU'AU BOUT"], 60, (lt - 0.5) / 0.3, tail_x=680)
    return flash(img, lt)


def s_c2(lt, dur):
    img = plateau(lt, conseiller=dict(mouth=talk(lt)), z=push(lt, dur, 1.5, 1.6), center=(CX - 100, CHEAD[1] + 200))
    bubble(img, 540, 380, ["360 €,", "PLUS LES FRAIS"], 70, lt / 0.3, tail_x=700)
    return flash(img, lt)


def s_compte(lt, dur):
    img = dim(salon(lt, "triste", deux_box=True), 0.8)
    big_number(img, (540, 500), "360 €", 240, RED, "POUR UNE BOX DÉBRANCHÉE", k=lt / 0.25)
    return shake(img, lt)


def s_echo(lt, dur):
    img = dim(salon(lt, "triste", z=1.4, center=(640, BASE - 600)), 0.7)
    tag(img, 540, 640, "« VOUS PAYEZ JUSQU'AU BOUT »", 72, RED, WHITE, rot=-4, k=lt / 0.25)
    return img


def s_code(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    big_number(img, (540, 280), "LA LOI DIT AUTRE CHOSE", 100, YEL, k=lt / 0.25)
    card(img, 540, 860, "CODE DE LA CONSOMMATION", "ENGAGEMENT DE PLUS DE 12 MOIS", [
        ("Partir dès le", "13e mois", 1.6, True), ("Il paie combien ?", "", 4.0, False)], lt - 0.6, rot=2)
    return img


def s_quart(lt, dur):
    img = dim(salon(lt, "choc" if lt < 1.0 else "neutre"), 0.8)
    big_number(img, (540, 360), "1/4", 260, GREEN, "DU RESTANT, AU MAXIMUM", k=lt / 0.25)
    if lt > 2.2:
        tag(img, 540, 760, "PAS LA TOTALITÉ", 70, RED, WHITE, rot=-4, k=(lt - 2.2) / 0.25)
    return shake(img, lt)


def s_calcul(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    tag(img, 540, 240, "FAIS LE CALCUL", 60, YEL, INK, rot=-4, k=lt / 0.25)
    big_number(img, (540, 470), "9 MOIS × 40 € = 360 €", 100, WHITE, k=(lt - 0.6) / 0.25)
    if lt > 3.0:
        big_number(img, (540, 800), counter(360, 90, lt - 3.0, 0.7, "{:,} €"), 220, GREEN, "UN QUART", k=1.0, rot=-3)
    return img


def s_demi(lt, dur):
    img = plateau(lt, conseiller=dict(mouth="smile"), z=push(lt, dur, 1.9, 2.1), center=(CHEAD[0], CHEAD[1] - 40))
    tag(img, 540, 330, "L'OPÉRATEUR A PAS TOUT FAUX", 54, WHITE, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 500, "AVANT 12 MOIS, TOUT EST DÛ", 50, RED, WHITE, rot=3, k=(lt - 1.4) / 0.25)
    return flash(img, lt)


def s_lettre(lt, dur):
    img = dim(salon(lt, "neutre"), 0.8)
    big_number(img, (540, 260), "15E MOIS", 150, YEL, k=lt / 0.25)
    card(img, 540, 860, "RÉSILIATION", "PAR ÉCRIT", [
        ("Engagement de 24 mois", "", 1.6, False), ("13e mois passé", "1/4 du restant", 2.4, True)],
        lt - 1.0, stamp="ENVOYÉ", stamp_t=3.6)
    return img


def s_facture(lt, dur):
    img = dim(salon(lt, "victoire"), 0.75)
    phone_big(img, 540, 860, lt, "10:15", [("Box", "Facture de clôture", "Montant : 90,00 €", OPE)])
    return img


def s_chute(lt, dur):
    img = salon(lt, "victoire", z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    big_number(img, (540, 280), "360 €", 160, RED, "ANNONCÉS", k=lt / 0.25, strike=ease((lt - 0.5) / 0.3))
    if lt > 0.9:
        big_number(img, (540, 620), "90 €", 200, GREEN, "PAYÉS", k=(lt - 0.9) / 0.25, rot=-3)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · CODE DE LA CONSOMMATION ART. L224-28 · CECI N'EST PAS UN CONSEIL", 20,
            (40, 40, 50), WHITE, rot=0, k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file", default="output/_work_droits_box/voice_raw.mp3")
    a = ap.parse_args()
    v = CartoonVideo("droits_box", "scripts/modele/8_box_resiliation.txt", "", "", corner="CONSO")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    T = {}
    sc = [("Vous partez avant", s_hook), ("Kévin a une box", s_box), ("Quinze mois plus tard", s_demenage),
          ("Il appelle", s_appel), ("Le conseiller soupire", s_c1), ("Et en tapant sur son clavier", s_c2),
          ("Kévin regarde son compte", s_compte)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("Vous payez jusqu'au bout", after=T["s_compte"])
    v.scene("Vous payez jusqu'au bout", s_echo, after=T["s_compte"])
    sc2 = [("Et pourtant, le Code", s_code), ("Ce que peu de gens savent", s_quart), ("Fais le calcul", s_calcul),
           ("Honnêtement, l'opérateur", s_demi), ("Sauf que Kévin", s_lettre), ("La facture de clôture", s_facture),
           ("Trois cent soixante annoncés", s_chute)]
    for phrase, fn in sc2:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    v.sfx(0.0, "impact", 1.0)
    v.sfx(1.8, "pop", 0.8)
    v.sfx(T["s_appel"], "attente", 0.7)
    v.sfx(T["s_compte"], "rate", 0.9)
    v.sfx(T["s_echo"], "impact", 0.8)
    v.sfx(T["s_quart"], "impact", 0.9)
    v.sfx(T["s_calcul"] + 3.0, "ticks", 0.7)
    v.sfx(T["s_lettre"] + 4.6, "tampon", 1.0)
    v.sfx(T["s_facture"], "notif", 0.9)
    v.sfx(T["s_chute"] + 0.9, "succes", 1.0)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
