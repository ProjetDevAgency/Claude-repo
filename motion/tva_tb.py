"""Actu éco (dim. 8 novembre 2026) : la TVA à 5,5 % sur l'électricité votée puis effacée. Style tableau blanc."""
import argparse

from whiteboard import BLUE, GREEN, GREY, INK, RED, TINT, Pen, WhiteboardVideo
from engine import F, ease, lerp

CY = 920


def check(p, x, y, t0, col=GREEN, s=1.0):
    p.line([(x - 22 * s, y), (x - 6 * s, y + 18 * s), (x + 26 * s, y - 22 * s)], t0, 0.25, col, 9)


def building(p, cx, base, w, h, t0, dur=1.0, label=None):
    """Bâtiment à colonnes (Assemblée, Sénat)."""
    x0, x1, top = cx - w / 2, cx + w / 2, base - h
    paths = [[(x0 - 30, top), (cx, top - h * 0.35), (x1 + 30, top), (x0 - 30, top)],
             [(x0 - 40, base), (x1 + 40, base)], [(x0, top + 20), (x1, top + 20)]]
    n = 5
    for i in range(n):
        x = x0 + 30 + i * (w - 60) / (n - 1)
        paths.append([(x, top + 30), (x, base - 10)])
    p.strokes(paths, t0, dur, INK, 8)
    if label:
        p.write((cx, base + 55), label, 44, INK, t0 + dur)


def house(p, cx, base, s, t0, dur=0.8):
    p.strokes([[(cx - s, base), (cx - s, base - s * 1.1), (cx, base - s * 1.9), (cx + s, base - s * 1.1),
                (cx + s, base), (cx - s, base)],
               [(cx - s * 0.25, base), (cx - s * 0.25, base - s * 0.6), (cx + s * 0.25, base - s * 0.6),
                (cx + s * 0.25, base)]], t0, dur, INK, 8)
    # éclair
    p.line([(cx + 0.1 * s, base - s * 1.55), (cx - 0.2 * s, base - s * 1.05), (cx + 0.1 * s, base - s * 1.05),
            (cx - 0.15 * s, base - s * 0.7)], t0 + dur, 0.3, RED, 8)


def facture(p, x, y, t0, tva_col=INK):
    p.doc(x, y, 640, 520, t0, "FACTURE D'ÉLECTRICITÉ", tcol=INK)
    for j, (lab, val) in enumerate([("ABONNEMENT", "…"), ("KWH CONSOMMÉS", "…")]):
        p.write((x - 260, y - 120 + j * 70), lab, 36, INK, t0 + 0.8 + 0.2 * j, 0.4, anchor="lm")
    p.write((x - 260, y + 40), "TVA", 50, INK, t0 + 1.2, 0.3, anchor="lm")
    p.write((x + 230, y + 40), "20 %", 64, tva_col, t0 + 1.4, 0.3, anchor="rm")


# ── scènes ──

def s_hook(d, img, lt, dur):
    p = Pen(d, img, lt)
    facture(p, 540, CY - 20, 0.0)
    p.cross(380, CY - 10, 560, CY + 80, 2.0, 0.3, RED, 10)
    p.write((540, CY + 170), "5,5 %", 90, RED, 2.3, 0.4)
    p.ellipse(540, CY + 170, 150, 65, 2.8, 0.4, RED, 7)
    p.write((540, CY + 340), "−269 € PAR AN", 64, GREEN, 3.1)


def s_vote(d, img, lt, dur):
    p = Pen(d, img, lt)
    building(p, 540, CY + 200, 560, 330, 0.0, 0.8, "ASSEMBLÉE NATIONALE")
    if lt > 0.6:
        k = ease((lt - 0.6) / 0.25)
        s = 1 + 0.4 * (1 - k)
        f = F(int(90 * s))
        d.rounded_rectangle([540 - 220 * s, CY - 330 - 70 * s, 540 + 220 * s, CY - 330 + 70 * s], radius=20,
                            outline=GREEN, width=10)
        d.text((540, CY - 330), "VOTÉ", font=f, fill=GREEN, anchor="mm")


def s_disparu(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 380), "2 JOURS PLUS TARD", 56, INK, 0.0, 0.5)
    # le papier « 5,5 % » en pointillés, qui s'efface
    a = max(0.0, 1 - ease((lt - 0.3) / 0.8))
    if a > 0:
        col = tuple(int(250 + (c - 250) * a) for c in RED)
        d.text((540, CY - 40), "TVA 5,5 %", font=F(110), fill=col, anchor="mm")
    for i in range(14):
        x = 200 + i * 50
        if lt > 0.3 + i * 0.03:
            d.line([x, CY - 140, x + 25, CY - 140], fill=GREY, width=6)
            d.line([x, CY + 60, x + 25, CY + 60], fill=GREY, width=6)
    p.write((540, CY + 260), "DISPARUE", 100, RED, 0.6, 0.5)


def s_amendement(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 400), "LUNDI 2 NOVEMBRE", 52, INK, 0.0)
    p.underline(320, 760, CY - 365, 0.6, 0.3, INK, 6)
    p.write((280, CY - 210), "20 %", 110, INK, 0.5, 0.4)
    p.arrow(420, CY - 210, 620, CY - 210, 1.2, 0.4, RED, 10)
    p.write((800, CY - 210), "5,5 %", 110, RED, 1.6, 0.4)
    p.write((540, CY - 90), "DE TVA", 50, GREY, 2.0)
    for j, (lab, t0) in enumerate([("L'ABONNEMENT", 4.2), ("LES KWH", 5.2), ("TOUTE LA FACTURE", 6.0)]):
        y = CY + 60 + j * 110
        p.rect(170, y - 35, 240, y + 35, t0, 0.3, INK, 6)
        check(p, 205, y, t0 + 0.3)
        p.write((280, y), lab, 52, INK, t0 + 0.3, anchor="lm")


def s_maison(d, img, lt, dur):
    p = Pen(d, img, lt)
    house(p, 300, CY + 100, 180, 0.0)
    p.write((300, CY + 170), "TOUT ÉLECTRIQUE", 40, INK, 0.6)
    p.write((300, CY - 420), "−269 €", 92, GREEN, 1.0, 0.6)
    p.write((300, CY - 340), "PAR AN", 40, GREEN, 1.6)
    house(p, 800, CY + 100, 90, 3.6, 0.5)
    p.write((800, CY + 170), "STUDIO", 40, INK, 4.1)
    p.write((800, CY - 120), "−54 €", 72, GREEN, 4.4, 0.5)
    p.write((540, CY + 330), "9 KVA · 10 000 KWH PAR AN · TARIF BLEU", 32, GREY, 2.0)


def s_qui(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 420), "QUI L'A PORTÉ ?", 60, INK, 0.0)
    p.person(250, CY - 20, 120, 0.8, 0.6, mood="neutre")
    p.person(830, CY - 20, 120, 1.6, 0.6, mood="neutre")
    p.write((250, CY + 180), "COMMUNISTES", 40, INK, 1.3)
    p.write((250, CY + 230), "(GDR)", 34, GREY, 1.6)
    p.write((830, CY + 180), "RASSEMBLEMENT", 40, INK, 2.1)
    p.write((830, CY + 230), "NATIONAL", 40, INK, 2.5)
    p.arrow(360, CY - 200, 470, CY - 260, 2.8, 0.3, INK, 7)
    p.arrow(720, CY - 200, 610, CY - 260, 3.0, 0.3, INK, 7)
    p.write((540, CY - 280), "=", 70, RED, 3.3, 0.2)
    p.write((540, CY + 380), "43 POUR · 13 CONTRE", 56, RED, 4.2)


def s_tabac(d, img, lt, dur):
    p = Pen(d, img, lt)
    # cigarette
    p.rect(200, CY - 80, 760, CY + 20, 0.0, 0.6, INK, 8)
    p.rect(760, CY - 80, 880, CY + 20, 0.6, 0.3, INK, 8, fill=(240, 200, 150))
    p.strokes([[(210, CY - 110), (190, CY - 170), (215, CY - 230)], [(250, CY - 110), (232, CY - 175), (255, CY - 240)]],
              0.9, 0.4, GREY, 6)
    p.write((540, CY - 360), "POUR PAYER LA BAISSE", 52, INK, 0.2)
    p.write((540, CY + 200), "+ TAXE SUR LE TABAC", 64, RED, 1.4)


def s_rejet(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 420), "MERCREDI 4 NOVEMBRE", 52, INK, 0.0)
    p.write((540, CY - 330), "PARTIE RECETTES DU BUDGET", 44, GREY, 0.8)
    base = CY + 300
    k = ease((lt - 3.6) / 0.9)
    if k > 0:
        d.rectangle([220, base - 520 * k, 460, base], fill=TINT[RED])
    p.rect(220, base - 520, 460, base, 3.6, 0.6, RED, 8)
    p.write((340, base + 60), "CONTRE", 44, RED, 3.8)
    p.write((340, base - 570), "458", 80, RED, 4.3, 0.4)
    p.line([(620, base), (860, base)], 4.6, 0.3, INK, 8)
    p.write((740, base + 60), "POUR", 44, INK, 4.6)
    p.write((740, base - 80), "0", 110, INK, 5.0, 0.3)
    p.line([(160, base), (920, base)], 3.4, 0.3, INK, 8)


def s_senat(d, img, lt, dur):
    p = Pen(d, img, lt)
    # version des députés, barrée
    p.doc(270, CY - 220, 360, 300, 0.0)
    p.write((270, CY - 290), "VERSION", 36, INK, 0.5)
    p.write((270, CY - 240), "DES DÉPUTÉS", 36, INK, 0.8)
    p.write((270, CY - 160), "TVA 5,5 %", 44, RED, 1.2)
    p.cross(110, CY - 360, 430, CY - 80, 2.6, 0.4)
    # version du gouvernement, qui part au Sénat
    p.doc(810, CY - 220, 360, 300, 3.2)
    p.write((810, CY - 290), "VERSION DU", 36, INK, 3.7)
    p.write((810, CY - 240), "GOUVERNEMENT", 36, INK, 4.0)
    p.write((810, CY - 160), "TVA 20 %", 44, INK, 4.4)
    p.arrow(810, CY - 50, 810, CY + 60, 4.8, 0.3, INK, 8)
    building(p, 810, CY + 330, 280, 180, 5.0, 0.8, "SÉNAT")
    p.write((300, CY + 200), "LA BAISSE ?", 56, RED, 5.6)
    p.write((300, CY + 280), "JAMAIS ÉCRITE", 56, RED, 6.1)


def s_avant(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 420), "TVA SUR TON ABONNEMENT", 52, INK, 0.0)
    x0, xm, x1 = 140, 560, 960
    yl, yh = CY + 150, CY - 170
    p.line([(x0, CY + 300), (x1, CY + 300)], 0.4, 0.3, INK, 6)
    p.line([(x0, yl), (xm, yl)], 1.2, 0.8, GREEN, 10)
    p.write((350, yl - 60), "5,5 %", 72, GREEN, 1.6, 0.4)
    p.line([(xm, yl), (xm, yh)], 3.6, 0.4, RED, 10)
    p.line([(xm, yh), (x1, yh)], 4.0, 0.6, RED, 10)
    p.write((770, yh - 60), "20 %", 72, RED, 4.3, 0.4)
    p.write((xm, CY + 360), "1ER AOÛT 2025", 44, INK, 3.0)
    p.line([(xm, CY + 290), (xm, CY + 310)], 3.0, 0.1, INK, 6)


def s_2025(d, img, lt, dur):
    p = Pen(d, img, lt)
    for j, (yr, txt, col, t0) in enumerate([("NOV. 2025", "VOTÉ", GREEN, 0.0), ("2026", "RESTÉ À 20 %", RED, 2.4)]):
        x = 300 + j * 480
        p.rect(x - 190, CY - 300, x + 190, CY + 60, t0, 0.6, INK, 8)
        p.line([(x - 190, CY - 200), (x + 190, CY - 200)], t0 + 0.5, 0.2, INK, 8)
        p.write((x, CY - 250), yr, 44, INK, t0 + 0.6)
        p.write((x, CY - 70), txt, 50 if j else 70, col, t0 + 1.0)
    p.arrow(500, CY - 120, 580, CY - 120, 2.2, 0.2, INK, 8)
    p.write((540, CY + 240), "L'ABONNEMENT", 52, INK, 2.8)


def s_suite(d, img, lt, dur):
    p = Pen(d, img, lt)
    building(p, 540, CY + 50, 480, 280, 0.0, 0.8, "SÉNAT")
    p.write((540, CY + 230), "AMENDEMENTS JUSQU'AU 19 NOV.", 40, GREY, 1.0)
    p.write((540, CY + 320), "VOTE VERS LE 28 NOV.", 52, RED, 1.8)


def s_chute(d, img, lt, dur):
    p = Pen(d, img, lt)
    p.write((540, CY - 380), "VOTÉE", 80, GREEN, 0.0, 0.3)
    check(p, 400, CY - 240, 0.3, GREEN, 1.6)
    check(p, 680, CY - 240, 0.6, GREEN, 1.6)
    p.write((400, CY - 150), "2025", 40, GREY, 0.4)
    p.write((680, CY - 150), "2026", 40, GREY, 0.7)
    p.write((540, CY + 60), "TVA", 70, INK, 1.0, 0.2)
    p.write((540, CY + 190), "20 %", 150, RED, 1.2, 0.3)
    p.ellipse(540, CY + 160, 300, 160, 1.6, 0.5, RED, 9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = WhiteboardVideo("eco_tva", "scripts/eco/tva_electricite.txt", "DIM. 8 NOV. 2026", "ÉLECTRICITÉ",
                        hook_lines=[("−269 € PAR AN", RED), ("SUR TA FACTURE", INK), ("D'ÉLECTRICITÉ", INK)],
                        hook_size=66)
    v.voice(a.voice_file)
    v.scene("Deux cent soixante-neuf euros de moins", s_hook)
    v.scene("Les députés l'ont voté", s_vote)
    v.scene("Deux jours plus tard", s_disparu)
    v.scene("Le lundi deux novembre", s_amendement)
    v.scene("Pour une maison tout électrique", s_maison)
    v.scene("Et le plus fou", s_qui)
    v.scene("Et pour payer la baisse", s_tabac)
    v.scene("Et pourtant, le mercredi", s_rejet)
    v.scene("Mais alors, pourquoi", s_senat)
    v.scene("Ce que peu de gens savent", s_avant)
    v.scene("Et l'an dernier", s_2025)
    v.scene("Le Sénat peut encore", s_suite)
    v.scene("Votée deux années de suite", s_chute)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
