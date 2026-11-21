"""Hausse de loyer (script 40, scripts/modele/40_hausse_loyer.dial, vidéo témoin du test T1) en dessin animé, moteur
« trait ». Kévin = Yann, le proprio = Paul K. Voix v4 accélérée à 64 s.

    python3 motion/trait/hausse_loyer.py                 → output/trait/hausse_loyer.mp4
    python3 motion/trait/hausse_loyer.py --stills 1,10
"""
import argparse
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/40_hausse_loyer.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "proprio": (os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT"), voix.REGLAGES_YANN)}

MARQUES = {0: [("six cent quatre-vingts euros", "[{}]")], 2: [("six cents euros", "[{}]")],
           5: [("ta chambre de bonne", "{{{}}}")], 9: [("Ta chambre de bonne", "{{{}}}")],
           11: [("une seule hausse par an", "[{}]"), ("l'indice des loyers", "[{}]")],
           12: [("neuf euros", "[{}]")], 14: [("huit voisins", "[{}]")], 16: [("six cent neuf euros", "[{}]")],
           17: [("Tout l'immeuble", "[{}]")], 19: [("Six cent quatre-vingts euros", "{{{}}}")]}


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("M:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append(("proprio" if ligne[0] == "M" else "nar", txt))
    return out


KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
PROPRIO = dict(cheveux="plaque", couleur_cheveux=(80, 70, 60), peau=(236, 190, 156), haut="chemise",
               couleur_haut=(200, 210, 226), bas=(50, 50, 64), chaussures=(30, 30, 36), lunettes=True, seed=40)
VOISINE = dict(cheveux="chignon", couleur_cheveux=(210, 210, 214), peau=(240, 200, 170), haut="uni",
               couleur_haut=(150, 110, 170), bas=(90, 80, 110), seed=41)
VOISINS = [dict(cheveux=h, couleur_cheveux=cc, peau=p, haut="uni", couleur_haut=c, bas=(70, 70, 84), seed=50 + i)
           for i, (h, cc, p, c) in enumerate([("court", (60, 40, 30), (230, 180, 140), (200, 120, 60)),
                                               ("chignon", (40, 30, 30), (200, 150, 110), (80, 150, 200)),
                                               ("chauve", (150, 150, 150), (236, 190, 156), (120, 160, 90)),
                                               ("boucles", (90, 60, 40), (180, 120, 90), (220, 180, 60)),
                                               ("court", (200, 160, 90), (240, 200, 170), (170, 80, 110))])]


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.2, cible=voix.CIBLE)
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    def W(li, prefixe, n=0, fin=False):
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t1" if fin else "t0"]

    kev, prop, voisine = Perso(**KEVIN), Perso(**PROPRIO), Perso(**VOISINE)
    voisins = [Perso(**v) for v in VOISINS]
    kev.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)
    prop.objet = lambda ctx, x, y, s: D.telephone(ctx, x + 35, y - 95, 0.7, rot=0.35)
    voisine.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)

    prop.pose(0, "oreille").emotion(0, "malin").emotion(L(7, 0), "colere")
    prop.pose(L(14, 0), "mains_hanches").emotion(L(14, 0), "colere")
    prop.pose(L(15, 0), "repos").emotion(L(15, 0), "triste")
    kev.pose(0, "telephone").emotion(0, "choc").emotion(L(2, 0), "content").pose(L(2, 0), "repos")
    kev.pose(L(4, 0), "telephone").emotion(L(4, 0), "neutre").emotion(L(8, 0), "triste").pose(L(8, 0), "repos")
    kev.emotion(L(13, 0), "triste").pose(L(14, 0), "objet").emotion(L(14, 0), "malin")
    kev.pose(L(16, 0), "telephone").emotion(L(16, 0), "content").pose(L(19, 0), "leve")
    kev.objet = lambda ctx, x, y, s: (D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1) if not (L(14, 0) <= f_t[0] < L(16, 0))
                                      else feuille(ctx, x, y - 90))
    voisine.pose(0, "telephone").emotion(0, "choc")
    for v in voisins:
        v.emotion(0, "neutre").emotion(L(15, 0), "content")
    f_t = [0.0]

    def feuille(ctx, x, y):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.06)
        rrect(ctx, -110, -140, 220, 280, 6)
        from dessin import paint
        paint(ctx, (252, 252, 248), 5, shade=0.95)
        ecrit(ctx, "600 × 1,57 %", 0, -70, 30, INK, big=True)
        ecrit(ctx, "= 9 €", 0, 0, 56, (40, 150, 80), big=True)
        ctx.restore()

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    def fond_flou(ctx, t, decor):
        decor(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)

    # ── scènes ──
    def s_proprio(ctx, t, lt):
        f_t[0] = t
        P = __import__("decors_piscine")
        P.bureau(ctx, t)
        prop.draw(ctx, 520, 1800, 0.95, t, bouche=bouche(t, "proprio"))
        ui.badge(ctx, 520, 1800 - 0.95 * 1150, "LE PROPRIO", lt - 0.2)
        if L(0, 0) <= t < L(1, 0) and t >= W(0, "six") - 0.1:
            ui.panneau(ctx, 640, 470, "680 €", t - W(0, "six") + 0.1, rot=0.05, size=120, fond=(255, 210, 40),
                       bord=INK, col=INK)
        if L(5, 0) <= t < L(6, 0) and t >= W(5, "ta") - 0.05:
            ui.panneau(ctx, 520, 560, "« CHAMBRE DE BONNE »", t - W(5, "ta") + 0.05, rot=-0.04, size=56)
        if t >= L(7, 0) and t < L(8, 0):
            traits_choc(ctx, 520, 1800 - 0.95 * 880, 160, t - L(7, 0))
        if L(15, 0) <= t:
            pass

    def ecran_msg(c, x0, y0, w, h, t):
        if t >= L(16, 0):
            ecrit(c, "sam. 19:12", x0 + w / 2, y0 + 34, 24, (120, 120, 130))
            C.bulle_msg(c, x0, y0 + 80, w, "Ok pour 609 €.", False, ease((t - W(16, "ok") + 0.2) / 0.3), size=60,
                        couleur=(220, 250, 220))
            return
        y = y0 + 20
        ecrit(c, "dim. 22:04", x0 + w / 2, y + 14, 24, (120, 120, 130))
        y += 40
        y += C.bulle_msg(c, x0, y, w, "Ton loyer passe à 680 € en janvier, sinon tu cherches ailleurs.", False,
                         ease((t - L(1, 0) + 0.3) / 0.3), size=36)
        if t >= W(4, "quatre") - 0.2:
            y += C.bulle_msg(c, x0, y, w, "80 € d'un coup, c'est beaucoup", True, ease((t - W(4, "quatre") + 0.2) / 0.3))
        if t >= W(4, "il") - 0.1:
            y += C.vocal(c, x0, y, w, t - W(4, "il"), ease((t - W(4, "il") + 0.1) / 0.3))
        if t >= L(6, 0):
            ecrit(c, "+ 1 min", x0 + 30, y + 10, 24, (120, 120, 130), ax=0)
            y += C.vocal(c, x0, y + 24, w, t - L(6, 0), ease((t - L(6, 0)) / 0.3))

    def s_tel(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Proprio", couleur=(60, 70, 120), contenu=lambda c, *a: ecran_msg(c, *a, t),
                    t=t)

    def s_appart(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        # velux et coup de peinture qui avance
        rrect(ctx, 100, 120, 300, 200, 10)
        from dessin import paint
        paint(ctx, (150, 200, 240), 6, shade=0.9)
        if t >= L(3, 0):
            k = ease((t - L(3, 0)) / 2.0)
            ctx.rectangle(-200, 760, 700 * k, 380)
            flat(ctx, (120, 190, 170), 0.85)
        kev.draw(ctx, 600, 1800, 0.95, t, bouche=bouche(t, "nar"))
        if L(2, 0) <= t < L(3, 0) and t >= W(2, "trente"):
            ui.panneau(ctx, 560, 560, "30 m² · 600 €", t - W(2, "trente"), rot=-0.04, size=70, fond=(255, 210, 40),
                       bord=INK, col=INK)
        if L(3, 0) <= t < L(4, 0) and t >= W(3, "il"):
            ui.panneau(ctx, 560, 560, "« LOCATAIRE EN OR »", t - W(3, "il"), rot=0.04, size=58, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def s_kev(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"))
        if t >= L(13, 0):
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (30, 20, 70), 0.3)

    def s_echo(ctx, t, lt):
        C.chambre(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 30), 0.45)
        ui.panneau(ctx, 540, 900, "CHAMBRE DE BONNE", lt, rot=-0.05, size=90)

    t_carte = L(10, 0)

    def s_regle(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))

    def h_regle(ctx, t, lt):
        ui.carte_regle(ctx, t - t_carte, "LA RÈGLE", [
            (0.15, "En cours de bail :\npas de hausse libre", "pas de hausse libre"),
            (W(11, "une") - t_carte, "Une seule hausse par an", "Une seule hausse"),
            (W(11, "si") - t_carte, "Si le bail le prévoit", "le bail le prévoit"),
            (W(11, "jamais") - t_carte, "Plafond : l'indice\ndes loyers (IRL)", "l'indice"),
        ], y0=300)
        ecrit(ctx, "Loi du 6 juillet 1989, art. 17-1 · IRL 3e trim. 2026 : + 1,57 %", 540, 1150, 26, (230, 230, 236))

    def s_calcul(ctx, t, lt):
        D.fond_sombre(ctx, t, (24, 34, 50))
        k = back(lt / 0.3)
        ctx.save()
        ctx.translate(540, 900)
        ctx.scale(k, k)
        rrect(ctx, -420, -330, 840, 660, 30)
        from dessin import paint
        paint(ctx, (250, 248, 240), 6, shade=0.95)
        ecrit(ctx, "600 €", 0, -220, 90, INK, big=True)
        if t >= W(12, "plus"):
            ecrit(ctx, "+ 1,57 % sur un an", 0, -100, 56, (40, 110, 200), big=True)
        if t >= W(12, "neuf"):
            ecrit(ctx, "= + 9 €", 0, 30, 120, (40, 150, 80), big=True, scale=back((t - W(12, "neuf")) / 0.3))
        if t >= W(12, "pas"):
            ecrit(ctx, "+ 80 €", 0, 200, 90, (210, 40, 50), big=True)
            ctx.move_to(-170, 200)
            ctx.line_to(170 * ease((t - W(12, "pas")) / 0.3) * 2 - 170, 200)
            stroke(ctx, 12, (210, 40, 50))
        ctx.restore()

    def s_hall(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        for i, v in enumerate(voisins):
            v.draw(ctx, 120 + i * 200, 1520, 0.55, t)
        prop.draw(ctx, 860, 1800, 0.85, t, bouche=0.0)
        kev.draw(ctx, 300, 1820, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(14, "huit"):
            ui.panneau(ctx, 540, 600, "8 VOISINS", t - W(14, "huit"), rot=-0.04, size=80, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def s_silence(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        prop.draw(ctx, 540, 1800, 0.95, t)

    def s_voisine(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        voisine.draw(ctx, 560, 1780, 0.9, t)
        if t >= W(17, "même"):
            ui.panneau(ctx, 560, 560, "MÊME MESSAGE", t - W(17, "même"), rot=0.04, size=70)

    def s_immeuble(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=False, colis=0)
        for i in range(min(9, 1 + int(lt * 4))):
            ctx.save()
            ctx.translate(380 + (i % 3) * 140, 640 + (i // 3) * 160)
            ctx.rotate(math.sin(i * 1.7) * 0.15)
            rrect(ctx, -60, -60, 120, 120, 4)
            flat(ctx, (255, 240, 140))
            ecrit(ctx, "9 € ?", 0, 0, 34, INK, big=True)
            ctx.restore()
        kev.draw(ctx, 800, 1800, 0.85, t, bouche=bouche(t, "nar"))

    def s_final(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"))
        ui.panneau(ctx, 540, 520, "680 €", lt, rot=-0.04, size=120, fond=(250, 250, 250), bord=(210, 40, 50),
                   col=INK)
        if lt > 0.6:
            ctx.move_to(380, 520)
            ctx.line_to(380 + 320 * ease((lt - 0.6) / 0.3), 520)
            stroke(ctx, 14, (210, 40, 50))
            ui.panneau(ctx, 560, 700, "609 €", lt - 0.8, rot=0.04, size=120, fond=(70, 205, 115), bord=INK, col=INK)

    # ── plans ──
    f.plan(0, s_proprio, [(0, *tete(520, 1800, 0.95), 1.45), (2.0, *tete(520, 1800, 0.95), 1.6)], fouet=False)
    f.plan(L(1, 0), s_tel, [(0, 540, 760, 1.0), (1.5, 560, 880, 1.35), (3.0, 520, 860, 1.2)])
    f.plan(L(2, 0), s_appart, [(0, 540, 1100, 1.0), (2.5, 560, 1080, 1.15)])
    f.plan(L(3, 0), s_appart, [(0, 300, 900, 1.3), (2.5, 540, 1080, 1.05)])
    f.plan(L(4, 0), s_tel, [(0, 540, 760, 1.0), (2.0, 560, 900, 1.35), (4.0, 520, 960, 1.2)])
    f.plan(L(5, 0), s_proprio, [(0, *tete(520, 1800, 0.95), 1.7), (2.0, *tete(520, 1810, 0.95), 1.85)])
    f.plan(L(6, 0), s_tel, [(0, 540, 940, 1.3), (1.5, 540, 960, 1.4)])
    f.plan(L(7, 0), s_proprio, [(0, *tete(520, 1790, 0.95), 1.95), (2.0, *tete(520, 1800, 0.95), 2.1)])
    f.plan(L(8, 0), s_kev, [(0, *tete(540, 1800, 0.95), 1.9), (1.2, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(9, 0), s_echo, [(0, 540, 960, 1.0), (1.2, 540, 960, 1.1)])
    f.plan(L(10, 0), s_regle, [(0, 540, 960, 1.0), (3, 620, 1010, 1.3), (6, 480, 930, 1.12), (9, 560, 980, 1.25)],
           hud=h_regle)
    f.plan(L(12, 0), s_calcul, [(0, 540, 760, 1.35), (2.5, 540, 900, 1.0), (4.5, 540, 1000, 1.3), (7.0, 540, 1080, 1.4)])
    f.plan(L(13, 0), s_kev, [(0, 540, 1150, 1.0), (2.0, *tete(540, 1800, 0.95), 1.7), (4.0, *tete(560, 1800, 0.95), 1.9)])
    f.plan(L(14, 0), s_hall, [(0, 300, 1100, 1.4), (2.0, 560, 1250, 1.0), (4.0, 800, 1150, 1.3)])
    f.plan(L(15, 0), s_silence, [(0, *tete(540, 1800, 0.95), 1.9), (1.5, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(16, 0), s_tel, [(0, 540, 760, 1.25), (2.0, 540, 800, 1.4)])
    f.plan(L(17, 0), s_voisine, [(0, 560, 1100, 1.1), (2.5, 560, 1060, 1.25)])
    f.plan(L(18, 0), s_immeuble, [(0, 560, 1100, 1.0), (2.0, 560, 1060, 1.15)])
    f.plan(L(19, 0), s_final, [(0, *tete(540, 1800, 0.95), 1.4), (2.0, *tete(540, 1800, 0.95), 1.55)])

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "ÉVITÉ PAR KÉVIN, PAR AN", [(0, 0), (W(16, "ok") + 0.3, 852)],
                                       apparition=L(1, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(W(0, "six"), "pop", 0.7), (L(1, 0), "notif", 0.7), (W(2, "trente"), "pop", 0.5),
                       (W(4, "quatre"), "pop", 0.5), (W(4, "il"), "notif", 0.5), (W(5, "ta"), "impact", 0.7),
                       (L(6, 0), "notif", 0.5), (L(7, 0), "impact", 0.8), (L(9, 0), "ticks", 0.4),
                       (W(11, "une"), "pop", 0.5), (W(11, "si"), "pop", 0.5), (W(11, "jamais"), "pop", 0.5),
                       (W(12, "neuf"), "succes", 0.5), (W(12, "pas"), "rate", 0.6), (W(14, "huit"), "pop", 0.6),
                       (L(16, 0), "notif", 0.8), (W(16, "ok"), "succes", 0.8), (W(17, "même"), "impact", 0.6),
                       (L(19, 0), "tampon", 0.6)]:
        f.son(tt, son, g)
    f.secousse(L(7, 0), 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/hausse_loyer.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_loyer"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
