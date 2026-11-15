"""Où va ton argent ? — méthode v3 (Kévin raconte, le méchant a sa voix).
    python3 motion/quotidien_ct.py casse     → « tout objet cassé est dû » (scripts/modele/17_objet_casse.dial)
    python3 motion/quotidien_ct.py pension   → pension alimentaire impayée, l'ARIPA (scripts/modele/18_pension_alimentaire.dial)
"""
import sys

from cartoon import FA, bubble, card, character, flash, idle, phone_big, room, shake
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, H, Image, ImageDraw, Recit, W, big_number, dim, echo,
                   gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from vol_ct import SARAH, badge, carte_sombre

VENDEUR = dict(shirt=(60, 60, 70), pants=(36, 36, 44), hair=(150, 110, 60), glasses=True)
EX = dict(shirt=(250, 250, 250), pants=(40, 80, 160), hair=(215, 175, 70))   # blond, sans casquette : ne pas le confondre avec Kévin
CLIENT = [dict(shirt=(90, 140, 200), pants=(40, 40, 50), hair=(60, 40, 30), mouth="o", sc=0.8, phone=True),
          dict(shirt=(200, 160, 60), pants=(40, 40, 50), hair=(30, 25, 20), long_hair=True, mouth="o", sc=0.8, phone=True)]
_bg = {}


# ═════════════ décors ═════════════

def vase(d, x, y, s=1.0, col=(70, 130, 200)):
    S = SS
    d.ellipse([(x - 40 * s) * S, (y - 110 * s) * S, (x + 40 * s) * S, (y - 10 * s) * S], fill=col, outline=INK, width=3 * S)
    d.rectangle([(x - 18 * s) * S, (y - 150 * s) * S, (x + 18 * s) * S, (y - 95 * s) * S], fill=col)
    d.rectangle([(x - 26 * s) * S, (y - 160 * s) * S, (x + 26 * s) * S, (y - 145 * s) * S], fill=col, outline=INK, width=3 * S)
    d.rectangle([(x - 30 * s) * S, (y - 14 * s) * S, (x + 30 * s) * S, y * S], fill=col)


def deco_bg():
    if "d" not in _bg:
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        s = SS
        cols = [(70, 130, 200), (220, 120, 90), (120, 190, 140), (240, 200, 90), (190, 120, 200)]
        for r, y in enumerate((620, 900)):                      # étagères pleines de vases
            d.rectangle([40 * s, y * s, 1040 * s, (y + 22) * s], fill=(150, 104, 74))
            for k in range(6):
                vase(d, 110 + k * 170, y, 0.8, cols[(k + r) % 5])
        _bg["d"] = im
    return _bg["d"]


def debris(d, t):
    """Les morceaux du vase par terre."""
    s = SS
    for k, (x, y, r) in enumerate([(560, 1520, 30), (620, 1540, 22), (500, 1550, 26), (660, 1515, 18), (590, 1560, 16)]):
        d.polygon([((x - r) * s, y * s), ((x + r * 0.2) * s, (y - r) * s), ((x + r) * s, (y + r * 0.4) * s)],
                  fill=(70, 130, 200), outline=INK)


def panneau(img, k=1.0, y=470):
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([250, y - 60, 830, y + 60], radius=14, fill=(250, 245, 230), outline=RED, width=8)
    d.text((540, y), "TOUT OBJET CASSÉ EST DÛ", font=FA(46), fill=RED, anchor="mm")


def plage_bg():
    if "p" not in _bg:
        s = SS
        im = Image.new("RGB", (W * s, H * s), (130, 200, 245))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 900 * s, W * s, 1250 * s], fill=(40, 140, 210))
        d.rectangle([0, 1250 * s, W * s, H * s], fill=(240, 215, 150))
        d.ellipse([780 * s, 260 * s, 960 * s, 440 * s], fill=(255, 220, 80))
        for x in (160, 520):                                            # vagues
            d.arc([x * s, 980 * s, (x + 200) * s, 1060 * s], 200, 340, fill=WHITE, width=8 * s)
        # le jet-ski
        d.polygon([(560 * s, 1180 * s), (1000 * s, 1180 * s), (940 * s, 1240 * s), (600 * s, 1240 * s)], fill=(230, 60, 60))
        d.rectangle([700 * s, 1130 * s, 820 * s, 1185 * s], fill=(30, 30, 36))
        _bg["p"] = im
    return _bg["p"]


# ═════════════ 1. « tout objet cassé est dû » ═════════════

def magasin(t, kpose="neutre", vendeur=None, clients=False, casse=True, z=1.0, center=(540, 1000), **kx):
    autres = [(560, CLIENT[0], {}, 1.3, BASE - 40), (680, CLIENT[1], {}, 2.1, BASE - 40)] if clients else ()
    return plan(deco_bg, t, kpose, mechant=vendeur or dict(mouth="flat"), look=VENDEUR, mx=860, autres=autres,
                devant=debris if casse else None, z=z, center=center, **kx)


def c_hook(lt, dur):
    img = gros_plan_mechant(deco_bg, VENDEUR, lt, dur, arm=0.9)
    badge(img, 540, 1190, "LE VENDEUR")
    bubble(img, 540, 570, ["450 € LE VASE,", "SINON J'APPELLE", "LA POLICE"], 64, (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def c_couture(lt, dur):
    img = magasin(lt, "choc", dict(mouth="grin", arm=0.9), clients=True, z=push(lt, dur, 1.0, 1.06))
    panneau(img, k=(lt - 2.0) / 0.3)
    if lt < 2.0:
        tag(img, 540, 470, "DEVANT UNE DIZAINE DE CLIENTS", 46, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return flash(img, lt)


def c_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=540, z=push(lt, dur, 1.0, 1.08), center=(540, 1000))
    for i, (txt, col, t0) in enumerate([("L'ANNIVERSAIRE DE SA MÈRE", YEL, 0.2), ("LE CADEAU PARFAIT", GREEN, 1.6)]):
        tag(img, 540, 420 + i * 140, txt, 52, col, INK, rot=(-4, 3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def c_demande(lt, dur):
    img = magasin(lt, "parle", dict(mouth="grin" if lt > 1.4 else "flat", arm=0.6), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "J'AI À PEINE FRÔLÉ L'ÉTAGÈRE", 46, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def c_coup1(lt, dur):
    img = gros_plan_mechant(deco_bg, VENDEUR, lt, dur, 1.95, 2.15, arm=0.9)
    bubble(img, 540, 560, ["FRÔLÉ ?", "C'EST ÉCRIT EN GROS,", "TU SAIS PAS LIRE ?"], 62, lt / 0.25, tail_x=660)
    return flash(img, lt)


def c_geste(lt, dur):
    img = magasin(lt, "triste", dict(mouth="grin", phone=True), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def c_coup2(lt, dur):
    img = gros_plan_mechant(deco_bg, VENDEUR, lt, dur, 2.2, 2.4, arm=0.5, phone=True)
    bubble(img, 540, 560, ["QUAND ON A PAS", "LES MOYENS, ON TOUCHE", "AVEC LES YEUX"], 58, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def c_silence(lt, dur):
    return magasin(lt, "carte", dict(mouth="grin", phone=True), z=push(lt, dur, 1.0, 1.04))


def c_echo(lt, dur):
    img = dim(gros_plan_kevin(deco_bg, lt, dur), 0.75)
    echo(img, "ON TOUCHE AVEC LES YEUX")
    return img


def c_regle(lt, dur):
    img = dim(magasin(lt, "neutre", dict(mouth="flat")), 0.88)
    panneau(img, y=500)
    d = ImageDraw.Draw(img)
    k = min(1.0, max(0.0, (lt - 1.0) / 0.3))
    if k > 0:
        d.line([(240, 420), (840, 580)], fill=RED, width=int(14 * k))
        d.line([(240, 580), (840, 420)], fill=RED, width=int(14 * k))
    tag(img, 540, 680, "CE PANNEAU NE CHANGE PAS LA LOI", 44, YEL, INK, rot=-3, k=(lt - 1.6) / 0.3)
    return img


def c_etagere(lt, dur):
    # gros plan sur l'étagère : le vase était au bord, en équilibre
    img = magasin(lt, "neutre", dict(mouth="flat"), z=push(lt, dur, 1.6, 1.75), center=(540, 760))
    tag(img, 540, 470, "POSÉ AU BORD, EN ÉQUILIBRE", 48, RED, WHITE, rot=-3, k=(lt - 2.0) / 0.3)
    if lt > 4.0:
        tag(img, 540, 600, "LA FAUTE DU MAGASIN", 56, YEL, INK, rot=2, k=(lt - 4.0) / 0.3)
    return img


def c_prix(lt, dur):
    img = dim(magasin(lt, "neutre", dict(mouth="flat")), 0.9)
    carte_sombre(img, "ET SI C'ÉTAIT TA FAUTE ?", [("Prix affiché : tu ne le dois pas", 0.4, False),
                                                   ("Seulement son prix d'achat", 1.6, False),
                                                   ("Facture à l'appui", 2.8, True)], lt, y0=470,
                 sous="JUSTICE.FR · CASSE EN MAGASIN")
    return img


def c_doute(lt, dur):
    img = magasin(lt, "triste", dict(mouth="flat"), z=push(lt, dur, 1.1, 1.18), center=(420, 1000))
    tag(img, 540, 420, "UN PEU COUPABLE QUAND MÊME", 48, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def c_demande2(lt, dur):
    img = magasin(lt, "parle", dict(mouth="o", brows="triste"), clients=True, z=push(lt, dur, 1.0, 1.06))
    for i, (txt, t0) in enumerate([("1. LA FACTURE DU VASE", 1.4), ("2. LE NOM DE SON ASSURANCE", 2.6)]):
        tag(img, 540, 420 + i * 130, txt, 50, YEL, INK, rot=(-3, 2)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def c_silence2(lt, dur):
    img = magasin(lt, "neutre", dict(mouth="o", brows="triste"), clients=True, z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "IL DIT PLUS RIEN", 56, WHITE, INK, rot=-3, k=(lt - 0.8) / 0.3)
    return img


def c_ramasse(lt, dur):
    img = magasin(lt, "victoire", dict(mouth="sad", brows="triste"), z=push(lt, dur, 1.0, 1.05))
    tag(img, 540, 420, "IL RAMASSE TOUT SEUL", 52, GREEN, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return img


def c_chute(lt, dur):
    img = dim(plan(deco_bg, lt, devant=debris, z=1.1, center=(540, 1150)), 0.6)       # pas de visage sous le texte
    big_number(img, (540, 470), "450 €", 150, GREEN, "ET LE CADEAU DE SA MÈRE", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CASSE INVOLONTAIRE EN MAGASIN · JUSTICE.FR", lt)
    return img


CASSE = (Recit("droits_casse", "scripts/modele/17_objet_casse.txt", "output/_work_droits_casse/voice_duo.wav",
               compteur=dict(label="GARDÉ PAR KÉVIN", depart=0, montant=450, phrase="Il ramasse")),
         [("Tu me paies", c_hook, ("impact", 1.0)), ("C'est ce que le vendeur", c_couture, ("whoosh", 0.6)),
          ("Et pourtant j'étais venu", c_montee, ("pop", 0.8)), ("Je lui dis que", c_demande, None),
          ("Frôlé", c_coup1, ("impact", 0.8)), ("Et en sortant", c_geste, ("whoosh", 0.5)),
          ("Quand on a pas", c_coup2, ("impact", 1.0)), ("Je dis rien", c_silence, None),
          ("On touche avec les yeux", c_echo, ("rate", 0.6)), ("Sauf que ce panneau", c_regle, ("tampon", 0.8, 1.0)),
          ("Mais alors pourquoi", c_etagere, ("pop", 0.7)), ("Et même si c'était", c_prix, ("ticks", 0.6)),
          ("Honnêtement", c_doute, None), ("Alors je range", c_demande2, ("pop", 0.7)),
          ("Il regarde l'étagère", c_silence2, None), ("Il ramasse", c_ramasse, None),
          ("Quatre cent cinquante euros, et", c_chute, ("impact", 0.9))])


# ═════════════ 2. la pension alimentaire ═════════════

ENFANTS = [dict(shirt=(250, 190, 60), pants=(60, 90, 160), hair=(70, 45, 30), sc=0.5, mouth="smile"),
           dict(shirt=(120, 200, 150), pants=(60, 90, 160), hair=(150, 90, 40), long_hair=True, sc=0.5, mouth="smile")]


def chez_sarah(t, kpose="neutre", sarah=None, enfants=True, z=1.0, center=(540, 1000)):
    autres = [(780, SARAH, sarah or dict(mouth="flat"), 1.7)]
    if enfants:
        autres += [(935, ENFANTS[0], {}, 0.4), (1020, ENFANTS[1], {}, 0.9)]   # à droite : jamais sous les sous-titres
    return plan(salon_bg, t, kpose, kx=260, autres=autres, z=z, center=center)


def message(img, lignes, lt, y0=420, nom="L'EX"):
    """Une conversation de messagerie en grand (bulles grises = l'ex)."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([110, y0, 970, y0 + 120 + 150 * len(lignes)], radius=40, fill=(20, 22, 30))
    d.text((540, y0 + 55), nom, font=FA(40), fill=(200, 200, 210), anchor="mm")
    for k, (txt, t0) in enumerate(lignes):
        if lt < t0:
            continue
        y = y0 + 110 + k * 150
        d.rounded_rectangle([150, y, 930, y + 120], radius=30, fill=(60, 64, 78))
        d.text((180, y + 60), txt, font=FA(36), fill=WHITE, anchor="lm")


def p_hook(lt, dur):
    img = gros_plan_mechant(plage_bg, EX, lt, dur, arm=0.5, phone=True)
    badge(img, 540, 1190, "L'EX DE SA SŒUR")
    bubble(img, 540, 570, ["2 400 € DE PENSION ?", "VA VOIR UN AVOCAT,", "SI T'AS DE QUOI"], 60, (lt + 0.3) / 0.3,
           tail_x=660)
    return shake(img, lt)


def p_couture(lt, dur):
    img = chez_sarah(lt, "choc", dict(mouth="sad", phone=True), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "6 MOIS SANS UN EURO", 56, RED, WHITE, rot=-3, k=(lt - 0.3) / 0.3)
    if lt > 3.4:
        tag(img, 540, 560, "ET LUI, EN JET-SKI SUR INSTA", 46, WHITE, INK, rot=2, k=(lt - 3.4) / 0.3)
    return flash(img, lt)


def p_montee(lt, dur):
    img = chez_sarah(lt, "neutre", dict(mouth="grin", arm=0.9), z=push(lt, dur, 1.0, 1.08))
    for i, (txt, col, t0) in enumerate([("SEULE AVEC LES PETITS", YEL, 0.2), ("UN CDI · JAMAIS UN RETARD", GREEN, 1.6)]):
        tag(img, 540, 420 + i * 140, txt, 50, col, INK, rot=(-4, 3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def p_demande(lt, dur):
    img = dim(chez_sarah(lt, "neutre", dict(mouth="flat", phone=True)), 0.8, blur=6, dark=0.6)
    message(img, [("J'ai besoin de l'argent pour la cantine", 0.2)], lt, nom="SARAH → L'EX")
    tag(img, 540, 900, "🎤 MESSAGE VOCAL", 48, YEL, INK, rot=-3, k=(lt - 2.6) / 0.3)
    return img


def p_coup1(lt, dur):
    img = gros_plan_mechant(plage_bg, EX, lt, dur, 1.95, 2.15, arm=0.4, phone=True)
    bubble(img, 540, 560, ["LA CANTINE ?", "T'AS QU'À LEUR FAIRE", "DES SANDWICHS"], 62, lt / 0.25, tail_x=660)
    return flash(img, lt)


def p_geste(lt, dur):
    img = dim(chez_sarah(lt, "triste", dict(mouth="sad", phone=True)), 0.8, blur=6, dark=0.6)
    tag(img, 540, 420, "2 MINUTES APRÈS", 56, RED, WHITE, rot=-3, k=(lt - 0.2) / 0.3)
    return img


def p_coup2(lt, dur):
    img = gros_plan_mechant(plage_bg, EX, lt, dur, 2.2, 2.4, arm=0.8, phone=True)
    bubble(img, 540, 560, ["UNE MÈRE QUI SAIT PAS", "GÉRER UN BUDGET,", "C'EST PAS MON PROBLÈME"], 56, lt / 0.25,
           tail_x=660)
    return shake(flash(img, lt), lt)


def p_silence(lt, dur):
    return chez_sarah(lt, "triste", dict(mouth="sad"), z=push(lt, dur, 1.0, 1.05))


def p_echo(lt, dur):
    img = dim(plan(salon_bg, lt, autres=[(540, SARAH, dict(mouth="sad"), 1.7)], z=2.0, center=(540, 900)), 0.75)
    echo(img, "PAS SON PROBLÈME")
    return img


def p_aripa(lt, dur):
    img = dim(chez_sarah(lt, "telephone", dict(mouth="flat")), 0.9)
    carte_sombre(img, "L'ARIPA", [("Un service de la CAF", 0.4, False), ("Gratuit, sans avocat", 1.4, False),
                                  ("Elle récupère la pension à ta place", 2.6, True)], lt, y0=470,
                 sous="PENSION-ALIMENTAIRE.CAF.FR")
    return img


def p_demarche(lt, dur):
    img = chez_sarah(lt, "neutre", dict(mouth="flat", phone=True), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE JUGEMENT + LA DEMANDE EN LIGNE", 44, YEL, INK, rot=-3, k=(lt - 1.0) / 0.3)
    tag(img, 540, 560, "10 MINUTES", 56, GREEN, INK, rot=2, k=(lt - 2.6) / 0.3)
    return img


def p_asf(lt, dur):
    img = dim(chez_sarah(lt, "neutre", dict(mouth="smile")), 0.85)
    big_number(img, (540, 560), "≈ 200 €", 150, GREEN, "PAR MOIS ET PAR ENFANT, AVANCÉS PAR LA CAF", k=lt / 0.3)
    return img


def p_doute(lt, dur):
    img = chez_sarah(lt, "triste", dict(mouth="sad"), z=push(lt, dur, 1.1, 1.18), center=(640, 1000))
    tag(img, 540, 420, "ET S'IL SE VENGEAIT ?", 54, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def p_patron(lt, dur):
    img = dim(chez_sarah(lt, "neutre", dict(mouth="flat")), 0.85)
    card(img, 540, 760, "ARIPA → SON EMPLOYEUR", "PAIEMENT DIRECT", [("Pension due chaque mois", "", 0.4, False),
                                                                    ("+ les mois impayés", "", 1.1, False),
                                                                    ("Prélevée sur son salaire", "", 1.8, True)], lt, rot=2)
    return img


def p_fiche(lt, dur):
    img = dim(chez_sarah(lt, "victoire", dict(mouth="grin", arm=0.9)), 0.85)
    d = ImageDraw.Draw(img)
    d.rectangle([200, 420, 880, 900], fill=(252, 252, 248), outline=INK, width=6)
    d.text((540, 480), "FICHE DE PAIE", font=FA(54), fill=INK, anchor="mm")
    for k, (lab, val, col) in enumerate([("Salaire", "2 100,00", INK), ("Pension · ARIPA", "− 400,00", RED),
                                         ("Arriérés · ARIPA", "− 200,00", RED)]):
        y = 590 + k * 95
        if lt > 0.4 + k * 0.6:
            d.text((240, y), lab, font=FA(40), fill=INK, anchor="lm")
            d.text((840, y), val, font=FA(40), fill=col, anchor="rm")
    return img


def p_jetski(lt, dur):
    img = plan(plage_bg, lt, autres=[(780, EX, dict(mouth="sad", brows="triste"), 0.6)], z=1.0)
    tag(img, 540, 420, "VENDU", 90, RED, WHITE, rot=-6, k=(lt - 0.3) / 0.2)
    return shake(img, lt - 0.3)


def p_chute(lt, dur):
    img = dim(plan(salon_bg, lt, z=1.0), 0.6)                                         # pas de visage sous le texte
    big_number(img, (540, 470), "2 400 €", 150, GREEN, "SANS AVOCAT", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · ARIPA (CAF) · PENSION FIXÉE PAR UN JUGEMENT", lt)
    return img


PENSION = (Recit("droits_pension", "scripts/modele/18_pension_alimentaire.txt", "output/_work_droits_pension/voice_duo.wav",
                 compteur=dict(label="RÉCUPÉRÉ PAR SARAH", depart=0, montant=2400, phrase="Le mois suivant")),
           [("Tu me réclames", p_hook, ("impact", 1.0)), ("C'est ce que l'ex", p_couture, ("whoosh", 0.6)),
            ("Et pourtant ma sœur", p_montee, ("pop", 0.8)), ("Elle lui écrit", p_demande, ("notif", 0.6)),
            ("La cantine", p_coup1, ("impact", 0.8)), ("Et deux minutes après", p_geste, ("notif", 0.5)),
            ("Une mère qui sait pas", p_coup2, ("impact", 1.0)), ("Elle dit rien", p_silence, None),
            ("Pas son problème", p_echo, ("rate", 0.6)), ("Sauf que pour ma sœur", p_aripa, ("pop", 0.8)),
            ("Mais alors il faut quoi", p_demarche, ("ticks", 0.6)), ("Et pendant que la CAF", p_asf, ("succes", 0.6)),
            ("Honnêtement", p_doute, None), ("Sauf que l'ARIPA", p_patron, ("tampon", 0.8, 1.6)),
            ("Le mois suivant", p_fiche, None), ("Il a vendu", p_jetski, ("impact", 0.8)),
            ("Deux mille quatre cents euros, et", p_chute, ("impact", 0.9))])

if __name__ == "__main__":
    rec, beats = {"casse": CASSE, "pension": PENSION}[sys.argv[1]]
    rec.fabriquer(beats)
