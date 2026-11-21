"""Trois ACCROCHES VISUELLES inventées (démo du 21 nov.) : Noël, argent, colis cassé. ~5 s chacune, voix de Yann.

    python3 motion/trait/accroches_demo.py            → output/trait/accroche_noel.mp4, accroche_argent.mp4,
                                                        accroche_colis.mp4 + accroches_demo.mp4 (les trois à la suite)
    python3 motion/trait/accroches_demo.py --stills
"""
import argparse
import math
import os
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import (INK, LW, ROOT, back, circle, ease, ecrit, ellipse, flat, halo, paint, poly, rrect,  # noqa: E402
                    stroke)
from film import Film  # noqa: E402
from liste_remboursements import KEVIN  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

YANN = (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN)
TXT = {
    "noel": "Ma belle-sœur m'a envoyé une facture de [cent quatre-vingts euros]… pour le repas de Noël chez ma "
            "{propre mère}.",
    "argent": "Ma banque m'a pris [cent vingt euros] de frais en un mois. Elle avait le droit d'en prendre "
              "{quatre-vingts}.",
    "colis": "Mon colis est arrivé {en miettes}. Le livreur m'a dit, signe là, c'est pas ton problème.",
}


# ───────────────────────── dessins ─────────────────────────
def neige(ctx, t, n=70):
    rnd = random.Random(3)
    for i in range(n):
        x0, v, r = rnd.uniform(-100, 1180), rnd.uniform(60, 140), rnd.uniform(4, 10)
        y = (rnd.uniform(0, 2200) + t * v) % 2200 - 150
        circle(ctx, x0 + 30 * math.sin(t + i), y, r)
        flat(ctx, (255, 255, 255), 0.85)


def sapin(ctx, x, y, s, t):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -40, -80, 80, 80, 6)
    paint(ctx, (120, 80, 50), LW, shade=0.85)
    for k, (w, h) in enumerate(((300, 260), (240, 230), (170, 200))):
        yy = -80 - k * 170
        poly(ctx, [(-w, yy), (0, yy - h - 60), (w, yy)])
        paint(ctx, (40, 140, 80), LW, shade=0.85)
    for i in range(9):
        a = i * 2.4
        bx, by = math.sin(a) * (60 + i * 18), -150 - i * 55
        circle(ctx, bx, by, 18)
        lum = 0.5 + 0.5 * math.sin(t * 5 + i)
        flat(ctx, [(230, 60, 60), (255, 210, 40), (80, 150, 240)][i % 3])
        halo(ctx, bx, by, 50, (255, 230, 150), 0.25 * lum)
    poly(ctx, [(0, -720), (14, -690), (46, -690), (20, -670), (30, -640), (0, -658), (-30, -640), (-20, -670),
               (-46, -690), (-14, -690)])
    paint(ctx, (255, 210, 40), 4, shade=1)
    ctx.restore()


def cadeau(ctx, x, y, s, k_ouvre, t):
    """Paquet cadeau (x = milieu, y = bas). k_ouvre 0 → 1 : le couvercle s'envole."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    trem = 0 if k_ouvre > 0 else 6 * math.sin(t * 40)
    ctx.rotate(trem * 0.004)
    rrect(ctx, -200, -300, 400, 300, 12)
    paint(ctx, (200, 40, 60), LW, shade=0.85)
    ctx.rectangle(-30, -300, 60, 300)
    flat(ctx, (255, 210, 40))
    ctx.save()
    ctx.translate(0, -300 - 500 * k_ouvre)
    ctx.rotate(-1.2 * k_ouvre)
    rrect(ctx, -220, -70, 440, 80, 12)
    paint(ctx, (220, 50, 70), LW, shade=0.85)
    ctx.rectangle(-30, -70, 60, 80)
    flat(ctx, (255, 210, 40))
    for sgn in (-1, 1):
        ellipse(ctx, sgn * 60, -100, 60, 36)
        paint(ctx, (255, 210, 40), 5, shade=0.9)
    ctx.restore()
    ctx.restore()


def facture_ressort(ctx, x, y, k, t, titre, montant):
    """Facture au bout d'un ressort qui jaillit de la boîte (k 0 → 1, avec rebond)."""
    h = 620 * k
    ctx.save()
    n = 9
    ctx.move_to(x, y)
    for i in range(n + 1):
        ctx.line_to(x + (40 if i % 2 else -40), y - h * i / n)
    stroke(ctx, 10, (150, 150, 160))
    ctx.translate(x, y - h)
    ctx.rotate(0.15 * math.sin(t * 9) * (1 - min(1, k)) + 0.05 * math.sin(t * 3))
    sc = max(0.001, k)
    ctx.scale(sc, sc)
    rrect(ctx, -270, -330, 540, 360, 14)
    paint(ctx, (252, 252, 246), LW, shade=0.95)
    ecrit(ctx, "FACTURE", 0, -270, 54, (200, 40, 60), big=True)
    ecrit(ctx, titre, 0, -190, 34, INK)
    ecrit(ctx, montant, 0, -70, 110, (200, 40, 60), big=True)
    ctx.restore()


def tirelire(ctx, x, y, s, t, fuite=0.0):
    """Cochon tirelire de profil (x = milieu, y = sol). fuite > 0 : trou sous le ventre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for dx in (-130, -60, 70, 140):
        rrect(ctx, dx - 24, -90, 48, 90, 14)
        paint(ctx, (240, 150, 170), LW, shade=0.85)
    ellipse(ctx, 0, -230, 260, 180)
    paint(ctx, (250, 170, 190), LW, shade=0.85)
    ellipse(ctx, 250, -230, 60, 70)
    paint(ctx, (240, 150, 170), LW, shade=0.85)
    for dy in (-20, 20):
        ellipse(ctx, 262, -230 + dy, 9, 14)
        flat(ctx, INK)
    circle(ctx, 140, -290, 14)
    flat(ctx, INK)
    poly(ctx, [(60, -390), (100, -470), (140, -380)])
    paint(ctx, (240, 150, 170), LW, shade=0.85)
    rrect(ctx, -60, -410, 120, 18, 8)
    flat(ctx, INK)
    if fuite > 0:
        ellipse(ctx, -20, -56, 34 * min(1, fuite), 12 * min(1, fuite))
        flat(ctx, INK)
    ctx.restore()


def piece(ctx, x, y, r, t, i=0):
    ellipse(ctx, x, y, r, r * abs(math.cos(t * 6 + i)) + 3)
    paint(ctx, (240, 190, 50), 4, shade=0.85)


def seau_banque(ctx, x, y, s, n):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-150, -220), (150, -220), (120, 0), (-120, 0)])
    paint(ctx, (60, 90, 160), LW, shade=0.85)
    ecrit(ctx, "FRAIS", 0, -140, 46, (255, 255, 255), big=True)
    ecrit(ctx, "BANCAIRES", 0, -90, 30, (255, 255, 255), big=True)
    for i in range(min(n, 12)):
        ellipse(ctx, -90 + (i % 5) * 45, -230 - (i // 5) * 16, 30, 10)
        paint(ctx, (240, 190, 50), 3, shade=0.85)
    ctx.restore()


def carton_vole(ctx, x, y, s, rot, k_casse, t):
    """Carton FRAGILE ; k_casse > 0 : il s'ouvre en morceaux."""
    if k_casse <= 0:
        C.carton(ctx, x, y, s, rot=rot, label="FRAGILE")
        return
    rnd = random.Random(7)
    for i in range(14):
        a = rnd.uniform(-math.pi, 0)
        v = rnd.uniform(300, 900)
        px = x + math.cos(a) * v * k_casse
        py = y + math.sin(a) * v * k_casse + 600 * k_casse * k_casse
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(rnd.uniform(-3, 3) * k_casse)
        w, h = rnd.uniform(40, 110), rnd.uniform(30, 90)
        poly(ctx, [(-w / 2, -h / 2), (w / 2, -h / 3), (w / 3, h / 2), (-w / 2, h / 3)])
        paint(ctx, (30, 30, 40) if i % 3 == 0 else (190, 140, 90), 4, shade=0.9)
        if i % 3 == 0:
            ctx.move_to(-w / 3, -h / 4)
            ctx.line_to(w / 4, h / 4)
            stroke(ctx, 3, (150, 200, 240))
        ctx.restore()


# ───────────────────────── films ─────────────────────────
def film(cle, work):
    voice, words = voix.build([("nar", TXT[cle])], {"nar": YANN}, work, gap=0.2, speed=1.2)
    f = Film(voice, words)

    def W(prefixe, n=0):
        import re
        ws = [w for w in words if re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t0"]

    kev = Perso(**KEVIN)
    kev.objet = lambda c, x, y, s: None
    bouche = lambda t: f.bouche(t, "nar") * 0.7          # noqa: E731

    if cle == "noel":
        t_ouvre = W("facture") - 0.15
        kev.pose(0, "objet").emotion(0, "content").pose(t_ouvre + 0.1, "leve").emotion(t_ouvre + 0.1, "choc")
        kev.emotion(W("propre"), "colere").pose(W("propre"), "mains_hanches")

        def sc(ctx, t, lt):
            D.salon(ctx, t)
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (20, 20, 60), 0.35)
            sapin(ctx, 880, 1560, 1.0, t)
            kev.draw(ctx, 260, 1900, 0.88, t, bouche=bouche(t))
            k = ease((t - t_ouvre) / 0.25) if t >= t_ouvre else 0.0
            cadeau(ctx, 600, 1620, 0.8, k, t)
            if t >= t_ouvre + 0.05:
                kk = min(1.0, (t - t_ouvre - 0.05) / 0.3)
                kk = kk + 0.12 * math.sin((t - t_ouvre) * 18) * math.exp(-(t - t_ouvre) * 4)
                facture_ressort(ctx, 600, 1400, kk, t, "Repas de Noël", "180 €")
            if t >= W("propre"):
                ui.panneau(ctx, 540, 380, "CHEZ MA PROPRE MÈRE", t - W("propre"), rot=-0.04, size=64)
            neige(ctx, t)

        cam = [(0, 560, 1250, 1.25), (t_ouvre, 600, 1150, 1.15), (t_ouvre + 0.3, 600, 980, 1.0),
               (f.dur, 560, 960, 1.06)]
        sons = [(t_ouvre, "impact", 0.8), (t_ouvre + 0.15, "pop", 0.7), (W("propre"), "tampon", 0.6)]
        sec = t_ouvre + 0.1
    elif cle == "argent":
        t_fuite = W("frais") - 0.1
        t_droit = W("quatre")
        kev.pose(0, "objet").emotion(0, "content").emotion(t_fuite + 0.3, "choc").pose(t_fuite + 0.3, "leve")
        kev.pose(t_droit, "pointe").emotion(t_droit, "malin")

        def sc(ctx, t, lt):
            C.chambre(ctx, t)
            kev.draw(ctx, 230, 1900, 0.88, t, bouche=bouche(t))
            fuite = ease((t - t_fuite) / 0.3) if t >= t_fuite else 0.0
            tirelire(ctx, 660, 1500, 0.95, t, fuite)
            # pièces qui entrent par la fente
            for i in range(8):
                k = ((t * 1.4) + i / 8) % 1
                if k < 0.5:
                    piece(ctx, 650 + 10 * math.sin(i), 700 + k * 2 * 420, 34, t, i)
            n_tombees = 0
            if fuite > 0:
                for i in range(10):
                    k = ((t - t_fuite) * 1.3 + i / 10)
                    if k < 0:
                        continue
                    kk = k % 1
                    piece(ctx, 640 + 6 * math.sin(i * 3), 1460 + kk * 240, 30, t, i)
                n_tombees = int((t - t_fuite) * 9)
            seau_banque(ctx, 640, 1940, 0.9, n_tombees)
            if t >= W("cent") - 0.1:
                ui.panneau(ctx, 560, 420, "−120 € EN 1 MOIS", t - W("cent") + 0.1, rot=-0.04, size=80)
            if t >= t_droit:
                ui.panneau(ctx, 580, 600, "DROIT : 80 € MAX", t - t_droit, rot=0.04, size=72, fond=(70, 205, 115),
                           bord=INK, col=INK)

        cam = [(0, 600, 1200, 1.2), (t_fuite, 640, 1400, 1.3), (t_fuite + 0.6, 560, 1100, 1.05),
               (f.dur, 540, 1000, 1.0)]
        sons = [(0.1, "ticks", 0.5), (t_fuite, "rate", 0.7), (W("cent"), "impact", 0.6), (t_droit, "succes", 0.6)]
        sec = t_fuite + 0.05
    else:
        t_crash = W("miettes") - 0.25
        t_gel = t_crash + 0.5
        t_liv = W("livreur")
        livreur = Perso(cheveux="court", couleur_cheveux=(40, 30, 30), peau=(220, 170, 130), haut="polo",
                        couleur_haut=(240, 170, 30), bas=(50, 50, 60), seed=90)
        livreur.objet = lambda c, x, y, s: None
        livreur.pose(0, "repos").emotion(0, "neutre").pose(t_liv, "pointe_g").emotion(t_liv, "malin")
        kev.pose(0, "objet").emotion(0, "content").pose(t_crash, "leve").emotion(t_crash, "choc")
        kev.pose(t_liv + 0.4, "repos").emotion(t_liv + 0.4, "colere")

        def sc(ctx, t, lt):
            C.palier(ctx, t, mot=False, colis=0)
            livreur.draw(ctx, 860, 1800, 0.85, t)
            kev.draw(ctx, 280, 1880, 0.88, t, bouche=bouche(t))
            # ralenti entre le crash et le gel, puis image figée sur les morceaux
            if t < t_crash:
                y = -250 + 1750 * (min(1, t / max(0.3, t_crash)) ** 2)
                carton_vole(ctx, 560, y, 0.9, 0.4 * t, 0, t)
            else:
                tt = min(t, t_gel)
                k = (tt - t_crash) / 0.5 * 0.55          # ralenti : le temps avance 2 fois moins vite
                carton_vole(ctx, 560, 1500, 0.9, 0, max(0.02, k), t)
                if t >= t_gel:
                    ctx.rectangle(-600, -600, 2400, 3200)
                    flat(ctx, (255, 255, 255), max(0, 0.6 - (t - t_gel) * 3))
                    ui.panneau(ctx, 540, 560, "−450 €", t - t_gel, rot=-0.05, size=150)
            if t >= t_liv + 0.2:
                ui.bulle(ctx, 700, 820, "Signe là, c'est pas ton problème !", t - t_liv - 0.2, size=44, cote=-1)

        cam = [(0, 560, 900, 1.15), (t_crash, 560, 1300, 1.35), (t_gel, 560, 1250, 1.25),
               (t_liv, 640, 1100, 1.05), (f.dur, 600, 1000, 1.0)]
        sons = [(t_crash, "impact", 0.9), (t_crash + 0.05, "rate", 0.6), (t_gel, "tampon", 0.7),
                (t_liv + 0.2, "pop", 0.5)]
        sec = t_crash + 0.02

    f.plan(0, sc, cam, fouet=False)
    if cle == "colis":
        def rec(ctx, t):
            if t < t_gel:
                return
            rrect(ctx, 30, 120, 1020, 1680, 40)
            stroke(ctx, 10, (210, 40, 50), alpha=0.8)
            ecrit(ctx, "● REC  PALIER 3e", 80, 180, 38, (210, 40, 50), big=True, ax=0,
                  alpha=1.0 if int(t * 3) % 2 else 0.35)
        f.ecran(rec)
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in sons:
        f.son(tt, son, g)
    f.secousse(sec, 14)
    f.dur += 0.6
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args()
    outs = []
    for cle in ("noel", "argent", "colis"):
        work = ROOT / f"output/trait/_work_accroche_{cle}"
        f = film(cle, work)
        print(cle, f"{f.dur:.1f} s")
        if a.stills:
            f.stills([0.05, f.dur * 0.25, f.dur * 0.45, f.dur * 0.65, f.dur * 0.9], work / "stills")
        else:
            out = ROOT / f"output/trait/accroche_{cle}.mp4"
            f.render(str(out))
            outs.append(out)
    if outs:
        lst = ROOT / "output/trait/_accroches.txt"
        lst.write_text("".join(f"file '{o}'\n" for o in outs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(ROOT / "output/trait/accroches_demo.mp4")], check=True)
        print("→", ROOT / "output/trait/accroches_demo.mp4")


if __name__ == "__main__":
    main()
