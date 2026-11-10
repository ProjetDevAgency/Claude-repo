"""Tes droits : l'argent prêté à un ami et la prescription de 5 ans. Ouverture mépris + bruitages."""
import argparse

from PIL import ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, shake, shock_lines, shot, tag)
from prime_ct import salon_bg

BASE = 1560
JULIEN = dict(shirt=(230, 120, 40), pants=(40, 50, 70), hair=(25, 20, 18))
KX, JX = 300, 760
JHEAD = (JX, BASE - 700)
KHEAD = (KX, BASE - 700)
SMS = (52, 199, 89)
BANK = (60, 110, 230)


def manette(d, x, y):
    s = SS
    d.rounded_rectangle([(x - 50) * s, (y - 22) * s, (x + 50) * s, (y + 22) * s], radius=18 * s, fill=(30, 30, 36))
    d.ellipse([(x + 18) * s, (y - 8) * s, (x + 30) * s, (y + 4) * s], fill=RED)
    d.ellipse([(x - 34) * s, (y - 8) * s, (x - 20) * s, (y + 6) * s], fill=(90, 90, 100))


def salon(t, kpose=None, julien=None, z=1.0, center=None, pad=True):
    big = salon_bg().copy()
    d = ImageDraw.Draw(big)
    if julien is not None:
        bob, blink = idle(t, 0.8)
        character(d, JX, BASE + bob, **{**JULIEN, "blink": blink, **julien})
        if pad:
            manette(d, JX - 40, BASE - 420 + bob)
    if kpose:
        kevin(d, KX, BASE, kpose, t)
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    if lt < 1.8:      # Julien en gros plan, la phrase de mépris en énorme
        img = salon(lt, julien=dict(mouth=talk(lt), arm=0.2), z=push(lt, 1.8, 2.3, 2.45),
                    center=(JHEAD[0], JHEAD[1] + 110))
        tag(img, 540, 330, "« DANS UN MOIS,", 92, WHITE, INK, rot=-4, k=1.0)
        tag(img, 540, 500, "JE TE DOIS PLUS RIEN »", 84, RED, WHITE, rot=3, k=(lt + 0.3) / 0.3)
        return shake(img, lt)
    img = salon(lt, "triste", julien=dict(mouth="grin"), z=push(lt - 1.8, dur - 1.8, 1.05, 1.18), center=(540, 1000))
    big_number(img, (540, 330), counter(0, 1400, lt - 1.8, 0.6, "{:,} €"), 190, YEL, "QU'IL LUI DOIT", k=1.0)
    return flash(img, lt - 1.8)


def s_tease(lt, dur):
    img = dim(salon(lt, "neutre", julien=dict(mouth="grin")), 0.8)
    big_number(img, (540, 560), "20 €", 260, GREEN, "VONT TOUT CHANGER", k=lt / 0.25)
    return shake(img, lt)


def s_pret(lt, dur):
    if lt < 2.4:
        img = salon(lt, "neutre", julien=dict(mouth="sad", brows="triste"), z=push(lt, 2.4, 1.0, 1.1),
                    center=(540, 1000), pad=False)
        tag(img, 540, 300, "IL Y A PRESQUE 5 ANS", 66, WHITE, INK, rot=-4, k=lt / 0.25)
        tag(img, 540, 460, "JULIEN PERD SON BOULOT", 56, RED, WHITE, rot=3, k=(lt - 0.9) / 0.25)
        return flash(img, lt)
    img = dim(salon(lt, "telephone", pad=False), 0.8)
    phone_big(img, 540, 860, lt - 2.4, "11:02", [("Banque", "Virement envoyé", "À Julien · −1 400 €", BANK)])
    if lt > 5.0:
        tag(img, 540, 260, "PAS DE PAPIER, ENTRE POTES", 54, YEL, INK, rot=-4, k=(lt - 5.0) / 0.25)
    return img


def s_depuis(lt, dur):
    img = salon(lt, "parle", julien=dict(mouth="flat"), z=push(lt, dur, 1.05, 1.15), center=(540, 1000))
    tag(img, 540, 300, "DEPUIS : RIEN", 80, WHITE, INK, rot=-4, k=lt / 0.25)
    return flash(img, lt)


def s_julien1(lt, dur):
    img = salon(lt, julien=dict(mouth=talk(lt), arm=0.4), z=push(lt, dur, 1.9, 2.1), center=(JHEAD[0] - 60, JHEAD[1] + 60))
    bubble(img, 520, 380, ["FRÈRE, C'EST LA LOI.", "AU BOUT DE 5 ANS,", "C'EST PRESCRIT"], 58, (lt - 0.4) / 0.3, tail_x=680)
    return flash(img, lt)


def s_julien2(lt, dur):
    img = salon(lt, "triste", julien=dict(mouth=talk(lt)), z=push(lt, dur, 1.1, 1.2), center=(540, 980))
    bubble(img, 640, 380, ["T'AURAIS DÛ ME LE", "RÉCLAMER AVANT"], 58, lt / 0.3, tail_x=760)
    return flash(img, lt)


def s_date(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    big_number(img, (540, 360), "J−23", 280, RED, "AVANT LA FIN DU DÉLAI", k=lt / 0.25)
    return shake(img, lt)


def s_echo(lt, dur):
    img = dim(salon(lt, "triste", z=1.4, center=(KHEAD[0] + 100, KHEAD[1] + 100)), 0.7)
    tag(img, 540, 640, "« JE TE DOIS PLUS RIEN »", 80, RED, WHITE, rot=-4, k=lt / 0.25)
    return img


def s_5ans(lt, dur):
    img = dim(salon(lt, julien=dict(mouth="grin")), 0.8)
    big_number(img, (540, 300), "5 ANS", 220, YEL, "POUR RÉCLAMER UNE DETTE", k=lt / 0.25)
    if lt > 2.6:
        tag(img, 540, 760, "APRÈS : MÊME LE JUGE NE PEUT RIEN", 52, RED, WHITE, rot=-3, k=(lt - 2.6) / 0.25)
    return img


def s_repart(lt, dur):
    img = dim(salon(lt, "choc" if lt < 1.2 else "neutre"), 0.8)
    if lt < 1.2:
        shock_lines(img, 540, 900, 300, lt)
    big_number(img, (540, 280), "NON !", 200, GREEN, k=lt / 0.25)
    if lt > 2.0:
        card(img, 540, 900, "CODE CIVIL", "LE DÉLAI REPART À ZÉRO SI…", [
            ("Il reconnaît sa dette", "par écrit", 1.4, True),
            ("Ou il en rembourse", "une partie", 3.0, True)], lt - 2.0, rot=2)
    return img


def s_message(lt, dur):
    img = dim(salon(lt, "telephone"), 0.8)
    rows = [("SMS", "Moi", "Tu peux déjà me rendre 20 € ?", SMS)]
    if lt > 3.4:
        rows.append(("Banque", "Virement reçu", "+20 € · Pour la dette", BANK))
    phone_big(img, 540, 860, lt, "19:40", rows)
    if lt > 2.4 and lt < 3.4:
        tag(img, 540, 260, "JULIEN, GÊNÉ…", 60, WHITE, INK, rot=-4, k=(lt - 2.4) / 0.25)
    if lt > 4.0:
        tag(img, 540, 260, "« POUR LA DETTE »", 66, YEL, INK, rot=-4, k=(lt - 4.0) / 0.25)
    return img


def s_reset(lt, dur):
    img = dim(salon(lt, "victoire"), 0.75)
    tag(img, 540, 260, "RECONNAISSANCE DE DETTE", 58, GREEN, INK, rot=-3, k=lt / 0.25)
    if lt < 2.4:
        v = max(0, 23 - int(23 * ease((lt - 0.4) / 1.0)))
        big_number(img, (540, 640), f"J−{v}" if lt < 1.4 else "J−0", 230, RED, "", k=1.0)
    else:
        big_number(img, (540, 640), "5 ANS", 260, GREEN, "LE COMPTEUR REPART", k=(lt - 2.4) / 0.25)
        return shake(img, lt - 2.4)
    return img


def s_demi(lt, dur):
    if lt < 3.0:
        img = salon(lt, julien=dict(mouth="smile"), z=push(lt, 3.0, 1.9, 2.1), center=(JHEAD[0], JHEAD[1] - 40))
        tag(img, 540, 330, "JULIEN A PAS TOUT FAUX", 58, WHITE, INK, rot=-4, k=lt / 0.25)
        tag(img, 540, 500, "SANS TRACE, DUR À PROUVER", 50, RED, WHITE, rot=3, k=(lt - 1.2) / 0.25)
        return flash(img, lt)
    img = dim(salon(lt, "neutre"), 0.8)
    card(img, 540, 840, "LES PREUVES DE KÉVIN", "PRÊT DE MOINS DE 1 500 €", [
        ("Virement de départ", "1 400 €", 0.4, True),
        ("Virement de Julien", "« Pour la dette »", 1.2, True)], lt - 3.0, rot=-2)
    return flash(img, lt - 3.0)


def s_chute(lt, dur):
    img = salon(lt, "victoire", julien=dict(mouth="sad", brows="triste"), z=push(lt, dur, 1.1, 1.2), center=(540, 1000))
    big_number(img, (540, 280), "+20 €", 170, GREEN, "REÇUS", k=lt / 0.25)
    if lt > 0.9:
        big_number(img, (540, 660), "1 380 €", 170, RED, "ENCORE DUS", k=(lt - 0.9) / 0.25, rot=-3)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · CODE CIVIL ART. 2224 ET 2240 · CECI N'EST PAS UN CONSEIL JURIDIQUE", 20,
            (40, 40, 50), WHITE, rot=0, k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file", default="output/_work_droits_argent_prete/voice_raw.mp3")
    a = ap.parse_args()
    v = CartoonVideo("droits_argent_prete", "scripts/modele/7_argent_prete.txt", "", "", corner="ARGENT")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    T = {}
    sc = [("Dans un mois", s_hook), ("Il le sait pas encore", s_tease), ("Il y a presque cinq ans", s_pret),
          ("Depuis, rien", s_depuis), ("Julien rigole", s_julien1), ("Et en reprenant sa manette", s_julien2),
          ("Kévin regarde la date", s_date)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("Je te dois plus rien", after=T["s_date"])
    v.scene("Je te dois plus rien", s_echo, after=T["s_date"])
    sc2 = [("Et pourtant, Julien", s_5ans), ("Mais alors, Kévin perd", s_repart), ("Alors Kévin envoie", s_message),
           ("Ces vingt euros", s_reset), ("Honnêtement, Julien", s_demi), ("Vingt euros reçus", s_chute)]
    for phrase, fn in sc2:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    v.sfx(0.0, "impact", 1.0)
    v.sfx(1.8, "ticks", 0.6)
    v.sfx(T["s_tease"], "pop", 0.8)
    v.sfx(T["s_pret"] + 2.4, "notif", 0.9)
    v.sfx(T["s_julien1"], "whoosh", 0.5)
    v.sfx(T["s_date"], "impact", 0.9)
    v.sfx(T["s_echo"], "rate", 0.8)
    v.sfx(T["s_repart"], "impact", 0.9)
    v.sfx(T["s_message"], "notif", 0.9)
    v.sfx(T["s_message"] + 3.4, "notif", 0.9)
    v.sfx(T["s_reset"] + 2.4, "succes", 1.0)
    v.sfx(T["s_chute"] + 0.9, "pop", 0.8)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
