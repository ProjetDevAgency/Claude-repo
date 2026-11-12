"""Logo (800x800) et bannière YouTube (2560x1440) pour la chaîne éco."""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

NAME = sys.argv[1] if len(sys.argv) > 1 else "OÙ VA TON ARGENT ?"
FONT = "../../assets/fonts/Montserrat-ExtraBold.ttf"
BG, RED, YELLOW, WHITE, GREY = (16, 16, 18), (214, 40, 48), (255, 210, 0), (242, 242, 242), (70, 70, 78)


def F(s):
    return ImageFont.truetype(FONT, s)


def coin(d, cx, cy, r):
    """Pièce € rouge avec une flèche jaune qui s'échappe."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.ellipse([cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82], outline=(240, 90, 96), width=max(3, int(r * 0.04)))
    d.text((cx - r * 0.06, cy + r * 0.02), "€", font=F(int(r * 1.15)), fill=WHITE, anchor="mm")
    # flèche montante vers la droite
    w = max(6, int(r * 0.13))
    p0 = (cx + r * 0.35, cy + r * 0.25)
    p1 = (cx + r * 1.05, cy - r * 0.75)
    d.line([p0, p1], fill=YELLOW, width=w)
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    L = r * 0.38
    tip = [p1, (p1[0] - L * math.cos(a - 0.5), p1[1] - L * math.sin(a - 0.5)),
           (p1[0] - L * math.cos(a + 0.5), p1[1] - L * math.sin(a + 0.5))]
    d.polygon(tip, fill=YELLOW)


# --- logo (rond chez YouTube : tout tient dans le cercle central)
S = 800
logo = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(logo)
coin(d, S * 0.46, S * 0.54, S * 0.27)
logo.save("logo_eco_v1.png")

# --- bannière : contenu dans la zone sûre mobile 1546x423 au centre
W, H = 2560, 1440
ban = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(ban)
for gx in range(30, W, 60):
    for gy in range(30, H, 60):
        d.point((gx, gy), fill=(40, 40, 46))
# barres de graphique en fond, discrètes
base = H / 2 + 330
for i, h in enumerate([120, 180, 140, 260, 210, 330, 290, 420]):
    x = 120 + i * 70
    d.rectangle([x, base - h, x + 44, base], fill=(34, 34, 40))
    x2 = W - 120 - (i + 1) * 70
    d.rectangle([x2, base - h, x2 + 44, base], fill=(34, 34, 40))
cx, cy = W / 2, H / 2
title_f, sub_f = F(98), F(40)
tw = d.textlength(NAME, font=title_f)
logo_r = 105
group = 2 * logo_r + 60 + tw + logo_r * 0.4
left = cx - group / 2
coin(d, left + logo_r, cy - 10, logo_r)
tx = left + 2.4 * logo_r + 60
d.text((tx, cy - 70), NAME, font=title_f, fill=WHITE, anchor="lm")
d.rectangle([tx + 4, cy + 10, tx + 200, cy + 20], fill=YELLOW)
d.text((tx, cy + 75), "L'ACTU ÉCO EN 1 MINUTE · CHAQUE JOUR", font=sub_f, fill=YELLOW, anchor="lm")
ban.save("banniere_eco_v1.png", optimize=True)
ban.crop((int(cx - 773), int(cy - 211), int(cx + 773), int(cy + 212))).save("banniere_eco_v1_apercu_mobile.png")
print("zone utilisée", int(group), "/ 1546 px")
