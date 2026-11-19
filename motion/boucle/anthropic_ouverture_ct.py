"""19 nov. — 37_anthropic_ouverture.dial : le grand frère achète Anthropic « au marché » à l'ouverture (111,50 $).
    python3 motion/boucle/anthropic_ouverture_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from semaine_ct import GREEN, RED, V2, WHITE, YEL, recit, salon_bg, table_fg  # noqa: E402

# Le même grand frère que dans les vidéos 14 et 21 (capuche noire, cheveux bruns) : pas le sosie de Kévin.
FRERE = dict(shirt=(40, 40, 50), pants=(50, 50, 60), hair=(25, 20, 15), hood=(30, 30, 38))
MERE = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
PERE = dict(shirt=(70, 110, 160), pants=(50, 50, 60), hair=(150, 150, 150), glasses=True)
PARENTS = [(460, PERE, dict(mouth="flat", sc=0.92), 1.1), (675, MERE, dict(mouth="flat", sc=0.92), 2.3)]
PARENTS_CHOC = [(460, PERE, dict(mouth="o", sc=0.92), 1.1), (675, MERE, dict(mouth="o", sc=0.92), 2.3)]

V = V2(salon_bg, FRERE)
NOTE = "CAS TYPE · COURS DU 19/11/2026 (CNN, BLOOMBERG) · AMF · PAS UN CONSEIL EN INVESTISSEMENT"

ANTHROPIC = (recit("b_anthropic_ouverture", "37_anthropic_ouverture", "PERTE DU FRÈRE", 1000, "Plus tard, l'action"), [
    ("Ce soir, mes six mille", V.hook("h", "SON GRAND FRÈRE", ["MES 6 000 € SUR ANTHROPIC", "AURONT DOUBLÉ CE SOIR,", "ET TOI T'AURAS RIEN"], devant=table_fg, phone=True), ("impact", 1.0)),
    ("C'est ce que mon grand", V.scene("couture", "choc", [("JEUDI MIDI, CHEZ MES PARENTS", YEL, 0.3), ("SON APPLI DE BOURSE OUVERTE", WHITE, 2.4)], mechant=dict(mouth="grin", phone=True), autres=PARENTS, devant=table_fg, kx=190, mx=890), ("whoosh", 0.6)),
    ("Et pourtant, j'avais préparé", V.scene("montee", "victoire", [("2 ANS DE LIVRET", GREEN, 0.2), ("ET L'ENVIE D'ESSAYER", YEL, 1.6)], sans_mechant=True), ("pop", 0.8)),
    ("Je lui dis, tu l'as", V.scene("demande", "parle", [("TU L'AS PAYÉE COMBIEN ?", WHITE, 0.4)], mechant=dict(mouth="flat", phone=True), devant=table_fg, mx=820), None),
    ("Les livrets, c'est pour", V.gp("coup1", ["LES LIVRETS, C'EST POUR", "LES TROUILLARDS. MOI, 83 $", "COMME LES PROS"], devant=table_fg), ("impact", 0.8)),
    ("Et en se resservant", V.geste("geste", devant=table_fg), ("whoosh", 0.5)),
    ("Toi, ton livret", V.gp("coup2", ["TON LIVRET, IL VA DORMIR", "TOUTE TA VIE.", "COMME PAPA"], (2.2, 2.4), True, devant=table_fg, arm=0.8), ("impact", 1.0)),
    ("Je dis rien. Je finis", V.silence("silence", devant=table_fg), None),
    ("Comme les pros", V.echo("echo", "COMME LES PROS", devant=table_fg), ("rate", 0.6)),
    ("Sauf que quatre-vingt-trois", V.gros_mots("intro", [("83 $ = LE PRIX D'INTRO", WHITE, 0.3), ("SURTOUT POUR LES GROS", YEL, 2.2)], fond=salon_bg), ("pop", 0.6)),
    ("Ce que peu de gens", V.carte("marche", "ORDRE AU MARCHÉ", [("Achète au 1er prix venu", 0.6, True), ("peu importe lequel", 2.6, False)], "AMF · CHOISIR ET PASSER UN ORDRE DE BOURSE", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, comment", V.fiche("limite", "ORDRE À COURS LIMITÉ", "TU FIXES TON PRIX MAX", [("Prix sous ta limite", "ACHAT", 1.6, True), ("Prix au-dessus", "RIEN", 2.8, False)], fond=salon_bg), ("ticks", 0.5)),
    ("Alors je mets le mien", V.gros_mots("mien", [("MOI : LIMITE À 83 $", GREEN, 0.3), ("PAS UN CENTIME DE PLUS", YEL, 1.6)], fond=salon_bg), ("pop", 0.6)),
    ("Dans l'après-midi, son", V.tel("notif", "17:48", [("Bourse", "Ordre exécuté", "ANT · 111,50 $", RED)], "parle", tags=[("JE LIS SA NOTIF", RED, 2.0), ("DEVANT MES PARENTS", YEL, 3.0)]), ("notif", 0.4)),
    ("Ordre exécuté. Cent onze", V.scene("execute", "neutre", [("ORDRE EXÉCUTÉ", RED, 0.1), ("111,50 $", WHITE, 0.9)], mechant=dict(mouth="o", phone=True), autres=PARENTS_CHOC, devant=table_fg, kx=190, mx=890), ("impact", 0.5)),
    ("Trente-quatre pour cent", V.gros_mots("plus34", [("+ 34 %", RED, 0.2), ("AU-DESSUS DU PRIX DES PROS", WHITE, 0.9)], fond=salon_bg), ("pop", 0.4)),
    ("Plus tard, l'action", V.calcul("chute", "ANTHROPIC · 1er JOUR", [("OUVERTURE", 111.5, "111,50 $", YEL, 0.3), ("PLUS BAS", 92.72, "92,72 $", RED, 1.4)], "SUR 6 000 € : ≈ − 1 000 € SUR LE PAPIER", fond=salon_bg), ("ticks", 0.5)),
    ("Honnêtement", V.doute("doute", "SUR 10 ANS, IL A PEUT-ÊTRE RAISON", fond=salon_bg), None),
    ("Mon ordre à moi", V.scene("pas_passe", "victoire", [("MON ORDRE À 83 $", GREEN, 0.2), ("TOUJOURS PAS PASSÉ", YEL, 1.0)], mechant=dict(mouth="flat", brows=None), devant=table_fg, mx=820), ("succes", 0.6)),
    ("Six mille euros pour", V.fin("fin", "6 000 €", "ET MON LIVRET DORT TRANQUILLE", NOTE), ("impact", 0.9)),
])

if __name__ == "__main__":
    rec, beats = ANTHROPIC
    rec.fabriquer(beats)
