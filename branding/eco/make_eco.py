"""Logo final (800x800) et bannière YouTube (2560x1440) de « Où va ton argent ? » — version Kévin (proposition A).

Usage : python3 branding/eco/make_eco.py
  → logo_eco.png, banniere_eco.png, banniere_eco_apercu_mobile.png, banniere_eco_apercu_tv.png
L'ancienne version (pièce rouge + flèche) est dans make_eco_v1.py / *_v1.png.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_logo_v2 import (INK, KEVIN, SS, WHITE, YEL, F, ailes, billet, character, coin, pose,  # noqa: E402
                          rue)
import math  # noqa: E402

OUT = Path(__file__).resolve().parent
RAY = (255, 222, 70)


def kevin_sur(bg, cx, base, sc, contour, **kw):
    """Kévin dessiné en x2 sur un calque de la taille du fond, réduit, contour noir."""
    w, h = bg.size
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    character(ImageDraw.Draw(big), cx, base, sc=sc, **{**KEVIN, **kw})
    lay = rue.contour(big.resize((w, h), Image.LANCZOS), contour)
    bg.alpha_composite(lay)


def rayons(img, cx, cy, n=16, c=RAY):
    d = ImageDraw.Draw(img)
    R = 2 * max(img.size)
    for k in range(0, n, 2):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c)


# --- logo (rond chez TikTok / YouTube : tout tient dans le cercle)
S = 800
logo = Image.new("RGBA", (S, S), YEL + (255,))
rayons(logo, S / 2, S / 2)
kevin_sur(logo, 400, 1210, 1.3, 7, mouth="o", brows="haut")
pose(logo, ailes(billet(0.55, 14), 0.55), 150, 330)
pose(logo, ailes(billet(0.5, -16), 0.5), 680, 370)
pose(logo, coin(0.5), 130, 520)
logo.convert("RGB").save(OUT / "logo_eco.png")

# --- bannière : texte + visage dans la zone sûre mobile 1546x423 au centre
W, H = 2560, 1440
cx, cy = W // 2, H // 2
ban = Image.new("RGBA", (W, H), YEL + (255,))
rayons(ban, cx - 520, cy, n=28)
# Kévin à gauche de la zone sûre, tête entière dedans
kevin_sur(ban, cx - 600, cy + 495, 0.8, 5, mouth="o", brows="haut")
# billets qui s'envolent : 2 dans la zone sûre, les autres visibles sur ordi / TV
for x, y, sc, rot in [(cx - 800, cy - 110, 0.4, 14),
                      (cx - 1050, cy - 330, 0.6, 10), (cx + 980, cy - 380, 0.55, -12),
                      (cx + 1120, cy + 260, 0.5, 18), (cx - 1150, cy + 330, 0.5, -8)]:
    pose(ban, ailes(billet(sc, rot), sc), x, y)
pose(ban, coin(0.42), cx - 860, cy + 110)
d = ImageDraw.Draw(ban)
tx = cx - 370
# contour : stroke de Pillow sur un masque, puis fermeture 5 px (bouche le petit trou dans le « E » d'Anton)
masque = Image.new("L", ban.size, 0)
ImageDraw.Draw(masque).text((tx, cy - 75), "OÙ VA TON ARGENT ?", font=F(132, anton=True), fill=255, anchor="lm")
tour = Image.new("L", ban.size, 0)
ImageDraw.Draw(tour).text((tx, cy - 75), "OÙ VA TON ARGENT ?", font=F(132, anton=True), fill=255, anchor="lm",
                          stroke_width=12, stroke_fill=255)
ban.paste(INK, (0, 0), tour.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)))
ban.paste(WHITE, (0, 0), masque)
d = ImageDraw.Draw(ban)
pill_y = cy + 95
sub = "TES DROITS EN 1 MINUTE, AVEC KÉVIN"
sw = d.textlength(sub, font=F(40))
d.rounded_rectangle([tx, pill_y - 38, tx + sw + 56, pill_y + 38], radius=38, fill=INK)
d.text((tx + 28, pill_y), sub, font=F(40), fill=YEL, anchor="lm")
ban = ban.convert("RGB")
ban.save(OUT / "banniere_eco.png", optimize=True)
ban.crop((cx - 773, cy - 211, cx + 773, cy + 212)).save(OUT / "banniere_eco_apercu_mobile.png")
ban.crop((0, cy - 211, W, cy + 212)).save(OUT / "banniere_eco_apercu_ordi.png")

right = max(tx + d.textlength("OÙ VA TON ARGENT ?", font=F(132, anton=True)) + 12, tx + sw + 56)
print("texte de", tx, "à", int(right), "· zone sûre", cx - 773, "→", cx + 773)
