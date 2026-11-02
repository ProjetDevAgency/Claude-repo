"""Génère des photos de profil (1080x1080) : empreinte d'onglon stylisée."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "../assets/fonts/Montserrat-ExtraBold.ttf"
S = 1080


def half_points(w, h, side):
    """Demi-onglon : moitié d'un œuf (pointe en haut), bord intérieur droit."""
    pts = [(0, -h)]
    for i in range(1, 120):
        v = -1 + 2 * i / 120                       # -1 = pointe, 1 = talon
        x = w * math.sqrt(max(0, 1 - v * v)) * (0.78 + 0.32 * v)
        pts.append((side * x, v * h))
    pts.append((0, h))
    return pts


def hoof(draw, cx, cy, scale, color):
    w, h = 105 * scale, 190 * scale
    for side in (-1, 1):
        a = math.radians(-side * 3.2)                # les pointes se rapprochent, comme une vraie empreinte
        px, py = cx + side * 30 * scale, cy + h    # pivot au talon
        pts = []
        for x, y in half_points(w, h, side):
            y -= h
            pts.append((px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a)))
        draw.polygon(pts, fill=color)

def avatar(name, bg, fg, accent, text=None):
    img = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(img)
    # léger dégradé radial
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).ellipse([140, 100, 940, 900], fill=60)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGB", (S, S), accent), img, glow)
    d = ImageDraw.Draw(img)
    hoof(d, S / 2, S / 2 + (10 if not text else -40), 1.55 if not text else 1.25, fg)
    if text:
        f = ImageFont.truetype(FONT, 92)
        w = d.textlength(text, font=f)
        d.text(((S - w) / 2, 820), text, font=f, fill=fg)
    img.save(name)


avatar("avatar_1_vert.png", (24, 46, 34), (240, 228, 205), (60, 98, 70))
avatar("avatar_2_noir_texte.png", (18, 18, 18), (244, 196, 48), (55, 45, 20), "SOUS LE SABOT")
avatar("avatar_3_terre.png", (122, 72, 40), (250, 240, 225), (170, 110, 60))
