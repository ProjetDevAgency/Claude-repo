"""Démo d'ACCROCHE VISUELLE inventée (21 nov.) : « le ticket qui n'en finit pas ».
Une imprimante crache une facture interminable qui descend sur Kévin, « TOTAL 640 € » tombe comme un tampon,
Kévin déchire le ticket en deux : derrière, « 89 € » en vert et « −551 € ». Posée sur le début de la vidéo du garage
(mêmes voix, mêmes plans ensuite) pour comparer avec l'ouverture actuelle.

    python3 motion/trait/accroche_ticket.py            → output/trait/accroche_ticket.mp4
    python3 motion/trait/accroche_ticket.py --stills 0.3,1,2,3
"""
import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors_garage as G  # noqa: E402
import garage_travaux as GT  # noqa: E402
import ui  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, paint, rrect, stroke  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

LIGNES = [("VIDANGE", "89,00"), ("PLAQUETTES", "180,00"), ("DISQUES", "220,00"), ("ESSUIE-GLACES", "36,00"),
          ("BATTERIE", "115,00"), ("MAIN-D'ŒUVRE", "0,00")]
LARG = 560
PAS = 92


def ticket(ctx, x, y_haut, long, t_imp, t, coupe=None):
    """Ruban de ticket depuis y_haut sur une longueur long ; lignes imprimées selon long.
    coupe = (côté, k) : ne dessine que la moitié gauche (-1) ou droite (+1), écartée de k."""
    ctx.save()
    if coupe:
        cote, k = coupe
        ctx.translate(x + cote * 950 * k, y_haut + 1100 * k * k)
        ctx.rotate(cote * 1.1 * k)
        ctx.translate(-x, -y_haut)
        ctx.rectangle(x - 1000 if cote < 0 else x, -2000, 1000, 6000)
        ctx.clip()
    # ombre + papier avec bord dentelé
    for dx, col, a in ((14, (0, 0, 0), 0.3), (0, (252, 251, 246), 1.0)):
        ctx.move_to(x - LARG / 2 + dx, y_haut + dx)
        ctx.line_to(x + LARG / 2 + dx, y_haut + dx)
        n = 14
        for i in range(n + 1):
            xx = x + LARG / 2 - i * LARG / n + dx
            ctx.line_to(xx, y_haut + long + (18 if i % 2 else 0) + dx)
        ctx.close_path()
        if a < 1:
            flat(ctx, col, a)
        else:
            paint(ctx, col, 5, shade=0.97)
    ecrit(ctx, "GARAGE DU CENTRE", x, y_haut + 70, 40, INK, big=True)
    ecrit(ctx, "Facture n° 2611-047", x, y_haut + 120, 26, (110, 110, 120))
    yy = y_haut + 210
    for lib, prix in LIGNES:
        if yy + 30 > y_haut + long:
            break
        ecrit(ctx, lib, x - LARG / 2 + 40, yy, 38, INK, ax=0)
        ecrit(ctx, prix, x + LARG / 2 - 40, yy, 38, INK, ax=1)
        yy += PAS
    if yy + 120 < y_haut + long:
        ctx.move_to(x - LARG / 2 + 30, yy)
        ctx.line_to(x + LARG / 2 - 30, yy)
        ctx.set_dash([14, 10])
        stroke(ctx, 4, (140, 140, 150))
        ctx.set_dash([])
    ctx.restore()


def imprimante(ctx, x, y, t, actif):
    vib = 3 * math.sin(t * 60) if actif else 0
    rrect(ctx, x - 360 + vib, y - 160, 720, 190, 30)
    paint(ctx, (60, 66, 82), 7, shade=0.85)
    rrect(ctx, x - 300, y + 10, 600, 26, 10)
    flat(ctx, (20, 22, 28))
    ctx.arc(x + 260, y - 90, 16, 0, 2 * math.pi)
    flat(ctx, (90, 230, 120) if (actif and int(t * 8) % 2) else (60, 120, 70))


def construire(work):
    f = GT.construire(work)
    words = f.words if hasattr(f, "words") else None
    # instants depuis la voix du garage
    import re

    def W(li, prefixe, n=0):
        ws = [w for w in GT_words[0] if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t0"]
    t_cinq = W(0, "cinq")
    t_tot = t_cinq - 0.55            # le total tombe juste avant « cinq cent cinquante »
    t_dech = t_cinq + 0.15           # Kévin déchire sur le chiffre
    kev = Perso(**GT.KEVIN)
    kev.pose(0, "leve").emotion(0, "choc").pose(t_dech - 0.15, "objet").emotion(t_dech, "malin")
    kev.objet = lambda c, x, y, s: None

    def s_ticket(ctx, t, lt):
        # fond : l'atelier assombri
        G.atelier(ctx, t, pont=0.6)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (14, 16, 28), 0.55)
        y0 = 150
        long = min(930, 60 + 1150 * ease(min(1, lt / max(0.3, t_tot - 0.1))))
        imprimante(ctx, 540, y0 - 20, t, lt < t_tot)
        kev.draw(ctx, 540, 2020, 0.85, t, bouche=f.bouche(t, "nar") * 0.7)
        if t < t_dech:
            ticket(ctx, 540, y0, long, 0, t)
            if t >= t_tot:
                k = back((t - t_tot) / 0.25)
                ctx.save()
                ctx.translate(540, y0 + 700)
                ctx.rotate(-0.08)
                ctx.scale(k, k)
                rrect(ctx, -250, -70, 500, 140, 14)
                stroke(ctx, 10, (210, 40, 50))
                ecrit(ctx, "TOTAL 640 €", 0, 0, 78, (210, 40, 50), big=True)
                ctx.restore()
            traits_choc(ctx, 540, 2020 - 0.85 * 880, 150, lt)
        else:
            kd = ((t - t_dech) / 0.45) ** 1.3
            # derrière le ticket : la vraie somme
            k2 = back((t - t_dech - 0.1) / 0.35)
            ui.panneau(ctx, 540, 560, "89 €", t - t_dech - 0.1, rot=-0.04, size=200, fond=(70, 205, 115), bord=INK,
                       col=INK)
            if t >= t_dech + 0.35:
                ui.panneau(ctx, 560, 820, "551 € ÉCONOMISÉS", t - t_dech - 0.35, rot=0.04, size=72,
                           fond=(255, 210, 40), bord=INK, col=INK)
            for cote in (-1, 1) if kd < 2.5 else ():
                ticket(ctx, 540, y0, 930, 0, t, coupe=(cote, kd))
            _ = k2

    # remplace le premier plan (la phrase d'accroche) par le ticket, garde tout le reste
    p0 = f.plans[0]
    p0["scene"] = s_ticket
    p0["cam"] = [(0, 540, 760, 1.12), (0.8, 540, 840, 1.08), (max(1.2, t_tot - 0.1), 540, 1000, 1.0),
                 (t_dech + 0.6, 540, 940, 1.06)]
    for tt, son, g in [(0.05, "ticks", 0.6), (0.6, "ticks", 0.5), (t_tot, "tampon", 0.9), (t_dech, "impact", 0.8),
                       (t_dech + 0.35, "succes", 0.6)]:
        f.son(tt, son, g)
    f.secousse(t_tot, 10)
    return f


GT_words = [None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/accroche_ticket.mp4"))
    ap.add_argument("--duree", type=float, default=12.0)
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_garage"
    import voix
    _, words = voix.build(GT.lignes(), GT.VOIX, work, gap=0.2, cible=voix.CIBLE)
    GT_words[0] = words
    f = construire(work)
    f.dur = a.duree
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], ROOT / "output/trait/_work_ticket")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
