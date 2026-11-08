"""Série L'argent qui détruit les familles — n°2 : le rapport des donations (Claire et Julien)."""
import argparse

from engine import (BG, GREEN, GREY, PANEL, RED, WHITE, YELLOW, F, Video, back, bar, ease, fmt, lerp, mix,
                    person, pop_text, tag, text)
from shein import arrow

CY = 860          # zone d'animation sous le cadre du hook
BLUE = (80, 160, 240)


def bubble(d, x, y, lines, col=WHITE, k=1.0, size=40):
    w = max(F(size).getlength(l) for l in lines) + 60
    h = len(lines) * (size + 14) + 40
    c = mix(BG, col, k)
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=30, fill=c)
    d.polygon([(x - 30, y + h / 2 - 2), (x + 10, y + h / 2 - 2), (x - 40, y + h / 2 + 40)], fill=c)
    for j, l in enumerate(lines):
        text(d, (x, y - h / 2 + 20 + (size + 14) * (j + 0.5)), l, size, BG, alpha=k)


def doc(d, x, y, w, h, title, lines, k=1.0, tcol=RED):
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=20, fill=mix(BG, WHITE, k))
    text(d, (x, y - h / 2 + 50), title, 38, tcol, alpha=k)
    for j, l in enumerate(lines):
        text(d, (x, y - h / 2 + 130 + j * 62), l, 40, BG, alpha=k)


def siblings(d, lt, julien_col=YELLOW, claire_col=GREY):
    person(d, 300, CY + 120, 150, mix(BG, julien_col, ease(lt / 0.3)))
    text(d, (300, CY + 230), "JULIEN", 36, julien_col)
    person(d, 780, CY + 120, 150, mix(BG, claire_col, ease(lt / 0.3)))
    text(d, (780, CY + 230), "CLAIRE", 36, claire_col)


def s_hook(d, img, lt, dur):
    n = 150_000 * ease(lt / 1.0)
    text(d, (540, CY - 240), f"{fmt(n)} €", 110, YELLOW)
    siblings(d, lt)
    if lt > 0.6:
        arrow(d, 540, CY - 160, 360, CY - 10, YELLOW, 10)
    if lt > 2.0:
        text(d, (780, CY - 20), "?", 120, RED)
    if lt > 3.0:
        tag(d, 540, CY + 340, "DÉCOUVERT CHEZ LE NOTAIRE", 44, RED)


def s_papier(d, img, lt, dur):
    # sac + papier plié
    d.rounded_rectangle([370, CY - 150, 710, CY + 180], radius=40, fill=(150, 90, 60))
    d.arc([440, CY - 260, 640, CY - 60], 180, 360, fill=(150, 90, 60), width=22)
    k = ease((lt - 0.4) / 0.6)
    d.rectangle([470, CY - 150 - 120 * k, 610, CY - 150 + 40], fill=WHITE)
    text(d, (540, CY - 190 - 120 * k + 120), "?", 60, BG)
    if lt > 1.2:
        tag(d, 540, CY + 300, "UN SEUL PAPIER", 52, RED)
    if lt > 2.6:
        tag(d, 540, CY + 410, "UN APPARTEMENT À LYON · IL Y A 15 ANS", 34, (70, 70, 78))


def s_montee(d, img, lt, dur):
    person(d, 540, CY - 120, 170, GREY)
    text(d, (540, CY + 10), "CLAIRE", 36, GREY)
    pop_text(d, (540, CY + 130), "6 ANS", 110, WHITE, lt - 0.4)
    pop_text(d, (540, CY + 230), "DE DIMANCHES À L'HÔPITAL", 46, BLUE, lt - 0.8)
    if lt > 2.6:
        tag(d, 540, CY + 340, "JAMAIS RIEN DEMANDÉ", 44, (70, 70, 78))


def s_coups(d, img, lt, dur):
    siblings(d, 1.0)
    bubble(d, 330, CY - 250, ["C'ÉTAIT UN CADEAU,", "ÇA COMPTE PAS"], WHITE, ease(lt / 0.3))
    if lt > 3.4:
        bubble(d, 560, CY - 60, ["AVEC TON PETIT", "SALAIRE DE PROF"], RED, ease((lt - 3.4) / 0.3))


def s_silence(d, img, lt, dur):
    person(d, 540, CY - 60, 190, GREY)
    if lt > 1.8:
        pop_text(d, (540, CY + 230), "« ÇA COMPTE PAS. »", 72, RED, lt - 1.8)


def s_843(d, img, lt, dur):
    k = ease(lt / 0.4)
    doc(d, 540, CY - 60, 900, 520, "CODE CIVIL · ARTICLE 843",
        ["TOUT HÉRITIER DOIT RAPPORTER", "À SES COHÉRITIERS CE QU'IL", "A REÇU PAR DONATION"] if lt > 1.6 else [], k)
    if lt > 4.6:
        tag(d, 540, CY + 330, "LE CADEAU REVIENT DANS L'HÉRITAGE", 44, RED)


def s_valeur(d, img, lt, dur):
    rows = [("IL Y A 15 ANS", 150_000, GREY, 0.2), ("AUJOURD'HUI", 300_000, RED, 2.4)]
    for j, (lab, v, col, d0) in enumerate(rows):
        if lt < d0:
            continue
        k = ease((lt - d0) / 0.8)
        y = CY - 300 + j * 260
        text(d, (100, y), lab, 42, WHITE, anchor="lm")
        bar(d, 100, y + 50, 880, 80, k * v / 320_000, col)
        text(d, (980, y + 180), f"{fmt(v * k)} €", 64, col if j else WHITE, anchor="rm")
    if lt > 3.4:
        tag(d, 540, CY + 330, "VALEUR DU BIEN AU MOMENT DE L'HÉRITAGE · ART. 860", 30, (70, 70, 78))


def s_exception(d, img, lt, dur):
    doc(d, 540, CY - 100, 860, 460, "ACTE DE DONATION", ["……………………", "« HORS PART", "SUCCESSORALE »"], ease(lt / 0.4), GREY)
    if lt > 4.0:
        d.line([200, CY - 120, 880, CY + 40], fill=RED, width=16)
        tag(d, 540, CY + 260, "AUCUNE MENTION DANS L'ACTE", 46, RED)


def s_demi(d, img, lt, dur):
    pop_text(d, (540, CY - 220), "UN COUP DE POUCE", 70, YELLOW, lt)
    pop_text(d, (540, CY - 100), "OU", 50, WHITE, lt - 0.6)
    pop_text(d, (540, CY + 20), "UNE AVANCE ?", 70, RED, lt - 1.2)


def s_preuve(d, img, lt, dur):
    k = ease(lt / 0.5)
    y = lerp(CY + 400, CY - 80, ease((lt - 1.6) / 0.8))
    doc(d, 540, y, 820, 440, "ORDRE DE VIREMENT", ["150 000 €", "POUR L'APPARTEMENT", "DE JULIEN"], k)
    if lt > 3.2:
        tag(d, 720, y + 160, "SIGNÉ : PAPA", 40, BLUE)
    if lt > 3.6:
        tag(d, 540, CY + 330, "LE SEUL PAPIER QU'ELLE AVAIT GARDÉ", 40, RED)


def s_chute(d, img, lt, dur):
    pop_text(d, (540, CY - 200), "150 000 €", 110, YELLOW, lt)
    pop_text(d, (540, CY - 100), "DE CADEAU", 54, WHITE, lt)
    pop_text(d, (540, CY + 60), "300 000 €", 110, RED, lt - 1.2)
    pop_text(d, (540, CY + 160), "DE DETTE", 54, WHITE, lt - 1.2)
    if lt > 2.2:
        tag(d, 540, CY + 330, "CAS TYPE · CECI N'EST PAS UN CONSEIL JURIDIQUE", 28, (70, 70, 78))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = Video("famille_2_rapport", "scripts/finance/famille_2_rapport.txt",
              "L'ARGENT QUI DÉTRUIT LES FAMILLES", "HÉRITAGE")
    v.voice(a.voice_file)
    v.scene("Cent cinquante mille euros offerts", s_hook)
    v.scene("Elle a gardé un seul papier", s_papier)
    v.scene("Claire, elle, a jamais", s_montee)
    v.scene("Chez le notaire, Julien rigole", s_coups)
    v.scene("Claire dit rien", s_silence)
    v.scene("Et pourtant, le Code civil", s_843)
    v.scene("Mais alors, Julien rend", s_valeur)
    v.scene("Sauf qu'il existe une exception", s_exception)
    v.scene("Honnêtement, Julien", s_demi)
    v.scene("Julien demande une preuve", s_preuve)
    v.scene("Cent cinquante mille euros de cadeau", s_chute, after=40)
    v.render()


if __name__ == "__main__":
    main()
