"""Boucle du 18 nov. — 35_frais_agence.dial : l'agent immobilier et les 1 200 € de frais d'agence.
    python3 motion/boucle/frais_agence_ct.py            (APERCU=planche.png pour la planche de contrôle)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from semaine_ct import (BASE, BLEU, GREEN, GRIS, INK, RED, SS, V2, W, WHITE, YEL, FA, ImageDraw, _cache, _enseigne,  # noqa: E402
                        recit, room, salon_bg)

# ───────────── décor : l'agence immobilière ─────────────

def agence_immo_bg():
    def f():
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        _enseigne(d, "AGENCE IMMOBILIÈRE", (20, 60, 110), WHITE)
        return im
    return _cache("agence_immo", f)


def bureau_fg(d, t):
    s = SS
    d.rectangle([560 * s, 1260 * s, W * s, 1560 * s], fill=(120, 80, 56))
    d.rectangle([560 * s, 1260 * s, W * s, 1285 * s], fill=(150, 105, 75))
    d.rectangle([700 * s, 1215 * s, 860 * s, 1265 * s], fill=WHITE, outline=INK, width=3 * s)       # le bail imprimé
    d.text((780 * s, 1240 * s), "BAIL", font=FA(int(28 * s)), fill=INK, anchor="mm")


# ───────────── personnages ─────────────

AGENT = dict(shirt=(35, 40, 60), pants=(35, 40, 60), hair=(175, 175, 180), tie=True, glasses=True)   # gris + lunettes : pas le sosie de Kévin
MERE = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
MERE_X = [(470, MERE, dict(mouth="flat", sc=0.92), 0.8)]
CANDIDATS = [(x, dict(shirt=c, pants=(40, 40, 60), hair=h, sc=0.8, **({"long_hair": True} if i % 2 else {})), {}, 0.5 * i,
              BASE - 70) for i, (x, c, h) in enumerate(zip((560, 690, 820, 950),
                                                          ((200, 80, 60), (90, 160, 90), (120, 120, 200), (230, 180, 60)),
                                                          ((60, 40, 30), (200, 160, 80), (30, 25, 20), (150, 90, 40))))]

V = V2(agence_immo_bg, AGENT)

FRAIS = (recit("b_frais_agence", "35_frais_agence", "ÉCONOMISÉ", 870, "Ce soir-là, le studio"), [
    ("Tu me paies mille", V.hook("h", "L'AGENT IMMOBILIER", ["TU ME PAIES 1 200 €", "DE FRAIS D'AGENCE, SINON", "L'APPART PART CE SOIR"], devant=bureau_fg), ("impact", 1.0)),
    ("C'est ce que l'agent", V.scene("couture", "choc", [("MON PREMIER STUDIO", YEL, 0.3), ("DEVANT MA MÈRE", WHITE, 1.4)], mechant=dict(mouth="grin"), autres=MERE_X, devant=bureau_fg, mx=820), ("whoosh", 0.6)),
    ("Et pourtant j'étais", V.scene("montee", "victoire", [("1er CDI LUNDI", GREEN, 0.2), ("2 ANS D'APPRENTISSAGE", YEL, 1.6)], fond=salon_bg, sans_mechant=True, autres=[(780, MERE, dict(mouth="smile"), 0.8)]), ("pop", 0.8)),
    ("Je lui dis, c'est presque", V.scene("demande", "parle", [("PRESQUE 2 MOIS DE LOYER ?", WHITE, 0.4)], mechant=dict(mouth="flat"), autres=MERE_X, devant=bureau_fg, mx=820), None),
    ("Vingt-cinq mètres carrés au-dessus", V.gp("coup1", ["25 M² AU-DESSUS", "D'UN KEBAB, ET", "TU NÉGOCIES ?"], devant=bureau_fg), ("impact", 0.8)),
    ("Et en rangeant le bail", V.geste("geste", devant=bureau_fg), ("whoosh", 0.5)),
    ("Un apprenti qui vit", V.gp("coup2", ["UN APPRENTI CHEZ SA", "MÈRE, ÇA SIGNE", "ET ÇA DIT MERCI"], (2.2, 2.4), True, devant=bureau_fg, arm=0.8), ("impact", 1.0)),
    ("Je dis rien. Ma mère", V.silence("silence", devant=bureau_fg, autres=MERE_X), None),
    ("Au-dessus d'un kebab", V.echo("echo", "AU-DESSUS D'UN KEBAB", devant=bureau_fg), ("rate", 0.6)),
    ("Sauf que les frais", V.carte("regle", "FRAIS D'AGENCE", [("Plafonnés au mètre carré", 0.4, True), ("C'est la loi ALUR", 2.2, False)], "LOI DU 6 JUILLET 1989 · ARTICLE 5", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, ça fait combien", V.calcul("calcul", "STUDIO 25 M² · ZONE TENDUE", [("ANNONCÉ", 1200, "1 200 €", RED, 0.6), ("MAXIMUM LÉGAL", 330, "≈ 330 €", GREEN, 2.2)], "10,09 €/M² + 3,03 €/M² D'ÉTAT DES LIEUX", fond=salon_bg), ("ticks", 0.6)),
    ("Ce que peu de gens", V.gros_mots("reste", [("ET LE RESTE ?", WHITE, 0.6), ("C'EST LE PROPRIÉTAIRE", GREEN, 1.8)], fond=salon_bg), ("pop", 0.5)),
    ("Sur le papier", V.scene("dossiers", "neutre", [("6 DOSSIERS DERRIÈRE MOI", YEL, 0.3)], sans_mechant=True, autres=CANDIDATS), None),
    ("Honnêtement", V.doute("doute", "IL LOUE À QUI IL VEUT", fond=salon_bg), None),
    ("Alors je lis le calcul", V.scene("riposte", "telephone", [("À VOIX HAUTE", RED, 0.3), ("DEVANT 6 CANDIDATS", YEL, 1.4)], sans_mechant=True, autres=CANDIDATS), ("impact", 0.6)),
    ("Le couple du fond", V.scene("temoin", None, [("ILS RANGENT LEUR CHÉQUIER", WHITE, 0.2)], sans_mechant=True, autres=CANDIDATS, z=(1.1, 1.15), fx=False), None),
    ("L'agent relit sa fiche", V.muet("muet", "PLU RIEN", devant=bureau_fg), None),
    ("Ce soir-là, le studio", V.scene("twist", "victoire", [("LE STUDIO EST À MOI", GREEN, 0.3), ("POUR ≈ 330 €", YEL, 1.8)], mechant=dict(mouth="flat", arm=0.4), autres=[(130, MERE, dict(mouth="grin", sc=0.9), 0.8)], devant=bureau_fg, mx=820), ("succes", 0.8)),
    ("Merci, et bonne installation", V.gp("merci", ["MERCI, ET BONNE", "INSTALLATION"], (1.9, 2.0), devant=bureau_fg, mouth="smile", brows=None), ("pop", 0.4)),
    ("Mille deux cents euros. Et", V.fin("fin", "1 200 €", "ET C'EST LUI QUI DIT MERCI", "CAS TYPE · LOI DU 6 JUILLET 1989 ART. 5 · PLAFONDS 2026 · SERVICE-PUBLIC.FR"), ("impact", 0.9)),
])

if __name__ == "__main__":
    rec, beats = FRAIS
    rec.fabriquer(beats)
