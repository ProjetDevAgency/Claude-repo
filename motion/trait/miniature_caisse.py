"""Miniature TikTok (1080x1920) de l'erreur de caisse. Zone sûre 3:4 : y de 240 à 1680.

    python3 motion/trait/miniature_caisse.py   → output/trait/erreur_caisse_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_caisse as K  # noqa: E402
from dessin import sauver_miniature, H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from erreur_caisse import KEVIN, TANTE  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    K.magasin(ctx, t)
    kev, tante = Perso(**KEVIN), Perso(**TANTE)
    kev.pose(0, "leve").emotion(0, "choc")
    kev.objet = lambda c, x, y, s: None
    tante.pose(0, "objet").emotion(0, "malin")
    tante.objet = lambda c, x, y, s: K.fiche_paie(c, x, y - 100, 0.3, rot=0.06)
    tante.draw(ctx, 820, 2000, 0.95, t)
    kev.draw(ctx, 260, 2100, 1.05, t)
    traits_choc(ctx, 260, 2100 - 1.05 * 880, 160, 0.5)
    K.fiche_paie(ctx, 560, 1240, 0.5, rouge=1.0, rot=-0.08)
    vignette(ctx, 0.4)

    def ligne(txt, y, size, fond, col, rot):
        s = texte(txt, size, col, True)
        w, h = s.get_width() + 60, s.get_height() + 30
        ctx.save()
        ctx.translate(540, y)
        ctx.rotate(rot)
        rrect(ctx, -w / 2 + 10, -h / 2 + 12, w, h, 18)
        flat(ctx, (0, 0, 0), 0.4)
        rrect(ctx, -w / 2, -h / 2, w, h, 18)
        ctx.set_source_rgb(*[v / 255 for v in fond])
        ctx.fill_preserve()
        stroke(ctx, 8, INK)
        ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2 + 2)
        ctx.paint()
        ctx.restore()

    ligne("MA TANTE M'A FAIT PAYER", 380, 80, (255, 210, 40), INK, -0.04)
    ligne("L'ERREUR DE SA FILLE", 540, 84, (250, 250, 250), INK, 0.02)
    ligne("RETENUE SUR MA PAIE", 690, 62, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/erreur_caisse_miniature.png"
    sauver_miniature(surf, out)
    print("→", out)


if __name__ == "__main__":
    main()
