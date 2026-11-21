"""Miniature TikTok (1080x1920) de la vidéo liste « 5 remboursements ». Zone sûre 3:4 : y de 240 à 1680.

    python3 motion/trait/miniature_liste.py   → output/trait/liste_remboursements_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_liste as L_  # noqa: E402
import decors_ville as V  # noqa: E402
from dessin import H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from liste_remboursements import KEVIN  # noqa: E402
from perso import Perso  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    V.ville_nuit(ctx, t)
    kev = Perso(**KEVIN)
    kev.pose(0, "pointe").emotion(0, "malin")
    kev.objet = lambda c, x, y, s: None
    kev.draw(ctx, 230, 2000, 1.0, t)
    for i, (m, ic, x, y, s) in enumerate([("15 €", "train", 520, 1240, 0.5), ("72 €", "ticket", 700, 1220, 0.55),
                                          ("40 €", "banque", 890, 1240, 0.6), ("290 €", "tel", 600, 1640, 0.72),
                                          ("600 €", "avion", 870, 1660, 0.85)]):
        L_.enveloppe(ctx, x, y, s, m, ic, lueur=1.0 if i == 4 else 0.0, rot=0.05 * (i % 2 * 2 - 1))
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

    ligne("5 REMBOURSEMENTS", 380, 110, (255, 210, 40), INK, -0.04)
    ligne("QUE TU LAISSES FILER", 560, 76, (250, 250, 250), INK, 0.02)
    ligne("LE PLUS GROS : 600 €", 710, 64, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/liste_remboursements_miniature.png"
    surf.write_to_png(str(out))
    print("→", out)


if __name__ == "__main__":
    main()
