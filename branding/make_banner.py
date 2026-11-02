"""Bannière YouTube 2560x1440. Tout le contenu tient dans la zone sûre
1546x423 au centre (la seule partie visible sur mobile)."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from make_avatars import half_points

W, H = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
BG, ACCENT, CREAM, GOLD = (24, 46, 34), (60, 98, 70), (240, 228, 205), (226, 186, 92)
FONT = "../assets/fonts/Montserrat-ExtraBold.ttf"

img = Image.new("RGB", (W, H), BG)
glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse([W / 2 - 1000, H / 2 - 420, W / 2 + 1000, H / 2 + 420], fill=90)
glow = glow.filter(ImageFilter.GaussianBlur(220))
img = Image.composite(Image.new("RGB", (W, H), ACCENT), img, glow)

# empreintes discrètes en fond (un chemin de vache qui traverse)
trail = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(trail)
random.seed(4)


def hoof(draw, cx, cy, scale, color, rot=0):
    w, h = 105 * scale, 190 * scale
    r = math.radians(rot)
    for side in (-1, 1):
        a = math.radians(-side * 3.2)
        px, py = side * 30 * scale, h
        for_pts = []
        for x, y in half_points(w, h, side):
            y -= h
            x2 = px + x * math.cos(a) - y * math.sin(a)
            y2 = py + x * math.sin(a) + y * math.cos(a) - h
            for_pts.append((cx + x2 * math.cos(r) - y2 * math.sin(r),
                            cy + x2 * math.sin(r) + y2 * math.cos(r)))
        draw.polygon(for_pts, fill=color)


for k in range(14):
    x = -100 + k * 210
    y = 1180 - k * 70 + (40 if k % 2 else -40)
    hoof(td, x, y, 0.32, (255, 255, 255, 13), rot=65)
img = Image.alpha_composite(img.convert("RGBA"), trail)

d = ImageDraw.Draw(img)
cx, cy = W / 2, H / 2
sx = cx - SAFE_W / 2
title = ImageFont.truetype(FONT, 128)
sub = ImageFont.truetype(FONT, 44)
logo_w, gap = 170, 70
text_w = max(d.textlength("SOUS LE SABOT", font=title),
             d.textlength("Chaque vache qui boite cache une histoire", font=sub))
group = logo_w + gap + text_w
left = cx - group / 2                      # groupe logo + texte centré
hoof(d, left + logo_w / 2, cy - 10 + 190 * 0.78, 0.78, CREAM)  # la fonction dessine au-dessus du point donné
tx = left + logo_w + gap
d.text((tx, cy - 135), "SOUS LE SABOT", font=title, fill=CREAM)
d.rectangle([tx + 6, cy + 30, tx + 220, cy + 40], fill=GOLD)
d.text((tx, cy + 70), "Chaque vache qui boite cache une histoire", font=sub, fill=GOLD)
img.convert("RGB").save("banniere_youtube.png", optimize=True)

# aperçu mobile = zone sûre
img.crop((int(cx - SAFE_W / 2), int(cy - SAFE_H / 2), int(cx + SAFE_W / 2), int(cy + SAFE_H / 2))) \
   .convert("RGB").save("banniere_apercu_mobile.png")
print("ok", int(group), "px utilisés sur", SAFE_W)
