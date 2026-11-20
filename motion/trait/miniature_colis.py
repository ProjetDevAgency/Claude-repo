"""Miniature TikTok (1080x1920) du colis jamais reçu. Zone sûre du recadrage 3:4 de TikTok : y de 240 à 1680.

    python3 motion/trait/miniature_colis.py   → output/trait/colis_perdu_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
from colis_perdu import KEVIN, PERE  # noqa: E402
from dessin import H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    C.palier(ctx, t, mot=False, colis=0)        # le mot serait caché par les titres
    ctx.rectangle(0, 0, W, H)
    flat(ctx, (10, 14, 30), 0.15)
    kev, pere = Perso(**KEVIN), Perso(**PERE)
    kev.pose(0, "telephone").emotion(0, "choc")
    kev.objet = lambda c, x, y, s: D.telephone(c, x - 10, y - 60, 0.9, rot=-0.1)
    pere.pose(0, "telephone").emotion(0, "colere")
    pere.objet = lambda c, x, y, s: D.telephone(c, x - 10, y - 60, 0.9, rot=-0.1)
    pere.draw(ctx, 860, 2060, 0.92, t)
    traits_choc(ctx, 860, 2060 - 0.92 * 880, 145, 0.5, color=(255, 255, 255))
    kev.draw(ctx, 260, 2200, 1.1, t)
    traits_choc(ctx, 260, 2200 - 1.1 * 880, 160, 0.5)
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

    ligne("1 200 €", 380, 160, (255, 210, 40), INK, -0.04)
    ligne("COLIS « LIVRÉ »", 560, 86, (250, 250, 250), INK, 0.02)
    ligne("JAMAIS REÇU", 700, 78, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/colis_perdu_miniature.png"
    surf.write_to_png(str(out))
    print("→", out)


if __name__ == "__main__":
    main()
