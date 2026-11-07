"""Vidéo éco : le SMIC (à publier le dimanche 8 novembre 2026)."""
import argparse
import math

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, F, Video, back, bar, ease, fmt, lerp,
                    load_country, mix, person, pop_text, tag, text)

CY = 760  # centre vertical de la zone d'animation


def s_2012(d, img, lt, dur):
    k = ease(lt / 0.8)
    x0, x1, y = 140, 940, CY + 80
    d.line([x0, y, lerp(x0, x1, k), y], fill=GREY, width=8)
    for yr, frac in [(2012, 0), (2016, 0.28), (2020, 0.57), (2026, 1)]:
        if k >= frac:
            x = lerp(x0, x1, frac)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=RED if yr == 2012 else WHITE)
            text(d, (x, y + 60), str(yr), 40, WHITE)
    pop_text(d, (540, CY - 140), "0 COUP DE POUCE", 92, RED, lt - 0.5)
    pop_text(d, (540, CY - 30), "DEPUIS 14 ANS", 56, WHITE, lt - 0.8)
    if lt > 2.2:
        tag(d, 540, CY + 260, "LUNDI 9 NOVEMBRE · MATIGNON", 40, RED)


def s_paie(d, img, lt, dur):
    k = ease(lt / 0.5)
    y0 = lerp(H_OFF, 0, k)
    d.rounded_rectangle([170, CY - 300 + y0, 910, CY + 240 + y0], radius=30, fill=WHITE)
    text(d, (540, CY - 230 + y0), "BULLETIN DE SALAIRE", 36, (60, 60, 60))
    d.line([230, CY - 180 + y0, 850, CY - 180 + y0], fill=(200, 200, 200), width=3)
    n = 1477.93 * ease(lt / 1.2)
    text(d, (540, CY - 60 + y0), f"{fmt(int(n), 0)} €", 120, BG)
    text(d, (540, CY + 40 + y0), "NET PAR MOIS", 40, (90, 90, 90))
    if lt > 1.3:
        tag(d, 540, CY + 160 + y0, "9,74 € DE L'HEURE", 44, RED)


H_OFF = 900


def s_1sur10(d, img, lt, dur):
    pop_text(d, (540, CY - 330), "2 MILLIONS", 110, YELLOW, lt)
    pop_text(d, (540, CY - 230), "DE SALARIÉS AU SMIC", 46, WHITE, lt - 0.2)
    for i in range(10):
        x = 120 + (i % 5) * 210
        y = CY + 10 + (i // 5) * 260
        k = ease((lt - 0.3 - 0.06 * i) / 0.3)
        if k <= 0:
            continue
        col = YELLOW if (i == 2 and lt > 1.2) else mix(BG, GREY, k)
        person(d, x, y, 120 * (0.7 + 0.3 * k), col)
    if lt > 1.4:
        tag(d, 540, CY + 470, "1 SALARIÉ SUR 10", 48, RED)


def s_auto(d, img, lt, dur):
    text(d, (540, CY - 330), "HAUSSES AUTOMATIQUES", 56, WHITE, alpha=min(1, lt / 0.3))
    rows = [("JANV. 2026", 1.18, 0.0), ("JUIN 2026", 2.41, 0.9)]
    for j, (lab, v, d0) in enumerate(rows):
        y = CY - 170 + j * 200
        k = ease((lt - d0) / 0.8)
        if lt < d0:
            continue
        text(d, (120, y), lab, 42, WHITE, anchor="lm")
        bar(d, 120, y + 40, 840, 56, k * v / 3.0, YELLOW)
        text(d, (140 + 840 * k * v / 3.0 + 20, y + 68), f"+{fmt(v * k, 2)} %", 44, WHITE, anchor="lm")
    if lt > 2.6:
        pop_text(d, (540, CY + 330), "= RATTRAPER LES PRIX", 60, RED, lt - 2.6)


def s_2012b(d, img, lt, dur):
    pop_text(d, (540, CY - 200), "JUILLET 2012", 70, WHITE, lt)
    pop_text(d, (540, CY), "+0,6 %", 200, YELLOW, lt - 0.3, 0.45)
    if lt > 1.0:
        tag(d, 540, CY + 200, "LE DERNIER VRAI COUP DE POUCE", 44, RED)


def s_matignon(d, img, lt, dur):
    text(d, (540, CY - 340), "OBJECTIF DU MINISTRE", 52, WHITE, alpha=min(1, lt / 0.3))
    k = ease((lt - 0.4) / 1.6)
    cx, cy, r = 540, CY + 120, 330
    d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=PANEL, width=60)
    frac = (lerp(1477.93, 1500, k) - 1400) / 200
    d.arc([cx - r, cy - r, cx + r, cy + r], 180, 180 + 180 * frac, fill=YELLOW, width=60)
    a = math.radians(180 + 180 * (100 / 200))
    d.line([cx + (r - 50) * math.cos(a), cy + (r - 50) * math.sin(a), cx + (r + 50) * math.cos(a),
            cy + (r + 50) * math.sin(a)], fill=RED, width=10)
    text(d, (cx, cy - 60), f"{fmt(lerp(1477.93, 1500, k), 0)} €", 110, WHITE)
    text(d, (cx, cy + 20), "NET", 40, GREY)
    if lt > 2.0:
        tag(d, 540, CY + 330, "LA BARRE DES 1 500 €", 46, RED)


def s_syndicats(d, img, lt, dur):
    text(d, (540, CY - 360), "CE QUE DEMANDENT LES SYNDICATS", 44, WHITE, alpha=min(1, lt / 0.3))
    rows = [("MINISTRE", 1500, GREY, 0.0), ("CFDT", 1578, YELLOW, 0.5), ("CGT", 1626, YELLOW, 1.6),
            ("FO", 2000, RED, 2.6)]
    for j, (lab, v, col, d0) in enumerate(rows):
        if lt < d0:
            continue
        y = CY - 240 + j * 170
        k = ease((lt - d0) / 0.7)
        text(d, (100, y), lab, 42, WHITE, anchor="lm")
        frac = (v - 1300) / 800 * k
        bar(d, 100, y + 38, 760, 60, frac, col)
        text(d, (110 + 760 * frac + 20, y + 68), f"{fmt(lerp(1300, v, k), 0)} €", 40, WHITE, anchor="lm")


FRA = ESP = None


def s_espagne(d, img, lt, dur):
    global FRA, ESP
    if FRA is None:
        FRA, ESP = load_country("FRA"), load_country("ESP")
    lon0, lat1, sc = -10.0, 51.5, 50
    P = lambda lo, la: (90 + (lo - lon0) * sc, CY - 560 + (lat1 - la) * sc * 1.35)  # noqa: E731
    k = ease(lt / 0.6)
    for rings, col in [(FRA, mix(BG, PANEL, k)), (ESP, mix(BG, mix(PANEL, RED, 0.45 * ease((lt - 0.6) / 0.5)), k))]:
        for ring in rings:
            pts = [P(lo, la) for lo, la in ring if lo > -11 and la > 35]
            if len(pts) > 2:
                d.polygon(pts, fill=col, outline=GREY)
    pop_text(d, P(-3.7, 40.3), "+5 %", 96, YELLOW, lt - 0.6)
    pop_text(d, P(2.4, 46.8), "1 500 € ?", 64, WHITE, lt - 1.0)
    if lt > 2.2:
        tag(d, 540, CY + 590, "DES ÉCONOMISTES DIVISÉS", 44, RED)


def s_femmes(d, img, lt, dur):
    pop_text(d, (540, CY - 350), "QUI EST AU SMIC ?", 64, WHITE, lt)
    for i in range(10):
        x = 120 + (i % 5) * 210
        y = CY - 100 + (i // 5) * 260
        k = ease((lt - 0.2 - 0.05 * i) / 0.3)
        if k <= 0:
            continue
        col = YELLOW if i < 6 else GREY
        person(d, x, y, 120 * (0.7 + 0.3 * k), mix(BG, col, k))
    if lt > 0.9:
        tag(d, 540, CY + 330, "6 SUR 10 SONT DES FEMMES", 44, RED)
    if lt > 2.6:
        tag(d, 540, CY + 430, "1 SUR 4 À TEMPS PARTIEL", 40, (70, 70, 78))


def s_question(d, img, lt, dur):
    pop_text(d, (540, CY - 120), "1 500 €", 170, YELLOW, lt, 0.45)
    pop_text(d, (540, CY + 60), "VICTOIRE", 90, GREEN, lt - 0.6)
    pop_text(d, (540, CY + 170), "OU MINIMUM ?", 90, RED, lt - 1.2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("eco_smic", "scripts/eco/smic.txt", "SAM. 7 NOV. 2026", "SMIC")
    v.voice(a.voice_file)
    v.scene("Depuis deux mille douze", s_2012)
    v.scene("Aujourd'hui, le SMIC", s_paie)
    v.scene("Plus de deux millions", s_1sur10)
    v.scene("Chaque premier janvier", s_auto)
    v.scene("Le dernier vrai coup", s_2012b)
    v.scene("Et pourtant", s_matignon)
    v.scene("Mais alors", s_syndicats)
    v.scene("Pendant ce temps", s_espagne)
    v.scene("Près de six smicards", s_femmes)
    v.scene("Alors honnêtement", s_question)
    v.render()


if __name__ == "__main__":
    main()
