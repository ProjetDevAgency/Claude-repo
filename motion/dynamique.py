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
    dx = int(160 * k) * sens
    out = img.copy()
    for j in range(1, 5):
        dec = Image.new("RGB", img.size, (0, 0, 0))
        dec.paste(img, (dx * j // 4, 0))
        out = Image.blend(out, dec, 0.5 / j)
    return out


def claque(lt, dur=0.18, amp=0.12):
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
                    img = fouet(img, 1 - l / 0.14 if l < 0.14 else 0, 1 if k % 2 else -1)
                return img
            t0 += d
        return plans[-1][1](lt, dur)
    f.__name__ = nom or "sequence"
    return f


# ───────────── fonds ─────────────

def fond_flou(fond, lt, k=1.0):
    """Le décor de l'histoire, flouté et assombri : on reste dans le lieu, l'objet passe devant."""
    return dim(plan(fond, lt, z=1.15), k, blur=16, dark=0.5)


def rayons(img, lt, col=(255, 255, 255), alpha=26):
    """Rayons qui tournent lentement derrière l'objet (donne du mouvement à un plan fixe)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = W // 2, 860
    for i in range(12):
        a = math.radians(i * 30 + lt * 12)
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


def titre_choc(img, mots, lt, y=440, size=96, pas=0.18, col=WHITE, accent=None):
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
        _pose(img, lay, W / 2, 1000 + math.sin(lt * 3) * 8, sc, rot=-3 + math.sin(lt * 2) * 1.5)
        _main(ImageDraw.Draw(img), W / 2 + 40, 1500)
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
