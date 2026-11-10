"""Fausse 3D (vue isométrique) pour « Le village des abonnés ».

Le village est une grille de cases vue en diagonale. Chaque bâtiment est une boîte à 3 faces
(dessus clair, côtés plus sombres) avec un toit. On dessine la carte en x2 puis une « caméra »
cadre et zoome dessus, comme les autres vidéos.
"""
import math

from PIL import Image, ImageDraw

from cartoon import FA, INK, SS, WHITE, YEL, character
from engine import H, W

TW, TH = 160, 80           # taille d'une case à l'écran (losange 2:1)
OX, OY = 540, 1000         # écran de la case (0, 0)
HK = TW / 96               # échelle des hauteurs et des petits objets

GRASS = (118, 196, 96)
GRASS2 = (108, 186, 88)
ROAD = (120, 122, 132)
WATER = (80, 160, 230)
SKY = (150, 210, 245)


def iso(i, j, z=0.0):
    """Case (i, j) à la hauteur z → point écran (coordonnées finales)."""
    return OX + (i - j) * TW / 2, OY + (i + j) * TH / 2 - z * HK


def P(i, j, z=0.0):
    x, y = iso(i, j, z)
    return x * SS, y * SS


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def tile(d, i, j, col, w=1, dd=1):
    d.polygon([P(i, j), P(i + w, j), P(i + w, j + dd), P(i, j + dd)], fill=col)


def box(d, i, j, w, dd, h, col, z0=0.0):
    """Boîte posée sur la case (i, j), de w×dd cases et h pixels de haut."""
    A, B, C, D = (i, j), (i + w, j), (i + w, j + dd), (i, j + dd)
    d.polygon([P(*D, z0), P(*C, z0), P(*C, z0 + h), P(*D, z0 + h)], fill=shade(col, 0.82))   # face gauche
    d.polygon([P(*B, z0), P(*C, z0), P(*C, z0 + h), P(*B, z0 + h)], fill=shade(col, 0.66))   # face droite
    d.polygon([P(*A, z0 + h), P(*B, z0 + h), P(*C, z0 + h), P(*D, z0 + h)], fill=shade(col, 1.08))  # dessus


def roof(d, i, j, w, dd, h, rh, col):
    """Toit à deux pans, faîte dans l'axe i."""
    r1, r2 = P(i, j + dd / 2, h + rh), P(i + w, j + dd / 2, h + rh)
    d.polygon([P(i, j, h), P(i + w, j, h), r2, r1], fill=shade(col, 0.75))
    d.polygon([P(i, j + dd, h), P(i + w, j + dd, h), r2, r1], fill=col)
    d.polygon([P(i + w, j, h), P(i + w, j + dd, h), r2], fill=shade(col, 0.6))


def maison(d, i, j, k=1.0, col=(245, 215, 150), toit=(205, 75, 60)):
    h = 46 * k
    box(d, i + 0.15, j + 0.15, 0.7, 0.7, h, col)
    if k > 0.6:
        roof(d, i + 0.1, j + 0.1, 0.8, 0.8, h, 30 * (k - 0.6) / 0.4, toit)
        x, y = iso(i + 0.85, j + 0.5, 12)
        d.rectangle([(x - 7 * HK) * SS, (y - 10 * HK) * SS, (x + 7 * HK) * SS, (y + 12 * HK) * SS], fill=(110, 75, 50))


def mairie(d, i, j):
    box(d, i, j, 2, 1.4, 70, (240, 236, 225))
    box(d, i + 0.2, j + 0.2, 1.6, 1.0, 14, (60, 80, 150), z0=70)
    x, y = iso(i + 1.0, j + 0.7, 84)
    q = HK
    d.line([x * SS, y * SS, x * SS, (y - 70 * q) * SS], fill=INK, width=int(4 * q * SS))
    for k, c in enumerate([(35, 70, 160), (245, 245, 245), (215, 40, 50)]):
        d.rectangle([(x + k * 12 * q) * SS, (y - 70 * q) * SS, (x + (k + 1) * 12 * q) * SS, (y - 46 * q) * SS], fill=c)
    fx, fy = iso(i + 2, j + 0.7, 40)
    d.rounded_rectangle([(fx - 46 * q) * SS, (fy - 12 * q) * SS, (fx + 10 * q) * SS, (fy + 10 * q) * SS], radius=int(4 * q * SS),
                        fill=WHITE, outline=(35, 70, 160), width=int(2 * q * SS))
    d.text(((fx - 18 * q) * SS, fy * SS), "MAIRIE", font=FA(int(16 * q * SS)), fill=(35, 70, 160), anchor="mm")


def epicerie(d, i, j, k=1.0, ghost=False):
    col = (250, 240, 220) if not ghost else (235, 235, 240)
    h = 56 * k
    box(d, i, j, 1.6, 1.2, h, col)
    if k > 0.7:
        for s in range(6):   # store à rayures sur la face gauche
            a, b = j + 1.2, i + s * 1.6 / 6
            c1 = (230, 60, 60) if s % 2 == 0 else WHITE
            d.polygon([P(b, a, h * 0.72), P(b + 1.6 / 6, a, h * 0.72), P(b + 1.6 / 6, a + 0.25, h * 0.55),
                       P(b, a + 0.25, h * 0.55)], fill=c1)


def chapiteau(d, i, j, k=1.0):
    cx, cy = i + 0.8, j + 0.8
    top = iso(cx, cy, 110 * k)
    pts = [iso(cx + 0.8 * math.cos(a), cy + 0.8 * math.sin(a), 30 * k) for a in [x * math.pi / 6 for x in range(12)]]
    base = [iso(cx + 0.8 * math.cos(a), cy + 0.8 * math.sin(a), 0) for a in [x * math.pi / 6 for x in range(12)]]
    d.polygon([(x * SS, y * SS) for x, y in base[1:7]] + [(x * SS, y * SS) for x, y in pts[6:0:-1]], fill=(250, 230, 240))
    for s in range(12):
        a, b = pts[s], pts[(s + 1) % 12]
        if 0 <= s <= 6:
            d.polygon([(top[0] * SS, top[1] * SS), (a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)],
                      fill=(220, 50, 70) if s % 2 == 0 else WHITE)
    q = HK
    d.line([top[0] * SS, top[1] * SS, top[0] * SS, (top[1] - 22 * q) * SS], fill=INK, width=int(3 * q * SS))
    d.polygon([(top[0] * SS, (top[1] - 22 * q) * SS), ((top[0] + 16 * q) * SS, (top[1] - 16 * q) * SS),
               (top[0] * SS, (top[1] - 10 * q) * SS)], fill=YEL)


def pont(d, i, j, casse=False):
    """Pont sur la rivière (cases i..i+1, axe j)."""
    if casse:
        box(d, i, j, 0.35, 1, 10, (150, 110, 80), z0=4)
        box(d, i + 0.75, j, 0.25, 1, 10, (150, 110, 80), z0=4)
    else:
        box(d, i, j, 1, 1, 10, (150, 110, 80), z0=4)
        for jj in (j, j + 0.92):
            box(d, i, jj, 1, 0.08, 14, (120, 85, 60), z0=14)


def arbre(d, i, j, s=HK):
    x, y = iso(i + 0.5, j + 0.5)
    d.rectangle([(x - 4 * s) * SS, (y - 22 * s) * SS, (x + 4 * s) * SS, y * SS], fill=(110, 75, 50))
    d.ellipse([(x - 20 * s) * SS, (y - 62 * s) * SS, (x + 20 * s) * SS, (y - 18 * s) * SS], fill=(60, 150, 70))
    d.ellipse([(x - 12 * s) * SS, (y - 58 * s) * SS, (x + 6 * s) * SS, (y - 40 * s) * SS], fill=(90, 180, 90))


def terrain(d, i, j, w=1, dd=1, n=None):
    """Terrain à bâtir : losange plus clair, bord en pointillés."""
    tile(d, i, j, (150, 210, 125), w, dd)
    pts = [iso(i, j), iso(i + w, j), iso(i + w, j + dd), iso(i, j + dd), iso(i, j)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        for t in range(0, int(L), 14):
            a, b = t / L, min(1, (t + 7) / L)
            d.line([(x0 + (x1 - x0) * a) * SS, (y0 + (y1 - y0) * a) * SS,
                    (x0 + (x1 - x0) * b) * SS, (y0 + (y1 - y0) * b) * SS], fill=WHITE, width=int(4 * SS))


def mystere(d, i, j, k=1.0):
    box(d, i, j, 1, 1, 70 * k, (30, 30, 36))
    x, y = iso(i + 0.5, j + 0.5, 70 * k)
    d.text((x * SS, (y - 2) * SS), "?", font=FA(int(40 * HK * SS)), fill=WHITE, anchor="mm")


def habitant(d, i, j, col, k=1.0):
    x, y = iso(i + 0.5, j + 0.5)
    s = k * HK
    d.ellipse([(x - 7 * s) * SS, (y - 40 * s) * SS, (x + 7 * s) * SS, (y - 26 * s) * SS], fill=(243, 196, 160))
    d.rounded_rectangle([(x - 8 * s) * SS, (y - 27 * s) * SS, (x + 8 * s) * SS, y * SS], radius=int(5 * s * SS), fill=col)


# ───────────── la carte ─────────────

RIVIERE_I = -5           # la rivière coule le long de i = -5 (deux cases de large)
ROUTE_J = 0              # route principale le long de j = 0
ARBRES = [(-8, -3), (-7, 3), (-2, -6), (4, -6), (6, 2), (5, 6), (-2, 6), (6, -2), (-8, 1), (2, -7), (-6, -6), (7, 6),
          (-1, -4.5), (3.5, 4.5)]
TERRAINS = {"maisons": [(1.3, 3.0), (2.5, 3.0), (3.7, 3.0), (-2.0, 1.4), (-2.0, 2.6), (-3.2, 2.6), (-3.2, 1.4), (1.3, 4.2)],
            "epicerie": (2.0, 1.2), "fete": (-2.8, -2.8), "mystere": (3.4, -1.6)}
MAIRIE = (1.2, -2.8)


def carte(etat):
    """Dessine la carte selon l'état : dict avec pont, epicerie, fete, maisons (liste de k), fantomes…"""
    big = Image.new("RGB", (W * SS, H * SS), GRASS)
    d = ImageDraw.Draw(big)
    for i in range(-14, 15):
        for j in range(-14, 15):
            if (i + j) % 2 == 0:
                tile(d, i, j, GRASS2)
    for j in range(-14, 15):
        tile(d, RIVIERE_I, j, WATER)
        tile(d, RIVIERE_I + 1, j, WATER)
    for i in range(-14, 15):
        if i not in (RIVIERE_I, RIVIERE_I + 1):
            tile(d, i, ROUTE_J, ROAD)
    for j in range(-9, 10):
        if j != ROUTE_J:
            tile(d, 0, j, ROAD)
    # objets, dessinés de l'arrière vers l'avant (i + j croissant)
    objs = []
    objs.append((RIVIERE_I + ROUTE_J, lambda: [pont(d, RIVIERE_I, ROUTE_J, casse=not etat.get("pont")),
                                                pont(d, RIVIERE_I + 1, ROUTE_J, casse=not etat.get("pont"))]))
    objs.append((sum(MAIRIE) + 3.4, lambda: mairie(d, *MAIRIE)))
    for (i, j) in ARBRES:
        objs.append((i + j + 1, lambda i=i, j=j: arbre(d, i, j)))
    mk = etat.get("maisons", [])
    for n, (i, j) in enumerate(TERRAINS["maisons"]):
        k = mk[n] if n < len(mk) else 0
        if k > 0:
            cols = [(245, 215, 150), (200, 225, 250), (250, 190, 190), (210, 240, 200)]
            objs.append((i + j + 1.7, lambda i=i, j=j, k=k, c=cols[n % 4]: maison(d, i, j, k, c)))
        elif etat.get("terrains", True):
            objs.append((-100, lambda i=i, j=j: terrain(d, i, j)))
    ei, ej = TERRAINS["epicerie"]
    if etat.get("epicerie", 0) > 0:
        objs.append((ei + ej + 2.8, lambda: epicerie(d, ei, ej, etat["epicerie"])))
    elif etat.get("terrains", True):
        objs.append((-100, lambda: terrain(d, ei, ej, 1.6, 1.2)))
    fi, fj = TERRAINS["fete"]
    if etat.get("fete", 0) > 0:
        objs.append((fi + fj + 3.2, lambda: chapiteau(d, fi, fj, etat["fete"])))
    elif etat.get("terrains", True):
        objs.append((-100, lambda: terrain(d, fi, fj, 1.6, 1.6)))
    if etat.get("mystere", 0) > 0:
        mi, mj = TERRAINS["mystere"]
        objs.append((mi + mj + 2, lambda mi=mi, mj=mj: mystere(d, mi, mj, etat["mystere"])))
    for n, (i, j, c) in enumerate(etat.get("habitants", [])):
        objs.append((i + j + 1, lambda i=i, j=j, c=c: habitant(d, i, j, c)))
    if etat.get("maire"):
        mi, mj = etat["maire"]
        x, y = iso(mi + 0.5, mj + 0.5)
        objs.append((mi + mj + 1, lambda x=x, y=y: character(
            d, x, y, sc=0.09 * HK, shirt=(40, 50, 90), pants=(40, 50, 90), hair=(70, 50, 40), arm=0.9, mouth="grin")))
    for _, fn in sorted(objs, key=lambda o: o[0]):
        fn()
    return big


_cache = {}


def carte_cache(etat):
    key = repr(sorted(etat.items()))
    if key not in _cache:
        if len(_cache) > 40:
            _cache.clear()
        _cache[key] = carte(etat)
    return _cache[key]


def camera(big, z=1.0, center=(540, 960)):
    """Cadre la carte. Renvoie (image 1080x1920, fonction monde→écran)."""
    w2, h2 = int(W * SS / z), int(H * SS / z)
    x0 = int(min(max(center[0] * SS - w2 / 2, 0), W * SS - w2))
    y0 = int(min(max(center[1] * SS - h2 / 2, 0), H * SS - h2))
    img = big.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.LANCZOS)

    def to_screen(i, j, zz=0.0):
        x, y = iso(i, j, zz)
        return (x * SS - x0) * W / w2, (y * SS - y0) * H / h2
    return img, to_screen
