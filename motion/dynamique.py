"""Chantier visuel du 19 nov. (prompts/analyse_concurrent_laficelle.md) : plus de plans, plus de mouvement.

- sequence()      : une scène découpée en plusieurs plans courts, avec un coup de fouet (flou de mouvement) entre eux.
- inserts « objet du sujet », plein écran, pour ouvrir chaque vidéo autrement :
    insert_notif (téléphone en main + notification), insert_appli (solde qui change de couleur),
    insert_document (devis / facture / lettre avec le montant tamponné), insert_calendrier (pages qui tombent),
    insert_etiquette (étiquette de prix qui se balance), insert_compte (compte à rebours J-x).
- chiffre_anime() : un chiffre qui défile de a à b, l'ancien barré, rouge → vert.
- titre_choc()    : les mots-clés qui tombent un par un en haut de l'image.
- reaction()      : Kévin choqué, traits de choc, zoom qui claque.

Style maison (aplats, contours noirs, palette de cartoon.py) : on reprend des principes, jamais le look d'un autre compte.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from cartoon import FA, GREEN, INK, RED, WHITE, YEL, back, dim, ease, shock_lines
from engine import F, H, W
from recit import KHEAD, plan

SKIN = (243, 196, 160)
SKIN_D = (205, 150, 112)


# ───────────── montage ─────────────

def fouet(img, k, sens=1):
    """Coup de fouet : flou de mouvement horizontal qui s'éteint (k = 1 au début du plan, 0 à la fin)."""
    if k <= 0:
        return img
    dx = int(90 * k) * sens
    out = img.copy()
    for j in range(1, 5):
        dec = Image.new("RGB", img.size, (0, 0, 0))
        dec.paste(img, (dx * j // 4, 0))
        out = Image.blend(out, dec, 0.5 / j)
    return out


def claque(lt, dur=0.22, amp=0.06):
    """Zoom qui claque au début d'un plan : renvoie un facteur de zoom en plus (amp → 0)."""
    if lt >= dur:
        return 0.0
    return amp * (1 - ease(lt / dur))


def zoom_centre(img, z, cx=W // 2, cy=H // 2):
    if z <= 1.001:
        return img
    w, h = int(W / z), int(H / z)
    x0 = int(min(max(cx - w / 2, 0), W - w))
    y0 = int(min(max(cy - h / 2, 0), H - h))
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


def sequence(*plans, nom=None):
    """plans = [(durée, fn(lt, dur)), …] ; le dernier prend le temps restant. Coup de fouet + claque à chaque coupe."""
    def f(lt, dur):
        t0 = 0.0
        for k, (d, fn) in enumerate(plans):
            last = k == len(plans) - 1
            if last or lt < t0 + d:
                pl = (dur - t0) if last else d
                l = lt - t0
                img = fn(l, max(pl, 0.1))
                if k:
                    img = zoom_centre(img, 1 + claque(l))
                    img = fouet(img, 1 - l / 0.1 if l < 0.1 else 0, 1 if k % 2 else -1)
                return img
            t0 += d
        return plans[-1][1](lt, dur)
    f.__name__ = nom or "sequence"
    return f


# ───────────── fonds ─────────────

def fond_flou(fond, lt, k=1.0):
    """Le décor de l'histoire, flouté et assombri : on reste dans le lieu, l'objet passe devant."""
    return dim(plan(fond, lt, z=1.15 + 0.035 * lt, center=(540 + 30 * math.sin(lt * 0.8), 1000)), k, blur=16, dark=0.5)


def rayons(img, lt, col=(255, 255, 255), alpha=26):
    """Rayons qui tournent lentement derrière l'objet (donne du mouvement à un plan fixe)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = W // 2, 860
    for i in range(12):
        a = math.radians(i * 30 + lt * 22)
        b = a + math.radians(11)
        d.polygon([(cx, cy), (cx + 2000 * math.cos(a), cy + 2000 * math.sin(a)),
                   (cx + 2000 * math.cos(b), cy + 2000 * math.sin(b))], fill=col + (alpha,))
    img.paste(lay, (0, 0), lay)
    return img


def _pose(img, lay, cx, cy, sc=1.0, rot=0.0):
    if rot:
        lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    if sc != 1.0:
        lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
    img.paste(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)), lay)


# ───────────── chiffres et titres ─────────────

def _fmt(v, unite):
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",") if isinstance(v, float) and v % 1 else f"{int(v):,}".replace(",", " ")
    return f"{s} {unite}".strip()


def chiffre_anime(img, xy, a, b, lt, t0=0.3, dur=0.7, unite="€", size=170, sous=None, barre=True):
    """Le chiffre a s'affiche, se fait barrer, puis b défile jusqu'à sa valeur. b < a → rouge ; b > a → vert."""
    x, y = xy
    d = ImageDraw.Draw(img)
    if lt < t0:
        k = back(lt / 0.25)
        f = FA(max(10, int(size * (0.5 + 0.5 * k))))
        d.text((x + 6, y + 8), _fmt(a, unite), font=f, fill=(0, 0, 0), anchor="mm")
        d.text((x, y), _fmt(a, unite), font=f, fill=WHITE, anchor="mm")
        return
    k = ease((lt - t0) / dur)
    v = a + (b - a) * k
    v = round(v, 2) if isinstance(b, float) else int(round(v))
    col = GREEN if b > a else RED
    if barre:
        fa = FA(int(size * 0.5))
        ta = _fmt(a, unite)
        ya = y - size * 0.85
        d.text((x, ya), ta, font=fa, fill=(200, 200, 210), anchor="mm")
        w = fa.getlength(ta)
        d.line([x - w / 2 - 8, ya + 4, x + w / 2 + 8, ya - 4], fill=RED, width=10)
    f = FA(size)
    d.text((x + 6, y + 8), _fmt(v, unite), font=f, fill=(0, 0, 0), anchor="mm")
    d.text((x, y), _fmt(v, unite), font=f, fill=col if k > 0.05 else WHITE, anchor="mm")
    if sous:
        d.text((x, y + size * 0.72), sous, font=FA(int(size * 0.3)), fill=WHITE, anchor="mm")


def titre_choc(img, mots, lt, y=440, size=96, pas=0.26, col=WHITE, accent=None):
    """Les mots tombent un par un en haut de l'image (le mot `accent` en jaune, sur bandeau rouge)."""
    d = ImageDraw.Draw(img)
    f = FA(size)
    lignes, cur = [], []
    for m in mots:
        if cur and f.getlength(" ".join(cur + [m])) > 960:
            lignes.append(cur)
            cur = []
        cur.append(m)
    lignes.append(cur)
    i = 0
    for j, ligne in enumerate(lignes):
        larg = f.getlength(" ".join(ligne))
        x = W / 2 - larg / 2
        yy = y + j * (size + 18)
        for m in ligne:
            k = (lt - i * pas) / 0.16
            i += 1
            w = f.getlength(m)
            if k > 0:
                dy = int((1 - back(min(k, 1))) * -60)
                if m == accent:
                    d.rounded_rectangle([x - 12, yy - size * 0.62 + dy, x + w + 12, yy + size * 0.62 + dy], radius=14, fill=RED)
                    d.text((x + w / 2, yy + dy), m, font=f, fill=YEL, anchor="mm")
                else:
                    d.text((x + w / 2 + 5, yy + 6 + dy), m, font=f, fill=(0, 0, 0), anchor="mm")
                    d.text((x + w / 2, yy + dy), m, font=f, fill=col, anchor="mm")
            x += w + f.getlength(" ")


# ───────────── inserts « objet du sujet » ─────────────

def _main(d, cx, cy, sc=1.0):
    """Une main (pouce devant) qui tient un objet par le bas."""
    s = sc
    d.rounded_rectangle([cx - 150 * s, cy - 40 * s, cx + 150 * s, cy + 260 * s], radius=int(90 * s), fill=SKIN, outline=INK, width=6)
    d.rounded_rectangle([cx - 190 * s, cy - 130 * s, cx - 100 * s, cy + 60 * s], radius=int(45 * s), fill=SKIN, outline=INK, width=6)
    d.rectangle([cx - 160 * s, cy + 200 * s, cx + 160 * s, cy + 420 * s], fill=(46, 150, 90), outline=INK, width=6)


def insert_notif(fond, app, titre, msg, heure="12:30", col=(52, 199, 89), mots=None, accent=None):
    """Téléphone tenu en main, l'écran s'allume, la notification tombe (t = 0,25 s)."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt)
        lay = Image.new("RGBA", (640, 1180), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, 639, 1179], radius=80, fill=(20, 20, 26, 255))
        allume = min(1.0, lt / 0.15)
        ecran = tuple(int(c * allume) for c in (40, 50, 96))
        d.rounded_rectangle([22, 22, 617, 1157], radius=64, fill=ecran + (255,))
        d.rounded_rectangle([250, 40, 390, 80], radius=20, fill=(20, 20, 26, 255))
        if allume >= 1:
            d.text((320, 230), heure, font=F(140), fill=WHITE + (255,), anchor="mm")
        k = ease((lt - 0.25) / 0.3)
        if k > 0:
            y = int(360 - (1 - k) * 260)
            d.rounded_rectangle([40, y, 600, y + 200], radius=36, fill=(246, 246, 250, 250))
            d.rounded_rectangle([64, y + 50, 160, y + 146], radius=26, fill=col + (255,))
            d.text((112, y + 98), app[0], font=F(52), fill=WHITE + (255,), anchor="mm")
            d.text((186, y + 70), titre, font=F(40), fill=INK + (255,), anchor="lm")
            d.text((186, y + 140), msg, font=F(36), fill=(90, 90, 100, 255), anchor="lm")
        sc = 0.9 + 0.1 * back(lt / 0.3)
        _pose(img, lay, W / 2, 1070 + math.sin(lt * 3) * 8, sc * 0.9, rot=-3 + math.sin(lt * 2) * 1.5)
        _main(ImageDraw.Draw(img), W / 2 + 40, 1540)
        if mots:
            titre_choc(img, mots, lt - 0.35, accent=accent)
        return img
    return f


def insert_appli(fond, label, a, b, unite="€", t_change=0.5, mots=None, accent=None, sous=None):
    """Écran d'appli (banque, bourse) : le solde a défile vers b, l'ancien est barré."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=(GREEN if b > a else RED))
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 140, 560, 940, 1500
        d.rounded_rectangle([x0, y0, x1, y1], radius=60, fill=(24, 24, 32), outline=INK, width=8)
        d.rounded_rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24], radius=44, fill=(245, 246, 250))
        d.rectangle([x0 + 24, y0 + 60, x1 - 24, y0 + 170], fill=(60, 90, 200))
        d.text((W / 2, y0 + 115), label, font=FA(52), fill=WHITE, anchor="mm")
        chiffre_anime(img, (W / 2, 1020), a, b, lt, t0=t_change, unite=unite, size=150, sous=None)
        if sous and lt > t_change + 0.6:
            tk = ease((lt - t_change - 0.6) / 0.25)
            d.rounded_rectangle([x0 + 70, 1220, x1 - 70, 1330], radius=24, fill=(RED if b < a else GREEN))
            d.text((W / 2, 1275), sous, font=FA(int(54 * (0.6 + 0.4 * tk))), fill=WHITE, anchor="mm")
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def insert_document(fond, titre, lignes, montant, tampon=None, t_tampon=0.9, mots=None, accent=None):
    """Feuille (devis, facture, lettre) qui arrive en tournant ; le montant est entouré, puis un tampon claque."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=YEL, alpha=20)
        lay = Image.new("RGBA", (760, 1000), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle([0, 0, 759, 999], fill=(252, 252, 248, 255), outline=INK + (255,), width=6)
        d.text((48, 90), titre, font=FA(64), fill=INK + (255,), anchor="lm")
        d.line([48, 150, 712, 150], fill=(200, 200, 205, 255), width=4)
        for j, l in enumerate(lignes):
            d.text((48, 220 + j * 70), l, font=F(38), fill=(70, 70, 80, 255), anchor="lm")
        ym = 300 + len(lignes) * 70
        d.text((712, ym), montant, font=FA(110), fill=RED + (255,), anchor="rm")
        ke = ease((lt - 0.5) / 0.3)
        if ke > 0:
            w = FA(110).getlength(montant)
            d.arc([712 - w - 40, ym - 90, 732, ym + 90], 200, 200 + 330 * ke, fill=RED + (255,), width=10)
        if tampon and lt > t_tampon:
            sk = back((lt - t_tampon) / 0.25)
            sl = Image.new("RGBA", (520, 170), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sl)
            sd.rounded_rectangle([8, 8, 511, 161], radius=20, outline=RED + (255,), width=10)
            sd.text((260, 85), tampon, font=FA(int(80 * (1.5 - 0.5 * sk))), fill=RED + (255,), anchor="mm")
            sl = sl.rotate(14, expand=True, resample=Image.BICUBIC)
            lay.paste(sl, (120, 640), sl)
        k = back(lt / 0.35)
        _pose(img, lay, W / 2, 1020, 0.6 + 0.4 * k, rot=(1 - ease(lt / 0.35)) * -25 + 3)
        if mots:
            titre_choc(img, mots, lt - 0.2, accent=accent)
        return img
    return f


def insert_calendrier(fond, mois, de, a, legende=None, mots=None, accent=None):
    """Bloc calendrier : les pages tombent de `de` à `a` (une page toutes les 0,08 s)."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt)
        d = ImageDraw.Draw(img)
        n = a - de
        jour = de + min(n, int(max(0.0, lt - 0.3) / 0.08)) if n > 0 else a
        x0, y0, x1, y1 = 240, 620, 840, 1300
        d.rounded_rectangle([x0 + 14, y0 + 18, x1 + 14, y1 + 18], radius=30, fill=(0, 0, 0))
        d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=WHITE, outline=INK, width=8)
        d.rounded_rectangle([x0, y0, x1, y0 + 160], radius=30, fill=RED, outline=INK, width=8)
        d.text((W / 2, y0 + 82), mois.upper(), font=FA(80), fill=WHITE, anchor="mm")
        d.text((W / 2, y0 + 400), str(jour), font=FA(330), fill=INK, anchor="mm")
        if legende and jour == a:
            d.text((W / 2, y1 - 70), legende, font=FA(50), fill=RED, anchor="mm")
        # la page qui s'envole
        ph = (lt - 0.3) % 0.08 / 0.08 if 0.3 < lt < 0.3 + n * 0.08 else None
        if ph is not None:
            lay = Image.new("RGBA", (600, 520), (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([0, 0, 599, 519], fill=(250, 250, 250, 230), outline=INK + (255,), width=6)
            _pose(img, lay, W / 2 + ph * 500, 1000 - ph * 600, 1.0 - ph * 0.4, rot=ph * 50)
        if mots:
            titre_choc(img, mots, lt - 0.2, accent=accent)
        return img
    return f


def insert_etiquette(fond, objet, prix, mots=None, accent=None):
    """Étiquette de prix attachée à une ficelle, qui se balance ; l'objet écrit dessus."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=YEL, alpha=22)
        ang = 18 * math.exp(-lt * 1.6) * math.sin(lt * 9)
        lay = Image.new("RGBA", (700, 900), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.line([350, 0, 350, 260], fill=INK + (255,), width=8)
        d.polygon([(130, 360), (350, 230), (570, 360), (570, 860), (130, 860)], fill=YEL + (255,), outline=INK + (255,))
        d.ellipse([325, 290, 375, 340], fill=(40, 40, 50, 255))
        d.text((350, 500), objet, font=FA(64), fill=INK + (255,), anchor="mm")
        d.text((350, 680), prix, font=FA(150), fill=RED + (255,), anchor="mm")
        _pose(img, lay, W / 2, 900, 0.7 + 0.3 * back(lt / 0.3), rot=ang)
        if mots:
            titre_choc(img, mots, lt - 0.2, accent=accent)
        return img
    return f


def insert_compte(fond, j, legende, mots=None, accent=None):
    """Compte à rebours : « J-x » qui claque, avec la date limite."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=RED, alpha=24)
        d = ImageDraw.Draw(img)
        k = back(lt / 0.25)
        f_ = FA(max(10, int(300 * (0.5 + 0.5 * k))))
        d.text((W / 2 + 8, 1000 + 10), f"J-{j}", font=f_, fill=(0, 0, 0), anchor="mm")
        d.text((W / 2, 1000), f"J-{j}", font=f_, fill=RED, anchor="mm")
        if lt > 0.4:
            d.text((W / 2, 1220), legende, font=FA(60), fill=WHITE, anchor="mm")
        if mots:
            titre_choc(img, mots, lt - 0.2, accent=accent)
        return img
    return f


# ───────────── réactions ─────────────

def reaction(fond, mots=None, accent=None, devant=None, **kextra):
    """Kévin choqué en gros plan : traits de choc, tremblement, zoom qui claque."""
    def f(lt, dur):
        img = plan(fond, lt, "choc", devant=devant, z=1.9 + claque(lt, 0.2, 0.25), center=(KHEAD[0] + 40, KHEAD[1] + 60), **kextra)
        shock_lines(img, W // 2 - 40, 640, 330, lt)
        if mots:
            titre_choc(img, mots, lt - 0.05, accent=accent)
        return img
    return f


__all__ = ["sequence", "fouet", "claque", "zoom_centre", "fond_flou", "rayons", "chiffre_anime", "titre_choc",
           "insert_notif", "insert_appli", "insert_document", "insert_calendrier", "insert_etiquette", "insert_compte",
           "reaction"]


# ───────────── illustrations : ce qu'on voit = ce qui est dit (correction du client, 19 nov.) ─────────────

def _lisse(t):
    return ease(max(0.0, min(1.0, t)))


def graphique(fond, points, t_trace=1.6, titre="ANT", reperes=(), limite=None, limite_txt=None, unite="$",
              mots=None, accent=None, depart=None):
    """Courbe de cours qui se dessine de gauche à droite, avec le prix qui suit la pointe.
    points : prix successifs ; reperes : [(indice, texte)] posés sur la courbe une fois atteints ;
    limite : prix d'une ligne horizontale pointillée (ordre à cours limité)."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 90, 600, 990, 1420
        d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(18, 20, 30), outline=INK, width=8)
        d.text((x0 + 50, y0 + 70), titre, font=FA(64), fill=WHITE, anchor="lm")
        vals = list(points) + ([limite] if limite else [])
        lo, hi = min(vals) * 0.97, max(vals) * 1.02
        gx0, gx1, gy0, gy1 = x0 + 60, x1 - 60, y0 + 150, y1 - 80

        def P(i, v):
            return gx0 + (gx1 - gx0) * i / (len(points) - 1), gy1 - (gy1 - gy0) * (v - lo) / (hi - lo)
        for k in range(1, 4):                                         # grille
            yy = gy0 + (gy1 - gy0) * k / 4
            d.line([gx0, yy, gx1, yy], fill=(45, 48, 62), width=2)
        if limite:
            ly = P(0, limite)[1]
            for xx in range(int(gx0), int(gx1), 40):
                d.line([xx, ly, xx + 22, ly], fill=YEL, width=6)
            if limite_txt:
                d.text((gx0 + 6, ly + 34), limite_txt, font=FA(40), fill=YEL, anchor="lm")
        p = _lisse(lt / t_trace) * (len(points) - 1)
        n = int(p)
        pts = [P(i, points[i]) for i in range(n + 1)]
        if n < len(points) - 1:
            a, b = points[n], points[n + 1]
            v = a + (b - a) * (p - n)
            pts.append(P(p, v))
        else:
            v = points[-1]
        ref = points[0] if depart is None else depart
        col = GREEN if v >= ref else RED
        if len(pts) > 1:
            d.line(pts, fill=col, width=10, joint="curve")
        tx, ty = pts[-1]
        d.ellipse([tx - 16, ty - 16, tx + 16, ty + 16], fill=WHITE, outline=col, width=6)
        txt = _fmt(round(v, 2) if isinstance(points[-1], float) or v % 1 else v, unite)
        w = FA(54).getlength(txt)
        bx = min(max(tx - w / 2 - 20, x0 + 20), x1 - w - 60)
        d.rounded_rectangle([bx, ty - 110, bx + w + 40, ty - 40], radius=18, fill=col)
        d.text((bx + 20 + w / 2, ty - 75), txt, font=FA(54), fill=INK if col == GREEN else WHITE, anchor="mm")
        for i, lab in reperes:
            if p >= i:
                rx, ry = P(i, points[i])
                d.ellipse([rx - 12, ry - 12, rx + 12, ry + 12], fill=YEL)
                d.text((rx, ry + 52 if points[i] < points[0] else ry + 52), lab, font=FA(36), fill=YEL, anchor="mm")
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def defile_prix(fond, prix, titre="ORDRE AU MARCHÉ", fin_txt="ACHETÉ", unite="$", pas=0.28, mots=None, accent=None):
    """Écran de cotation : les prix défilent vite, chacun plus haut ; au dernier, le tampon tombe."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=RED, alpha=18)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([110, 640, 970, 1320], radius=40, fill=(14, 16, 24), outline=INK, width=8)
        d.text((W / 2, 720), titre, font=FA(58), fill=YEL, anchor="mm")
        i = min(len(prix) - 1, int(max(0.0, lt) / pas))
        if i:                                                          # le prix précédent, plus petit, au-dessus
            d.text((W / 2, 850), _fmt(prix[i - 1], unite), font=FA(52), fill=(110, 115, 130), anchor="mm")
        k = back(((lt % pas) / 0.15) if i < len(prix) - 1 else min(1, (lt - i * pas) / 0.15))
        d.text((W / 2, 1020), _fmt(prix[i], unite), font=FA(int(150 * (0.7 + 0.3 * k))), fill=RED if i else WHITE, anchor="mm")
        if i == len(prix) - 1 and lt > i * pas + 0.3:
            sk = back((lt - i * pas - 0.3) / 0.25)
            sl = Image.new("RGBA", (560, 170), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sl)
            sd.rounded_rectangle([8, 8, 551, 161], radius=20, outline=RED + (255,), width=10)
            sd.text((280, 85), fin_txt, font=FA(int(84 * (1.5 - 0.5 * sk))), fill=RED + (255,), anchor="mm")
            _pose(img, sl, W / 2, 1210, 1.0, rot=-10)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def livret(fond, titre="LIVRET", lignes=(), total=None, dort=False, mots=None, accent=None, t_ligne=0.35):
    """Livret d'épargne ouvert : les lignes de versement s'ajoutent une par une ; dort=True → des « Z » qui montent."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        d = ImageDraw.Draw(img)
        x0, y0 = 170, 640
        d.rounded_rectangle([x0 + 14, y0 + 18, x0 + 754, y0 + 718], radius=26, fill=(0, 0, 0))
        d.rounded_rectangle([x0, y0, x0 + 740, y0 + 700], radius=26, fill=(60, 110, 200), outline=INK, width=8)
        d.rectangle([x0 + 30, y0 + 120, x0 + 710, y0 + 670], fill=(252, 252, 246), outline=INK, width=4)
        d.text((x0 + 370, y0 + 62), titre, font=FA(62), fill=WHITE, anchor="mm")
        for j, (a, b) in enumerate(lignes):
            if lt > 0.2 + j * t_ligne:
                yy = y0 + 175 + j * 62
                d.text((x0 + 60, yy), a, font=F(34), fill=(80, 80, 90), anchor="lm")
                d.text((x0 + 680, yy), b, font=F(34), fill=(30, 130, 70), anchor="rm")
        if total and lt > 0.2 + len(lignes) * t_ligne:
            k = back((lt - 0.2 - len(lignes) * t_ligne) / 0.25)
            d.text((x0 + 680, y0 + 610), total, font=FA(int(70 * (0.6 + 0.4 * k))), fill=INK, anchor="rm")
        if dort:
            for j in range(3):
                ph = (lt * 0.7 + j / 3) % 1
                zz = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                ImageDraw.Draw(zz).text((80, 80), "Z", font=FA(int(70 + 50 * ph)), fill=WHITE + (int(255 * (1 - ph)),), anchor="mm")
                _pose(img, zz, x0 + 640 + ph * 120, y0 - 40 - ph * 260, 1.0, rot=-15)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def billets_envoles(img, lt, cx=540, cy=1100, n=9, t0=0.0, seed=3):
    """Des billets qui s'échappent d'un point et s'envolent en tournant (« envolés »)."""
    if lt < t0:
        return img
    for j in range(n):
        ph = (lt - t0) * 0.9 - j * 0.12
        if ph <= 0 or ph > 1.6:
            continue
        ang = (j * 47 + seed * 13) % 360
        dx = math.cos(math.radians(ang)) * 380 * ph + math.sin(ph * 6 + j) * 40
        dy = -520 * ph - 80 * j % 120
        b = Image.new("RGBA", (190, 100), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([4, 4, 185, 95], radius=10, fill=(110, 190, 120, 255), outline=INK + (255,), width=5)
        bd.ellipse([70, 25, 120, 75], outline=INK + (255,), width=4)
        bd.text((95, 50), "€", font=F(36), fill=INK + (255,), anchor="mm")
        _pose(img, b, cx + dx, cy + dy, 1.0 - 0.3 * min(ph, 1), rot=ph * 260 + j * 30)
    return img


def vapeur(img, lt, x, y):
    """Vapeur qui monte d'un plat chaud."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for j in range(3):
        ph = (lt * 0.6 + j / 3) % 1
        xx = x + (j - 1) * 40 + math.sin(ph * 7 + j) * 18
        yy = y - ph * 160
        r = 14 + ph * 22
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 255, 255, int(150 * (1 - ph))))
    img.paste(lay, (0, 0), lay)
    return img


__all__ += ["graphique", "defile_prix", "livret", "billets_envoles", "vapeur"]


# ───────────── scènes de dialogue vivantes (gestes liés au texte, caméra qui glisse) ─────────────

def cle(lt, keys):
    """Interpolation douce entre des clés [(t, valeur)]."""
    if lt <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if lt <= t1:
            return v0 + (v1 - v0) * ease((lt - t0) / max(t1 - t0, 0.01))
    return keys[-1][1]


def geste_parle(lt, base=0.35, amp=0.3, vite=3.5):
    """Bras qui accompagne la parole + bouche qui bouge."""
    return dict(arm=base + amp * abs(math.sin(lt * vite)), mouth="o" if int(lt * 7) % 2 else "grin")


def tags_flottants(img, lt, tags, y0=420):
    """Bandeaux qui arrivent puis flottent doucement (au lieu de rester figés)."""
    from cartoon import tag
    for k, (txt, col, t0) in enumerate(tags):
        fg = INK if col in (YEL, WHITE, GREEN) else WHITE
        rot = (-3, 2, -2)[k % 3] + 1.5 * math.sin(lt * 2.2 + k)
        tag(img, 540 + 10 * math.sin(lt * 1.7 + k), y0 + 140 * k + 6 * math.sin(lt * 2.6 + k), txt,
            54 if len(txt) < 22 else 46, col, fg, rot=rot, k=(lt - t0) / 0.3)


def vapeur_devant(devant, x=570, y=1380):
    """Le premier plan + de la vapeur qui monte du plat, dessinée dans le décor (elle suit la caméra)."""
    from cartoon import SS
    def g(d, t):
        devant(d, t)
        for j in range(3):
            ph = (t * 0.6 + j / 3) % 1
            xx = (x + (j - 1) * 36 + math.sin(ph * 7 + j) * 16) * SS
            yy = (y - ph * 150) * SS
            r = (16 - ph * 10) * SS
            c = int(235 - ph * 60)
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(c, c, c + 5))
    return g


def dialogue(fond, look, kpose="neutre", mechant=None, autres=(), devant=None, pan=((0, 540),), zoom=((0, 1.2),),
             cy=1000, kx=None, mx=None, tags=(), mots=None, accent=None, kextra=None):
    """Plan de dialogue vivant. mechant / autres / kextra peuvent être des fonctions du temps (lt → dict / liste)."""
    from recit import KX, MX
    def f(lt, dur):
        m = mechant(lt) if callable(mechant) else mechant
        a = autres(lt) if callable(autres) else autres
        kx_ = kextra(lt) if callable(kextra) else (kextra or {})
        img = plan(fond, lt, kpose, kx=kx or KX, mechant=m, look=look, mx=mx or MX, autres=a, devant=devant,
                   z=cle(lt, list(zoom)), center=(cle(lt, list(pan)), cy), **kx_)
        if tags:
            tags_flottants(img, lt, tags)
        if mots:
            titre_choc(img, mots, lt - 0.05, accent=accent)
        return img
    return f


def gp_vivant(fond, look, lignes, devant=None, z=(1.9, 2.1), secoue=False, base=0.4, amp=0.35, mots_bulle=56, **pose):
    """Gros plan du méchant qui parle EN GESTICULANT, la caméra respire, la bulle arrive."""
    from cartoon import bubble, flash, shake
    from recit import MHEAD, push
    def f(lt, dur):
        p = {**geste_parle(lt, base, amp), **pose}
        img = plan(fond, lt, mechant=p, look=look, devant=devant, z=push(lt, dur, *z),
                   center=(MHEAD[0] - 40 + 18 * math.sin(lt * 1.4), MHEAD[1] + 40 + 10 * math.sin(lt * 1.1)))
        bubble(img, 540, 560, lignes, mots_bulle, lt / 0.25, tail_x=660)
        img = flash(img, lt)
        return shake(img, lt) if secoue else img
    return f


def echo_vivant(fond, txt, devant=None, **kextra):
    """L'écho : Kévin en gros plan qui encaisse, la caméra se rapproche, les mots pulsent."""
    from cartoon import dim as _dim
    from recit import KHEAD, push
    def f(lt, dur):
        img = plan(fond, lt, "triste", devant=devant, z=push(lt, dur, 1.95, 2.35), center=(KHEAD[0] + 40, KHEAD[1] + 40), **kextra)
        img = _dim(img, 0.6)
        t = f"« {txt} »"
        size = 92
        while FA(size).getlength(t) > 960 and size > 50:
            size -= 4
        s = int(size * (1 + 0.04 * math.sin(lt * 5)) * (0.6 + 0.4 * back(lt / 0.3)))
        d = ImageDraw.Draw(img)
        d.text((546, 478), t, font=FA(s), fill=(0, 0, 0), anchor="mm")
        d.text((540, 470), t, font=FA(s), fill=WHITE, anchor="mm")
        return img
    return f


__all__ += ["cle", "geste_parle", "tags_flottants", "vapeur_devant", "dialogue", "gp_vivant", "echo_vivant"]


# ───────────── illustrations « arnaques en ligne » (épisode 4 du feuilleton) ─────────────

def liste_noire(fond, titre="LISTE NOIRE · AMF", trouve=None, t_trouve=0.9, mots=None, accent=None, n=9):
    """Une liste officielle qui défile (noms masqués) ; trouve=texte → une ligne rouge surlignée + tampon."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 130, 600, 950, 1460
        d.rounded_rectangle([x0 + 14, y0 + 18, x1 + 14, y1 + 18], radius=24, fill=(0, 0, 0))
        d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(250, 250, 248), outline=INK, width=8)
        d.rounded_rectangle([x0, y0, x1, y0 + 120], radius=24, fill=(24, 24, 30))
        d.text((W / 2, y0 + 62), titre, font=FA(58), fill=WHITE, anchor="mm")
        scroll = (lt * 160) % 90 if trouve is None or lt < t_trouve else 0
        for j in range(n):
            yy = y0 + 170 + j * 90 - scroll
            if yy < y0 + 140 or yy > y1 - 50:
                continue
            w = 260 + (j * 137) % 300
            ligne_trouvee = trouve and lt >= t_trouve and j == 4
            if ligne_trouvee:
                k = ease((lt - t_trouve) / 0.25)
                d.rectangle([x0 + 30, yy - 34, x0 + 30 + (x1 - x0 - 60) * k, yy + 34], fill=RED)
                d.text((x0 + 60, yy), trouve, font=FA(48), fill=WHITE, anchor="lm")
            else:
                d.rounded_rectangle([x0 + 60, yy - 14, x0 + 60 + w, yy + 14], radius=14, fill=(200, 200, 206))
                d.text((x1 - 60, yy), ".com", font=F(30), fill=(150, 150, 160), anchor="rm")
        if trouve and lt > t_trouve + 0.4:
            sk = back((lt - t_trouve - 0.4) / 0.25)
            sl = Image.new("RGBA", (520, 170), (0, 0, 0, 0))
            sd = ImageDraw.Draw(sl)
            sd.rounded_rectangle([8, 8, 511, 161], radius=20, outline=RED + (255,), width=10)
            sd.text((260, 85), "SUR LA LISTE", font=FA(int(76 * (1.5 - 0.5 * sk))), fill=RED + (255,), anchor="mm")
            _pose(img, sl, W / 2 + 120, 1320, 1.0, rot=-12)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def recherche(fond, champ, texte, resultat=None, col=RED, t_resultat=None, mots=None, accent=None, vitesse=14):
    """Barre de recherche : le texte se tape lettre par lettre, puis la carte de résultat tombe."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, alpha=16)
        d = ImageDraw.Draw(img)
        d.text((W / 2, 690), champ, font=FA(52), fill=YEL, anchor="mm")
        d.rounded_rectangle([110, 760, 970, 880], radius=60, fill=WHITE, outline=INK, width=8)
        d.ellipse([150, 790, 210, 850], outline=(120, 120, 130), width=8)
        d.line([200, 840, 225, 865], fill=(120, 120, 130), width=8)
        n = min(len(texte), int(max(0.0, lt - 0.2) * vitesse))
        t = texte[:n] + ("|" if int(lt * 3) % 2 and n < len(texte) else "")
        d.text((250, 820), t, font=F(48), fill=INK, anchor="lm")
        t_r = t_resultat if t_resultat is not None else 0.4 + len(texte) / vitesse
        if resultat and lt > t_r:
            k = back((lt - t_r) / 0.3)
            lay = Image.new("RGBA", (860, 300), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([0, 0, 859, 299], radius=30, fill=(252, 252, 250, 255), outline=col + (255,), width=10)
            for j, l in enumerate(resultat):
                ld.text((430, 90 + j * 110), l, font=FA(64 if j == 0 else 48), fill=(col if j == 0 else INK) + (255,), anchor="mm")
            _pose(img, lay, W / 2, 1120, 0.7 + 0.3 * k)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def conversation(fond, contact, messages, mots=None, accent=None):
    """Téléphone tenu en main avec une messagerie : messages = [(cote 'moi'|'lui'|'info', texte, t0)]."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        lay = Image.new("RGBA", (640, 1180), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, 639, 1179], radius=80, fill=(20, 20, 26, 255))
        d.rounded_rectangle([22, 22, 617, 1157], radius=64, fill=(236, 229, 221, 255))
        d.rectangle([22, 90, 617, 200], fill=(40, 120, 100, 255))
        d.ellipse([48, 112, 116, 180], fill=(200, 200, 205, 255))
        d.text((140, 146), contact, font=F(38), fill=WHITE + (255,), anchor="lm")
        y = 250
        for cote, txt, t0 in messages:
            if lt < t0:
                continue
            k = back((lt - t0) / 0.25)
            fnt = F(32)
            lignes, cur = [], ""
            for m in txt.split():
                if fnt.getlength((cur + " " + m).strip()) > 380:
                    lignes.append(cur)
                    cur = m
                else:
                    cur = (cur + " " + m).strip()
            lignes.append(cur)
            h = 30 + 44 * len(lignes)
            w = max(fnt.getlength(l) for l in lignes) + 50
            if cote == "info":
                d.rounded_rectangle([320 - w / 2, y, 320 + w / 2, y + h], radius=20, fill=(255, 236, 200, 255))
                x = 320 - w / 2 + 25
                col = (150, 60, 40, 255)
            elif cote == "moi":
                d.rounded_rectangle([590 - w, y, 590, y + h], radius=24, fill=(214, 248, 196, 255))
                x = 590 - w + 25
                col = INK + (255,)
            else:
                d.rounded_rectangle([50, y, 50 + w, y + h], radius=24, fill=(255, 255, 255, 255))
                x = 75
                col = INK + (255,)
            if k > 0.3:
                for j, l in enumerate(lignes):
                    d.text((x, y + 37 + j * 44), l, font=fnt, fill=col, anchor="lm")
            y += h + 24
        _pose(img, lay, W / 2, 1070 + math.sin(lt * 2.5) * 6, 0.9, rot=-2 + math.sin(lt * 1.8))
        _main(ImageDraw.Draw(img), W / 2 + 40, 1540)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


def tel_voiture(fond, legende="+20 % / SEMAINE", mots=None, accent=None):
    """Le téléphone du frère montre un gars et sa voiture de sport qui défile (vidéo des réseaux)."""
    def f(lt, dur):
        img = fond_flou(fond, lt)
        rayons(img, lt, col=YEL, alpha=18)
        lay = Image.new("RGBA", (640, 1180), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, 639, 1179], radius=80, fill=(20, 20, 26, 255))
        d.rounded_rectangle([22, 22, 617, 1157], radius=64, fill=(30, 34, 60, 255))
        d.rectangle([22, 760, 617, 1157], fill=(60, 60, 70, 255))                     # la route
        for k in range(6):
            xx = (k * 160 - lt * 600) % 760 - 80
            d.rectangle([xx, 900, xx + 90, 915], fill=(230, 230, 230, 255))
        cx = 320 + math.sin(lt * 2) * 20
        d.rounded_rectangle([cx - 230, 650, cx + 230, 790], radius=50, fill=(220, 40, 50, 255), outline=INK + (255,), width=6)
        d.polygon([(cx - 130, 650), (cx - 60, 570), (cx + 90, 570), (cx + 160, 650)], fill=(200, 30, 40, 255), outline=INK + (255,))
        for wx in (cx - 140, cx + 140):
            d.ellipse([wx - 50, 740, wx + 50, 840], fill=(30, 30, 34, 255), outline=(120, 120, 120, 255), width=8)
        d.rounded_rectangle([60, 120, 580, 240], radius=30, fill=(0, 0, 0, 160))
        d.text((320, 180), legende, font=FA(66), fill=GREEN + (255,), anchor="mm")
        d.text((320, 1080), "♥  12 k      ➤", font=F(40), fill=WHITE + (255,), anchor="mm")
        _pose(img, lay, W / 2, 1070, 0.8 + 0.1 * back(lt / 0.3), rot=-3 + math.sin(lt * 2) * 1.5)
        _main(ImageDraw.Draw(img), W / 2 + 40, 1540)
        if mots:
            titre_choc(img, mots, lt - 0.1, accent=accent)
        return img
    return f


__all__ += ["liste_noire", "recherche", "conversation", "tel_voiture"]


# ───────────── ouverture : un visage dès la 1re image (correction du client, 20 nov.) ─────────────

def visage_chiffre(fond, look, txt, sous=None, devant=None, couleur=None, mots=None, accent=None, **pose):
    """1er plan de chaque vidéo : le méchant en gros plan qui parle (visage visible à la 1re image), le chiffre
    en grand AU-DESSUS de sa tête (jamais sur le visage). Puis l'objet du sujet au plan suivant."""
    from cartoon import big_number
    from recit import MHEAD
    def f(lt, dur):
        p = {**geste_parle(lt, 0.45, 0.3), **pose}
        img = plan(fond, lt, mechant=p, look=look, devant=devant, z=1.9 + 0.12 * ease(lt / max(dur, 0.1)),
                   center=(MHEAD[0] - 40 + 14 * math.sin(lt * 1.4), MHEAD[1] + 40))
        big_number(img, (540, 430), txt, 150, couleur or YEL, sous, k=min(1.0, 0.35 + lt / 0.25), rot=-3)
        if mots:
            titre_choc(img, mots, lt - 0.05, y=300, accent=accent)
        return img
    return f


__all__ += ["visage_chiffre"]
