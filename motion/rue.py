"""Style « rue vue de face » (2D à contours noirs) + contour noir pour la vue 3D du village.

- contour(layer) : ajoute un contour noir épais autour de tout ce qui est dessiné sur un calque transparent.
- contour_aretes(img) : dessine un trait noir sur les arêtes fortes d'une image (pour la carte isométrique).
- rue(...) : le décor de face (ciel, nuages, collines, route qui file vers l'horizon).
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from cartoon import FA, INK, SS, WHITE, YEL, character
from engine import H, W

SKY_TOP, SKY_BOT = (120, 190, 240), (200, 230, 250)
HILL = (120, 185, 95)
GRASS = (110, 190, 80)
ROAD = (115, 118, 128)
LINE = (25, 25, 30)
HORIZON = 900


def contour(layer, w=10):
    """Calque RGBA → même calque avec un contour noir de w pixels autour des formes."""
    a = layer.split()[3]
    grow = a.filter(ImageFilter.MaxFilter(w * 2 + 1))
    out = Image.new("RGBA", layer.size, LINE + (0,))
    out.putalpha(grow)
    out.alpha_composite(layer)
    return out


def contour_aretes(img, seuil=60, w=5):
    """Trait sombre là où la couleur change fortement (effet dessin animé sur une image déjà dessinée)."""
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    dx = np.abs(np.diff(a, axis=1)).sum(axis=2)
    dy = np.abs(np.diff(a, axis=0)).sum(axis=2)
    m = np.zeros(a.shape[:2], bool)
    m[:, 1:] |= dx > seuil
    m[1:, :] |= dy > seuil
    mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(w))
    out = img.convert("RGB").copy()
    out.paste(LINE, (0, 0), mask)
    return out


def nuage(d, x, y, s):
    for dx, dy, r in ((-60, 10, 50), (0, -20, 65), (60, 10, 50), (25, 25, 45), (-25, 25, 45)):
        d.ellipse([(x + dx * s - r * s) * SS, (y + dy * s - r * s) * SS, (x + dx * s + r * s) * SS,
                   (y + dy * s + r * s) * SS], fill=WHITE + (255,))


def decor_rue(t=0.0):
    """Fond de la scène de rue, en x2 (SS)."""
    big = Image.new("RGBA", (W * SS, H * SS), SKY_BOT + (255,))
    d = ImageDraw.Draw(big)
    for y in range(0, HORIZON * SS, 8):
        k = y / (HORIZON * SS)
        c = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * k) for i in range(3))
        d.rectangle([0, y, W * SS, y + 8], fill=c + (255,))
    nuages = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dn = ImageDraw.Draw(nuages)
    for (x, y, s) in ((160, 260, 0.9), (620, 180, 1.1), (950, 330, 0.8), (420, 420, 0.6)):
        nuage(dn, (x + t * 12) % (W + 200) - 100, y, s)
    big.alpha_composite(contour(nuages, 6))
    collines = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(collines)
    dc.ellipse([-300 * SS, (HORIZON - 160) * SS, 600 * SS, (HORIZON + 300) * SS], fill=(130, 195, 105, 255))
    dc.ellipse([400 * SS, (HORIZON - 120) * SS, 1400 * SS, (HORIZON + 300) * SS], fill=HILL + (255,))
    big.alpha_composite(contour(collines, 6))
    d = ImageDraw.Draw(big)
    d.rectangle([0, HORIZON * SS, W * SS, H * SS], fill=GRASS + (255,))
    route = Image.new("RGBA", big.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(route)
    dr.polygon([(470 * SS, HORIZON * SS), (610 * SS, HORIZON * SS), (1250 * SS, H * SS), (-170 * SS, H * SS)],
               fill=ROAD + (255,))
    for q in range(7):                                       # pointillés en perspective
        k0 = (q / 7 + t * 0.15) % 1.0
        k1 = k0 + 0.05
        y0, y1 = HORIZON + (H - HORIZON) * k0 ** 1.6, HORIZON + (H - HORIZON) * min(1, k1) ** 1.6
        w0, w1 = 3 + 14 * k0, 3 + 14 * k1
        dr.polygon([((540 - w0) * SS, y0 * SS), ((540 + w0) * SS, y0 * SS), ((540 + w1) * SS, y1 * SS),
                    ((540 - w1) * SS, y1 * SS)], fill=WHITE + (255,))
    big.alpha_composite(contour(route, 5))
    return big


def panneau_ville(nom, habitants, x=540, y=430, s=1.0):
    """Panneau d'entrée de ville + plaque « HABITANTS ». Renvoie un calque RGBA (x2) avec contour."""
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def R(a, b, c, e):
        return [(x + a * s) * SS, (y + b * s) * SS, (x + c * s) * SS, (y + e * s) * SS]
    d.rectangle(R(-250, 80, -225, 470), fill=(150, 150, 160, 255))
    d.rectangle(R(225, 80, 250, 470), fill=(150, 150, 160, 255))
    d.rounded_rectangle(R(-330, -110, 330, 110), radius=int(24 * s * SS), fill=WHITE + (255,))
    d.rounded_rectangle(R(-305, -86, 305, 86), radius=int(16 * s * SS), outline=(215, 40, 50, 255),
                        width=int(18 * s * SS))
    d.text((x * SS, (y - 25 * s) * SS), nom.split("-")[0], font=FA(int(96 * s * SS)), fill=INK, anchor="mm")
    reste = "-".join(nom.split("-")[1:])
    d.text((x * SS, (y + 52 * s) * SS), reste.upper(), font=FA(int(54 * s * SS)), fill=INK, anchor="mm")
    d.rounded_rectangle(R(-130, 130, 130, 270), radius=int(18 * s * SS), fill=WHITE + (255,))
    d.text((x * SS, (y + 160 * s) * SS), "HABITANTS", font=FA(int(32 * s * SS)), fill=INK, anchor="mm")
    d.text((x * SS, (y + 225 * s) * SS), f"{habitants:,}".replace(",", " "), font=FA(int(80 * s * SS)),
           fill=(40, 160, 70), anchor="mm")
    return contour(lay, 9)


def maire_face(x, base, sc, t=0.0, **pose):
    from village import maire
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    maire(ImageDraw.Draw(lay), x, base, t, sc=sc, **pose)
    return contour(lay, 10)


COULEURS = [(220, 60, 60), (60, 120, 220), (240, 180, 40), (90, 180, 100), (170, 90, 200), (240, 130, 60),
            (60, 170, 180), (230, 230, 235), (40, 40, 50), (250, 150, 190)]
CHEVEUX = [(30, 25, 20), (90, 60, 40), (200, 150, 60), (20, 20, 25), (120, 70, 40)]


def foule(pseudos, t=0.0, rangs=((1270, 0.30, 7), (1390, 0.36, 6), (1530, 0.43, 5)), centre_libre=180):
    """Habitants de face sur la route, avec leur pseudo au-dessus de la tête. Renvoie un calque RGBA (x2)."""
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tags = []
    n = 0
    for (base, sc, nb) in rangs:
        xs = [80 + (W - 160) * (q + 0.5) / nb for q in range(nb)]
        for x in xs:
            if abs(x - 540) < centre_libre and base < 1500:
                continue
            col = COULEURS[n % len(COULEURS)]
            bob = math.sin(t * 6 + n) * 6
            character(d, x, base + bob, sc=sc, shirt=col, pants=(50, 50, 70), hair=CHEVEUX[n % 5],
                      long_hair=(n % 3 == 1), mouth="grin" if n % 2 else "o", arms_up=(n % 4 == 0),
                      arm=0.6 if n % 4 == 2 else 0.0)
            if n < len(pseudos):
                tags.append((x, base + bob - 900 * sc, pseudos[n]))
            n += 1
    lay = contour(lay, 6)
    dt = ImageDraw.Draw(lay)
    for x, y, p in tags:
        f = FA(int(26 * SS))
        w = f.getlength(p) / SS + 22
        dt.rounded_rectangle([(x - w / 2) * SS, (y - 24) * SS, (x + w / 2) * SS, (y + 18) * SS], radius=10 * SS,
                             fill=WHITE + (255,), outline=INK + (255,), width=3 * SS)
        dt.text((x * SS, (y - 3) * SS), p, font=f, fill=INK, anchor="mm")
    return lay


def vers_ecran(big):
    return big.convert("RGB").resize((W, H), Image.LANCZOS)
