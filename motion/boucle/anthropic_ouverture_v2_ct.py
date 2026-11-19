"""Version « chantier visuel » de 37_anthropic_ouverture : même script, même voix, nouvelle animation.
Ouverture en 4 plans (appli → frère → la table → Kévin choqué), objets du sujet en plein écran, coups de fouet
à chaque coupe, sous-titres plus discrets.
    python3 motion/boucle/anthropic_ouverture_v2_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dynamique as D  # noqa: E402
from anthropic_ouverture_ct import ANTHROPIC, FRERE, PARENTS, V  # noqa: E402
from recit import gros_plan_mechant, plan  # noqa: E402
from semaine_ct import GREEN, RED, WHITE, YEL, recit, salon_bg, table_fg  # noqa: E402
from anthropic_ouverture_ct import PARENTS_CHOC  # noqa: E402


def frere_gp(mots, accent=None):
    def f(lt, dur):
        img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 1.9, 2.05, devant=table_fg, phone=True, mouth="grin",
                                arm=0.45 + 0.3 * abs(math.sin(lt * 3.2)))
        D.titre_choc(img, mots, lt - 0.05, accent=accent)
        return img
    return f


def table_large(mots, accent=None):
    def f(lt, dur):
        img = plan(salon_bg, lt, "triste", kx=190, mechant=dict(mouth="grin", phone=True, arm=0.6), look=FRERE, mx=890,
                   autres=PARENTS, devant=table_fg, z=1.0 + 0.08 * lt, center=(540, 1000))
        D.titre_choc(img, mots, lt - 0.05, accent=accent)
        return img
    return f


OUVERTURE = D.sequence(
    (1.45, D.graphique(salon_bg, [6000, 6900, 8100, 9800, 12000], t_trace=1.3, titre="SES 6 000 € · ANT", unite="€", mots=["6 000 €", "SUR", "ANTHROPIC"], accent="6 000 €")),
    (1.15, frere_gp(["DOUBLÉ", "CE", "SOIR"], accent="DOUBLÉ")),
    (9.0, D.reaction(salon_bg, mots=["ET", "TOI", "T'AURAS", "RIEN"], accent="RIEN", devant=table_fg)),
    nom="h")

SEANCE = [111.5, 106, 99, 101.2, 97, 95, 92.72, 94, 96.5, 95.5, 97.17]     # repères réels : ouverture, plus bas, clôture
REPERES = [(0, "OUVERTURE"), (6, "PLUS BAS 92,72"), (10, "CLÔTURE")]


def couture_vapeur(lt, dur):
    img = V.scene("couture_v", "choc", [("JEUDI MIDI, CHEZ MES PARENTS", YEL, 0.3), ("SON APPLI DE BOURSE OUVERTE", WHITE, 2.4)],
                  mechant=dict(mouth="grin", phone=True), autres=PARENTS, devant=table_fg, kx=190, mx=890)(lt, dur)
    return D.vapeur(img, lt, 575, 1350)


def papier(lt, dur):
    img = V.gros_mots("papier_b", [("SUR SES 6 000 €", WHITE, 0.2), ("≈ − 770 € POUR LUI", RED, 0.9)], fond=salon_bg)(lt, dur)
    return D.billets_envoles(img, lt, 540, 1550, n=7, t0=0.3)


TABLE = D.vapeur_devant(table_fg)
TAGS_COUTURE = [("JEUDI MIDI, CHEZ MES PARENTS", YEL, 0.3), ("SON APPLI DE BOURSE OUVERTE", WHITE, 2.4)]

VIVANT = {
    "C'est ce que mon grand": (D.dialogue(salon_bg, FRERE, "triste", mechant=lambda lt: dict(mouth="grin", phone=True, arm=0.55 + 0.15 * math.sin(lt * 2)),
                                          autres=PARENTS, devant=TABLE, kx=190, mx=890, pan=((0, 380), (1.8, 380), (2.8, 760)),
                                          zoom=((0, 1.15), (3.0, 1.3)), tags=TAGS_COUTURE), ("whoosh", 0.6)),
    "Je lui dis, tu l'as": (D.dialogue(salon_bg, FRERE, "parle", mx=820, devant=TABLE, pan=((0, 360), (1.6, 360), (2.4, 720)), zoom=((0, 1.25),),
                                       mechant=lambda lt: dict(mouth="flat", phone=True, arm=0.3) if lt < 1.8 else dict(D.geste_parle(lt, 0.3, 0.2, 6), phone=True),
                                       tags=[("TU L'AS PAYÉE COMBIEN ?", WHITE, 0.4)]), None),
    "Les livrets, c'est pour": (D.gp_vivant(salon_bg, FRERE, ["LES LIVRETS, C'EST POUR", "LES TROUILLARDS. MOI, 83 $", "COMME LES PROS"], devant=table_fg, phone=True), ("impact", 0.8)),
    "Et en se resservant": (D.dialogue(salon_bg, FRERE, "triste", mx=820, devant=TABLE, pan=((0, 700),), zoom=((0, 1.3), (2.5, 1.45)),
                                       mechant=lambda lt: dict(mouth="grin", arm=0.3 + 0.5 * abs(math.sin(lt * 2.5))),
                                       tags=[("IL EN RAJOUTE", RED, 0.4)]), ("whoosh", 0.5)),
    "Je dis rien. Je finis": (D.dialogue(salon_bg, FRERE, "triste", mx=820, devant=TABLE, pan=((0, 640), (1.4, 360)), zoom=((0, 1.2), (2.2, 1.4)),
                                         mechant=dict(mouth="grin", phone=True, arm=0.5), kextra=lambda lt: dict(arm=0.12 + 0.12 * abs(math.sin(lt * 3)))), None),
    "Comme les pros": (D.echo_vivant(salon_bg, "COMME LES PROS", devant=table_fg), ("rate", 0.6)),
    "Ordre exécuté. Cent onze": (D.dialogue(salon_bg, FRERE, "neutre", kx=190, mx=890, devant=TABLE, pan=((0, 450), (1.2, 820)), zoom=((0, 1.15), (1.5, 1.3)),
                                            autres=PARENTS_CHOC, mechant=dict(mouth="o", phone=True, arm=0.9),
                                            tags=[("ORDRE EXÉCUTÉ", RED, 0.1), ("111,50 $", WHITE, 0.9)]), ("impact", 0.5)),
    "Honnêtement": (D.dialogue(salon_bg, FRERE, "triste", mx=820, devant=TABLE, pan=((0, 330), (3.0, 430)), zoom=((0, 1.3), (3.0, 1.4)),
                               mechant=dict(mouth="grin", phone=True, arm=0.5), tags=[("SUR 10 ANS, IL A PEUT-ÊTRE RAISON", WHITE, 0.4)]), None),
}

REMPLACE = {
    "Et pourtant, j'avais préparé": (D.livret(salon_bg, "MON LIVRET", [("2024", "+ 150 € / mois"), ("2025", "+ 150 € / mois"), ("Intérêts", "+ 120 €")], "4 000 €", mots=["2", "ANS", "DE", "LIVRET"], accent="LIVRET"), ("pop", 0.8)),
    "Toi, ton livret": (D.sequence((1.9, D.gp_vivant(salon_bg, FRERE, ["TON LIVRET, IL VA DORMIR", "TOUTE TA VIE.", "COMME PAPA"], devant=table_fg, z=(2.2, 2.4), secoue=True, base=0.6)),
                                   (9.0, D.livret(salon_bg, "TON LIVRET", [], "4 000 €", dort=True, mots=["COMME", "PAPA"], t_ligne=0.0)), nom="coup2"), ("impact", 1.0)),
    "Ce que peu de gens": (D.sequence((2.3, V.carte("marche_a", "ORDRE AU MARCHÉ", [("Achète au 1er prix venu", 0.5, True)], "AMF · CHOISIR ET PASSER UN ORDRE DE BOURSE", fond=salon_bg)),
                                      (9.0, D.defile_prix(salon_bg, [98.0, 104.2, 107.9, 111.5], mots=["PEU", "IMPORTE", "LEQUEL"])), nom="marche"), ("pop", 0.8)),
    "Mais alors, comment": (D.sequence((2.4, V.fiche("limite_a", "ORDRE À COURS LIMITÉ", "TU FIXES TON PRIX MAX", [("Prix sous ta limite", "ACHAT", 0.8, True)], fond=salon_bg)),
                                       (9.0, D.graphique(salon_bg, [104.0, 99.5, 102.0, 97.0, 100.5], t_trace=1.2, titre="ANT", limite=90.0, limite_txt="TA LIMITE", mots=["AU-DESSUS", "RIEN", "PASSE"], accent="RIEN")), nom="limite"), ("ticks", 0.5)),
    "Sur le papier, sept": (papier, ("pop", 0.4)),
    "Mon ordre à moi": (D.graphique(salon_bg, SEANCE, t_trace=0.9, titre="ANT · 19 NOV.", reperes=[(6, "PLUS BAS 92,72")], limite=83.0, limite_txt="MON ORDRE · 83 $", mots=["TOUJOURS", "PAS", "PASSÉ"], accent="PASSÉ"), ("succes", 0.6)),
    "Ce soir, mes six mille": (OUVERTURE, ("impact", 0.0)),
    "Sauf que quatre-vingt-trois": (D.insert_etiquette(salon_bg, "PRIX D'INTRO", "83 $", mots=["SURTOUT", "POUR", "LES", "GROS"], accent="GROS"), ("pop", 0.3)),
    "Alors je mets le mien": (D.insert_document(salon_bg, "MON ORDRE · ANT", ["Achat", "Type : cours limité", "Limite :"], "83 $", tampon="EN ATTENTE", t_tampon=1.6, mots=["PAS", "UN", "CENTIME", "DE", "PLUS"]), ("pop", 0.3)),
    "En fin d'après-midi, son": (D.insert_notif(salon_bg, "Bourse", "Ordre exécuté", "ANT · 111,50 $", "17:48", RED, mots=["JE", "LIS", "SA", "NOTIF"], accent="NOTIF"), ("notif", 0.3)),
    "À la clôture, elle finit": (D.sequence(
        (2.6, D.graphique(salon_bg, SEANCE, t_trace=2.2, titre="ANT · 19 NOV.", reperes=REPERES, depart=111.5)),
        (9.0, V.calcul("soir_b", "ANTHROPIC · 1er JOUR", [("PRIX D'INTRO", 83, "83 $", GREEN, 0.2), ("SON ACHAT", 111.5, "111,50 $", RED, 0.6), ("CLÔTURE", 97.17, "97,17 $", (255, 204, 40), 1.0)], "PRIX D'INTRO : + 17 % · LUI : − 13 %", fond=salon_bg)),
        nom="soir"), ("ticks", 0.3)),
}

rec0, beats0 = ANTHROPIC
REC = recit("b_anthropic_ouverture_v2", "37_anthropic_ouverture", "PERTE DU FRÈRE", 770, "Sur le papier, sept", dynamique=True)
REMPLACE.update(VIVANT)
BEATS = [(cle, *REMPLACE[cle]) if cle in REMPLACE else (cle, fn, son) for cle, fn, son in beats0]

if __name__ == "__main__":
    REC.fabriquer(BEATS)
