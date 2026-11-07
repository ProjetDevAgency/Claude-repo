"""Vidéo éco : le prix du lait (mardi 10 novembre 2026)."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, bar, ease, fmt, lerp, mix,
                    person, pop_text, tag, text)
from shein import arrow

CY = 760


def s_hook(d, img, lt, dur):
    n = -60000 * ease(lt / 1.4)
    text(d, (540, CY - 60), f"{fmt(n)} €", 150, RED)
    pop_text(d, (540, CY + 90), "CETTE ANNÉE", 50, WHITE, lt - 0.4)
    if lt > 2.0:
        tag(d, 540, CY + 230, "PAS LA FAUTE DES SUPERMARCHÉS ?", 42, (70, 70, 78))


def s_vache(d, img, lt, dur):
    tag(d, 540, CY - 380, "CALVADOS", 44, (70, 70, 78))
    # brique de lait qui se vide
    x0, y0, w, h = 390, CY - 280, 300, 520
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=24, outline=WHITE, width=8)
    lvl = lerp(0.9, 0.55, ease((lt - 0.6) / 1.6))
    d.rounded_rectangle([x0 + 12, y0 + h * (1 - lvl), x0 + w - 12, y0 + h - 12], radius=16, fill=WHITE)
    if lt > 1.4:
        tag(d, 540, CY + 340, "−200 L PAR VACHE", 56, RED)


def s_calcul(d, img, lt, dur):
    rows = [("LAIT EN MOINS", "−44 000 €", WHITE, 0.2), ("CHARGES EN PLUS", "−15 000 €", WHITE, 1.4),
            ("MANQUE", "≈ −60 000 €", RED, 2.6)]
    for j, (lab, val, col, d0) in enumerate(rows):
        if lt < d0:
            continue
        y = CY - 260 + j * 230
        if j == 2:
            d.line([100, y - 90, 980, y - 90], fill=GREY, width=4)
        text(d, (100, y), lab, 44, GREY, anchor="lm")
        pop_text(d, (980 - 200, y), val, 70 if j < 2 else 84, col, lt - d0)


def s_visite(d, img, lt, dur):
    for j, s in enumerate(["LECLERC", "CARREFOUR", "AUCHAN"]):
        if lt > 0.3 + 0.4 * j:
            tag(d, 540, CY - 300 + j * 130, s, 52, (70, 70, 78))
    if lt > 2.2:
        pop_text(d, (540, CY + 170), "« TOUT LE MONDE DOIT", 52, YELLOW, lt - 2.2)
        pop_text(d, (540, CY + 250), "VIVRE DE SON TRAVAIL »", 52, YELLOW, lt - 2.2)


def s_qui(d, img, lt, dur):
    pop_text(d, (540, CY - 80), "?", 340, YELLOW, lt, 0.4)
    pop_text(d, (540, CY + 210), "AVEC QUI ?", 80, WHITE, lt - 0.7)


def chain(d, lt, hl):
    steps = ["FERME", "INDUSTRIEL", "SUPERMARCHÉ", "TOI"]
    for j, s in enumerate(steps):
        k = ease((lt - 0.35 * j) / 0.35)
        if k <= 0:
            continue
        y = CY - 330 + j * 200
        col = RED if s == hl else PANEL
        d.rounded_rectangle([250, y - 60, 830, y + 60], radius=30, fill=mix(BG, col, k))
        text(d, (540, y), s, 52, WHITE, alpha=k)
        if j > 0:
            arrow(d, 540, y - 140, 540, y - 70, GREY, 8)


def s_industriels(d, img, lt, dur):
    chain(d, lt, "INDUSTRIEL" if lt > 1.6 else None)
    if lt > 3.2:
        tag(d, 540, CY + 520, "LE PRIX SE DÉCIDE SANS LUI", 44, RED)


def s_demande(d, img, lt, dur):
    pop_text(d, (540, CY - 330), "+8 CENTIMES / LITRE", 64, YELLOW, lt)
    for j, (lab, v, col, d0) in enumerate([("DEMANDÉ EN 2025", 3.5, YELLOW, 1.6), ("OBTENU", 0.5, RED, 3.4)]):
        if lt < d0:
            continue
        k = ease((lt - d0) / 0.8)
        y = CY - 120 + j * 260
        text(d, (100, y), lab, 44, WHITE, anchor="lm")
        bar(d, 100, y + 50, 880, 80, k * v / 4.0, col)
        text(d, (980, y + 190), f"{fmt(v * k, 1)} %", 70, col, anchor="rm")


def s_boucle(d, img, lt, dur):
    pop_text(d, (540, CY - 160), "PAS DE HAUSSE EN RAYON", 58, WHITE, lt)
    if lt > 0.8:
        arrow(d, 540, CY - 90, 540, CY + 30, RED, 10)
    pop_text(d, (540, CY + 110), "PAS DE HAUSSE", 58, RED, lt - 1.0)
    pop_text(d, (540, CY + 185), "POUR LE LAIT", 58, RED, lt - 1.0)


def s_sondage(d, img, lt, dur):
    for i in range(10):
        x = 120 + (i % 5) * 210
        y = CY - 220 + (i // 5) * 260
        k = ease((lt - 0.05 * i) / 0.3)
        col = YELLOW if i < 6 else GREY
        person(d, x, y, 120, mix(BG, col, k))
    pop_text(d, (540, CY + 330), "64 %", 130, YELLOW, lt - 1.0)
    if lt > 1.8:
        tag(d, 540, CY + 460, "PRÊTS À PAYER PLUS CHER", 44, (70, 70, 78))


def s_bilan(d, img, lt, dur):
    rows = [("LE CONSOMMATEUR", "VEUT PAYER", GREEN, 0.2), ("LE SUPERMARCHÉ", "DIT QU'IL SOUTIENT", GREEN, 1.4),
            ("L'ÉLEVEUR", "ATTEND TOUJOURS", RED, 2.8)]
    for j, (who, what, col, d0) in enumerate(rows):
        if lt < d0:
            continue
        y = CY - 250 + j * 220
        pop_text(d, (540, y), who, 56, WHITE, lt - d0)
        tag(d, 540, y + 80, what, 40, col)


def s_question(d, img, lt, dur):
    chain(d, 5, None)
    if lt > 0.6:
        tag(d, 540, CY + 520, "QUI GARDE L'ARGENT ?", 56, RED)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("eco_lait", "scripts/eco/lait.txt", "MAR. 10 NOV. 2026", "AGRICULTURE")
    v.voice(a.voice_file)
    v.scene("Cet éleveur va perdre", s_hook)
    v.scene("Guillaume élève", s_vache)
    v.scene("Le calcul est brutal", s_calcul)
    v.scene("Le vendredi six novembre", s_visite)
    v.scene("Et pourtant, c'est pas", s_qui)
    v.scene("Avec les industriels", s_industriels)
    v.scene("Cette année, il demande", s_demande)
    v.scene("À chaque fois", s_boucle)
    v.scene("Le plus fou", s_sondage)
    v.scene("Le consommateur veut", s_bilan)
    v.scene("Alors honnêtement", s_question)
    v.render()


if __name__ == "__main__":
    main()
