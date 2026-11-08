"""Tes droits : la prime d'activité ratée à cause d'une case. Héros récurrent Kévin."""
import argparse

from PIL import Image, ImageDraw

from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, F, back, big_number, bubble, card,
                     character, counter, dim, ease, flash, idle, kevin, notif, push, room, shake, shock_lines, shot,
                     tag)
from engine import H, W

LEA = dict(shirt=(170, 90, 190), pants=(40, 40, 60), hair=(200, 140, 60), long_hair=True)
BASE = 1560
KX, LX = 300, 780
KHEAD = (KX, BASE - 700)
LHEAD = (LX, BASE - 700)
CAF = (30, 110, 200)

_bg = {}


def pause_bg():
    """Salle de pause : comptoir et machine à café."""
    if "p" in _bg:
        return _bg["p"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1120 * s, 420 * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([0, 1110 * s, 440 * s, 1140 * s], fill=(160, 112, 80))
    d.rounded_rectangle([90 * s, 860 * s, 290 * s, 1110 * s], radius=20 * s, fill=(60, 60, 70))
    d.rectangle([130 * s, 900 * s, 250 * s, 960 * s], fill=(120, 200, 255))
    d.rectangle([160 * s, 1030 * s, 220 * s, 1100 * s], fill=WHITE)
    _bg["p"] = im
    return im


def salon_bg():
    """Chez Kévin le soir : canapé."""
    if "s" in _bg:
        return _bg["s"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60 * s, 1180 * s, 1020 * s, 1480 * s], radius=50 * s, fill=(180, 70, 60))
    d.rounded_rectangle([60 * s, 1080 * s, 1020 * s, 1260 * s], radius=50 * s, fill=(200, 84, 72))
    _bg["s"] = im
    return im


def pause(t, kpose=None, lea=None, z=1.0, center=None):
    big = pause_bg().copy()
    d = ImageDraw.Draw(big)
    if lea is not None:
        bob, blink = idle(t, 0.9)
        character(d, LX, BASE + bob, **{**LEA, "blink": blink, **lea})
    if kpose:
        kevin(d, KX, BASE, kpose, t)
    return shot(big, z, center=center)


def salon(t, kpose="telephone", z=1.0, center=None):
    big = salon_bg().copy()
    d = ImageDraw.Draw(big)
    kevin(d, 540, BASE, kpose, t)
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


def simulator(img, cx, cy, lt, rows, result=None, result_col=RED, hl=None, k=None):
    """Téléphone avec le simulateur CAF. rows : [(libellé, valeur, t0)] ; hl : index de la ligne surlignée."""
    k = ease(lt / 0.35) if k is None else k
    if k <= 0:
        return
    pw, ph = 600, 1060
    lay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=70, fill=(20, 20, 26, 255))
    d.rounded_rectangle([18, 18, pw - 19, ph - 19], radius=56, fill=(246, 247, 250, 255))
    d.rounded_rectangle([pw / 2 - 70, 34, pw / 2 + 70, 70], radius=18, fill=(20, 20, 26, 255))
    d.rectangle([18, 90, pw - 19, 190], fill=CAF + (255,))
    d.text((pw / 2, 140), "SIMULATEUR · PRIME D'ACTIVITÉ", font=F(26), fill=WHITE + (255,), anchor="mm")
    y = 250
    for j, (lab, val, t0) in enumerate(rows):
        if lt < t0:
            break
        if hl == j:
            d.rounded_rectangle([34, y - 18, pw - 34, y + 112], radius=16, fill=(255, 220, 70, 255))
        d.text((54, y + 8), lab, font=F(28), fill=(90, 90, 100, 255), anchor="lm")
        d.rounded_rectangle([54, y + 34, pw - 54, y + 96], radius=12, fill=WHITE + (255,), outline=(200, 200, 210, 255),
                            width=3)
        d.text((74, y + 65), val, font=F(32), fill=INK + (255,), anchor="lm")
        y += 140
    if result is not None:
        d.rounded_rectangle([54, ph - 230, pw - 54, ph - 80], radius=20, fill=result_col + (255,))
        d.text((pw / 2, ph - 155), result, font=FA(90), fill=WHITE + (255,), anchor="mm")
    sc = 0.8 + 0.2 * back(lt / 0.35)
    lay = lay.resize((int(pw * sc), int(ph * sc)))
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


FORM = [("Code postal", "69008", 0.0), ("Date de naissance", "14/03/1998", 0.0), ("Situation", "Salarié", 0.0)]


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    if lt < 1.0:      # gros plan choc + compteur
        img = salon(lt, "choc", z=2.3, center=(540, BASE - 760))
        shock_lines(img, 540, 900, 300, lt)
        big_number(img, (540, 300), counter(0, 240, lt, 0.6), 230, YEL, "PAR MOIS", k=1.0)
        return shake(flash(img, lt), lt)
    if lt < 2.0:      # plan large, salle de pause
        img = pause(lt, "neutre", lea=dict(mouth="grin"), z=push(lt - 1, 1, 1.0, 1.06), center=(540, 1000))
        big_number(img, (540, 300), "240 €", 200, YEL, "JAMAIS TOUCHÉS", k=1.0)
        return flash(img, lt - 1.0)
    if lt < 2.9:      # gros plan sur Léa qui rigole
        img = pause(lt, lea=dict(mouth="grin", arm=0.4), z=push(lt - 2, 0.9, 2.1, 2.3), center=(LHEAD[0], LHEAD[1] - 40))
        tag(img, 540, 330, "DEPUIS 2 ANS", 70, RED, WHITE, rot=-4, k=(lt - 2.0) / 0.25)
        return flash(img, lt - 2.0)
    img = pause(lt, "triste", lea=dict(mouth="grin"), z=push(lt - 2.9, dur - 2.9, 1.2, 1.35), center=(540, 960))
    big_number(img, (540, 300), "1 SEULE CASE", 170, YEL, "QUI A TOUT CHANGÉ", k=(lt - 2.9) / 0.3)
    return flash(img, lt - 2.9)


def s_cdi(lt, dur):
    img = pause(lt, "neutre", lea=dict(mouth="smile"), z=push(lt, dur, 1.0, 1.1), center=(540, 1000))
    tag(img, 540, 300, "CDI", 90, WHITE, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 560), counter(0, 1400, lt - 0.6, 0.6, "{:,} € NET"), 130, YEL, k=(lt - 0.6) / 0.2)
    return flash(img, lt)


def s_lea(lt, dur):
    img = pause(lt, "neutre", lea=dict(mouth=talk(lt), arm=0.4), z=push(lt, dur, 1.8, 2.0), center=(LHEAD[0] - 60, LHEAD[1] + 40))
    bubble(img, 540, 380, ["LA PRIME D'ACTIVITÉ,", "C'EST POUR", "LES CHÔMEURS"], 56, (lt - 0.6) / 0.3, tail_x=700)
    return flash(img, lt)


def s_lea2(lt, dur):
    img = pause(lt, "triste", lea=dict(mouth=talk(lt), arm=0.6), z=push(lt, dur, 1.2, 1.3), center=(540, 980))
    bubble(img, 680, 380, ["TOI T'ES EN CDI,", "OUBLIE"], 64, lt / 0.3, tail_x=780)
    return flash(img, lt)


def s_oublie(lt, dur):
    img = dim(pause(lt, "triste", lea=dict(mouth="smile")), 0.7)
    big_number(img, (540, 520), "1 SUR 3", 220, YEL, "DES GENS QUI Y ONT DROIT", k=(lt - 0.6) / 0.3)
    return shake(img, lt - 0.6)


def s_simu(lt, dur):
    if lt < 1.4:      # Kévin sur son canapé, téléphone en main, la caméra pousse
        img = salon(lt, "telephone", z=push(lt, 1.4, 1.3, 1.7), center=(540, BASE - 560))
        tag(img, 540, 300, "UN SOIR", 70, WHITE, INK, rot=-4, k=lt / 0.3)
        return flash(img, lt)
    img = dim(salon(lt, "telephone"), 0.75)
    t = lt - 1.4
    rows = [(a, b, 0.4 + 0.5 * j) for j, (a, b, _) in enumerate(FORM)] + [("Aide au logement", "1 400", 2.4)]
    simulator(img, 540, 900, t, rows, result="0 €" if t > 4.0 else None, hl=3 if t > 2.4 else None)
    return img


def s_zero(lt, dur):
    img = dim(salon(lt, "triste"), 0.8)
    big_number(img, (540, 760), "0 €", 330, RED, k=lt / 0.25)
    return shake(img, lt)


def s_referme(lt, dur):
    img = salon(lt, "triste", z=push(lt, dur, 1.6, 1.8), center=(540, BASE - 640))
    tag(img, 540, 330, "LÉA AVAIT RAISON", 64, WHITE, INK, rot=-4, k=(lt - 0.8) / 0.3)
    return flash(img, lt)


def s_case(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    rows = [("Aide au logement", "0", 0.0), ("Salaire net", "1 400", 3.2)]
    big_number(img, (540, 230), "LE PIÈGE", 130, YEL, k=lt / 0.3)
    simulator(img, 540, 1000, lt, rows, hl=0 if lt < 3.2 else 1, k=1.0)
    if lt > 1.0:
        tag(img, 540, 400, "CETTE CASE = AIDE AU LOGEMENT", 46, RED, WHITE, rot=-3, k=(lt - 1.0) / 0.3)
    return img


def s_recommence(lt, dur):
    if lt < 2.6:
        img = dim(salon(lt, "telephone"), 0.75)
        rows = [("Aide au logement", "0", 0.0), ("Salaire net", "1 400", 0.0)]
        simulator(img, 540, 900, lt, rows, result=counter(0, 240, lt - 0.6, 0.6, "+{:,} €") if lt > 0.6 else None,
                  result_col=GREEN, k=1.0)
        return shake(img, lt - 0.6)
    if lt < 4.6:
        img = salon(lt, "choc", z=2.0, center=(540, BASE - 760))
        shock_lines(img, 540, 900, 300, lt)
        big_number(img, (540, 300), "3 000 €", 210, YEL, "PAR AN, PRESQUE", k=(lt - 2.6) / 0.25)
        return shake(flash(img, lt - 2.6), lt - 2.6)
    img = salon(lt, "telephone", z=push(lt - 4.6, dur - 4.6, 1.4, 1.6), center=(540, BASE - 600))
    notif(img, 540, 140, "Appel", "Appel à Léa", "Pas de réponse", (lt - 4.8) / 0.4, col=GREEN)
    return flash(img, lt - 4.6)


def s_tous(lt, dur):
    img = dim(salon(lt, "parle"), 0.75)
    if lt < 5.6:
        for j, (lab, x, y, rot) in enumerate([("CDI", 300, 380, -5), ("CDD", 780, 380, 4), ("INTÉRIM", 300, 620, 3),
                                              ("ALTERNANCE", 780, 620, -4)]):
            tag(img, x, y, lab, 70, YEL, INK, rot=rot, k=(lt - 0.8 - 0.35 * j) / 0.25)
        big_number(img, (540, 960), "PETIT SALAIRE", 120, WHITE, "= TU PEUX Y AVOIR DROIT", k=(lt - 2.6) / 0.3)
        tag(img, 540, 1260, "LA CAF TE PRÉVIENT PAS", 56, RED, WHITE, rot=-3, k=(lt - 4.4) / 0.3)
        return img
    card(img, 540, 820, "TOUS LES 3 MOIS", "DÉCLARATION TRIMESTRIELLE", [
        ("Salaires préremplis", "à vérifier", 0.6, True), ("Une erreur", "trop perçu", 2.2, True)], lt - 5.6, rot=2)
    return img


def s_demi(lt, dur):
    img = pause(lt, lea=dict(mouth="smile", arm=0.3), z=push(lt, dur, 1.9, 2.1), center=(LHEAD[0], LHEAD[1] - 40))
    tag(img, 540, 330, "LÉA A PAS TOUT FAUX", 60, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 510, "PLUS DE SALAIRE = MOINS DE PRIME", 46, RED, WHITE, rot=3, k=(lt - 1.4) / 0.3)
    return flash(img, lt)


def s_perdus(lt, dur):
    img = dim(salon(lt, "triste"), 0.8)
    big_number(img, (540, 380), "2 ANS", 230, YEL, "PERDUS ?", k=lt / 0.3, strike=ease((lt - 2.0) / 0.4))
    tag(img, 540, 760, "PAS DE RATTRAPAGE", 60, RED, WHITE, rot=-4, k=(lt - 2.2) / 0.3)
    tag(img, 540, 920, "À PARTIR DU MOIS DE LA DEMANDE", 46, WHITE, INK, rot=3, k=(lt - 3.4) / 0.3)
    return shake(img, lt - 2.0)


def s_chute(lt, dur):
    img = salon(lt, "triste", z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    big_number(img, (540, 300), counter(0, 5760, lt, 0.8, "{:,} €"), 190, RED, "LAISSÉS SUR LA TABLE", k=1.0)
    tag(img, 540, 600, "POUR 1 SEULE CASE", 66, YEL, INK, rot=-4, k=(lt - 1.0) / 0.3)
    if lt > 1.0:
        tag(img, 540, 1760, "CAS TYPE · MONTANT INDICATIF · CECI N'EST PAS UN CONSEIL", 24, (40, 40, 50), WHITE, rot=0,
            k=(lt - 1.0) / 0.3)
    return flash(img, lt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_prime_activite", "scripts/modele/3_prime_activite.txt", "", "", corner="AIDES")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    v.scene("Deux cent quarante euros par mois", s_hook)
    v.scene("Kévin est en CDI", s_cdi)
    v.scene("À la pause", s_lea)
    v.scene("Et en reprenant son café", s_lea2)
    v.scene("Kévin oublie", s_oublie)
    v.scene("Et pourtant, un soir", s_simu)
    v.scene("Zéro", s_zero, after=v.at("euro", after=v.at("Résultat")) + 0.05)
    v.scene("Kévin referme l'appli", s_referme)
    v.scene("Sauf que cette case", s_case)
    v.scene("Kévin recommence", s_recommence)
    v.scene("Ce que peu de gens savent", s_tous)
    v.scene("Honnêtement, Léa", s_demi)
    v.scene("Mais alors, les deux ans", s_perdus)
    v.scene("Deux ans laissés sur la table", s_chute)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
