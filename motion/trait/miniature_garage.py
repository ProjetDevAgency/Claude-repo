"""Miniature TikTok (1080x1920) du garage qui facture des travaux non demandés. Zone sûre du recadrage 3:4 : y de 240 à 1680.

    python3 motion/trait/miniature_garage.py   → output/trait/garage_travaux_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_garage as G  # noqa: E402
from dessin import H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402
from garage_travaux import GARAGISTE, KEVIN  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    G.atelier(ctx, t, pont=0.55)
    ctx.rectangle(0, 0, W, H)
    flat(ctx, (10, 14, 30), 0.12)
    kev, bp = Perso(**KEVIN), Perso(**GARAGISTE)
    kev.emotion(0, "malin")
    kev.pose(0, "objet")
    kev.objet = lambda c, x, y, s: G.fiche(c, x, y - 90, 0.55, rot=-0.06)
    bp.pose(0, "mains_hanches").emotion(0, "malin")
    bp.draw(ctx, 820, 2060, 0.95, t)
    kev.draw(ctx, 270, 2190, 1.1, t)
    traits_choc(ctx, 270, 2190 - 1.1 * 880, 160, 0.5)
    vignette(ctx, 0.45)

    def ligne(txt, y, size, fond, col, rot):
        s = texte(txt, size, col, True)
        w, h = s.get_width() + 60, s.get_height() + 30
        ctx.save()
        ctx.translate(500, y)
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

    ligne("551 € ÉCONOMISÉS", 380, 110, (255, 210, 40), INK, -0.04)
    ligne("640 € POUR UNE VIDANGE", 560, 70, (250, 250, 250), INK, 0.02)
    ligne("LE GARAGISTE DE MA MÈRE", 700, 60, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/garage_travaux_miniature.png"
    surf.write_to_png(str(out))
    print("→", out)


if __name__ == "__main__":
    main()
