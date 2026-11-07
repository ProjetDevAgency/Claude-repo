"""Vidéo éco : le prix du gaz (mercredi 11 novembre 2026)."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, Video, back, bar, ease, fmt, lerp, mix,
                    person, pop_text, tag, text)

CY = 760


def people(d, lt, n_red, total=3, size=170, y=CY - 120):
    gap = 260 if total == 3 else 210
    x0 = 540 - gap * (total - 1) / 2
    for i in range(total):
        k = ease((lt - 0.15 * i) / 0.3)
        col = RED if (i < n_red and lt > 0.8) else GREY
        person(d, x0 + i * gap, y, size, mix(BG, col, k))


def s_hook(d, img, lt, dur):
    people(d, lt, 1)
    pop_text(d, (540, CY + 200), "1 FRANÇAIS SUR 3", 70, RED, lt - 0.8)
    if lt > 1.8:
        tag(d, 540, CY + 310, "A DU MAL À PAYER SON GAZ", 42, (70, 70, 78))


def s_facture(d, img, lt, dur):
    d.rounded_rectangle([200, CY - 360, 880, CY + 160], radius=30, fill=WHITE)
    text(d, (540, CY - 290), "FACTURE DE GAZ", 40, (60, 60, 60))
    k1 = ease((lt - 0.4) / 1.0)
    k2 = ease((lt - 3.0) / 1.0)
    n = 100 * (1 + 0.066 * k1) * (1 + 0.058 * k2)
    text(d, (540, CY - 140), f"{fmt(n, 1)}", 150, BG)
    text(d, (540, CY - 30), "BASE 100 EN OCTOBRE", 34, (110, 110, 110))
    if lt > 0.6:
        tag(d, 540, CY + 260, "+6,6 % AU 1ER NOVEMBRE", 46, RED)
    if lt > 3.0:
        tag(d, 540, CY + 370, "+5,8 % EN DÉCEMBRE ?", 46, (70, 70, 78))


def s_mediateur(d, img, lt, dur):
    pop_text(d, (540, CY - 300), "2 000 SONDÉS", 56, WHITE, lt)
    n = 34 * ease((lt - 1.2) / 1.0)
    if lt > 1.2:
        text(d, (540, CY - 40), f"{int(n)} %", 220, RED)
        tag(d, 540, CY + 160, "DU MAL À PAYER GAZ OU ÉLECTRICITÉ", 38, (70, 70, 78))
    tag(d, 540, CY + 330, "SOURCE : MÉDIATEUR DE L'ÉNERGIE", 30, PANEL)


def s_pire(d, img, lt, dur):
    for j, (lab, v, d0) in enumerate([("TOUS", 34, 0.0), ("MOINS DE 35 ANS", 55, 1.0), ("COMMERÇANTS", 77, 2.4)]):
        if lt < d0:
            continue
        k = ease((lt - d0) / 0.8)
        y = CY - 300 + j * 230
        text(d, (100, y), lab, 44, WHITE, anchor="lm")
        bar(d, 100, y + 50, 880, 80, k * v / 100, RED if j else GREY)
        text(d, (980, y + 180), f"{int(v * k)} %", 64, RED if j else WHITE, anchor="rm")


def thermo(d, x, y, r, temp, col):
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=16)
    d.arc([x - r, y - r, x + r, y + r], 135, 135 + 270 * (temp - 14) / 10, fill=col, width=16)
    text(d, (x, y), f"{fmt(temp, 0)}°", int(r * 0.7), WHITE)


def s_coupent(d, img, lt, dur):
    temp = lerp(21, 17, ease((lt - 0.4) / 1.6))
    thermo(d, 540, CY - 170, 220, temp, mix(YELLOW, BLUE_C, ease((lt - 0.4) / 1.6)))
    if lt > 1.6:
        tag(d, 540, CY + 180, "3 FOYERS SUR 4 ONT BAISSÉ LE CHAUFFAGE", 36, (70, 70, 78))
    if lt > 3.6:
        tag(d, 540, CY + 300, "1 SUR 2 A EU FROID CHEZ LUI", 40, RED)


BLUE_C = (80, 160, 240)


def s_avant(d, img, lt, dur):
    vals = [("2020", 18), ("2021", 25), ("2026", 34)]
    base = CY + 300
    for j, (yr, v) in enumerate(vals):
        k = ease((lt - 0.5 * j) / 0.7)
        x = 260 + j * 280
        h = 15 * v * k
        d.rounded_rectangle([x - 80, base - h, x + 80, base], radius=16, fill=RED if j == 2 else GREY)
        text(d, (x, base + 60), yr, 44, WHITE)
        if k > 0.5:
            text(d, (x, base - h - 50), f"{v} %", 56, WHITE)
    if lt > 2.2:
        tag(d, 540, CY - 440, "PRESQUE LE DOUBLE", 52, RED)


def s_experts(d, img, lt, dur):
    n = 12_000_000 * ease(lt / 1.4)
    text(d, (540, CY - 120), fmt(n), 130, RED)
    pop_text(d, (540, CY + 20), "DE FOYERS", 60, WHITE, lt - 0.6)
    if lt > 1.8:
        tag(d, 540, CY + 170, "EN PRÉCARITÉ ÉNERGÉTIQUE", 46, (70, 70, 78))


def s_directrice(d, img, lt, dur):
    d.rounded_rectangle([290, CY - 330, 790, CY + 130], radius=30, fill=PANEL)
    pop_text(d, (540, CY - 230), "HAUSSES", 80, WHITE, lt - 0.3)
    pop_text(d, (540, CY - 130), "AU MOINS JUSQU'À", 50, YELLOW, lt - 0.6)
    if lt > 0.9:
        d.rectangle([290, CY + 20, 790, CY + 130], fill=RED)
        text(d, (540, CY + 75), "DÉBUT 2027", 60, WHITE)
    if lt > 1.2:
        tag(d, 540, CY + 260, "SELON LE MÉDIATEUR DE L'ÉNERGIE", 38, (70, 70, 78))


def s_marie(d, img, lt, dur):
    person(d, 540, CY - 180, 230, mix(BG, GREY, ease(lt / 0.4)))
    pop_text(d, (540, CY + 60), "MARIE-CLAUDE · YVELINES", 46, WHITE, lt - 0.3)
    if lt > 1.4:
        tag(d, 540, CY + 180, "+ DE 250 € DE GAZ PAR MOIS", 46, RED)
    if lt > 3.6:
        tag(d, 540, CY + 300, "19 °C PARTOUT", 46, BLUE_C)


def s_question(d, img, lt, dur):
    thermo(d, 540, CY - 170, 220, 19 + 2 * __import__("math").sin(lt * 2), YELLOW)
    pop_text(d, (540, CY + 190), "TU CHAUFFES", 74, WHITE, lt - 0.3)
    pop_text(d, (540, CY + 280), "À COMBIEN ?", 74, YELLOW, lt - 0.6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("eco_gaz", "scripts/eco/gaz.txt", "MER. 11 NOV. 2026", "ÉNERGIE")
    v.voice(a.voice_file)
    v.scene("Un Français sur trois", s_hook)
    v.scene("Au premier novembre", s_facture)
    v.scene("Le Médiateur de l'énergie a", s_mediateur)
    v.scene("Et pourtant, le pire", s_pire)
    v.scene("Mais alors, comment", s_coupent)
    v.scene("Avant la guerre", s_avant)
    v.scene("Selon les experts", s_experts)
    v.scene("Et la directrice", s_directrice)
    v.scene("Sur un marché", s_marie)
    v.scene("Alors honnêtement", s_question)
    v.render()


if __name__ == "__main__":
    main()
