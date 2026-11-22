"""Erreur de caisse retenue sur la paie (script 42, scripts/modele/42_erreur_caisse.dial), moteur « trait ».
Kévin = Yann, la tante (patronne) = Victoire. Voix v4 accélérée à 64 s. Caméra « plans » (gros plans sur les mots).
TEST accroche « repost » (titre écrit en haut + Kévin dès l'image 0) ; TEST partage : carte récap à garder.

    python3 motion/trait/erreur_caisse.py                 → output/trait/erreur_caisse.mp4
    python3 motion/trait/erreur_caisse.py --stills 1,10
"""
import argparse
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_caisse as K  # noqa: E402
import decors_colis as C  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from accroches_demo import neige, sapin  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, paint, rrect, stroke, texte  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/42_erreur_caisse.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "tante": ("O31r762Gb3WFygrEOGh0", voix.REGLAGES_YANN)}          # Victoire (fr, parisienne)
TITRE = "MA TANTE M'A FAIT PAYER L'ERREUR\nDE SA PROPRE FILLE…"

MARQUES = {0: [("sa propre fille", "{{{}}}")], 3: [("la famille passe avant tout", "[{}]")],
           4: [("erreur de caisse", "{{{}}}")], 5: [("soixante euros", "[{}]"), ("C'est la règle", "{{{}}}")],
           7: [("le canapé de ta mère", "{{{}}}")], 9: [("C'est la règle", "{{{}}}")],
           11: [("le Code du travail les interdit", "[{}]")], 12: [("trois ans en arrière", "[{}]")],
           14: [("Caisse quatre", "{{{}}}")], 15: [("ma cousine", "{{{}}}")], 17: [("soixante euros en plus", "[{}]")],
           19: [("la règle", "[{}]")]}

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="polo",
             couleur_haut=(220, 60, 60), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
TANTE = dict(cheveux="chignon", couleur_cheveux=(90, 60, 40), peau=(205, 145, 105), haut="chemise",
             couleur_haut=(240, 240, 248), bas=(40, 40, 60), lunettes=True, seed=95)
JADE = dict(cheveux="boucles", couleur_cheveux=(60, 40, 30), peau=(215, 160, 120), haut="polo",
            couleur_haut=(220, 60, 60), bas=(50, 50, 70), seed=96)
FAMILLE = [dict(cheveux=h, couleur_cheveux=cc, peau=p, haut="uni", couleur_haut=c, bas=(70, 70, 84), seed=97 + i)
           for i, (h, cc, p, c) in enumerate([("plaque", (120, 110, 100), (198, 138, 98), (90, 120, 170)),
                                               ("chignon", (60, 46, 40), (205, 145, 105), (190, 90, 110)),
                                               ("court", (40, 30, 30), (198, 138, 98), (80, 150, 110))])]


def bureau(ctx, t):
    """Bureau de la tante, animé : store qui laisse passer des bandes de lumière mobiles, poussière."""
    import random
    from dessin import circle, poly
    __import__("decors_piscine").bureau(ctx, t)
    for k in range(3):
        x = 200 + k * 330 + 260 * math.sin(t * 0.7 + k)
        poly(ctx, [(x - 50, -200), (x + 50, -200), (x + 380, 2200), (x - 380, 2200)])
        flat(ctx, (255, 245, 210), 0.10 + 0.04 * math.sin(t * 3 + k))
    rnd = random.Random(5)
    for i in range(40):
        x0, y0, v = rnd.uniform(0, 1080), rnd.uniform(0, 1900), rnd.uniform(20, 60)
        circle(ctx, x0 + 40 * math.sin(t * 0.8 + i), (y0 - t * v) % 1900, rnd.uniform(3, 7))
        flat(ctx, (255, 255, 240), 0.5)


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("M:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append(("tante" if ligne[0] == "M" else "nar", txt))
    return out


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

    def plan(li, scene, *plans, hud=None):
        """plans = [(instant absolu ou None pour le début, x, y, zoom)] : caméra « plans » calée sur les mots."""
        t0 = L(li, 0)
        cam = [(0 if ta is None else max(0.0, ta - t0 - 0.04), x, y, z) for ta, x, y, z in plans]
        f.plan(L(li, 0) if li else 0, scene, cam, fouet=bool(li), hud=hud)

    kev, tante, jade = Perso(**KEVIN), Perso(**TANTE), Perso(**JADE)
    famille = [Perso(**p) for p in FAMILLE]
    f_t = [0.0]

    def objet_kev(ctx, x, y, s):
        t = f_t[0]
        if L(1, 0) <= t < L(2, 0) or L(14, 0) <= t < L(15, 0):
            K.ticket_cloture(ctx, x, y - 110, 0.32, rot=-0.08)
        elif L(4, 0) <= t < L(5, 0):
            K.fiche_paie(ctx, x, y - 100, 0.3, rouge=1.0, rot=-0.06)
        else:
            D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)

    kev.objet = objet_kev
    tante.objet = lambda c, x, y, s: K.fiche_paie(c, x, y - 100, 0.26, rot=0.06)
    jade.objet = lambda c, x, y, s: None

    kev.pose(0, "leve").emotion(0, "choc").pose(L(1, 0), "objet").emotion(L(1, 0), "malin")
    kev.pose(L(2, 0), "repos").emotion(L(2, 0), "content").emotion(L(3, 0), "content")
    kev.pose(L(4, 0), "objet").emotion(L(4, 0), "choc").pose(L(6, 0), "pointe").emotion(L(6, 0), "neutre")
    kev.pose(L(8, 0), "repos").emotion(L(8, 0), "triste").pose(L(13, 0), "haussement")
    kev.pose(L(14, 0), "objet").emotion(L(14, 0), "malin").pose(L(16, 0), "telephone").emotion(L(16, 0), "neutre")
    kev.pose(L(17, 0), "leve").emotion(L(17, 0), "content").pose(L(18, 0), "repos").emotion(L(19, 0), "malin")
    tante.pose(0, "repos").emotion(0, "content").pose(L(5, 0), "objet").emotion(L(5, 0), "malin")
    tante.pose(L(7, 0), "pointe_g").emotion(L(7, 0), "colere").pose(L(16, 0), "repos").emotion(L(16, 0), "triste")
    jade.pose(0, "repos").emotion(0, "content").emotion(L(17, 0), "triste")
    for p in famille:
        p.pose(0, "repos").emotion(0, "content")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    # ── titre écrit en haut (TEST accroche) : 3,5 premières secondes ──
    def titre(ctx, t):
        if t > 3.6:
            return
        a = min(1.0, t / 0.15) * (1 if t < 3.3 else max(0.0, (3.6 - t) / 0.3))
        ss = [texte(l, 54, INK, True) for l in TITRE.split("\n")]
        w = max(x.get_width() for x in ss) + 60
        h = sum(x.get_height() for x in ss) + 40
        ctx.save()
        ctx.translate(540, 300)
        ctx.rotate(-0.02)
        rrect(ctx, -w / 2 + 8, -h / 2 + 10, w, h, 18)
        flat(ctx, (0, 0, 0), 0.35 * a)
        rrect(ctx, -w / 2, -h / 2, w, h, 18)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.fill_preserve()
        stroke(ctx, 7, INK, alpha=a)
        yy = -h / 2 + 20
        for x in ss:
            ctx.set_source_surface(x, -x.get_width() / 2, yy)
            ctx.paint_with_alpha(a)
            yy += x.get_height()
        ctx.restore()

    # ── scènes ──
    t_ding = W(0, "payer")

    def s_hook(ctx, t, lt):
        f_t[0] = t
        K.magasin(ctx, t)
        kev.draw(ctx, 380, 1720, 0.85, t, bouche=bouche(t, "nar"))
        K.caisse(ctx, 520, 1760, 0.9, 2, tiroir=ease((t - t_ding) / 0.15) if t >= t_ding else 0.0, t=t)
        if t >= t_ding:                         # la fiche de paie jaillit du tiroir vers la caméra
            k = min(1.0, (t - t_ding) / 0.45)
            K.fiche_paie(ctx, 720 + 40 * k, 1450 - 520 * k, 0.15 + 0.55 * back(k), rouge=(t - W(0, "l'erreur")) / 0.3
                         if t >= W(0, "l'erreur") else 0.0, rot=0.6 * (1 - k) - 0.05)
        if t >= W(0, "fille"):
            ui.panneau(ctx, 540, 1250, "SA PROPRE FILLE", t - W(0, "fille"), rot=-0.04, size=70)

    def s_ticket(ctx, t, lt):
        f_t[0] = t
        K.magasin(ctx, t)
        kev.draw(ctx, 540, 1880, 0.95, t, bouche=bouche(t, "nar"))
        if t >= W(1, "ticket") - 0.1:
            K.ticket_cloture(ctx, 760, 760, 0.85 * back((t - W(1, "ticket") + 0.1) / 0.3), rot=0.06,
                             entoure=(t - W(1, "prouve")) / 0.4 if t >= W(1, "prouve") else 0.0)

    def s_caisse(ctx, t, lt):
        f_t[0] = t
        K.magasin(ctx, t)
        kev.draw(ctx, 380, 1720, 0.85, t, bouche=bouche(t, "nar"))
        K.caisse(ctx, 520, 1760, 0.9, 2, t=t)
        if t >= W(2, "premier"):
            ui.panneau(ctx, 540, 520, "1ER JOB · CAISSIER", t - W(2, "premier"), rot=-0.04, size=66,
                       fond=(255, 210, 40), bord=INK, col=INK)
        if t >= W(2, "qu'elle"):
            tante.draw(ctx, 920, 1700, 0.7, t)
            ui.badge(ctx, 920, 1700 - 0.7 * 1150, "MA TANTE, LA PATRONNE", t - W(2, "qu'elle"))

    def s_noel(ctx, t, lt):
        f_t[0] = t
        D.salon(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (20, 20, 60), 0.3)
        sapin(ctx, 960, 1560, 0.9, t)
        for i, p in enumerate(famille):
            p.draw(ctx, 120 + i * 170, 1700, 0.55, t)
        tante.draw(ctx, 640, 1780, 0.85, t, bouche=0.6 * abs(math.sin(t * 9)))
        kev.draw(ctx, 900, 1800, 0.6, t)
        if t >= W(3, "la", 1) - 0.1:
            ui.panneau(ctx, 540, 500, "« LA FAMILLE AVANT TOUT »", t - W(3, "la", 1) + 0.1, rot=-0.04, size=60,
                       fond=(250, 250, 250), bord=(40, 150, 80), col=INK)
        neige(ctx, t, n=30)

    def s_casier(ctx, t, lt):
        f_t[0] = t
        K.casiers(ctx, t)
        kev.draw(ctx, 380, 1880, 0.92, t, bouche=bouche(t, "nar"))
        if t >= W(4, "fiche") - 0.1:
            K.fiche_paie(ctx, 760, 820, 0.75 * back((t - W(4, "fiche") + 0.1) / 0.3), rot=0.05,
                         rouge=(t - W(4, "erreur")) / 0.4 if t >= W(4, "erreur") else 0.0)

    def s_tante(ctx, t, lt):
        f_t[0] = t
        bureau(ctx, t)
        tante.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "tante"))
        if L(5, 0) <= t < L(6, 0):
            if t >= W(5, "soixante") - 0.05:
                ui.panneau(ctx, 300, 560, "− 60 €", t - W(5, "soixante") + 0.05, rot=-0.06, size=110)
            if t >= W(5, "c'est") - 0.05:
                ui.panneau(ctx, 640, 760, "« C'EST LA RÈGLE »", t - W(5, "c'est") + 0.05, rot=0.04, size=60)
        if L(7, 0) <= t < L(8, 0):
            traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, t - L(7, 0))
            if t >= W(7, "canapé") - 0.1:
                ui.panneau(ctx, 540, 520, "« LE CANAPÉ DE TA MÈRE »", t - W(7, "canapé") + 0.1, rot=0.04, size=56)

    def s_duo(ctx, t, lt):
        f_t[0] = t
        bureau(ctx, t)
        tante.draw(ctx, 780, 1780, 0.85, t)
        kev.draw(ctx, 300, 1860, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(6, "mes"):
            ui.bulle(ctx, 540, 640, "Mes comptes tombaient juste !", t - W(6, "mes"), size=46)

    def s_kev(ctx, t, lt):
        f_t[0] = t
        K.casiers(ctx, t)
        kev.draw(ctx, 540, 1840, 0.95, t, bouche=bouche(t, "nar"))
        if t >= L(13, 0):
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (30, 20, 70), 0.3)
            if t >= W(13, "soixante"):
                ui.bulle(ctx, 540, 560, "60 € perdus pour le magasin aussi…", t - W(13, "soixante"), size=42)

    def s_echo(ctx, t, lt):
        bureau(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 30), 0.5)
        ui.panneau(ctx, 540, 900, "C'EST LA RÈGLE.", lt, rot=-0.05, size=100)

    t_r = L(10, 0)

    def s_fond(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))
        __import__("decors_liste").rayons(ctx, 540, 700, t * 2.5, (120, 200, 190), alpha=0.12)
        __import__("decors_liste").pieces_flottantes(ctx, t * 2.0, n=26)

    def h_regle(ctx, t, lt):
        ctx.save()
        ctx.translate(18 * math.sin(t * 1.6), 22 * math.sin(t * 1.1))
        ctx.rotate(0.015 * math.sin(t * 1.3))
        ui.carte_regle(ctx, t - t_r, "LA RÈGLE", [
            (0.15, "Erreur de caisse :\npas de retenue sur la paie", "pas de retenue"),
            (W(11, "c'est") - t_r, "C'est une sanction en argent,\ninterdite", "interdite"),
            (W(11, "seule") - t_r, "Seule exception :\nla faute lourde (exprès)", "la faute lourde"),
        ], y0=300)
        ctx.restore()
        ecrit(ctx, "Code du travail, art. L1331-2 · Cass. soc. 14 déc. 2022", 540, 1150, 26, (230, 230, 236))

    def s_comment(ctx, t, lt):
        s_fond(ctx, t, lt)
        k = back(lt / 0.3)
        ctx.save()
        ctx.translate(540 + 18 * math.sin(t * 1.6), 860 + 22 * math.sin(t * 1.1))
        ctx.rotate(0.02 * math.sin(t * 1.3))
        ctx.scale(k, k)
        rrect(ctx, -430, -320, 860, 640, 30)
        paint(ctx, (250, 248, 240), 6, shade=0.95)
        ecrit(ctx, "Je récupère comment ?", 0, -230, 56, INK, big=True)
        if t >= W(12, "un"):
            ecrit(ctx, "1. Un message écrit", -370, -90, 54, (40, 110, 200), big=True, ax=0)
        if t >= W(12, "l'article"):
            ecrit(ctx, "2. L'article L1331-2", -370, 30, 54, (40, 110, 200), big=True, ax=0)
        if t >= W(12, "trois") - 0.2:
            ecrit(ctx, "jusqu'à 3 ANS en arrière", 0, 190, 62, (40, 150, 80), big=True,
                  scale=back((t - W(12, "trois") + 0.2) / 0.3))
        ctx.restore()

    def s_bureau_soir(ctx, t, lt):
        f_t[0] = t
        bureau(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 40), 0.18)
        kev.draw(ctx, 300, 1880, 0.9, t, bouche=bouche(t, "nar"))
        K.ticket_cloture(ctx, 740, 820, 0.95, rot=0.05,
                         entoure=(t - W(14, "caisse") + 0.1) / 0.4 if t >= W(14, "caisse") - 0.1 else 0.0)
        if t >= W(14, "pas"):
            ui.panneau(ctx, 740, 1320, "PAS LA MIENNE", t - W(14, "pas"), rot=-0.05, size=64)

    def s_jade(ctx, t, lt):
        f_t[0] = t
        K.magasin(ctx, t)
        jade.draw(ctx, 380, 1720, 0.85, t)
        K.caisse(ctx, 520, 1760, 0.9, 4, t=t)
        if t >= W(15, "cousine") - 0.1:
            ui.badge(ctx, 380, 1720 - 0.85 * 1150, "JADE, SA FILLE", t - W(15, "cousine") + 0.1)

    def ecran_msg(c, x0, y0, w, h, t):
        ecrit(c, "lun. 08:12", x0 + w / 2, y0 + 30, 24, (120, 120, 130))
        C.bulle_msg(c, x0, y0 + 70, w, "Bonjour, la retenue pour erreur de caisse est interdite (art. L1331-2). "
                    "Le ticket de clôture montre la caisse 4.", True, ease((t - L(16, 0)) / 0.3), size=32)
        rrect(c, x0 + w - 300, y0 + 380, 260, 330, 14)
        paint(c, (250, 250, 246), 3, shade=1)
        ecrit(c, "CAISSE 4", x0 + w - 170, y0 + 480, 40, INK, big=True)
        ecrit(c, "−60,00", x0 + w - 170, y0 + 600, 36, (210, 40, 50), big=True)
        if t >= W(16, "elle"):
            ecrit(c, "Vu ✓✓", x0 + w - 40, y0 + 750, 28, (90, 90, 100), ax=1)

    def s_message(ctx, t, lt):
        fond = lambda c, tt: K.casiers(c, tt)          # noqa: E731
        fond(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)
        C.grand_tel(ctx, 540, 900, 0.95, "Tante Nadia", couleur=(40, 160, 90),
                    contenu=lambda c, *a: ecran_msg(c, *a, t), t=t)

    def s_paie(ctx, t, lt):
        f_t[0] = t
        K.casiers(ctx, t)
        kev.draw(ctx, 320, 1880, 0.9, t, bouche=bouche(t, "nar"))
        K.fiche_paie(ctx, 740, 820, 0.75 * back(lt / 0.3), rot=-0.04, rouge=(lt - 0.4) / 0.4, plus=True)

    t_recap = W(17, "et")

    def h_recap(ctx, t):                        # TEST partage / enregistrement : la carte à garder, 3 s pleines
        if not (t_recap <= t < t_recap + 3.4):
            return
        ctx.rectangle(0, 0, 1080, 1920)
        flat(ctx, (10, 10, 20), 0.45 * min(1.0, (t - t_recap) / 0.2))
        ui.carte_regle(ctx, t - t_recap, "À GARDER", [
            (0.1, "Erreur de caisse retenue\nsur ta paie = INTERDIT", "INTERDIT"),
            (0.5, "Sauf faute lourde\n(fait exprès)", "faute lourde"),
            (0.9, "Réclame par écrit :\njusqu'à 3 ans en arrière", "3 ans"),
        ], y0=330)

    def s_final(ctx, t, lt):
        f_t[0] = t
        K.magasin(ctx, t)
        jade.draw(ctx, 940, 1640, 0.6, t)
        K.caisse(ctx, 980, 1660, 0.62, 9, t=t)
        kev.draw(ctx, 380, 1720, 0.85, t, bouche=bouche(t, "nar"))
        K.caisse(ctx, 520, 1760, 0.9, 2, t=t)
        if t >= L(19, 0):
            ui.panneau(ctx, 540, 520, "SAUF AVANT LA RÈGLE", t - L(19, 0), rot=-0.04, size=74, fond=(255, 210, 40),
                       bord=INK, col=INK)

    # ── plans (caméra « plans » : un gros plan calé sur chaque mot clé) ──
    plan(0, s_hook, (None, 540, 1100, 1.0), (W(0, "payer") + 0.2, 600, 900, 1.35),
         (W(0, "fille"), 540, 1150, 1.05))
    plan(1, s_ticket, (None, 540, 1100, 1.0), (W(1, "prouve"), 740, 760, 1.6))
    plan(2, s_caisse, (None, 540, 1100, 1.0), (W(2, "premier"), 520, 700, 1.4), (W(2, "qu'elle"), 760, 1150, 1.25))
    plan(3, s_noel, (None, 560, 1150, 1.0), (W(3, "la", 1), 600, 700, 1.4))
    plan(4, s_casier, (None, 540, 1100, 1.0), (W(4, "fiche"), 700, 900, 1.25), (W(4, "erreur"), 760, 820, 1.7))
    plan(5, s_tante, (None, *tete(540, 1800, 0.95), 1.4), (W(5, "soixante"), 420, 700, 1.6),
         (W(5, "c'est"), 600, 800, 1.5))
    plan(6, s_duo, (None, 540, 1150, 1.0), (W(6, "mes"), 340, 900, 1.45), (W(6, "elle"), 760, 1050, 1.3))
    plan(7, s_tante, (None, *tete(540, 1800, 0.95), 1.6), (W(7, "canapé"), 540, 700, 1.9))
    plan(8, s_kev, (None, *tete(540, 1840, 0.95), 1.7))
    plan(9, s_echo, (None, 540, 960, 1.0), (L(9, 0) + 0.5, 540, 900, 1.3))
    plan(10, s_fond, (None, 540, 960, 1.0), (W(11, "c'est"), 560, 980, 1.25), (W(11, "seule"), 520, 940, 1.12),
         hud=h_regle)
    plan(12, s_comment, (None, 540, 860, 1.0), (W(12, "trois"), 540, 1040, 1.45))
    plan(13, s_kev, (None, 540, 1150, 1.0), (W(13, "soixante"), 600, 800, 1.4))
    plan(14, s_bureau_soir, (None, 540, 1100, 1.0), (W(14, "caisse"), 740, 760, 1.7), (W(14, "pas"), 700, 1000, 1.3))
    plan(15, s_jade, (None, 540, 1100, 1.0), (W(15, "cousine"), 400, 900, 1.5))
    plan(16, s_message, (None, 540, 900, 1.0), (W(16, "elle"), 640, 1150, 1.5))
    plan(17, s_paie, (None, 540, 1100, 1.0), (W(17, "soixante"), 740, 820, 1.6), (t_recap, 540, 960, 1.0))
    plan(18, s_final, (None, 540, 1100, 1.0), (L(19, 0), 540, 800, 1.3))

    # ── compteur, titre, sous-titres, sons ──
    f.ecran(titre)
    f.ecran(h_recap)
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ PAR KÉVIN", [(0, 0), (W(17, "soixante") + 0.3, 60)],
                                       apparition=L(2, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(t_ding, "impact", 0.9), (t_ding + 0.05, "succes", 0.4), (W(0, "fille"), "tampon", 0.6),
                       (W(1, "prouve"), "pop", 0.6), (W(4, "erreur"), "rate", 0.6), (W(5, "soixante"), "impact", 0.6),
                       (W(5, "c'est"), "tampon", 0.6), (L(7, 0), "impact", 0.8), (L(9, 0), "ticks", 0.4),
                       (W(11, "c'est"), "pop", 0.5), (W(11, "seule"), "pop", 0.5), (W(12, "trois"), "succes", 0.5),
                       (W(14, "caisse"), "impact", 0.7), (W(15, "cousine"), "tampon", 0.6), (L(16, 0), "notif", 0.7),
                       (W(17, "soixante"), "succes", 0.8), (t_recap, "pop", 0.6), (L(19, 0), "tampon", 0.7)]:
        f.son(tt, son, g)
    f.secousse(t_ding, 14)
    f.secousse(L(7, 0), 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/erreur_caisse.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_caisse"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
