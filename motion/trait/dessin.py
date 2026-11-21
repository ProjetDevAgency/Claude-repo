"""Primitives du style « trait » : aplats + contour d'encre épais + ombrage doux sur un côté.

Tout est vectoriel (Cairo) : on peut zoomer x3 sur un visage sans perdre de netteté.
Les textes passent par Pillow (vraies polices TTF) puis sont posés comme des images.
"""
import math
from functools import lru_cache
from pathlib import Path

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H, FPS = 1080, 1920, 30
F_TXT = str(ROOT / "assets/fonts/Montserrat-ExtraBold.ttf")
F_BIG = str(ROOT / "assets/fonts/Anton-Regular.ttf")

INK = (30, 27, 36)
LW = 6                      # épaisseur du contour (à l'échelle 1)


def rgb(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        c = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(v / 255 for v in c[:3])


def mix(a, b, k):
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


def dark(c, k=0.8):
    return tuple(int(v * k) for v in c)


# ───────────── courbes de temps ─────────────

def clamp(t, a=0.0, b=1.0):
    return max(a, min(b, t))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def back(t, c=1.9):
    """Arrivée avec petit dépassement (le « pop »)."""
    t = clamp(t)
    return max(1e-3, 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2)


def spring(t, f=3.0, d=5.0):
    """Ressort amorti : 0 → 1 avec rebonds (pour ce qui se balance)."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-d * t) * math.cos(2 * math.pi * f * t)


# ───────────── formes ─────────────

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def circle(ctx, x, y, r):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def poly(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def paint(ctx, color, lw=LW, shade=0.80, light=None, alpha=1.0):
    """Remplit le chemin courant : aplat + ombre douce sur la droite, puis contour d'encre."""
    c = rgb(color)
    if shade < 1:
        x0, y0, x1, y1 = ctx.fill_extents()
        g = cairo.LinearGradient(x0, 0, x1, 0)
        g.add_color_stop_rgba(0, *c, alpha)
        g.add_color_stop_rgba(0.58, *c, alpha)
        g.add_color_stop_rgba(1, *(v * shade for v in c), alpha)
        ctx.set_source(g)
    else:
        ctx.set_source_rgba(*c, alpha)
    if lw:
        ctx.fill_preserve()
        stroke(ctx, lw, alpha=alpha)
    else:
        ctx.fill()


def stroke(ctx, lw=LW, color=INK, alpha=1.0):
    ctx.set_source_rgba(*rgb(color), alpha)
    ctx.set_line_width(lw)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def flat(ctx, color, alpha=1.0):
    ctx.set_source_rgba(*rgb(color), alpha)
    ctx.fill()


def tube(ctx, pts, width, color, lw=LW):
    """Membre en tube (bras, jambes) : trait d'encre large puis trait de couleur par-dessus."""
    for w, c in ((width + 2 * lw, INK), (width, color)):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.set_source_rgb(*rgb(c))
        ctx.set_line_width(w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()


def ombre_sol(ctx, x, y, rx, alpha=0.28):
    ellipse(ctx, x, y, rx, rx * 0.16)
    ctx.set_source_rgba(0, 0, 0, alpha)
    ctx.fill()


def cone_lumiere(ctx, x, y, w_top, w_bot, h, alpha=0.16, color=(255, 236, 190)):
    """Faisceau de lumière (projecteur au plafond)."""
    g = cairo.LinearGradient(0, y, 0, y + h)
    c = rgb(color)
    g.add_color_stop_rgba(0, *c, alpha)
    g.add_color_stop_rgba(1, *c, 0)
    poly(ctx, [(x - w_top / 2, y), (x + w_top / 2, y), (x + w_bot / 2, y + h), (x - w_bot / 2, y + h)])
    ctx.set_source(g)
    ctx.fill()


def halo(ctx, x, y, r, color, alpha=0.5):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    c = rgb(color)
    g.add_color_stop_rgba(0, *c, alpha)
    g.add_color_stop_rgba(1, *c, 0)
    ctx.set_source(g)
    circle(ctx, x, y, r)
    ctx.fill()


def vignette(ctx, force=0.55):
    g = cairo.RadialGradient(W / 2, H * 0.45, H * 0.25, W / 2, H * 0.45, H * 0.78)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, force)
    ctx.set_source(g)
    ctx.paint()


# ───────────── textes (Pillow → Cairo) ─────────────

def pil_to_surface(img):
    a = np.asarray(img.convert("RGBA"), dtype=np.uint16)
    al = a[..., 3:4]
    pm = (a[..., :3] * al // 255).astype(np.uint8)
    bgra = np.concatenate([pm[..., ::-1], a[..., 3:4].astype(np.uint8)], axis=2)
    h, w = bgra.shape[:2]
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    buf = np.zeros((h, stride), np.uint8)
    buf[:, :w * 4] = bgra.reshape(h, w * 4)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    surf.flush()
    np.frombuffer(surf.get_data(), np.uint8).reshape(h, stride)[:] = buf
    surf.mark_dirty()
    return surf


@lru_cache(maxsize=64)
def font(path, size):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=4096)
def texte(txt, size, color=(255, 255, 255), big=False, outline=0, outline_color=INK):
    """Image d'un texte (surface Cairo), mise en cache."""
    f = font(F_BIG if big else F_TXT, size)
    x0, y0, x1, y1 = f.getbbox(txt, stroke_width=outline)
    pad = 4 + outline
    img = Image.new("RGBA", (x1 - x0 + 2 * pad, size + 2 * pad + outline * 2 + size // 4), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - x0, pad), txt, font=f, fill=tuple(color) + (255,),
                             stroke_width=outline, stroke_fill=tuple(outline_color) + (255,))
    bb = img.getbbox() or (0, 0, 1, 1)
    img = img.crop((0, 0, img.width, bb[3] + 2))
    return pil_to_surface(img)


def blit(ctx, surf, x, y, ax=0.5, ay=0.5, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.001 or alpha <= 0.001:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(scale, scale)
    ctx.set_source_surface(surf, -surf.get_width() * ax, -surf.get_height() * ay)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def ecrit(ctx, txt, x, y, size, color=(255, 255, 255), big=False, ax=0.5, ay=0.5, scale=1.0, rot=0.0,
          alpha=1.0, outline=0):
    s = texte(txt, size, tuple(color), big, outline)
    blit(ctx, s, x, y, ax, ay, scale, rot, alpha)
    return s.get_width() * scale, s.get_height() * scale


def sauver_miniature(surf, out, saturation=None):
    """Enregistre une miniature avec la même saturation que les vidéos (+35 %, validé par le client le 21 nov.)."""
    import os
    from PIL import Image, ImageEnhance
    sat = saturation or float(os.environ.get("TRAIT_SATURATION", "1.35"))
    surf.write_to_png(str(out))
    im = Image.open(out).convert("RGB")
    ImageEnhance.Color(im).enhance(sat).save(out)
