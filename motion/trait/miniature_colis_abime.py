"""Miniature TikTok (1080x1920) du colis de Noël cassé. Zone sûre 3:4 : y de 240 à 1680.

    python3 motion/trait/miniature_colis_abime.py   → output/trait/colis_abime_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_colis as C  # noqa: E402
from accroches_demo import carton_vole  # noqa: E402
from colis_abime import KEVIN, SOEUR, console  # noqa: E402
from dessin import sauver_miniature, H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    C.palier(ctx, t, mot=False, colis=0)
    kev, soeur = Perso(**KEVIN), Perso(**SOEUR)
    kev.pose(0, "leve").emotion(0, "choc")
    kev.objet = lambda c, x, y, s: None
    soeur.pose(0, "pointe_g").emotion(0, "content")
    soeur.objet = lambda c, x, y, s: None
    soeur.draw(ctx, 840, 2000, 0.95, t)
    kev.draw(ctx, 250, 2100, 1.05, t)
    traits_choc(ctx, 250, 2100 - 1.05 * 880, 160, 0.5)
    carton_vole(ctx, 560, 1500, 0.9, 0, 0.35, t)
    console(ctx, 560, 1420, 0.6, fendu=1.0, rot=-0.15)
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

    ligne("COLIS DE NOËL CASSÉ", 380, 88, (255, 210, 40), INK, -0.04)
    ligne("J'AVAIS SIGNÉ LE BON…", 550, 76, (250, 250, 250), INK, 0.02)
    ligne("450 € RÉCUPÉRÉS QUAND MÊME", 700, 54, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/colis_abime_miniature.png"
    sauver_miniature(surf, out)
    print("→", out)


if __name__ == "__main__":
    main()
