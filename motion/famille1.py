"""Série L'argent qui détruit les familles — n°1 : déshériter ses enfants (réserve héréditaire)."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, ease, lerp, mix, person, pop_text,
                    tag, text)
from shein import arrow

CY = 760
PINK = (230, 120, 160)


def testament(d, x, y, s, k=1.0, lines=("TOUT À MA", "NOUVELLE ÉPOUSE")):
    w, h = 0.75 * s, s
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=18, fill=mix(BG, WHITE, k))
    text(d, (x, y - h * 0.36), "TESTAMENT", int(s * 0.1), RED, alpha=k)
    for j, l in enumerate(lines):
        text(d, (x, y - h * 0.08 + j * s * 0.12), l, int(s * 0.062), BG, alpha=k)
    d.line([x - w * 0.3, y + h * 0.33, x + w * 0.3, y + h * 0.33], fill=mix(BG, GREY, k), width=4)


def kids(d, x0, y, lt, col=GREY, crossed=False, gap=170, size=110):
    for i in range(3):
        k = ease((lt - 0.1 * i) / 0.3)
        x = x0 + i * gap
        person(d, x, y, size, mix(BG, col, k))
        if crossed and k > 0.9:
            d.line([x - 50, y - 120, x + 50, y + 60], fill=RED, width=12)
            d.line([x + 50, y - 120, x - 50, y + 60], fill=RED, width=12)


def pie(d, cx, cy, r, free_frac, k=1.0, free_col=PINK, res_col=YELLOW):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mix(BG, res_col, k))
    if free_frac > 0:
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * free_frac, fill=mix(BG, free_col, k))


def s_hook(d, img, lt, dur):
    testament(d, 540, CY - 220, 380 * max(0.4, back(lt / 0.5)))
    kids(d, 370, CY + 260, lt - 0.6, GREY, crossed=lt > 1.6)
    if lt > 3.2:
        tag(d, 540, CY + 450, "LA LOI L'EN EMPÊCHE", 56, RED)


def s_famille(d, img, lt, dur):
    person(d, 540, CY - 260, 150, WHITE)
    text(d, (540, CY - 120), "LE PÈRE", 36, GREY)
    if lt > 0.8:
        kids(d, 190, CY + 160, lt - 0.8, GREY, gap=150, size=95)
        text(d, (340, CY + 260), "3 ENFANTS", 34, GREY)
    if lt > 2.2:
        person(d, 870, CY + 160, 110, mix(BG, PINK, ease((lt - 2.2) / 0.3)))
        text(d, (870, CY + 260), "NOUVELLE ÉPOUSE", 30, PINK)
    if lt > 4.0:
        arrow(d, 600, CY - 160, 830, CY + 30, PINK, 10)
        tag(d, 540, CY + 430, "TOUT POUR ELLE, RIEN POUR EUX", 44, RED)
    if lt > 7.0:
        tag(d, 540, CY + 540, "DÉCOUVERT CHEZ LE NOTAIRE", 38, (70, 70, 78))


def s_reserve(d, img, lt, dur):
    pop_text(d, (540, CY - 260), "« C'EST SON ARGENT »", 60, WHITE, lt)
    if lt > 1.4:
        d.line([180, CY - 260, 900, CY - 260], fill=RED, width=12)
    if lt > 2.6:
        pop_text(d, (540, CY - 40), "LA RÉSERVE", 100, YELLOW, lt - 2.6)
        pop_text(d, (540, CY + 70), "HÉRÉDITAIRE", 100, YELLOW, lt - 2.6)
    if lt > 4.6:
        tag(d, 540, CY + 260, "UNE PART REVIENT FORCÉMENT AUX ENFANTS", 38, (70, 70, 78))


def s_parts(d, img, lt, dur):
    rows = [("1 ENFANT", 1 / 2, "1/2 LIBRE", 0.0), ("2 ENFANTS", 1 / 3, "1/3 LIBRE", 1.4), ("3 ET +", 1 / 4, "1/4 LIBRE", 2.6)]
    for j, (lab, f, sub, d0) in enumerate(rows):
        if lt < d0:
            continue
        k = ease((lt - d0) / 0.5)
        x = 200 + j * 340
        pie(d, x, CY - 120, 130, f * k)
        text(d, (x, CY + 60), lab, 40, WHITE)
        text(d, (x, CY + 115), sub, 36, PINK)
    if lt > 4.2:
        d.rounded_rectangle([140, CY + 200, 940, CY + 270], radius=20, fill=PANEL)
        d.ellipse([170, CY + 215, 210, CY + 255], fill=YELLOW)
        text(d, (230, CY + 235), "RÉSERVÉ AUX ENFANTS", 36, WHITE, anchor="lm")
    if lt > 5.6:
        tag(d, 540, CY + 380, "CODE CIVIL, ARTICLE 913", 40, RED)


def s_epouse(d, img, lt, dur):
    pop_text(d, (540, CY - 380), "ET LA NOUVELLE ÉPOUSE ?", 54, PINK, lt)
    opts = [("1/4 EN PLEINE PROPRIÉTÉ", 2.6), ("1/4 + USUFRUIT DU RESTE", 3.8), ("TOUT EN USUFRUIT", 5.2)]
    for j, (s, d0) in enumerate(opts):
        if lt > d0:
            y = CY - 220 + j * 150
            d.rounded_rectangle([130, y - 55, 950, y + 55], radius=26, fill=PANEL)
            text(d, (180, y), f"{j + 1}", 44, PINK, anchor="lm")
            text(d, (240, y), s, 40, WHITE, anchor="lm")
    if lt > 7.2:
        tag(d, 540, CY + 330, "ELLE PEUT VIVRE DANS LA MAISON TOUTE SA VIE", 34, GREEN)
    if lt > 2.6:
        tag(d, 540, CY + 440, "ART. 1094-1", 34, (70, 70, 78))


def s_reduction(d, img, lt, dur):
    testament(d, 540, CY - 220, 330)
    if lt > 1.2:
        k = ease((lt - 1.2) / 0.6)
        d.line([300, CY - 380, lerp(300, 780, k), lerp(CY - 380, CY - 60, k)], fill=RED, width=14)
    if lt > 1.8:
        pop_text(d, (540, CY + 90), "ACTION EN RÉDUCTION", 64, YELLOW, lt - 1.8)
        tag(d, 540, CY + 200, "LES ENFANTS RÉCUPÈRENT LEUR PART", 40, GREEN)
        tag(d, 540, CY + 310, "ART. 920", 34, (70, 70, 78))


def s_vivant(d, img, lt, dur):
    pop_text(d, (540, CY - 330), "LES DONATIONS DE SON VIVANT", 48, WHITE, lt)
    pop_text(d, (540, CY - 250), "COMPTENT AUSSI", 70, YELLOW, lt - 0.5)
    # calendrier « la veille »
    d.rounded_rectangle([370, CY - 140, 710, CY + 160], radius=24, fill=PANEL)
    d.rectangle([370, CY - 140, 710, CY - 70], fill=RED)
    text(d, (540, CY - 105), "LA VEILLE", 36, WHITE)
    text(d, (540, CY + 40), "J-1", 110, WHITE)
    if lt > 2.4:
        d.line([360, CY - 150, 720, CY + 170], fill=RED, width=14)
        tag(d, 540, CY + 300, "ÇA CHANGE RIEN · ART. 922", 40, (70, 70, 78))


def s_chute(d, img, lt, dur):
    k = ease(lt / 0.8)
    pie(d, 540, CY - 150, 230, 0.25 * k)
    if lt > 0.9:
        text(d, (460, CY - 100), "3/4", 80, BG)
        text(d, (460, CY - 30), "ENFANTS", 36, BG)
        text(d, (650, CY - 265), "1/4", 50, BG)
    if lt > 2.6:
        tag(d, 540, CY + 180, "LE TESTAMENT A CRÉÉ UNE GUERRE", 46, RED)
    if lt > 3.4:
        tag(d, 540, CY + 330, "CECI N'EST PAS UN CONSEIL JURIDIQUE", 28, (70, 70, 78))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("famille_1_desheriter", "scripts/finance/famille_1_desheriter.txt",
              "L'ARGENT QUI DÉTRUIT LES FAMILLES", "HÉRITAGE")
    v.voice(a.voice_file)
    v.scene("Un père déshérite", s_hook)
    v.scene("Prenons une famille typique", s_famille)
    v.scene("Sur le papier", s_reserve)
    v.scene("Avec un enfant", s_parts)
    v.scene("Mais alors, la nouvelle", s_epouse)
    v.scene("Et si le testament", s_reduction)
    v.scene("Ce que peu de gens savent", s_vivant)
    v.scene("Dans cette famille", s_chute)
    v.render()


if __name__ == "__main__":
    main()
