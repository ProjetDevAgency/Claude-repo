"""Tes droits : heures sup jamais payées, la preuve dans les SMS du patron. Ouverture « mépris »."""
import argparse

from PIL import ImageDraw

from cartoon import (GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, room, shake, shock_lines, shot, tag)
from engine import H, W

BASE = 1560
PATRON = dict(shirt=(150, 60, 40), pants=(40, 40, 50), hair=(90, 90, 96))
PX, KX = 760, 300
PHEAD = (PX, BASE - 700)
KHEAD = (KX, BASE - 700)
SMS = (52, 199, 89)

_bg = {}


def boutique_bg():
    if "b" in _bg:
        return _bg["b"]
    s = SS
    im = room("vide").copy()
    d = ImageDraw.Draw(im)
    cols = [(220, 90, 90), (90, 150, 220), (240, 200, 90), (120, 200, 140), (200, 120, 200)]
    for r in range(3):            # étagères de vêtements pliés
        y = 520 + r * 190
        d.rectangle([40 * s, (y + 120) * s, 520 * s, (y + 140) * s], fill=(120, 80, 56))
        for j in range(6):
            x = 60 + j * 76
            d.rounded_rectangle([x * s, (y + 50) * s, (x + 64) * s, (y + 120) * s], radius=10 * s,
                                fill=cols[(j + r) % 5])
    d.rectangle([560 * s, 1180 * s, 1080 * s, 1500 * s], fill=(120, 80, 56))     # comptoir
    d.rectangle([560 * s, 1180 * s, 1080 * s, 1210 * s], fill=(150, 104, 74))
    d.rounded_rectangle([880 * s, 1060 * s, 1040 * s, 1180 * s], radius=12 * s, fill=(50, 50, 60))  # caisse
    d.rectangle([900 * s, 1080 * s, 1020 * s, 1120 * s], fill=(120, 220, 160))
    # horloge
    d.ellipse([820 * s, 200 * s, 960 * s, 340 * s], fill=WHITE, outline=INK, width=8 * s)
    d.line([890 * s, 270 * s, 890 * s, 215 * s], fill=INK, width=8 * s)
    d.line([890 * s, 270 * s, 935 * s, 270 * s], fill=INK, width=8 * s)
    _bg["b"] = im
    return im


def boutique(t, kpose=None, patron=None, z=1.0, center=None, rideau=0.0):
    big = boutique_bg().copy()
    d = ImageDraw.Draw(big)
    if patron is not None:
        bob, blink = idle(t, 0.4)
        character(d, PX, BASE - 40 + bob, **{**PATRON, "blink": blink, **patron})
    if kpose:
        kevin(d, KX, BASE, kpose, t)
    if rideau > 0:   # rideau métallique qui descend
        s = SS
        yb = int(H * 0.62 * rideau)
        d.rectangle([0, 0, W * s, yb * s], fill=(130, 134, 145))
        for y in range(30, yb, 34):
            d.line([0, y * s, W * s, y * s], fill=(100, 104, 115), width=5 * s)
        d.rectangle([0, (yb - 24) * s, W * s, yb * s], fill=(80, 84, 95))
    return shot(big, z, center=center)


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    """Ouverture mépris : le patron en gros plan dit la phrase, écrite en énorme, dès la 1re image."""
    if lt < 1.5:
        img = boutique(lt, patron=dict(mouth=talk(lt), arm=0.35), z=push(lt, 1.5, 2.3, 2.45),
                       center=(PHEAD[0], PHEAD[1] - 120))
        tag(img, 540, 330, "« PAS DE PREUVE,", 96, WHITE, INK, rot=-4, k=1.0)
        tag(img, 540, 500, "PAS D'HEURE »", 96, RED, WHITE, rot=3, k=(lt + 0.3) / 0.3)
        return shake(img, lt)
    img = boutique(lt, "triste", patron=dict(mouth="grin"), z=push(lt - 1.5, dur - 1.5, 1.05, 1.2), center=(540, 1000))
    tag(img, 540, 300, "DEPUIS 3 ANS", 80, YEL, INK, rot=-4, k=(lt - 1.5) / 0.3)
    return flash(img, lt - 1.5)


def s_tease(lt, dur):
    img = dim(boutique(lt, "telephone", patron=dict(mouth="grin")), 0.8)
    phone_big(img, 540, 860, lt, "21:48", [("SMS", "Patron", "•••••••••••••", SMS)])
    tag(img, 540, 260, "LA PREUVE, C'EST LUI QUI L'ENVOIE", 50, YEL, INK, rot=-4, k=(lt - 0.8) / 0.3)
    return img


def s_vendeur(lt, dur):
    img = boutique(lt, "neutre", patron=dict(mouth="flat"), z=push(lt, dur, 1.0, 1.1), center=(540, 1000))
    tag(img, 540, 300, "VENDEUR", 80, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 470, "CONTRAT 35 H", 70, YEL, INK, rot=3, k=(lt - 0.8) / 0.3)
    return flash(img, lt)


def s_soir(lt, dur):
    img = boutique(lt, "triste", z=push(lt, dur, 1.5, 1.7), center=(KHEAD[0] + 160, KHEAD[1] + 60))
    tag(img, 540, 280, "APRÈS LA FERMETURE", 60, WHITE, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 520), "+4 H", 200, YEL, "PAR SEMAINE", k=(lt - 1.6) / 0.3)
    tag(img, 540, 800, "JAMAIS PAYÉES", 70, RED, WHITE, rot=3, k=(lt - 2.8) / 0.3)
    return flash(img, lt)


def s_ose(lt, dur):
    img = boutique(lt, "parle", patron=dict(mouth="flat"), z=push(lt, dur, 1.1, 1.2), center=(540, 980))
    tag(img, 540, 300, "UN VENDREDI, IL OSE", 64, YEL, INK, rot=-4, k=lt / 0.3)
    return flash(img, lt)


def s_patron1(lt, dur):
    img = boutique(lt, patron=dict(mouth=talk(lt), arm=0.5), z=push(lt, dur, 1.9, 2.1), center=(PHEAD[0] - 60, PHEAD[1] + 60))
    bubble(img, 520, 380, ["RIEN EST ÉCRIT,", "TU PEUX RIEN", "RÉCLAMER"], 62, (lt - 0.6) / 0.3, tail_x=680)
    return flash(img, lt)


def s_patron2(lt, dur):
    img = boutique(lt, "triste", patron=dict(mouth=talk(lt)), z=1.1, center=(540, 980), rideau=0.55 * ease(lt / 2.0))
    bubble(img, 600, 620, ["T'ES PAS CONTENT ?", "Y EN A 10 QUI", "ATTENDENT TA PLACE"], 52, (lt - 0.8) / 0.3, tail_x=740)
    return img


def s_echo(lt, dur):
    img = dim(boutique(lt, "triste", z=1.4, center=(KHEAD[0] + 100, KHEAD[1] + 100)), 0.7)
    tag(img, 540, 600, "« PAS DE PREUVE,", 84, WHITE, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 760, "PAS D'HEURE »", 84, RED, WHITE, rot=3, k=(lt - 0.2) / 0.25)
    return img


def s_calcul(lt, dur):
    img = dim(boutique(lt, "neutre"), 0.8)
    tag(img, 540, 240, "FAIS LE CALCUL", 60, YEL, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 470), "4 H × 45 SEM. × 3 ANS", 100, WHITE, k=(lt - 0.3) / 0.3)
    if lt > 3.4:
        big_number(img, (540, 720), counter(0, 540, lt - 3.4, 0.6, "{:,} H"), 170, YEL, "OFFERTES AU PATRON", k=1.0)
    if lt > 6.2:
        big_number(img, (540, 1050), "+ DE 6 000 €", 160, GREEN, "SANS LES MAJORATIONS", k=(lt - 6.2) / 0.25, rot=-3)
    return img


def s_code(lt, dur):
    img = dim(boutique(lt, patron=dict(mouth="flat")), 0.8)
    big_number(img, (540, 280), "LA LOI DIT L'INVERSE", 110, YEL, k=lt / 0.3)
    card(img, 540, 850, "CODE DU TRAVAIL", "EN CAS DE LITIGE", [
        ("Les horaires faits", "à fournir par l'employeur", 1.6, True),
        ("Le salarié", "des éléments précis", 4.2, False)], lt - 0.6, rot=2)
    return img


def s_sms(lt, dur):
    if lt < 1.6:
        img = boutique(lt, "telephone", z=push(lt, 1.6, 1.6, 1.9), center=(KHEAD[0] + 100, KHEAD[1] + 200))
        big_number(img, (540, 330), "QUELS ÉLÉMENTS ?", 130, WHITE, k=lt / 0.3)
        return flash(img, lt)
    img = dim(boutique(lt, "telephone"), 0.8)
    rows = [("SMS", "Patron · ven. 21:48", "Tu peux rester ce soir ?", SMS)]
    if lt > 3.4:
        rows.append(("SMS", "Patron · ven. 22:51", "Merci, t'es top", SMS))
    phone_big(img, 540, 860, lt - 1.6, "22:51", rows)
    if lt > 4.6:
        tag(img, 540, 250, "DATE + HEURE = LA PREUVE", 60, GREEN, INK, rot=-4, k=(lt - 4.6) / 0.3)
    return img


def s_3ans(lt, dur):
    img = dim(boutique(lt, "neutre"), 0.8)
    big_number(img, (540, 560), "3 ANS", 260, YEL, "DE SALAIRE EN ARRIÈRE", k=lt / 0.25)
    return shake(img, lt)


def s_demi(lt, dur):
    if lt < 2.6:
        img = boutique(lt, patron=dict(mouth="smile"), z=push(lt, 2.6, 1.9, 2.1), center=(PHEAD[0], PHEAD[1] - 40))
        tag(img, 540, 330, "LE PATRON A PAS TOUT FAUX", 56, WHITE, INK, rot=-4, k=lt / 0.3)
        tag(img, 540, 500, "SANS RIEN NOTER, C'EST PLUS DUR", 46, RED, WHITE, rot=3, k=(lt - 1.2) / 0.3)
        return flash(img, lt)
    img = dim(boutique(lt, "neutre"), 0.8)
    card(img, 540, 820, "CARNET DE KÉVIN", "HORAIRES NOTÉS DEPUIS LE DÉBUT", [
        ("Ven. 3 oct.", "19 h – 23 h", 0.3, False), ("Ven. 10 oct.", "19 h – 23 h", 0.5, False),
        ("Ven. 17 oct.", "19 h – 23 h", 0.7, True)], lt - 2.6, rot=-2)
    return flash(img, lt - 2.6)


def s_lettre(lt, dur):
    img = dim(boutique(lt, "neutre"), 0.8)
    card(img, 540, 800, "LETTRE RECOMMANDÉE AR", "AU PATRON", [
        ("Décompte des heures", "540 h", 0.6, True),
        ("À défaut", "je saisis", 2.2, False),
        ("les prud'hommes", "", 2.6, True)], lt, stamp="ENVOYÉ", stamp_t=3.6)
    return img


def s_arrangement(lt, dur):
    img = boutique(lt, "victoire", z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    tag(img, 540, 260, "2 SEMAINES PLUS TARD", 56, WHITE, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 520), "ARRANGEMENT", 150, GREEN, "PROPOSÉ PAR LE PATRON", k=(lt - 1.0) / 0.3)
    return flash(img, lt)


def s_chute(lt, dur):
    img = dim(boutique(lt, "victoire"), 0.75)
    phone_big(img, 540, 900, 1.0, "21:48", [("SMS", "Patron · ven. 21:48", "Tu peux rester ce soir ?", SMS)])
    tag(img, 540, 260, "LA PREUVE INTROUVABLE", 64, YEL, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 420, "ENVOYÉE DE SON PROPRE TÉLÉPHONE", 48, RED, WHITE, rot=3, k=(lt - 0.9) / 0.3)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · MONTANTS INDICATIFS · CECI N'EST PAS UN CONSEIL JURIDIQUE", 22, (40, 40, 50),
            WHITE, rot=0, k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_heures_sup", "scripts/modele/5_heures_sup.txt", "", "", corner="TRAVAIL")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    sc = [("Pas de preuve, pas d'heure. C'est", s_hook), ("Il le sait pas encore", s_tease),
          ("Kévin est vendeur", s_vendeur), ("Mais chaque soir", s_soir), ("Un vendredi, Kévin ose", s_ose),
          ("Son patron hausse", s_patron1), ("Et en baissant le rideau", s_patron2)]
    for phrase, fn in sc:
        v.scene(phrase, fn)
    T = {fn.__name__: v.at(phrase) for phrase, fn in sc}
    v.scene("Pas de preuve, pas d'heure", s_echo, after=T["s_patron2"] + 0.5)
    sc2 = [("Quatre heures par semaine", s_calcul), ("Et pourtant, le Code du travail", s_code),
           ("Mais alors, quels éléments", s_sms), ("Ce que peu de gens savent", s_3ans),
           ("Honnêtement, le patron", s_demi), ("Kévin envoie une lettre", s_lettre),
           ("Deux semaines plus tard", s_arrangement), ("La preuve introuvable", s_chute)]
    for phrase, fn in sc2:
        v.scene(phrase, fn)
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("Pas de preuve, pas d'heure", after=T["s_patron2"] + 0.5)
    # une douzaine de bruitages sur les moments forts
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["s_tease"], "notif", 0.9)
    v.sfx(T["s_soir"] + 1.6, "pop", 0.8)
    v.sfx(T["s_patron2"], "whoosh", 0.7)
    v.sfx(T["s_echo"], "impact", 0.9)
    v.sfx(T["s_calcul"] + 3.4, "ticks", 0.7)
    v.sfx(T["s_calcul"] + 6.2, "pop", 0.8)
    v.sfx(T["s_sms"] + 1.6, "notif", 0.9)
    v.sfx(T["s_sms"] + 3.4, "notif", 0.9)
    v.sfx(T["s_3ans"], "impact", 0.9)
    v.sfx(T["s_lettre"] + 3.6, "tampon", 1.0)
    v.sfx(T["s_arrangement"] + 1.0, "succes", 1.0)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
