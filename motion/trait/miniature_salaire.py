"""Miniature TikTok (1080x1920) du salaire en retard. Zone sûre du recadrage 3:4 : y de 240 à 1680.

    python3 motion/trait/miniature_salaire.py   → output/trait/salaire_retard_miniature.png
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_chantier as K  # noqa: E402
from dessin import H, INK, ROOT, W, flat, rrect, stroke, texte, vignette  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402
from salaire_retard import BEAUPERE, KEVIN  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    K._T[0] = t
    K.exterieur(ctx, t, camion_x=820)
    ctx.rectangle(0, 0, W, H)
    flat(ctx, (10, 14, 30), 0.12)
    kev, bp = Perso(**KEVIN), Perso(**BEAUPERE)
    kev.pose(0, "telephone").emotion(0, "choc")
    kev.objet = lambda c, x, y, s: D.telephone(c, x - 10, y - 60, 0.9, rot=-0.1)
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

    ligne("90 € RÉCUPÉRÉS", 380, 120, (255, 210, 40), INK, -0.04)
    ligne("PAIE EN RETARD", 560, 86, (250, 250, 250), INK, 0.02)
    ligne("MON BEAU-PÈRE PATRON", 700, 64, (232, 52, 60), (255, 255, 255), -0.03)
    out = ROOT / "output/trait/salaire_retard_miniature.png"
    surf.write_to_png(str(out))
    print("→", out)


if __name__ == "__main__":
    main()
