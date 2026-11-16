"""Où va ton argent ? — méthode v3 avec geste clivant et doute.
    python3 motion/vie_ct.py couple   → 50/50 ou au prorata (scripts/modele/19_couple_prorata.dial)
    python3 motion/vie_ct.py taxes    → taxes d'aéroport remboursables (scripts/modele/20_taxes_aeroport.dial)
"""
import sys

from anthropic_ct import table
from auto_ecole_ct import bureau_fg
from cartoon import FA, bubble, card, flash, phone_big, room, shake
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, H, Image, ImageDraw, Recit, W, barres, big_number, dim,
                   echo, gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from vol_ct import badge, carte_sombre

LEA = dict(shirt=(240, 200, 80), pants=(50, 50, 70), hair=(60, 40, 30), long_hair=True)
AGENT = dict(shirt=(40, 40, 50), pants=(40, 40, 50), hair=(90, 90, 95), tie=True, sc=0.9)
PERE_LEA = dict(shirt=(110, 120, 140), pants=(50, 50, 60), hair=(170, 170, 170), glasses=True)
MERE_LEA = dict(shirt=(170, 80, 90), pants=(50, 50, 60), hair=(120, 80, 50), long_hair=True)
YANIS = dict(shirt=(230, 90, 40), pants=(40, 50, 90), hair=(25, 20, 15))
FILLE = dict(shirt=(200, 120, 220), pants=(40, 40, 60), hair=(200, 160, 80), long_hair=True)
_bg = {}


# ═════════════ 1. 50/50 ou au prorata ═════════════

def agence(t, kpose="neutre", lea=None, z=1.0, center=(540, 1000)):
    return plan(lambda: room("vide"), t, kpose, kx=240, mechant=lea or dict(mouth="flat"), look=LEA, mx=480,
                autres=[(840, AGENT, dict(mouth="smile"), 2.0, BASE - 40)], devant=lambda d, t: bureau_fg(d), z=z,
                center=center)


def appart(t, kpose="neutre", lea=None, z=1.0, center=(540, 1000)):
    return plan(salon_bg, t, kpose, mechant=lea or dict(mouth="flat"), look=LEA, z=z, center=center)


def parents(t, kpose="neutre", lea=None, pere=None, z=1.0, center=(540, 1000)):
    autres = [(430, PERE_LEA, pere or dict(mouth="flat"), 1.1, BASE - 30), (650, MERE_LEA, dict(mouth="flat"), 2.3, BASE - 30)]
    return plan(salon_bg, t, kpose, kx=190, mechant=lea or dict(mouth="flat"), look=LEA, mx=890, autres=autres,
                devant=table, z=z, center=center)


def k_hook(lt, dur):
    img = gros_plan_mechant(lambda: room("vide"), LEA, lt, dur, arm=0.5, devant=lambda d, t: bureau_fg(d))
    badge(img, 540, 1190, "SA COPINE")
    bubble(img, 540, 570, ["TU GAGNES 2 FOIS MOINS ?", "PAS MON PROBLÈME,", "ON PAIE MOITIÉ-MOITIÉ"], 58,
           (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def k_couture(lt, dur):
    img = agence(lt, "neutre", dict(mouth="grin", arm=0.3), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LA SIGNATURE DU BAIL", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return flash(img, lt)


def k_montee(lt, dur):
    img = appart(lt, "victoire", dict(mouth="grin", arm=0.9), z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "LEUR PREMIER APPART", 56, GREEN, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def k_compte(lt, dur):
    img = appart(lt, "telephone", dict(mouth="grin" if lt > 1.8 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "UN AN PLUS TARD", 56, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    tag(img, 540, 560, "0 € DE CÔTÉ", 56, RED, WHITE, rot=2, k=(lt - 1.0) / 0.3)
    return flash(img, lt)


def k_coup1(lt, dur):
    img = gros_plan_mechant(salon_bg, LEA, lt, dur, 1.95, 2.15, arm=0.4)
    bubble(img, 540, 560, ["T'AVAIS QU'À NÉGOCIER", "TON SALAIRE. MOI, JE PAIE", "MA PART"], 58, lt / 0.25, tail_x=660)
    return flash(img, lt)


def k_geste(lt, dur):
    img = appart(lt, "triste", dict(mouth="grin", phone=True), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "ELLE EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def k_coup2(lt, dur):
    img = gros_plan_mechant(salon_bg, LEA, lt, dur, 2.2, 2.4, arm=0.8)
    bubble(img, 540, 560, ["UN HOMME QUI COMPTE", "SES CENTIMES,", "C'EST PAS SEXY"], 62, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def k_silence(lt, dur):
    return appart(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def k_echo(lt, dur):
    img = dim(gros_plan_kevin(salon_bg, lt, dur), 0.75)
    echo(img, "C'EST PAS SEXY")
    return img


def k_calcul(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    barres(img, "MOITIÉ-MOITIÉ", [("KÉVIN", 600, "600 €", (230, 80, 80), 1.6), ("LÉA", 2100, "2 100 €", (60, 200, 110), 2.4)],
           lt, sous="CE QUI RESTE CHAQUE MOIS · 1 800 € DE DÉPENSES")
    return img


def k_prorata(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    barres(img, "SELON CE QU'ON GAGNE", [("KÉVIN", 900, "900 €", (60, 200, 110), 2.4),
                                         ("LÉA", 1800, "1 800 €", (60, 200, 110), 3.2)],
           lt, sous="ELLE GAGNE 2 FOIS PLUS · ELLE MET 2 FOIS PLUS")
    return img


def k_total(lt, dur):
    img = dim(plan(salon_bg, lt, "neutre", kx=540), 0.85)
    big_number(img, (540, 560), "+300 € / MOIS", 110, GREEN, "3 600 € PAR AN POUR KÉVIN", k=lt / 0.3)
    return img


def k_dimanche(lt, dur):
    img = parents(lt, "parle", dict(mouth="o", brows="haut"))
    d = ImageDraw.Draw(img)
    k = min(1.0, lt / 0.4)
    if k > 0:
        d.rectangle([380, 1150, 600, 1260], fill=WHITE, outline=INK, width=4)
        for j in range(4):
            d.line([(400, 1175 + j * 22), (580, 1175 + j * 22)], fill=(150, 150, 160), width=4)
    tag(img, 540, 420, "DIMANCHE, CHEZ SES PARENTS", 50, YEL, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def k_doute(lt, dur):
    img = parents(lt, "triste", dict(mouth="sad", brows="colere"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "DEVANT SA FAMILLE…", 54, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def k_pere(lt, dur):
    img = parents(lt, "neutre", dict(mouth="o"), dict(mouth="flat", arm=0.3), z=push(lt, dur, 1.1, 1.25), center=(540, 950))
    tag(img, 540, 420, "SON PÈRE LIT LE TABLEAU", 52, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return img


def k_tranche(lt, dur):
    img = parents(lt, "victoire", dict(mouth="o", brows="triste"), dict(mouth="grin", arm=0.6), z=1.0)
    tag(img, 540, 420, "« ON FAIT COMME ÇA DEPUIS 30 ANS »", 44, GREEN, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return flash(img, lt)


def k_chute(lt, dur):
    img = dim(plan(salon_bg, lt, devant=table, z=1.1, center=(540, 1150)), 0.6)
    big_number(img, (540, 470), "3 600 €", 150, GREEN, "PAR AN, ET C'EST SON PÈRE QUI A TRANCHÉ", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · AUCUNE RÈGLE LÉGALE : UN CHOIX DE COUPLE", lt)
    return img


COUPLE = (Recit("droits_couple", "scripts/modele/19_couple_prorata.txt", "output/_work_droits_couple/voice_duo.wav",
                compteur=dict(label="EN PLUS POUR KÉVIN / AN", depart=0, montant=3600, phrase="Trois cents euros de plus")),
          [("Tu gagnes deux fois", k_hook, ("impact", 1.0)), ("C'est ce que ma copine", k_couture, ("whoosh", 0.6)),
           ("Et pourtant j'étais heureux", k_montee, ("pop", 0.8)), ("Un an plus tard", k_compte, ("rate", 0.5)),
           ("T'avais qu'à négocier", k_coup1, ("impact", 0.8)), ("Et en refermant", k_geste, ("whoosh", 0.5)),
           ("Un homme qui compte", k_coup2, ("impact", 1.0)), ("Je dis rien", k_silence, None),
           ("C'est pas sexy", k_echo, ("rate", 0.6)), ("Le soir, je fais", k_calcul, ("ticks", 0.6)),
           ("Mais alors c'est quoi", k_prorata, ("ticks", 0.6)), ("Trois cents euros de plus", k_total, None),
           ("Dimanche, chez ses parents", k_dimanche, ("whoosh", 0.7)), ("Honnêtement", k_doute, None),
           ("Son père met ses lunettes", k_pere, None), ("Et il lui fait", k_tranche, ("succes", 0.8)),
           ("Trois mille six cents euros, et", k_chute, ("impact", 0.9))])


# ═════════════ 2. les taxes d'aéroport ═════════════

def aeroport_bg():
    if "a" not in _bg:
        s = SS
        im = Image.new("RGB", (W * s, H * s), (215, 225, 235))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 300 * s, W * s, 1100 * s], fill=(150, 200, 240))             # baie vitrée
        for x in range(0, W, 180):
            d.rectangle([x * s, 300 * s, (x + 12) * s, 1100 * s], fill=(90, 100, 120))
        d.polygon([(200 * s, 760 * s), (880 * s, 700 * s), (900 * s, 730 * s), (220 * s, 800 * s)], fill=WHITE)  # avion
        d.polygon([(500 * s, 740 * s), (640 * s, 600 * s), (680 * s, 610 * s), (590 * s, 760 * s)], fill=WHITE)
        d.rectangle([0, 1500 * s, W * s, H * s], fill=(180, 180, 190))
        d.rounded_rectangle([480 * s, 150 * s, 1040 * s, 280 * s], radius=14 * s, fill=(20, 22, 30))
        d.text((510 * s, 215 * s), "BARCELONE · ANNULÉ", font=FA(44 * s), fill=(255, 200, 60), anchor="lm")
        _bg["a"] = im
    return _bg["a"]


def chez_kevin(t, kpose="telephone", z=1.0, center=(540, 1000)):
    return plan(salon_bg, t, kpose, kx=540, z=z, center=center)


def a_hook(lt, dur):
    img = gros_plan_mechant(salon_bg, YANIS, lt, dur, arm=0.5, phone=True)
    badge(img, 540, 1190, "SON MEILLEUR POTE")
    bubble(img, 540, 570, ["380 € NON REMBOURSABLES ?", "T'AVAIS QU'À PRENDRE", "L'OPTION, RADIN"], 58, (lt + 0.3) / 0.3,
           tail_x=660)
    return shake(img, lt)


def a_couture(lt, dur):
    img = dim(chez_kevin(lt, "choc"), 0.85, blur=6, dark=0.6)
    phone_big(img, 540, 900, lt, "21:47", [("Yanis", "Yanis", "Je viens plus, désolé", (230, 120, 40))])
    tag(img, 540, 420, "LA VEILLE DU DÉPART", 56, RED, WHITE, rot=-3, k=(lt - 0.3) / 0.3)
    return img


def a_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=360, autres=[(720, YANIS, dict(mouth="grin", arm=0.9), 1.2)],
               z=push(lt, dur, 1.0, 1.08))
    for i, (txt, col, t0) in enumerate([("LE MATCH AU CAMP NOU", YEL, 0.3), ("15 ANS D'AMITIÉ", GREEN, 1.8)]):
        tag(img, 540, 420 + i * 140, txt, 54, col, INK, rot=(-4, 3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def a_demande(lt, dur):
    img = chez_kevin(lt, "telephone", z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "TU ME REMBOURSES TON BILLET ?", 48, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def a_coup1(lt, dur):
    img = gros_plan_mechant(salon_bg, YANIS, lt, dur, 1.95, 2.15, arm=0.4, phone=True)
    bubble(img, 540, 560, ["TE REMBOURSER QUOI ?", "C'EST LA COMPAGNIE", "QUI GARDE L'ARGENT"], 60, lt / 0.25, tail_x=660)
    return flash(img, lt)


def a_geste(lt, dur):
    img = chez_kevin(lt, "triste", z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def a_coup2(lt, dur):
    img = gros_plan_mechant(salon_bg, YANIS, lt, dur, 2.2, 2.4, arm=0.8, phone=True)
    bubble(img, 540, 560, ["TOI DE TOUTE FAÇON,", "T'AS JAMAIS SU", "PROFITER DE LA VIE"], 62, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def a_silence(lt, dur):
    img = dim(chez_kevin(lt, "triste"), 0.85, blur=6, dark=0.6)
    phone_big(img, 540, 900, 1.0, "21:52", [("Vueling", "Embarquement", "BCN · Kévin", (60, 120, 220)),
                                            ("Vueling", "Embarquement", "BCN · Yanis", (60, 120, 220))])
    return img


def a_echo(lt, dur):
    img = dim(gros_plan_kevin(salon_bg, lt, dur), 0.75)
    echo(img, "JAMAIS SU PROFITER")
    return img


def a_regle(lt, dur):
    img = dim(plan(aeroport_bg, lt, "neutre", kx=540), 0.9)
    carte_sombre(img, "BILLET NON REMBOURSABLE ?", [("Tu n'as pas embarqué", 0.4, False),
                                                    ("Les taxes d'aéroport", 1.6, False),
                                                    ("= remboursables, par la loi", 2.8, True)], lt, y0=470,
                 sous="CODE DE LA CONSOMMATION · L224-66")
    return img


def a_comment(lt, dur):
    img = dim(chez_kevin(lt, "telephone"), 0.85)
    card(img, 540, 760, "DEMANDE DE REMBOURSEMENT", "TAXES ET REDEVANCES", [("Formulaire en ligne", "", 0.3, False),
                                                                             ("Gratuit", "", 1.0, False),
                                                                             ("Payé sous 30 jours", "", 1.7, True)], lt, rot=2)
    return img


def a_deux(lt, dur):
    img = dim(chez_kevin(lt, "telephone"), 0.85)
    for i, (txt, col, t0) in enumerate([("BILLET DE KÉVIN : OK", GREEN, 0.3), ("BILLET DE YANIS : OK", YEL, 1.6)]):
        tag(img, 540, 520 + i * 160, txt, 60, col, INK, rot=(-3, 2)[i], k=(lt - t0) / 0.3)
    return img


def a_virement(lt, dur):
    img = chez_kevin(lt, "victoire")
    phone_big(img, 540, 920, lt, "10:12", [("Banque", "Virement reçu", "VUELING · +110,00 €", (60, 110, 230))])
    return flash(img, lt)


def a_doute(lt, dur):
    img = chez_kevin(lt, "triste", z=push(lt, dur, 1.1, 1.18))
    tag(img, 540, 420, "15 ANS D'AMITIÉ, POUR 55 € ?", 50, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def a_twist(lt, dur):
    img = dim(chez_kevin(lt, "neutre"), 0.85, blur=6, dark=0.6)
    phone_big(img, 540, 900, lt, "23:04", [("Yanis", "Yanis", "Elle m'a quitté…", (230, 120, 40)),
                                           ("Yanis", "Yanis", "Ils sont encore bons ?", (230, 120, 40))])
    return img


def a_chute(lt, dur):
    img = dim(plan(aeroport_bg, lt, z=1.0), 0.6)
    big_number(img, (540, 470), "110 €", 150, GREEN, "ET C'EST LUI QUI EST RESTÉ À QUAI", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CODE DE LA CONSOMMATION L224-66 · MONTANTS INDICATIFS", lt)
    return img


TAXES = (Recit("droits_taxes", "scripts/modele/20_taxes_aeroport.txt", "output/_work_droits_taxes/voice_duo.wav",
               compteur=dict(label="RÉCUPÉRÉ PAR KÉVIN", depart=0, montant=110, phrase="Trois semaines plus tard")),
         [("Trois cent quatre-vingts", a_hook, ("impact", 1.0)), ("C'est ce que mon meilleur", a_couture, ("notif", 0.7)),
          ("Et pourtant j'avais", a_montee, ("pop", 0.8)), ("Je lui demande juste", a_demande, None),
          ("Te rembourser quoi", a_coup1, ("impact", 0.8)), ("Et en raccrochant", a_geste, ("whoosh", 0.5)),
          ("Toi de toute façon", a_coup2, ("impact", 1.0)), ("Je dis rien", a_silence, None),
          ("Jamais su profiter", a_echo, ("rate", 0.6)), ("Sauf que ce que presque", a_regle, ("pop", 0.8)),
          ("Mais alors comment", a_comment, ("ticks", 0.6)), ("Je fais la demande", a_deux, ("pop", 0.7)),
          ("Trois semaines plus tard", a_virement, None), ("Honnêtement", a_doute, None),
          ("Le soir même", a_twist, ("notif", 0.8)), ("Cent dix euros, et", a_chute, ("impact", 0.9))])

if __name__ == "__main__":
    rec, beats = {"couple": COUPLE, "taxes": TAXES}[sys.argv[1]]
    rec.fabriquer(beats)
