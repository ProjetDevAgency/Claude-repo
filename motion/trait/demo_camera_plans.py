"""Démo de la caméra « plans » (style La Ficelle) sur les 22 premières secondes du garage : plans fixes qui poussent
lentement, coupe nette sur un gros plan au mot clé, retour au large.

    python3 motion/trait/demo_camera_plans.py   → output/trait/garage_camera_plans.mp4
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import garage_travaux as G  # noqa: E402
import voix  # noqa: E402
from dessin import ROOT  # noqa: E402


def main():
    work = ROOT / "output/trait/_work_garage"
    _, words = voix.build(G.lignes(), G.VOIX, work, gap=0.2, cible=voix.CIBLE)
    f = G.construire(work)

    def W(li, prefixe, n=0):
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t0"]

    p = f.plans

    def loc(i, t):
        return max(0.0, t - p[i]["t0"] - 0.05)

    LARGE = (540, 1000, 1.0)
    # 0. « J'ai économisé 551 € sur le garagiste de ma mère. »
    p[0]["cam"] = [(0, *LARGE), (loc(0, W(0, "cinq")), 540, 720, 1.45), (loc(0, W(0, "garagiste")), 600, 1150, 1.2)]
    # 1. « Il répare sa voiture depuis vingt ans. Je lui avais laissé ma Clio… 89 €, écrit sur la fiche… »
    p[1]["cam"] = [(0, 540, 1050, 1.0), (loc(1, W(1, "vingt")), 600, 660, 1.9), (loc(1, W(1, "je")), 700, 1000, 1.25),
                   (loc(1, W(1, "quatre")), 760, 600, 1.9)]
    # 2. Le téléphone : « C'est prêt. 640 €. »
    p[2]["cam"] = [(0, 540, 900, 1.0), (loc(2, W(2, "six")), 540, 960, 1.9)]
    # 3. La facture, puis le tampon « NON DEMANDÉ »
    p[3]["cam"] = [(0, 540, 760, 1.05), (loc(3, W(3, "rien")), 560, 900, 1.7)]
    # 4. L'accueil : les 3 clients, puis le garagiste qui rigole
    p[4]["cam"] = [(0, 540, 1150, 1.0), (loc(4, W(4, "trois")), 160, 1100, 1.5), (loc(4, W(4, "il")), 780, 1120, 1.6)]
    f.dur = p[5]["t0"] + 2.5
    print("→", f.render(str(ROOT / "output/trait/garage_camera_plans.mp4")))


if __name__ == "__main__":
    main()
