"""Vidéo éco : Shein contourne la taxe sur les petits colis (lundi 9 novembre 2026)."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, bar, ease, fmt, lerp,
                    load_country, mix, pop_text, tag, text)

CY = 760


def box(d, x, y, s, label="COLIS", col=(176, 128, 80)):
    d.rounded_rectangle([x - s, y - s * 0.8, x + s, y + s * 0.8], radius=int(s * 0.12), fill=col)
    d.rectangle([x - s * 0.12, y - s * 0.8, x + s * 0.12, y + s * 0.8], fill=mix(col, BG, 0.25))
    text(d, (x, y + s * 0.45), label, int(s * 0.28), BG)


def arrow(d, x0, y0, x1, y1, col, w=10):
    d.line([x0, y0, x1, y1], fill=col, width=w)
    import math
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        d.line([x1, y1, x1 - 36 * math.cos(a + s * 0.5), y1 - 36 * math.sin(a + s * 0.5)], fill=col, width=w)


def s_hook(d, img, lt, dur):
    k = back(lt / 0.5)
    box(d, 540, CY - 120, 170 * max(0.3, k))
    if lt > 0.6:
        tag(d, 540, CY - 120, "TAXÉ", 70, RED)
    if lt > 1.6:
        n = 500_000_000 * ease((lt - 1.6) / 1.0)
        text(d, (540, CY + 170), f"{fmt(n)} €", 92, YELLOW)
        text(d, (540, CY + 260), "POUR PASSER À CÔTÉ", 46, WHITE, alpha=min(1, (lt - 2.0) / 0.3))


def s_taxes(d, img, lt, dur):
    box(d, 540, CY + 40, 170)
    pop_text(d, (540, CY - 300), "+3 €", 120, YELLOW, lt)
    if lt > 0.3:
        tag(d, 540, CY - 200, "DOUANE · 1ER JUILLET", 40, (70, 70, 78))
    pop_text(d, (540, CY + 330), "+2 €", 120, RED, lt - 2.2)
    if lt > 2.5:
        tag(d, 540, CY + 430, "FRAIS · 1ER NOVEMBRE", 40, RED)


def s_effet(d, img, lt, dur):
    text(d, (540, CY - 360), "L'EFFET", 64, WHITE, alpha=min(1, lt / 0.3))
    for j, (lab, v, d0) in enumerate([("TVA DÉCLARÉE (JUIN-AOÛT)", 48, 0.3), ("VENTES EN SEPTEMBRE", 25, 2.6)]):
        if lt < d0:
            continue
        k = ease((lt - d0) / 0.9)
        y = CY - 200 + j * 330
        text(d, (100, y), lab, 40, WHITE, anchor="lm")
        bar(d, 100, y + 50, 880, 70, 1 - k * v / 100, mix(GREEN, RED, k))
        text(d, (980, y + 180), f"−{int(v * k)} %", 80, RED, anchor="rm")


def s_parade(d, img, lt, dur):
    pop_text(d, (540, CY - 60), "?", 340, YELLOW, lt, 0.4)
    pop_text(d, (540, CY + 230), "LA PARADE", 80, WHITE, lt - 0.8)


MAP = None


def europe(d, lt, hl):
    global MAP
    if MAP is None:
        MAP = {c: load_country(c) for c in ("FRA", "DEU", "POL")}
    lon0, lat1, sc = -5.5, 56.0, 33
    P = lambda lo, la: (80 + (lo - lon0) * sc, CY - 480 + (lat1 - la) * sc * 1.5)  # noqa: E731
    for c, rings in MAP.items():
        col = mix(PANEL, RED, 0.6 * ease(lt / 0.6)) if c == hl else PANEL
        for ring in rings:
            pts = [P(lo, la) for lo, la in ring if -6 < lo < 25 and la > 41]
            if len(pts) > 2:
                d.polygon(pts, fill=col, outline=GREY)
    return P


def s_pologne(d, img, lt, dur):
    P = europe(d, lt, "POL")
    pop_text(d, P(19.4, 52.2), "POLOGNE", 46, WHITE, lt - 0.3)
    pop_text(d, P(2.5, 46.8), "FRANCE", 40, GREY, lt - 0.3)
    rows = [("+500 M€", 0.6), ("1 MILLIARD DEPUIS 2022", 2.0), ("≈ 1 MILLION DE M²", 3.6), ("10 000 SALARIÉS", 5.0)]
    shown = [s for s, d0 in rows if lt > d0]
    if shown:
        tag(d, 540, CY + 360, shown[-1], 56, RED)


def s_idee(d, img, lt, dur):
    y = CY - 60
    pts = [(160, "CHINE", "EN GROS"), (540, "POLOGNE", "ENTREPÔT UE"), (920, "FRANCE", "TON COLIS")]
    for j, (x, lab, sub) in enumerate(pts):
        k = ease((lt - 0.8 * j) / 0.4)
        if k <= 0:
            continue
        d.ellipse([x - 90 * k, y - 90 * k, x + 90 * k, y + 90 * k], fill=RED if j == 1 else PANEL)
        text(d, (x, y - 150), lab, 44, WHITE, alpha=k)
        text(d, (x, y + 150), sub, 34, GREY, alpha=k)
        if j > 0 and k > 0.5:
            arrow(d, pts[j - 1][0] + 100, y, x - 100, y, YELLOW)
    if lt > 4.0:
        d.line([700, CY + 200, 1000, CY + 200], fill=RED, width=8)
        tag(d, 540, CY + 330, "PLUS UN « PETIT COLIS IMPORTÉ »", 40, RED)


def s_resultat(d, img, lt, dur):
    pop_text(d, (540, CY - 150), "LIVRAISON + RAPIDE", 72, GREEN, lt)
    pop_text(d, (540, CY + 20), "FACTURE LIMITÉE", 72, YELLOW, lt - 1.2)


def s_voulait(d, img, lt, dur):
    P = europe(d, 1.0, "POL")
    k = ease(lt / 1.5)
    x0, y0 = 1080, CY - 200
    xa, ya = P(2.5, 46.8)
    xp, yp = P(19.4, 52.2)
    # la flèche qui visait la France se tord vers la Pologne
    tx, ty = lerp(xa, xp, k), lerp(ya, yp, k)
    arrow(d, x0, y0, tx + 60, ty, YELLOW, 12)
    if lt > 1.6:
        tag(d, 540, CY + 330, "ENTREPÔT DÉPLACÉ", 48, RED)


def s_question(d, img, lt, dur):
    pop_text(d, (540, CY - 260), "LA TAXE PROTÈGE QUI ?", 64, WHITE, lt)
    pop_text(d, (540, CY - 40), "LES COMMERÇANTS", 70, GREEN, lt - 0.8)
    pop_text(d, (540, CY + 50), "FRANÇAIS ?", 70, GREEN, lt - 0.8)
    pop_text(d, (540, CY + 220), "LES ENTREPÔTS", 70, RED, lt - 1.6)
    pop_text(d, (540, CY + 310), "POLONAIS ?", 70, RED, lt - 1.6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("eco_shein", "scripts/eco/shein.txt", "LUN. 9 NOV. 2026", "COLIS")
    v.voice(a.voice_file)
    v.scene("L'Europe a taxé", s_hook)
    v.scene("Depuis le premier juillet", s_taxes)
    v.scene("L'effet est immédiat", s_effet)
    v.scene("Et pourtant, Shein", s_parade)
    v.scene("La Pologne", s_pologne)
    v.scene("L'idée est simple", s_idee)
    v.scene("Résultat, la commande", s_resultat)
    v.scene("L'Europe voulait", s_voulait)
    v.scene("Alors honnêtement", s_question)
    v.render()


if __name__ == "__main__":
    main()
