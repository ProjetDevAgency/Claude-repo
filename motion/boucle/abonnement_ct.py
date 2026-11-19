"""Boucle du 19 nov. — 36_abonnement_transport.dial : le parrain patron et la moitié de l'abonnement de bus.
    python3 motion/boucle/abonnement_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import facades  # noqa: E402
from semaine_ct import (BASE, GREEN, INK, RED, SS, V2, W, WHITE, YEL, FA, ImageDraw, _cache, _enseigne,  # noqa: E402
                        recit, room, route_bg, salon_bg)

# ───────────── décor : l'atelier mécanique ─────────────

def atelier_meca_bg():
    def f():
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        d.rectangle([0, 1380 * s, W * s, 1560 * s], fill=(95, 98, 105))            # sol de l'atelier
        d.rectangle([60 * s, 640 * s, 440 * s, 900 * s], fill=(70, 70, 80))         # panneau à outils
        for i in range(6):
            x = 90 + i * 58
            d.rectangle([x * s, 680 * s, (x + 18) * s, 820 * s], fill=(190, 190, 200))
        facades.voiture(d, 700)                                                     # la voiture sur le pont
        _enseigne(d, "GARAGE · MÉCANIQUE", (30, 30, 36), YEL)
        return im
    return _cache("atelier_meca", f)


def tableau_fg(d, t):
    s = SS
    d.rectangle([600 * s, 640 * s, 1010 * s, 1120 * s], fill=(205, 170, 120), outline=INK, width=5 * s)
    d.rectangle([630 * s, 670 * s, 800 * s, 860 * s], fill=WHITE, outline=INK, width=3 * s)      # le planning
    d.text((715 * s, 700 * s), "PLANNING", font=FA(int(26 * s)), fill=INK, anchor="mm")
    for y in range(730, 850, 24):
        d.line([645 * s, y * s, 785 * s, y * s], fill=(150, 150, 160), width=3 * s)
    d.rectangle([820 * s, 680 * s, 990 * s, 960 * s], fill=WHITE, outline=INK, width=3 * s)      # l'article affiché
    d.text((905 * s, 715 * s), "L3261-2", font=FA(int(30 * s)), fill=RED, anchor="mm")
    d.text((905 * s, 790 * s), "50 %", font=FA(int(54 * s)), fill=INK, anchor="mm")
    d.text((905 * s, 860 * s), "DE TON", font=FA(int(26 * s)), fill=INK, anchor="mm")
    d.text((905 * s, 895 * s), "ABONNEMENT", font=FA(int(26 * s)), fill=INK, anchor="mm")


# ───────────── personnages ─────────────

PARRAIN = dict(shirt=(40, 40, 46), pants=(50, 60, 90), hair=(170, 170, 175), glasses=True)   # gris : pas le sosie de Kévin
BLEU = dict(shirt=(60, 90, 150))                                                          # Kévin en bleu de travail
MECANOS = [(x, dict(shirt=(60, 90, 150), pants=(60, 90, 150), hair=h, sc=0.8), dict(mouth="o"), 0.6 * i, BASE - 70)
           for i, (x, h) in enumerate(zip((400, 570, 740, 910), ((30, 25, 20), (150, 90, 40), (90, 90, 95), (60, 40, 30))))]

V = V2(atelier_meca_bg, PARRAIN, BLEU)

ABONNEMENT = (recit("b_abonnement", "36_abonnement_transport", "PAYÉ PAR LE PARRAIN", 540, "Le lundi, il trouve"), [
    ("Tu veux que je te paie", V.hook("h", "MON PARRAIN, MON PATRON", ["90 € DE BUS PAR MOIS ?", "VIENS À PIED, SINON", "VA BOSSER AILLEURS"]), ("impact", 1.0)),
    ("C'est ce que mon parrain", V.scene("couture", "choc", [("1er JOUR DE CDI", YEL, 0.3), ("ABONNEMENT À RENOUVELER VENDREDI", RED, 3.0)], mechant=dict(mouth="grin")), ("whoosh", 0.6)),
    ("Et pourtant j'étais fier", V.scene("montee", "victoire", [("PREMIER BLEU DE TRAVAIL", GREEN, 0.2), ("7 H, LE PREMIER À L'ATELIER", YEL, 1.6)], sans_mechant=True), ("pop", 0.8)),
    ("Une heure de bus", V.scene("trajet", "telephone", [("1 H DE BUS + LE TRAIN", WHITE, 0.2), ("JUSTE LA MOITIÉ, PARRAIN ?", YEL, 2.4)], fond=route_bg, sans_mechant=True), None),
    ("Le bus, c'est pour", V.gp("coup1", ["LE BUS, C'EST POUR", "LES GAMINS ET", "LES RETRAITÉS"]), ("impact", 0.8)),
    ("Et en refermant le capot", V.geste("geste"), ("whoosh", 0.5)),
    ("Je t'ai embauché", V.gp("coup2", ["EMBAUCHÉ POUR TA MÈRE.", "FAIS PAS LE SYNDICALISTE", "DANS MON ATELIER"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien. Je retourne", V.silence("silence"), None),
    ("Les gamins et les retraités", V.echo("echo", "LES GAMINS ET LES RETRAITÉS"), ("rate", 0.6)),
    ("Sauf que la moitié", V.gros_mots("moitie", [("LA MOITIÉ ?", WHITE, 0.3), ("C'EST PAS LUI QUI DÉCIDE", RED, 1.2)], fond=salon_bg), ("pop", 0.6)),
    ("Ce que peu de gens", V.carte("regle", "TRAJET DOMICILE-TRAVAIL", [("L'employeur paie 50 %", 0.6, True), ("de ton abonnement", 1.8, False), ("petit garage ou grosse boîte", 3.8, False)], "CODE DU TRAVAIL · L3261-2", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, il faut quoi", V.fiche("justif", "CE QU'IL FAUT", "POUR LA PRISE EN CHARGE", [("Abonnement à ton nom", "OUI", 1.0, True), ("Tickets à l'unité", "NON", 2.4, False)], fond=salon_bg), ("ticks", 0.5)),
    ("Sur le papier, cinq", V.calcul("calcul", "CE QU'IL TE DOIT", [("PAR MOIS", 45, "45 €", GREEN, 0.3), ("PAR AN", 540, "540 €", GREEN, 0.9)], "SUR UN ABONNEMENT À 90 € PAR MOIS", fond=salon_bg), ("ticks", 0.4)),
    ("Honnêtement", V.doute("doute", "5 ABONNEMENTS, ÇA PÈSE", fond=salon_bg), None),
    ("Le lendemain, j'affiche", V.scene("affiche", "parle", [("AU TABLEAU, SANS LUI EN PARLER", YEL, 0.3)], sans_mechant=True, devant=tableau_fg), ("pop", 0.6)),
    ("Les quatre mécanos", V.scene("temoins", None, [("4 MÉCANOS", WHITE, 0.2)], sans_mechant=True, autres=MECANOS, z=(1.05, 1.1), fx=False), None),
    ("Le lundi, il trouve", V.fiche("bureau", "SUR SON BUREAU", "LUNDI, 8 H", [("Abonnement de Kévin", "", 0.3, False), ("+ ceux des 4 mécanos", "", 1.2, True)], kpose="victoire"), ("succes", 0.8)),
    ("Il paie. Il dit", V.muet("muet", "IL PAIE"), None),
    ("Quatre-vingt-dix euros, et", V.fin("fin", "90 €", "ET LA MOITIÉ POUR TOUT L'ATELIER", "CAS TYPE · CODE DU TRAVAIL L3261-2 ET R3261-1 · SERVICE-PUBLIC.FR"), ("impact", 0.9)),
])

if __name__ == "__main__":
    rec, beats = ABONNEMENT
    rec.fabriquer(beats)
