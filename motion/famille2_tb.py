"""Famille n°2, le rapport des donations : version tableau blanc (même voix, même script)."""
import argparse

from whiteboard import BLUE, GREEN, GREY, INK, RED, TINT, Pen, WhiteboardVideo
from engine import ROOT, ease, lerp

CY = 900  # centre de la zone de dessin (entre le cadre du hook et les sous-titres)


def duo(p, t0=0.0, dur=0.8, j_mood="neutre", c_mood="neutre", j_arms="bas", names=True):
    p.person(300, CY + 130, 150, t0, dur, hair="court", mood=j_mood, arms=j_arms)
    p.person(780, CY + 130, 150, t0 + dur, dur, hair="long", mood=c_mood)
    if names:
        p.write((300, CY + 345), "JULIEN", 44, INK, t0 + dur * 0.8)
        p.write((780, CY + 345), "CLAIRE", 44, INK, t0 + dur * 1.8)


def s_hook(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((300, CY - 330), "150 000 €", 76, RED, 0.0, 0.7)
    p.ellipse(300, CY - 330, 250, 75, 0.7, 0.5, RED, 7)
    duo(p, 0.9, 0.6, j_mood="rire", j_arms="haut")
    p.write((780, CY - 230), "?", 150, RED, 2.6, 0.3)
    p.write((540, CY + 440), "DÉCOUVERT CHEZ LE NOTAIRE", 46, INK, 3.0)
    p.underline(220, 860, CY + 475, 4.0, 0.4)


def s_papier(d, img, lt, dur):
    p = Pen(d, img, lt)
    # le sac
    p.strokes([[(380, CY - 120), (700, CY - 120), (740, CY + 220), (340, CY + 220), (380, CY - 124)]], 0.0, 0.7, INK, 9)
    p.strokes([[(450, CY - 120), (470, CY - 230), (610, CY - 230), (630, CY - 120)]], 0.7, 0.4, INK, 9)
    # le papier plié qui dépasse
    k = ease((lt - 1.1) / 0.6)
    y = CY - 110 - 150 * k
    if y < CY - 126:
        d.rectangle([480, y, 600, CY - 125], fill=(255, 255, 255))
        d.line([480, CY - 125, 480, y, 600, y, 600, CY - 125], fill=INK, width=7)
        for j in range(3):
            if y + 30 + j * 30 < CY - 130:
                d.line([500, y + 30 + j * 30, 580, y + 30 + j * 30], fill=GREY, width=4)
    p.write((540, CY + 330), "UN SEUL PAPIER", 64, RED, 1.6)
    p.write((540, CY + 430), "UN APPARTEMENT À LYON", 44, INK, 2.8)
    p.write((540, CY + 500), "IL Y A 15 ANS", 44, GREY, 3.6)


def s_montee(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.person(300, CY + 160, 160, 0.0, 0.8, hair="long")
    # l'hôpital
    p.rect(560, CY - 120, 940, CY + 330, 0.8, 0.8, INK, 8)
    p.rect(700, CY + 200, 800, CY + 330, 1.4, 0.3, INK, 7)
    p.strokes([[(750, CY - 70), (750, CY + 50)], [(690, CY - 10), (810, CY - 10)]], 1.7, 0.4, RED, 16)
    for j in range(2):
        p.rect(600 + j * 220, CY + 90, 680 + j * 220, CY + 160, 2.0 + 0.2 * j, 0.2, INK, 6)
    p.write((540, CY - 320), "6 ANS", 120, INK, 0.3, 0.6)
    p.write((540, CY - 200), "DE DIMANCHES À L'HÔPITAL", 50, BLUE, 1.0)
    p.write((540, CY + 460), "JAMAIS RIEN DEMANDÉ", 50, INK, 2.8)
    p.underline(270, 810, CY + 495, 3.6, 0.4, BLUE)


def s_coups(d, img, lt, dur):
    p = Pen(d, img, 9.0 if lt > 0 else 0)  # les deux personnages déjà là
    duo(p, 0, 0.01, j_mood="rire", c_mood="neutre")
    p = Pen(d, img, lt)
    p.bubble(330, CY - 440, ["C'ÉTAIT UN CADEAU,", "ÇA COMPTE PAS"], 42, 0.1)
    if lt < 3.4:
        return
    p.bubble(520, CY - 265, ["AVEC TON PETIT", "SALAIRE DE PROF"], 38, 3.4, RED, tail="bas-gauche")


def s_silence(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.person(540, CY + 60, 190, 0.0, 0.9, hair="long", mood="triste")
    p.line([(160, CY + 120), (920, CY + 120)], 0.9, 0.5, INK, 9)  # la table
    p.write((540, CY + 400), "« ÇA COMPTE PAS. »", 76, RED, 1.8, 0.8)


def s_843(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.doc(540, CY - 60, 900, 560, 0.0, "CODE CIVIL · ARTICLE 843")
    for j, l in enumerate(["TOUT HÉRITIER DOIT RAPPORTER", "À SES COHÉRITIERS CE QU'IL", "A REÇU PAR DONATION"]):
        p.write((540, CY - 160 + j * 80), l, 44, INK, 1.6 + 0.9 * j, 0.9)
    p.underline(220, 860, CY + 30, 4.4, 0.4)
    p.write((540, CY + 360), "LE CADEAU REVIENT", 56, RED, 4.6)
    p.write((540, CY + 440), "DANS L'HÉRITAGE", 56, RED, 5.3)


def s_valeur(d, img, lt, dur):
    p = Pen(d, img, lt)
    base = CY + 300
    for j, (lab, v, col, t0) in enumerate([("IL Y A 15 ANS", "150 000 €", INK, 0.2),
                                            ("AUJOURD'HUI", "300 000 €", RED, 2.4)]):
        x = 320 + j * 440
        h = 260 if j == 0 else 520
        k = ease((lt - t0) / 0.8)
        top = base - h * k
        if k > 0:
            d.rectangle([x - 120, top, x + 120, base], fill=TINT[col])
        p.rect(x - 120, base - h, x + 120, base, t0, 0.8, col, 8)
        p.write((x, base - h - 60), v, 56, col, t0 + 0.8)
        p.write((x, base + 60), lab, 40, INK, t0 + 0.3)
    p.line([(120, base), (960, base)], 0.0, 0.3, INK, 8)
    p.write((540, CY + 470), "VALEUR DU BIEN AU JOUR DU PARTAGE · ART. 860", 32, GREY, 3.6)


def s_exception(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.doc(540, CY - 60, 820, 520, 0.0, "ACTE DE DONATION", tcol=INK)
    for j in range(3):
        p.line([(220, CY - 160 + j * 50), (860 - 80 * (j % 2), CY - 160 + j * 50)], 0.9 + 0.2 * j, 0.2, GREY, 5)
    p.write((540, CY + 50), "« HORS PART", 54, BLUE, 1.6)
    p.write((540, CY + 120), "SUCCESSORALE »", 54, BLUE, 2.2)
    p.cross(200, CY - 300, 880, CY + 180, 4.0, 0.5)
    p.write((540, CY + 360), "AUCUNE MENTION DANS L'ACTE", 52, RED, 4.5)


def s_demi(d, img, lt, dur):
    p = Pen(d, img, lt)
    # balance
    p.strokes([[(540, CY + 250), (540, CY - 120)], [(420, CY + 250), (660, CY + 250)]], 0.0, 0.5, INK, 9)
    tilt = 40 * ease((lt - 2.0) / 0.6)
    lx, rx = 230, 850
    ly, ry = CY - 120 + tilt, CY - 120 - tilt
    p.line([(lx, ly), (rx, ry)], 0.4, 0.4, INK, 9)
    for x, y, t0 in ((lx, ly, 0.8), (rx, ry, 1.0)):
        p.strokes([[(x, y), (x - 90, y + 140)], [(x, y), (x + 90, y + 140)],
                   [(x - 110, y + 140), (x + 110, y + 140)]], t0, 0.4, INK, 7)
    p.write((lx, ly + 200), "UN COUP", 46, GREEN, 0.4)
    p.write((lx, ly + 255), "DE POUCE", 46, GREEN, 0.8)
    p.write((rx, ry + 200), "UNE", 46, RED, 1.4)
    p.write((rx, ry + 255), "AVANCE", 46, RED, 1.7)
    p.write((540, CY + 400), "?", 120, INK, 2.2, 0.3)


def s_preuve(d, img, lt, dur):
    y = lerp(560, 0, ease((lt - 1.6) / 0.8))
    p = Pen(d, img, lt, dy=y)
    p.doc(540, CY - 80, 820, 520, 0.0, "ORDRE DE VIREMENT")
    p.write((540, CY - 120), "150 000 €", 80, INK, 0.0, 0.01)
    p.write((540, CY - 20), "POUR L'APPARTEMENT", 42, INK, 0.0, 0.01)
    p.write((540, CY + 40), "DE JULIEN", 42, INK, 0.0, 0.01)
    # signature à la main
    sig = [(560, CY + 120), (590, CY + 90), (610, CY + 140), (640, CY + 95), (660, CY + 130), (700, CY + 100),
           (730, CY + 125), (800, CY + 110)]
    p.line(sig, 2.6, 0.6, BLUE, 6)
    p.write((680, CY + 170), "PAPA", 36, BLUE, 3.2)
    p = Pen(d, img, lt)
    p.write((540, CY + 380), "LE SEUL PAPIER", 56, RED, 3.8)
    p.write((540, CY + 455), "QU'ELLE AVAIT GARDÉ", 56, RED, 4.4)


def s_chute(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 280), "150 000 €", 110, INK, 0.0, 0.6)
    p.write((540, CY - 170), "DE CADEAU", 56, GREY, 0.6)
    p.write((540, CY + 50), "300 000 €", 110, RED, 1.2, 0.6)
    p.write((540, CY + 160), "DE DETTE", 56, RED, 1.8)
    p.ellipse(540, CY + 90, 360, 140, 2.4, 0.6, RED, 8)
    p.write((540, CY + 420), "CAS TYPE · CECI N'EST PAS UN CONSEIL JURIDIQUE", 28, GREY, 3.0, 0.6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file", default=str(ROOT / "output/_work_famille_2_rapport/voice_raw.mp3"))
    a = ap.parse_args()
    v = WhiteboardVideo("famille_2_rapport_tb", "scripts/finance/famille_2_rapport.txt",
                        "L'ARGENT QUI DÉTRUIT LES FAMILLES", "HÉRITAGE",
                        hook_lines=[("150 000 € OFFERTS", INK), ("À SON FRÈRE", RED)])
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
