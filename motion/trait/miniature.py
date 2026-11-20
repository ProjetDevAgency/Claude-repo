"""Miniature TikTok façon La Ficelle : bandeau jaune (question) en haut, gros plan d'un personnage qui réagit,
bandeau sombre (phrase choc), puis « 0 € barré → gain » en bas.

    python3 motion/trait/miniature.py   → output/trait/miniature_remake_aides.jpg
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairo  # noqa: E402

from dessin import H, INK, LW, ROOT, W, circle, couche_floue, ecrit, flat, halo, paint, poly, rrect, stroke, texte  # noqa: E402
from perso import Perso  # noqa: E402
from six_aides_31dec import PATRON, deg  # noqa: E402


def bandeau(ctx, y, txt, size, fond, col, rot=0.0, pad=40):
    s = texte(txt, size, col, True)
    w, h = s.get_width() + 2 * pad, s.get_height() + 36
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.rotate(rot)
    rrect(ctx, -w / 2 + 10, -h / 2 + 12, w, h, 10)
    flat(ctx, (0, 0, 0), 0.4)
    rrect(ctx, -w / 2, -h / 2, w, h, 10)
    ctx.set_source_rgb(*[v / 255 for v in fond])
    ctx.fill_preserve()
    stroke(ctx, 9, INK)
    ctx.set_source_surface(s, -s.get_width() / 2, -s.get_height() / 2 + 4)
    ctx.paint()
    ctx.restore()


def miniature(question, choc, avant, apres, perso, emotion, sortie):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    deg(ctx, 0, 0, W, H, (54, 44, 40), (24, 22, 30))

    def bokeh(c):
        for i in range(16):
            halo(c, (i * 173) % W, (i * 311) % H, 160, (255, 200, 120) if i % 2 else (120, 160, 255), 0.55)
    couche_floue(ctx, bokeh, rayon=30, bord="constant")
    p = Perso(**perso)
    p.emotion(0, emotion).pose(0, "repos")
    s = 2.6
    ancre = p.draw(ctx, W / 2, H + 1000, s, 0.4, bouche=0.6 if emotion == "choc" else 0.0)
    if emotion == "triste":                                   # larmes sous les yeux
        hx, hy = ancre["tete"]
        k = perso.get("tete", 1.0) * s
        for sx in (-1, 1):
            ex, ey = hx + sx * 40 * k, hy + 10 * k
            for j in range(3):
                circle(ctx, ex + sx * 4 * j, hy + 14 * k + j * 20 * k, (9 - 2 * j) * k)
                paint(ctx, (120, 190, 255), LW * 0.8, shade=1)
    bandeau(ctx, 150, question, 108, (255, 214, 40), INK, rot=-0.015)
    bandeau(ctx, 1450, choc, 76, (34, 32, 44), (255, 255, 255), rot=0.01)
    # « 0 € barré → gain »
    ecrit(ctx, avant, 230, 1680, 150, (230, 230, 235), big=True, outline=6)
    ctx.move_to(110, 1700)
    ctx.line_to(360, 1650)
    stroke(ctx, 20, (232, 52, 60))
    poly(ctx, [(380, 1660), (470, 1660), (470, 1630), (530, 1685), (470, 1740), (470, 1710), (380, 1710)])
    paint(ctx, (255, 170, 40), LW, shade=1)
    ecrit(ctx, apres, 790, 1680, 190, (60, 220, 110), big=True, outline=7)
    surf.write_to_png(str(sortie) + ".png")
    from PIL import Image
    Image.open(str(sortie) + ".png").convert("RGB").save(str(sortie) + ".jpg", quality=92)


if __name__ == "__main__":
    miniature("AIDES AVANT LE 31/12 ?", "TON PATRON N'EN PARLE PAS", "0 €", "1 623 €", PATRON, "triste",
              ROOT / "output/trait/miniature_remake_aides")
