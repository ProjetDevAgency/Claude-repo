"""Feuilleton du grand frère, épisode 4 — 38_frere_plateforme.dial : la « plateforme » à 20 % garantis.
Style chantier visuel (ce qu'on voit = ce qui est dit).
    python3 motion/boucle/frere_plateforme_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dynamique as D  # noqa: E402
from anthropic_ouverture_ct import FRERE, PARENTS, V  # noqa: E402
from recit import gros_plan_mechant  # noqa: E402
from semaine_ct import GREEN, RED, WHITE, YEL, recit, salon_bg, table_fg  # noqa: E402

NOTE = "CAS TYPE · LISTES NOIRES AMF · PAS UN CONSEIL EN INVESTISSEMENT"
TABLE = D.vapeur_devant(table_fg)


def frere_gp(mots, accent=None):
    def f(lt, dur):
        img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 1.9, 2.05, devant=table_fg, phone=True, mouth="grin",
                                arm=0.45 + 0.3 * abs(math.sin(lt * 3.2)))
        D.titre_choc(img, mots, lt - 0.05, accent=accent)
        return img
    return f


OUVERTURE = D.sequence(
    (1.45, D.visage_chiffre(salon_bg, FRERE, "500 €", "POUR SA PLATEFORME", devant=table_fg, phone=True)),
    (1.2, D.insert_appli(salon_bg, "SA PLATEFORME", 500, 1037, t_change=0.15, sous="+ 20 % / SEMAINE", mots=["SINON", "TU", "FINIS"])),
    (9.0, D.reaction(salon_bg, mots=["TA", "VIE", "SUR", "TON", "LIVRET"], accent="LIVRET", devant=table_fg)),
    nom="h")

CONVERSATION = [("moi", "Bonjour, je veux investir 500 euros", 0.3), ("lui", "Super ! Envoyez vite, l'offre finit à minuit", 1.3),
                ("moi", "Quel est votre numéro d'agrément AMF ?", 2.8)]

BEATS = [
    ("Tu me prêtes cinq cents", OUVERTURE, ("impact", 0.0)),
    ("C'est ce que mon grand", D.sequence(
        (2.6, D.dialogue(salon_bg, FRERE, "triste", mechant=lambda lt: dict(mouth="grin", phone=True, arm=0.55 + 0.15 * math.sin(lt * 2)),
                         autres=PARENTS, devant=TABLE, kx=190, mx=890, pan=((0, 380), (1.2, 380), (2.2, 760)), zoom=((0, 1.15), (2.6, 1.3)),
                         tags=[("DIMANCHE, CHEZ MES PARENTS", YEL, 0.3), ("UNE SEMAINE APRÈS ANTHROPIC", WHITE, 1.4)])),
        (9.0, D.insert_notif(salon_bg, "Plateforme", "Offre spéciale", "Fin ce soir à minuit", "21:14", RED, mots=["FIN", "À", "MINUIT"], accent="MINUIT")),
        nom="couture"), ("whoosh", 0.6)),
    ("Et pourtant je l'aime", D.dialogue(salon_bg, FRERE, "neutre", mx=820, devant=TABLE, pan=((0, 420), (3.5, 640)), zoom=((0, 1.2), (3.5, 1.3)),
                                         mechant=lambda lt: dict(mouth="smile", phone=True, arm=0.3 + 0.1 * math.sin(lt * 2)),
                                         tags=[("LE VÉLO", GREEN, 0.6), ("LA CONDUITE", YEL, 1.4), ("MON 1er SALAIRE", WHITE, 2.4)]), ("pop", 0.6)),
    ("Je lui dis, c'est quoi", D.dialogue(salon_bg, FRERE, "parle", mx=820, devant=TABLE, pan=((0, 360), (1.4, 360), (2.2, 720)), zoom=((0, 1.25),),
                                          mechant=lambda lt: dict(mouth="flat", phone=True, arm=0.3) if lt < 1.6 else dict(D.geste_parle(lt, 0.3, 0.2, 6), phone=True),
                                          tags=[("C'EST QUOI, TA PLATEFORME ?", WHITE, 0.4)]), None),
    ("Un gars sur les réseaux", D.gp_vivant(salon_bg, FRERE, ["UN GARS SUR LES RÉSEAUX.", "20 % PAR SEMAINE, GARANTIS.", "JE ME REFAIS EN UN MOIS"], devant=table_fg, phone=True), ("impact", 0.8)),
    ("Et en me montrant le gars", D.tel_voiture(salon_bg, mots=["IL", "EN", "RAJOUTE"], accent="RAJOUTE"), ("whoosh", 0.4)),
    ("Toi, t'as peur de tout", D.gp_vivant(salon_bg, FRERE, ["T'AS PEUR DE TOUT.", "PAPA ET TOI,", "VOUS AUREZ JAMAIS RIEN"], devant=table_fg, z=(2.2, 2.4), secoue=True, base=0.6), ("impact", 1.0)),
    ("Je dis rien. Je regarde", D.dialogue(salon_bg, FRERE, "triste", mx=820, devant=TABLE, pan=((0, 640), (1.4, 360)), zoom=((0, 1.2), (2.2, 1.4)),
                                           mechant=dict(mouth="grin", phone=True, arm=0.9)), None),
    ("Vingt pour cent garantis", D.echo_vivant(salon_bg, "VINGT POUR CENT GARANTIS", devant=table_fg), ("rate", 0.6)),
    ("Sauf qu'un gain garanti", V.fiche("alerte", "SIGNAUX D'ALERTE", "SELON L'AMF", [("Gain élevé « garanti »", "1", 0.3, True), ("Décision urgente", "2", 1.0, False),
                                                                                    ("Virement à l'étranger", "3", 1.6, False)], fond=salon_bg), ("pop", 0.6)),
    ("Ce que peu de gens", D.liste_noire(salon_bg, mots=["LA", "LISTE", "NOIRE"], accent="NOIRE"), ("pop", 0.6)),
    ("Mais alors, comment on", D.sequence(
        (2.4, D.recherche(salon_bg, "LISTE NOIRE · AMF", "sa plateforme", mots=["ON", "TAPE", "LE", "NOM"])),
        (9.0, D.recherche(salon_bg, "REGISTRE OFFICIEL", "sa plateforme", ["AGRÉMENT", "AUCUN"], RED, t_resultat=0.6, mots=["ET", "SON", "AGRÉMENT"])),
        nom="verifie"), ("ticks", 0.5)),
    ("Je tape le nom", D.liste_noire(salon_bg, trouve="SA PLATEFORME", t_trouve=0.6, mots=["IL", "EST", "DEDANS"], accent="DEDANS"), ("impact", 0.6)),
    ("Alors j'écris au conseiller", D.conversation(salon_bg, "Conseiller Plateforme", CONVERSATION, mots=["JE", "FAIS", "LE", "CLIENT"], accent="CLIENT"), ("notif", 0.3)),
    ("Deux minutes après", D.conversation(salon_bg, "Conseiller Plateforme", [(c, t, -1) for c, t, _ in CONVERSATION] + [("info", "Ce contact vous a bloqué", 0.4)],
                                          mots=["BLOQUÉ"], accent="BLOQUÉ"), ("impact", 0.4)),
    ("Honnêtement", D.dialogue(salon_bg, FRERE, "triste", mx=820, devant=TABLE, pan=((0, 330), (3.0, 430)), zoom=((0, 1.3), (3.0, 1.4)),
                               mechant=dict(mouth="flat", phone=True, arm=0.5), tags=[("ET S'IL APPRENAIT EN PERDANT ?", WHITE, 0.4)]), None),
    ("Sur le papier, son argent", D.insert_document(salon_bg, "VIREMENT", ["Montant : 500 €", "Bénéficiaire : inconnu", "Pays : étranger"], "500 €",
                                                    tampon="PAS ENVOYÉ", t_tampon=1.2, mots=["UN", "COMPTE", "À", "L'ÉTRANGER"], accent="L'ÉTRANGER"), ("pop", 0.4)),
    ("Minuit passe", D.insert_notif(salon_bg, "Plateforme", "Offre spéciale", "Toujours dispo !", "08:12", RED, mots=["TOUJOURS", "LÀ"], accent="LÀ"), ("notif", 0.3)),
    ("Le soir, il revient", D.dialogue(salon_bg, FRERE, "neutre", mx=820, devant=TABLE, pan=((0, 400), (1.6, 700)), zoom=((0, 1.15), (2.2, 1.3)),
                                       mechant=lambda lt: dict(mouth="flat", phone=True, arm=0.9, brows=None)), None),
    ("Cinq cents euros. Et", lambda lt, dur: D.zoom_centre(V.fin("fin", "500 €", "ET C'EST LUI QUI DEMANDE LA LISTE", NOTE)(lt, dur), 1 + 0.03 * lt, 540, 700), ("impact", 0.9)),
]
BEATS[-1][1].__name__ = "fin_vivante"

REC = recit("b_frere_plateforme", "38_frere_plateforme", "GARDÉ PAR KÉVIN", 500, "Deux minutes après", dynamique=True)

if __name__ == "__main__":
    REC.fabriquer(BEATS)
