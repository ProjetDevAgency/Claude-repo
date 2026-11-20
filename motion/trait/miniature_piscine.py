"""Miniature TikTok (1080x1920) de l'histoire du pisciniste, dessinée avec le moteur « trait ».

    python3 motion/trait/miniature_piscine.py   → output/trait/piscine_dauphin_miniature.png

Le texte reste dans la zone sûre : TikTok recouvre le bas (description) et la droite (boutons).
"""
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_piscine as P  # noqa: E402
from dessin import H, INK, ROOT, W, ecrit, flat, halo, rrect, stroke, texte, vignette  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402
from piscine_dauphin import DAME, FILS  # noqa: E402


def main():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.3
    # décor : la piscine vide, le dauphin qui brille sous les feuilles
    ctx.save()
    ctx.translate(540, 1100)
    ctx.scale(1.25, 1.25)
    ctx.translate(-540, -1180)
    P.jardin(ctx, t)
    P.piscine(ctx, t, feuilles=0.3, fissure=1.0, propre=0.8)
    halo(ctx, *P.DAUPHIN, 300, (255, 240, 160), 0.45)
    ctx.restore()
    ctx.rectangle(0, 0, W, H)
    flat(ctx, (10, 14, 30), 0.18)

    # la dame au premier plan avec le chèque, le fils au téléphone qui s'énerve
    dame, fils = Perso(**DAME), Perso(**FILS)
    dame.pose(0, "objet").emotion(0, "content")
    dame.objet = lambda c, x, y, s: P.cheque(c, x, y - 175, 0.95, "6 000 €")
    fils.pose(0, "oreille").emotion(0, "colere")
    fils.objet = lambda c, x, y, s: __import__("decors").telephone(c, x + 35, y - 95, 0.7, rot=0.35)
    fils.draw(ctx, 905, 2120, 0.95, t)
    traits_choc(ctx, 905, 2120 - 0.95 * 880, 150, 0.5)
    dame.draw(ctx, 215, 2260, 1.15, t)
    vignette(ctx, 0.45)

    # titre (zone sûre : haut de l'image, à gauche des boutons)
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

    ligne("6 000 €", 250, 170, (255, 210, 40), INK, -0.04)
    ligne("POUR UNE PISCINE VIDE", 440, 84, (250, 250, 250), INK, 0.02)
    ligne("« ARNAQUEUR »", 590, 76, (232, 52, 60), (255, 255, 255), -0.03)

    out = ROOT / "output/trait/piscine_dauphin_miniature.png"
    surf.write_to_png(str(out))
    print("→", out)


if __name__ == "__main__":
    main()
