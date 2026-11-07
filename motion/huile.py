"""Vidéo éco : l'Espagne bloque 188 000 tonnes d'huile d'olive (lundi 9 novembre 2026)."""
import argparse
import math

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, bar, ease, fmt, lerp,
                    load_country, mix, pop_text, tag, text)

CY = 760
OIL = (196, 170, 40)


def bottle(d, x, y, s, fill=1.0, lock=False, price=None):
    """Bouteille d'huile en aplat (y = bas de la bouteille)."""
    w, h = 0.55 * s, 1.3 * s
    body = [x - w / 2, y - h, x + w / 2, y]
    d.rounded_rectangle(body, radius=int(0.18 * s), outline=WHITE, width=8)
    d.rectangle([x - 0.13 * s, y - h - 0.38 * s, x + 0.13 * s, y - h + 6], outline=WHITE, width=8)
    d.rectangle([x - 0.17 * s, y - h - 0.5 * s, x + 0.17 * s, y - h - 0.36 * s], fill=GREEN)
    if fill > 0:
        top = y - 12 - (h - 24) * fill
        d.rounded_rectangle([x - w / 2 + 12, top, x + w / 2 - 12, y - 12], radius=int(0.12 * s), fill=OIL)
    d.rounded_rectangle([x - w / 2 + 20, y - 0.75 * h, x + w / 2 - 20, y - 0.45 * h], radius=10, fill=WHITE)
    text(d, (x, y - 0.6 * h), "OLIVE", int(0.13 * s), BG)
    if lock:
        lx, ly, r = x + 0.3 * s, y - 0.25 * h, 0.22 * s
        d.arc([lx - r * 0.6, ly - r * 1.3, lx + r * 0.6, ly - r * 0.1], 180, 360, fill=RED, width=14)
        d.rounded_rectangle([lx - r, ly - r * 0.5, lx + r, ly + r * 0.8], radius=12, fill=RED)
    if price:
        tag(d, x - 0.35 * s, y - 0.95 * h, price, int(0.16 * s), YELLOW, BG)


def s_hook(d, img, lt, dur):
    k = back(lt / 0.5)
    bottle(d, 540, CY + 200, 380 * max(0.3, k), fill=0.85, lock=lt > 1.6)
    if lt > 2.0:
        tag(d, 540, CY + 320, "INTERDIT À LA VENTE", 52, RED)


ESP = None


def spain(d, k):
    global ESP
    if ESP is None:
        ESP = load_country("ESP")
    lon0, lat1, sc = -9.6, 44.0, 85
    P = lambda lo, la: (60 + (lo - lon0) * sc, CY - 470 + (lat1 - la) * sc * 1.3)  # noqa: E731
    for ring in ESP:
        pts = [P(lo, la) for lo, la in ring if lo > -10 and la > 35.5]
        if len(pts) > 2:
            d.polygon(pts, fill=mix(BG, mix(PANEL, OIL, 0.35), k), outline=GREY)
    return P


def s_moulins(d, img, lt, dur):
    P = spain(d, ease(lt / 0.5))
    pop_text(d, P(-3.7, 40.0), "ESPAGNE", 50, WHITE, lt - 0.2)
    if lt > 0.6:
        tag(d, 540, CY + 280, "12 % DE LA PRODUCTION", 50, (70, 70, 78))
    if lt > 3.0:
        n = 188_000 * ease((lt - 3.0) / 1.2)
        text(d, (540, CY + 420), f"{fmt(n)} TONNES", 90, YELLOW)
    if lt > 5.2:
        tag(d, 540, CY + 540, "BLOQUÉES JUSQU'AU 30 SEPT. 2027", 40, RED)


def s_pourquoi(d, img, lt, dur):
    pop_text(d, (540, CY - 80), "?", 340, YELLOW, lt, 0.4)
    pop_text(d, (540, CY + 210), "CACHER DE L'HUILE ?", 70, WHITE, lt - 0.6)


def s_trop(d, img, lt, dur):
    text(d, (540, CY - 380), "RÉCOLTE 2026-2027", 54, WHITE, alpha=min(1, lt / 0.3))
    # cuve qui se remplit et déborde
    x0, y0, w, h = 290, CY - 300, 500, 560
    lvl = min(1.08, 0.8 * ease((lt - 0.3) / 1.0) + 0.28 * ease((lt - 3.2) / 1.0))
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=WHITE, width=8)
    top = min(y0 + h - 8, y0 + h - (h - 8) * min(lvl, 1.0))
    d.rectangle([x0 + 8, top, x0 + w - 8, y0 + h - 8], fill=OIL)
    if lvl > 1.0:
        for j in range(3):
            xx = x0 + w - 10 + 30 * j
            d.ellipse([xx, y0 + 40 * j + 20 * math.sin(lt * 6 + j), xx + 26, y0 + 40 * j + 26 + 20 * math.sin(lt * 6 + j)], fill=OIL)
    if lt > 1.0:
        text(d, (540, CY + 330), "1,6 MILLION DE TONNES", 66, YELLOW)
    if lt > 3.2:
        tag(d, 540, CY + 450, "+23 %", 70, RED)
    if lt > 5.0:
        tag(d, 540, CY + 560, "4E RÉCOLTE DE L'HISTOIRE", 40, (70, 70, 78))


def s_prix(d, img, lt, dur):
    text(d, (540, CY - 380), "PRIX PAYÉ AU PRODUCTEUR", 50, WHITE, alpha=min(1, lt / 0.3))
    text(d, (540, CY - 320), "EXTRA VIERGE, PAR KILO", 34, GREY, alpha=min(1, lt / 0.3))
    x0, x1, yt, yb = 160, 920, CY - 180, CY + 220
    d.line([x0, yb, x1, yb], fill=GREY, width=4)
    k = ease((lt - 2.4) / 1.6)
    xe = lerp(x0, x1, k)
    y0v, y1v = lerp(yb, yt, 4 / 4.5), lerp(yb, yt, 3 / 4.5)
    ye = lerp(y0v, y1v, k)
    if lt > 0.4:
        d.ellipse([x0 - 14, y0v - 14, x0 + 14, y0v + 14], fill=WHITE)
        text(d, (x0 + 10, y0v - 60), "≈ 4 €", 60, WHITE, anchor="lm")
        text(d, (x0, yb + 50), "NOV. 2025", 34, GREY, anchor="lm")
    if k > 0:
        d.line([x0, y0v, xe, ye], fill=RED, width=10)
        d.ellipse([xe - 14, ye - 14, xe + 14, ye + 14], fill=RED)
    if k >= 1:
        text(d, (x1 - 10, ye - 60), "≈ 3 €", 60, RED, anchor="rm")
        text(d, (x1, yb + 50), "NOV. 2026", 34, GREY, anchor="rm")
    if lt > 6.5:
        tag(d, 540, CY + 380, "SOUS UN CERTAIN PRIX, ON PERD DE L'ARGENT", 34, RED)


def s_retire(d, img, lt, dur):
    # entrepôt dont la porte se ferme
    x0, y0, w, h = 240, CY - 260, 600, 440
    d.polygon([(x0 - 30, y0), (x0 + w / 2, y0 - 170), (x0 + w + 30, y0)], fill=PANEL)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=PANEL)
    for j in range(5):
        bottle(d, x0 + 90 + j * 105, y0 + h - 30, 130, fill=0.85)
    k = ease((lt - 0.6) / 1.4)
    d.rectangle([x0 + 20, y0 + 20, x0 + w - 20, y0 + 20 + (h - 40) * k], fill=(70, 70, 78))
    for j in range(int(8 * k)):
        yy = y0 + 40 + j * 50
        d.line([x0 + 30, yy, x0 + w - 30, yy], fill=(90, 90, 98), width=4)
    if lt > 2.2:
        tag(d, 540, CY + 300, "UNE PREMIÈRE", 52, RED)
    if lt > 4.6:
        tag(d, 540, CY + 410, "STOCKAGE AUX FRAIS DES MOULINS", 40, (70, 70, 78))


def s_avis(d, img, lt, dur):
    rows = [("SYNDICATS AGRICOLES", "APPLAUDISSENT", GREEN, 0.2), ("EXPORTATEURS", "PEUR DE PERDRE DES CLIENTS", RED, 1.6),
            ("EN RAYON", "LES PRIX POURRAIENT GRIMPER", YELLOW, 3.4)]
    for j, (who, what, col, d0) in enumerate(rows):
        if lt < d0:
            continue
        y = CY - 260 + j * 230
        pop_text(d, (540, y), who, 56, WHITE, lt - d0)
        tag(d, 540, y + 85, what, 40, col, BG if col == YELLOW else WHITE)


def s_bouteille(d, img, lt, dur):
    d.rectangle([140, CY + 230, 940, CY + 250], fill=PANEL)
    for j, x in enumerate([300, 540, 780]):
        bottle(d, x, CY + 230, 220, fill=0.85, price="? €" if (j == 1 and lt > 1.4) else None)
    pop_text(d, (540, CY - 340), "1ER PRODUCTEUR MONDIAL", 56, YELLOW, lt)
    if lt > 2.0:
        tag(d, 540, CY + 380, "ÇA FINIT DANS TA BOUTEILLE", 46, RED)


def s_question(d, img, lt, dur):
    pop_text(d, (540, CY - 200), "SAUVER", 90, GREEN, lt)
    pop_text(d, (540, CY - 100), "LES PRODUCTEURS", 70, GREEN, lt)
    pop_text(d, (540, CY + 60), "OU", 60, WHITE, lt - 0.8)
    pop_text(d, (540, CY + 200), "C'EST TOI", 90, RED, lt - 1.4)
    pop_text(d, (540, CY + 300), "QUI PAIES ?", 90, RED, lt - 1.4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("eco_huile", "scripts/eco/huile.txt", "LUN. 9 NOV. 2026", "HUILE D'OLIVE")
    v.voice(a.voice_file)
    v.scene("L'Espagne a une récolte", s_hook)
    v.scene("Le vendredi six novembre", s_moulins)
    v.scene("Mais alors, pourquoi", s_pourquoi)
    v.scene("Parce qu'il y en a trop", s_trop)
    v.scene("Et pourtant, pour les producteurs", s_prix)
    v.scene("Alors l'Espagne retire", s_retire)
    v.scene("Les syndicats agricoles", s_avis)
    v.scene("L'Espagne est le premier", s_bouteille)
    v.scene("Alors honnêtement", s_question)
    v.render()


if __name__ == "__main__":
    main()
