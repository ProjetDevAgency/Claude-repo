"""Éducation financière : le mythe de la SCI qui protège tout."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, ease, fmt, lerp, mix, person,
                    pop_text, tag, text)
from shein import arrow

CY = 760


def house(d, x, y, s, col=WHITE):
    d.polygon([(x - s, y - 0.2 * s), (x, y - 1.05 * s), (x + s, y - 0.2 * s)], fill=col)
    d.rectangle([x - 0.78 * s, y - 0.2 * s, x + 0.78 * s, y + 0.75 * s], fill=col)
    d.rectangle([x - 0.18 * s, y + 0.25 * s, x + 0.18 * s, y + 0.75 * s], fill=BG)


def card(d, x, y, w, h, label, col):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=22, fill=col)
    text(d, (x, y), label, 40, WHITE if col != WHITE else BG)


def s_hook(d, img, lt, dur):
    n = 2_000_000 * ease(lt / 1.3)
    text(d, (540, CY - 300), fmt(n), 130, YELLOW)
    pop_text(d, (540, CY - 190), "ONT CRU CE CONSEIL", 54, WHITE, lt - 0.6)
    k = back((lt - 1.4) / 0.5)
    if lt > 1.4:
        house(d, 540, CY + 120, 170 * max(0.3, k))
    if lt > 2.6:
        d.line([380, CY - 60, 700, CY + 260], fill=RED, width=22)
        d.line([700, CY - 60, 380, CY + 260], fill=RED, width=22)
        tag(d, 540, CY + 380, "ÇA PEUT TE COÛTER TA MAISON", 46, RED)


def s_conseil(d, img, lt, dur):
    d.rounded_rectangle([290, CY - 330, 790, CY + 230], radius=30, outline=YELLOW, width=10)
    tag(d, 540, CY - 330, "SCI", 56, YELLOW, BG)
    house(d, 540, CY - 20, 150)
    if lt > 1.6:
        tag(d, 540, CY + 340, "« PERSONNE NE PEUT TE LA PRENDRE »", 40, (70, 70, 78))
    if lt > 4.2:
        tag(d, 540, CY + 450, "DETTE · PROCÈS · DIVORCE", 44, RED)


def s_parts(d, img, lt, dur):
    rows = [("TOI", PANEL, 0.0), ("TES PARTS", RED if lt > 1.6 else PANEL, 0.4), ("LA SCI", PANEL, 0.8),
            ("LA MAISON", PANEL, 1.2)]
    for j, (lab, col, d0) in enumerate(rows):
        k = ease((lt - d0) / 0.35)
        if k <= 0:
            continue
        y = CY - 360 + j * 190
        card(d, 540, y, 520, 110, lab, mix(BG, col, k))
        if j:
            arrow(d, 540, y - 135, 540, y - 65, GREY, 8)
    if lt > 1.8:
        tag(d, 540, CY + 420, "SAISISSABLES", 60, RED)
    if lt > 3.4:
        tag(d, 540, CY + 530, "CODE DES PROCÉDURES CIVILES D'EXÉCUTION, R. 232-1", 28, (70, 70, 78))


def s_1857(d, img, lt, dur):
    k = ease(lt / 0.4)
    d.rounded_rectangle([110, CY - 360, 970, CY + 200], radius=26, fill=mix(BG, WHITE, k))
    text(d, (540, CY - 290), "CODE CIVIL · ARTICLE 1857", 40, RED, alpha=k)
    lines = ["« Les associés répondent", "indéfiniment des dettes", "sociales à proportion de", "leur part dans le capital »"]
    for j, l in enumerate(lines):
        if lt > 2.0 + 0.4 * j:
            text(d, (540, CY - 170 + j * 80), l, 50, BG)
    if lt > 4.2:
        tag(d, 540, CY + 330, "SANS PLAFOND", 64, RED)


def s_divorce(d, img, lt, dur):
    # balance
    cx, top = 540, CY - 320
    d.line([cx, top, cx, CY + 140], fill=WHITE, width=12)
    tilt = 0.0
    d.line([cx - 330, top + 60, cx + 330, top + 60], fill=WHITE, width=12)
    for side in (-1, 1):
        x = cx + side * 300
        d.line([x, top + 60, x - 80, top + 260], fill=GREY, width=4)
        d.line([x, top + 60, x + 80, top + 260], fill=GREY, width=4)
        d.arc([x - 120, top + 200, x + 120, top + 320], 0, 180, fill=WHITE, width=10)
        if lt > 1.0:
            card(d, x, top + 230, 150, 70, "50 %", RED)
    d.rectangle([cx - 140, CY + 140, cx + 140, CY + 170], fill=WHITE)
    if lt > 2.0:
        tag(d, 540, CY + 300, "PARTS ACHETÉES PENDANT LE MARIAGE", 40, (70, 70, 78))
    if lt > 3.4:
        tag(d, 540, CY + 410, "CODE CIVIL, ART. 1401", 34, (70, 70, 78))
    if lt > 5.0:
        tag(d, 540, CY + 520, "LA FORME CHANGE, PAS LE RÉSULTAT", 44, RED)


def s_transmettre(d, img, lt, dur):
    pop_text(d, (540, CY - 380), "SA VRAIE UTILITÉ : TRANSMETTRE", 50, GREEN, lt)
    person(d, 540, CY - 170, 150, GREY)
    for side in (-1, 1):
        k = ease((lt - 2.0) / 0.6)
        x = 540 + side * 290
        person(d, x, CY + 80, 120, mix(BG, YELLOW, k))
        if k > 0:
            arrow(d, 540 + side * 70, CY - 110, x - side * 40, CY - 20, GREEN, 8)
    if lt > 3.4:
        tag(d, 540, CY + 260, "100 000 € PAR PARENT ET PAR ENFANT", 42, GREEN)
    if lt > 5.0:
        tag(d, 540, CY + 370, "RENOUVELABLE TOUS LES 15 ANS", 42, (70, 70, 78))
    if lt > 7.6:
        tag(d, 540, CY + 480, "MOINS DE BLOCAGES À PLUSIEURS", 40, (70, 70, 78))


def s_prix(d, img, lt, dur):
    pop_text(d, (540, CY - 360), "LE PRIX À PAYER", 64, RED, lt)
    for j, (s, d0) in enumerate([("STATUTS À RÉDIGER", 0.3), ("ASSEMBLÉE GÉNÉRALE CHAQUE ANNÉE", 1.0),
                                  ("COMPTES À TENIR", 1.9)]):
        if lt > d0:
            y = CY - 180 + j * 160
            d.rounded_rectangle([110, y - 55, 970, y + 55], radius=26, fill=PANEL)
            d.ellipse([140, y - 22, 184, y + 22], fill=RED)
            text(d, (220, y), s, 40, WHITE, anchor="lm")


def s_papier(d, img, lt, dur):
    pop_text(d, (540, CY - 300), "SUR LE PAPIER", 50, GREY, lt)
    pop_text(d, (540, CY - 200), "INTOUCHABLE", 90, WHITE, lt - 0.3)
    if lt > 1.4:
        d.line([200, CY - 200, 880, CY - 200], fill=RED, width=14)
    pop_text(d, (540, CY + 20), "DANS LA LOI", 50, GREY, lt - 1.8)
    pop_text(d, (540, CY + 120), "ORGANISÉ", 90, YELLOW, lt - 2.1)


def s_chute(d, img, lt, dur):
    pop_text(d, (540, CY - 200), "TA TRANSMISSION", 70, GREEN, lt)
    if lt > 0.6:
        tag(d, 540, CY - 100, "PROTÉGÉE", 50, GREEN)
    pop_text(d, (540, CY + 80), "TON PATRIMOINE", 70, RED, lt - 1.4)
    if lt > 2.0:
        tag(d, 540, CY + 180, "BEAUCOUP MOINS", 50, RED)
    if lt > 2.6:
        tag(d, 540, CY + 400, "CECI N'EST PAS UN CONSEIL EN INVESTISSEMENT", 28, (70, 70, 78))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("fin_sci", "scripts/finance/sci_mythe.txt", "TON ARGENT, DÉCORTIQUÉ", "PATRIMOINE")
    v.voice(a.voice_file)
    v.scene("Plus de deux millions", s_hook)
    v.scene("Le conseil, c'est", s_conseil)
    v.scene("Sauf que toi", s_parts)
    v.scene("Mais alors, et si", s_1857)
    v.scene("Et en cas de divorce", s_divorce)
    v.scene("Ce que peu de gens savent", s_transmettre)
    v.scene("Mais tout ça a un prix", s_prix)
    v.scene("Sur le papier", s_papier)
    v.scene("La SCI protège", s_chute)
    v.render()


if __name__ == "__main__":
    main()
