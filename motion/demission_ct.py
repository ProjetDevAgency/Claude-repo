"""Tes droits : démissionner et toucher le chômage (reconversion). Hook « tu savais que si »."""
import argparse

from PIL import Image, ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, dim, ease,
                     flash, idle, kevin, push, room, shake, shock_lines, shot, tag)
from engine import H, W

BASE = 1560
CHEF = dict(shirt=(235, 190, 30), pants=(50, 50, 60), hair=(40, 30, 25), glasses=True)
CONSEILLER = dict(shirt=(70, 120, 190), pants=(40, 40, 50), hair=(120, 70, 40), long_hair=True)
KX, CX = 300, 760
KHEAD = (KX, BASE - 700)
CHEAD = (CX, BASE - 700)

_bg = {}


def entrepot_bg():
    if "e" in _bg:
        return _bg["e"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), (70, 76, 92))
    d = ImageDraw.Draw(im)
    for x0 in (0, 560):                       # racks
        for x in (x0 + 20, x0 + 500):
            d.rectangle([x * s, 300 * s, (x + 24) * s, 1500 * s], fill=(230, 120, 40))
        for y in (560, 860, 1160):
            d.rectangle([(x0 + 20) * s, y * s, (x0 + 524) * s, (y + 22) * s], fill=(40, 90, 170))
            for j in range(4):
                bx = x0 + 60 + j * 115
                d.rectangle([bx * s, (y - 150) * s, (bx + 100) * s, y * s], fill=(196, 150, 96))
                d.rectangle([(bx + 40) * s, (y - 150) * s, (bx + 60) * s, y * s], fill=(170, 126, 78))
    d.rectangle([0, 1500 * s, W * s, H * s], fill=(110, 112, 120))
    d.rectangle([0, 1600 * s, W * s, 1620 * s], fill=YEL)
    _bg["e"] = im
    return im


def bureau_bg():
    if "b" in _bg:
        return _bg["b"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1210 * s], fill=(150, 104, 74))
    _bg["b"] = im
    return im


def entrepot(t, kpose=None, chef=None, z=1.0, center=None, **kx):
    big = entrepot_bg().copy()
    d = ImageDraw.Draw(big)
    if chef is not None:
        bob, blink = idle(t, 0.6)
        character(d, CX, BASE + bob, **{**CHEF, "blink": blink, **chef})
    if kpose:
        kevin(d, KX, BASE, kpose, t, **kx)
    return shot(big, z, center=center)


def bureau(t, kpose=None, conseiller=None, z=1.0, center=None):
    big = bureau_bg().copy()
    d = ImageDraw.Draw(big)
    if conseiller is not None:
        bob, blink = idle(t, 1.1)
        character(d, CX, BASE - 40 + bob, **{**CONSEILLER, "blink": blink, **conseiller})
    s = SS
    d.rectangle([520 * s, 1180 * s, 1080 * s, 1500 * s], fill=(120, 80, 56))
    if kpose:
        kevin(d, KX, BASE, kpose, t)
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    if lt < 1.6:     # gros plan : Kévin, sa lettre en main, la question écrite en énorme
        img = entrepot(lt, "neutre", z=push(lt, 1.6, 2.1, 2.3), center=(KHEAD[0] + 120, KHEAD[1] + 60),
                       arm=0.45, hold="lettre", mouth="o", brows="haut")
        tag(img, 540, 300, "TU SAVAIS QUE SI", 90, WHITE, INK, rot=-4, k=1.0)
        tag(img, 540, 470, "TU DÉMISSIONNES…", 90, YEL, INK, rot=3, k=(lt + 0.4) / 0.3)
        return shake(img, lt)
    img = entrepot(lt, "choc", z=push(lt - 1.6, dur - 1.6, 1.6, 1.8), center=(KHEAD[0] + 60, KHEAD[1] - 60))
    shock_lines(img, 540, 900, 300, lt)
    big_number(img, (540, 330), "LE CHÔMAGE", 170, GREEN, "TU PEUX QUAND MÊME LE TOUCHER", k=(lt - 1.6) / 0.25)
    return flash(img, lt - 1.6)


def s_tease(lt, dur):
    img = dim(entrepot(lt, "neutre", arm=0.45, hold="lettre"), 0.75)
    big_number(img, (540, 520), "TOUT SE JOUE", 150, YEL, "AVANT LA LETTRE", k=lt / 0.3)
    return img


def s_entrepot(lt, dur):
    img = entrepot(lt, "neutre", chef=dict(mouth="flat"), z=push(lt, dur, 1.0, 1.1), center=(540, 1000))
    tag(img, 540, 280, "6 ANS DANS LE MÊME ENTREPÔT", 56, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 450, "SON RÊVE : ÉLECTRICIEN", 60, YEL, INK, rot=3, k=(lt - 1.8) / 0.3)
    return flash(img, lt)


def s_chef1(lt, dur):
    img = entrepot(lt, chef=dict(mouth=talk(lt), arm=0.4), z=push(lt, dur, 1.9, 2.1), center=(CHEAD[0] - 60, CHEAD[1] + 60))
    bubble(img, 520, 380, ["TU DÉMISSIONNES,", "TU PERDS", "TON CHÔMAGE"], 62, (lt - 0.6) / 0.3, tail_x=680)
    return flash(img, lt)


def s_chef2(lt, dur):
    img = entrepot(lt, "triste", chef=dict(mouth=talk(lt), clipboard=True), z=push(lt, dur, 1.1, 1.2), center=(540, 980))
    bubble(img, 640, 380, ["DE TOUTE FAÇON,", "TU REVIENDRAS"], 60, lt / 0.3, tail_x=760)
    return flash(img, lt)


def s_casier(lt, dur):
    big = entrepot_bg().copy()
    d = ImageDraw.Draw(big)
    s = SS
    for j in range(3):   # casiers
        x = 560 + j * 160
        d.rectangle([x * s, 700 * s, (x + 150) * s, 1500 * s], fill=(120, 130, 150), outline=(80, 90, 110), width=6 * s)
        for k in range(4):
            d.line([(x + 30) * s, (760 + k * 20) * s, (x + 120) * s, (760 + k * 20) * s], fill=(80, 90, 110), width=5 * s)
    kevin(d, KX, BASE, "triste", lt)
    img = shot(big, push(lt, dur, 1.2, 1.35), center=(540, 1000))
    tag(img, 540, 300, "LA LETTRE RESTE AU CASIER", 58, WHITE, INK, rot=-4, k=lt / 0.3)
    return flash(img, lt)


def s_echo(lt, dur):
    img = dim(entrepot(lt, "triste", z=1.4, center=(KHEAD[0] + 100, KHEAD[1] + 100)), 0.7)
    tag(img, 540, 640, "« TU PERDS TON CHÔMAGE »", 80, RED, WHITE, rot=-4, k=lt / 0.25)
    return img


def s_loi(lt, dur):
    img = dim(entrepot(lt, "neutre"), 0.8)
    big_number(img, (540, 330), "DEPUIS 2019", 170, YEL, k=lt / 0.3)
    tag(img, 540, 720, "LA DÉMISSION POUR RECONVERSION", 56, GREEN, INK, rot=-3, k=(lt - 1.6) / 0.3)
    big_number(img, (540, 1050), "COMMENT ?", 130, WHITE, k=(lt - 3.4) / 0.3)
    return shake(img, lt)


def s_cep(lt, dur):
    if lt < 4.2:
        img = bureau(lt, "parle", conseiller=dict(mouth="smile"), z=push(lt, 4.2, 1.05, 1.15), center=(540, 980))
        tag(img, 540, 270, "AVANT LA MOINDRE LETTRE", 56, RED, WHITE, rot=-4, k=lt / 0.3)
        tag(img, 540, 430, "CONSEILLER EN ÉVOLUTION PRO", 48, WHITE, INK, rot=3, k=(lt - 1.0) / 0.3)
        tag(img, 540, 580, "GRATUIT", 64, GREEN, INK, rot=-3, k=(lt - 2.4) / 0.3)
        return flash(img, lt)
    img = dim(bureau(lt, "neutre", conseiller=dict(mouth="smile")), 0.8)
    card(img, 540, 820, "COMMISSION RÉGIONALE", "TRANSITIONS PRO", [
        ("Projet", "réel et sérieux ?", 0.4, True)], lt - 4.2, rot=2)
    return img


def s_ordre(lt, dur):
    img = dim(entrepot(lt, "neutre"), 0.8)
    big_number(img, (540, 260), "5 ANS", 170, YEL, "DE TRAVAIL SALARIÉ SANS COUPURE", k=lt / 0.3)
    steps = [("1. CONSEILLER", 1.6), ("2. VALIDATION", 2.6), ("3. LA LETTRE", 3.6)]
    for j, (lab, t0) in enumerate(steps):
        tag(img, 540, 620 + j * 150, lab, 64, WHITE if j < 2 else GREEN, INK, rot=(-3, 3, -3)[j], k=(lt - t0) / 0.3)
    if lt > 5.6:
        tag(img, 540, 1160, "LETTRE TROP TÔT = PAS DE CHÔMAGE", 50, RED, WHITE, rot=-4, k=(lt - 5.6) / 0.25)
        return shake(img, lt - 5.6)
    return img


def s_legitime(lt, dur):
    img = dim(entrepot(lt, "neutre"), 0.8)
    card(img, 540, 820, "DÉMISSIONS LÉGITIMES", "EXEMPLES", [
        ("Suivre son conjoint muté", "", 2.2, True),
        ("Salaire qui arrive plus", "", 3.6, True)], lt, rot=-2)
    tag(img, 540, 300, "CE QUE PEU DE GENS SAVENT", 54, YEL, INK, rot=-4, k=lt / 0.3)
    return img


def s_demi(lt, dur):
    img = entrepot(lt, chef=dict(mouth="smile"), z=push(lt, dur, 1.9, 2.1), center=(CHEAD[0], CHEAD[1] - 40))
    tag(img, 540, 330, "LE CHEF A PAS TOUT FAUX", 60, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 500, "SANS MOTIF NI PROJET = RIEN", 50, RED, WHITE, rot=3, k=(lt - 1.2) / 0.3)
    return flash(img, lt)


def s_valide(lt, dur):
    if lt < 2.4:
        img = dim(bureau(lt, "neutre", conseiller=dict(mouth="grin")), 0.8)
        card(img, 540, 820, "COMMISSION RÉGIONALE", "TRANSITIONS PRO", [
            ("Projet", "réel et sérieux", 0.0, True), ("Avant la démission", "", 0.0, False),
            ("", "", 0.0, False)], lt + 1.0, rot=2, stamp="VALIDÉ", stamp_t=1.4)
        tag(img, 540, 280, "3 MOIS PLUS TARD", 60, WHITE, INK, rot=-4, k=lt / 0.3)
        return img
    img = entrepot(lt, "victoire", z=push(lt - 2.4, dur - 2.4, 1.2, 1.3), center=(540, 1000))
    tag(img, 540, 260, "LA LETTRE", 70, WHITE, INK, rot=-4, k=(lt - 2.4) / 0.3)
    tag(img, 540, 410, "FRANCE TRAVAIL", 60, YEL, INK, rot=3, k=(lt - 3.0) / 0.3)
    tag(img, 540, 560, "FORMATION ÉLECTRICIEN", 56, GREEN, INK, rot=-3, k=(lt - 3.6) / 0.3)
    return flash(img, lt - 2.4)


def s_chute(lt, dur):
    img = entrepot(lt, "victoire", z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    tag(img, 540, 300, "1. LE PAPIER", 90, YEL, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 500, "2. LA LETTRE", 90, WHITE, INK, rot=3, k=(lt - 0.9) / 0.25)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · CONDITIONS SUR FRANCETRAVAIL.FR · CECI N'EST PAS UN CONSEIL", 22, (40, 40, 50),
            WHITE, rot=0, k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_demission", "scripts/modele/6_demission_chomage.txt", "", "", corner="TRAVAIL")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    sc = [("Tu savais que si", s_hook), ("Kévin le sait pas encore", s_tease),
          ("Kévin bosse dans le même", s_entrepot), ("Son chef éclate de rire", s_chef1),
          ("Et en signant le planning", s_chef2), ("Kévin range sa lettre", s_casier)]
    T = {}
    for phrase, fn in sc:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("Tu perds ton chômage", after=T["s_casier"])
    v.scene("Tu perds ton chômage", s_echo, after=T["s_casier"])
    sc2 = [("Et pourtant, depuis", s_loi), ("Avant d'écrire la moindre lettre", s_cep),
           ("Sauf que l'ordre compte", s_ordre), ("Ce que peu de gens savent", s_legitime),
           ("Honnêtement, le chef", s_demi), ("Trois mois plus tard", s_valide), ("Le papier d'abord", s_chute)]
    for phrase, fn in sc2:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    v.sfx(0.0, "impact", 1.0)
    v.sfx(1.6, "pop", 0.8)
    v.sfx(T["s_chef1"], "whoosh", 0.5)
    v.sfx(T["s_echo"], "rate", 0.9)
    v.sfx(T["s_loi"], "impact", 0.9)
    v.sfx(T["s_cep"] + 2.4, "pop", 0.7)
    v.sfx(T["s_ordre"] + 5.6, "rate", 0.8)
    v.sfx(T["s_legitime"] + 2.2, "pop", 0.6)
    v.sfx(T["s_valide"] + 1.4, "tampon", 1.0)
    v.sfx(T["s_valide"] + 2.4, "succes", 1.0)
    v.sfx(T["s_chute"], "impact", 0.8)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
