"""Version « chantier visuel » de 37_anthropic_ouverture : même script, même voix, nouvelle animation.
Ouverture en 4 plans (appli → frère → la table → Kévin choqué), objets du sujet en plein écran, coups de fouet
à chaque coupe, sous-titres plus discrets.
    python3 motion/boucle/anthropic_ouverture_v2_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dynamique as D  # noqa: E402
from anthropic_ouverture_ct import ANTHROPIC, FRERE, PARENTS, V  # noqa: E402
from recit import gros_plan_mechant, plan  # noqa: E402
from semaine_ct import GREEN, RED, recit, salon_bg, table_fg  # noqa: E402


def frere_gp(mots, accent=None):
    def f(lt, dur):
        img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 1.9, 2.05, devant=table_fg, phone=True, mouth="grin", arm=0.5)
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
    (0.95, D.insert_appli(salon_bg, "SON APPLI DE BOURSE", 6000, 12000, t_change=0.2, mots=["6 000 €", "SUR", "ANTHROPIC"], accent="6 000 €")),
    (0.95, frere_gp(["SUR", "ANTHROPIC"])),
    (0.70, table_large(["DOUBLÉ", "CE", "SOIR"], accent="DOUBLÉ")),
    (9.0, D.reaction(salon_bg, mots=["ET", "TOI", "T'AURAS", "RIEN"], accent="RIEN", devant=table_fg)),
    nom="h")

REMPLACE = {
    "Ce soir, mes six mille": (OUVERTURE, ("impact", 0.0)),
    "Sauf que quatre-vingt-trois": (D.insert_etiquette(salon_bg, "PRIX D'INTRO", "83 $", mots=["SURTOUT", "POUR", "LES", "GROS"], accent="GROS"), ("pop", 0.3)),
    "Alors je mets le mien": (D.insert_document(salon_bg, "MON ORDRE · ANT", ["Achat", "Type : cours limité", "Limite :"], "83 $", tampon="EN ATTENTE", t_tampon=1.6, mots=["PAS", "UN", "CENTIME", "DE", "PLUS"]), ("pop", 0.3)),
    "En fin d'après-midi, son": (D.insert_notif(salon_bg, "Bourse", "Ordre exécuté", "ANT · 111,50 $", "17:48", RED, mots=["JE", "LIS", "SA", "NOTIF"], accent="NOTIF"), ("notif", 0.3)),
    "Le soir, elle redescend": (D.sequence(
        (1.7, D.insert_appli(salon_bg, "ANTHROPIC · ANT", 111.5, 101.0, unite="$", t_change=0.3, sous="− 9 % POUR LUI")),
        (9.0, V.calcul("soir_b", "ANTHROPIC · 1er JOUR", [("PRIX D'INTRO", 83, "83 $", GREEN, 0.2), ("SON ACHAT", 111.5, "111,50 $", RED, 0.6), ("LE SOIR", 101, "≈ 101 $", (255, 204, 40), 1.0)], "PRIX D'INTRO : + 22 % · LUI : − 9 %", fond=salon_bg)),
        nom="soir"), ("ticks", 0.3)),
}

rec0, beats0 = ANTHROPIC
REC = recit("b_anthropic_ouverture_v2", "37_anthropic_ouverture", "PERTE DU FRÈRE", 550, "Sur le papier, cinq", dynamique=True)
BEATS = [(cle, *REMPLACE[cle]) if cle in REMPLACE else (cle, fn, son) for cle, fn, son in beats0]

if __name__ == "__main__":
    REC.fabriquer(BEATS)
