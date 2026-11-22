"""Vidéo « FICELLE » n° 1 : calque de La Ficelle 7709614292470893857 (frais de scolarité, 61 / 153 / 183 €), moteur trait.
Script : scripts/modele/F1_frais_scolarite.dial. Analyse : prompts/ficelle/7709614292470893857.md.
Voix : narrateur et Kévin = Yann, l'agent = Paul K, Sofia = Natacha. Durée calquée (~100 s, la leur : 95 s).

    python3 motion/trait/ficelle_scolarite.py                 → output/trait/ficelle_scolarite.mp4
    python3 motion/trait/ficelle_scolarite.py --stills 1,10
"""
import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_colis as C  # noqa: E402
import decors_impots as I  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, paint, rrect  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/F1_frais_scolarite.dial"
VOIX = {"N": (voix.YANN, voix.REGLAGES_YANN), "K": (voix.YANN, voix.REGLAGES_YANN),
        "A": ("5l4ttmr4SKNgi0HnOelT", voix.REGLAGES_YANN), "S": ("Y2uuwzlt8SyNkjrPovVI", voix.REGLAGES_YANN)}
MARQUES = {0: [("trois cent soixante-sept euros", "[{}]")], 1: [("trente-et-un décembre", "{{{}}}")],
           4: [("Un seul", "[{}]")], 6: [("perdu", "{{{}}}")], 8: [("cent cinquante-trois euros", "[{}]")],
           10: [("Rien", "{{{}}}")], 12: [("Rien non plus", "{{{}}}")], 14: [("Où va ton argent", "[{}]")],
           16: [("Soixante et un euros", "[{}]"), ("cent cinquante-trois", "[{}]"),
                ("cent quatre-vingt-trois", "[{}]")], 19: [("Faux", "{{{}}}")], 21: [("deux ans pleins", "[{}]")],
           26: [("trois cent soixante-sept euros", "[{}]")], 29: [("Pas besoin de rendez-vous", "[{}]")],
           36: [("Sauf que sa mère en paie", "[{}]")], 39: [("Un certificat de scolarité", "[{}]")]}

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
AGENT = dict(cheveux="court", couleur_cheveux=(150, 150, 150), peau=(236, 196, 166), haut="chemise",
             couleur_haut=(220, 226, 240), bas=(50, 50, 64), lunettes=True, moustache=True, seed=120)
SOFIA = dict(cheveux="chignon", couleur_cheveux=(40, 28, 24), peau=(226, 170, 130), haut="uni",
             couleur_haut=(230, 120, 60), bas=(60, 60, 90), seed=80)


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("A:", "K:", "S:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append((ligne[0], txt))
    return out


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.12, cible=95)
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    def W(li, prefixe, n=0):
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t0"]

    def plan(li, scene, *plans, hud=None):
        t0 = L(li, 0)
        cam = [(0 if k[0] is None else max(0.0, k[0] - t0 - 0.04), *k[1:]) for k in plans]
        f.plan(L(li, 0) if li else 0, scene, cam, fouet=bool(li), hud=hud)

    kev, agent, sofia = Perso(**KEVIN), Perso(**AGENT), Perso(**SOFIA)
    f_t = [0.0]

    def objet_kev(ctx, x, y, s):
        t = f_t[0]
        if L(9, 0) <= t < L(14, 0):
            I.avis(ctx, x, y - 100, 0.28, 2026, "Revenus 2025", rot=-0.06)
        elif t >= L(37, 0):
            I.certificats(ctx, x, y - 100, 0.22, 3, t)
        else:
            D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)

    kev.objet = objet_kev
    agent.objet = lambda c, x, y, s: None
    sofia.objet = lambda c, x, y, s: None
    kev.pose(0, "mains_hanches").emotion(0, "malin").pose(L(2, 0), "pointe").emotion(L(2, 0), "content")
    kev.pose(L(9, 0), "objet").emotion(L(9, 0), "neutre").emotion(L(10, 0), "choc").emotion(L(13, 0), "triste")
    kev.pose(L(14, 0), "leve").emotion(L(14, 0), "content").pose(L(15, 0), "repos")
    kev.pose(L(28, 0), "pointe").emotion(L(28, 0), "neutre").pose(L(30, 0), "telephone").emotion(L(30, 0), "malin")
    kev.pose(L(37, 0), "objet").emotion(L(37, 0), "malin")
    agent.pose(0, "mains_hanches").emotion(0, "malin").emotion(L(3, 0), "choc").pose(L(5, 0), "leve")
    agent.pose(L(18, 0), "pointe_g").emotion(L(18, 0), "malin").pose(L(29, 0), "repos").emotion(L(29, 0), "neutre")
    agent.pose(L(33, 0), "pointe_g").emotion(L(33, 0), "malin").emotion(L(38, 0), "choc").pose(L(38, 0), "leve")
    sofia.pose(0, "repos").emotion(0, "content")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui in ("N", "K") else 1.0)

    # jour du calendrier selon le moment (compte à rebours qui avance dans la vidéo)
    def jour(t):
        for li, j in ((37, 40), (33, 41), (22, 42)):
            if t >= L(li, 0):
                return j
        return 43

    def s_guichet(ctx, t, lt, rideau=0.0, kev_x=230):
        f_t[0] = t
        I.accueil(ctx, t, rideau=rideau)
        agent.draw(ctx, 640, 1700, 0.85, t, bouche=bouche(t, "A"))
        I.guichet(ctx, 640, 1330)
        I.calendrier(ctx, 470, 1170, 0.7, jour(t), t, t_arrache=0.25 if t < 2 else
                     (L(22, 0) if L(22, 0) <= t < L(22, 0) + 1 else (L(33, 0) if L(33, 0) <= t < L(33, 0) + 1 else
                                                                       (L(37, 0) if t >= L(37, 0) else None))))
        D.etiquette(ctx, 800, 1260, 0.6, "367 €", t)
        kev.draw(ctx, kev_x, 1880, 0.92, t, bouche=bouche(t, "K"))

    def s_hook(ctx, t, lt):
        s_guichet(ctx, t, lt)

    def s_rideau(ctx, t, lt):
        s_guichet(ctx, t, lt, rideau=(t - W(5, "céder")) / 0.6 if t >= W(5, "céder") else 0.0)
        if L(4, 0) <= t < L(5, 0) and t >= W(4, "un"):
            ui.panneau(ctx, 540, 520, "UN SEUL TRUC", t - W(4, "un"), rot=-0.04, size=80)

    def s_urgence(ctx, t, lt):
        s_guichet(ctx, t, lt, rideau=1.0)
        if t >= W(6, "perdu") - 0.1:
            ui.panneau(ctx, 540, 520, "PERDU POUR TOUJOURS", t - W(6, "perdu") + 0.1, rot=-0.04, size=70)

    def s_pause(ctx, t, lt):
        f_t[0] = t
        I.salle_pause(ctx, t)
        sofia.draw(ctx, 760, 1840, 0.88, t, bouche=bouche(t, "S"))
        kev.draw(ctx, 360, 1860, 0.88, t, bouche=bouche(t, "K"))
        if t >= L(8, 0):
            ui.badge(ctx, 760, 1840 - 0.88 * 1150, "SOFIA, AU BOULOT", t - L(8, 0))
        if t >= W(8, "cent") - 0.1:
            ui.panneau(ctx, 640, 520, "− 153 € PAR AN", t - W(8, "cent") + 0.1, rot=-0.04, size=80,
                       fond=(70, 205, 115), bord=INK, col=INK)

    def s_avis(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 300, 1880, 0.9, t, bouche=bouche(t, "N"))
        n = 1 if t < L(11, 0) else 3
        for i in range(n):
            t_in = L(9, 0) if i == 0 else L(11, 0) + 0.3 + 0.15 * i
            k = ease((t - t_in) / 0.35)
            I.avis(ctx, 720 - i * 40, 800 + i * 50 + 1000 * (1 - k), 0.75, 2026 - i, f"Revenus {2025 - i}",
                   rot=0.05 - i * 0.06)
        if L(10, 0) <= t < L(11, 0) or L(12, 0) <= t < L(13, 0):
            ui.panneau(ctx, 720, 1300, "RIEN", t - (L(10, 0) if t < L(11, 0) else L(12, 0)), rot=-0.05, size=110)

    def ecran_abo(c, x0, y0, w, h, t):
        ecrit(c, "@souslesabot", x0 + w / 2, y0 + 80, 44, INK, big=True)
        ecrit(c, "Où va ton argent ?", x0 + w / 2, y0 + 140, 34, (90, 90, 100))
        rrect(c, x0 + 80, y0 + 220, w - 160, 100, 50)
        flat(c, (60, 170, 100))
        ecrit(c, "Abonné ✓", x0 + w / 2, y0 + 270, 44, (255, 255, 255), big=True)
        for i in range(6):
            rrect(c, x0 + 30 + (i % 3) * 178, y0 + 380 + (i // 3) * 260, 166, 240, 10)
            flat(c, [(70, 90, 140), (200, 120, 60), (60, 150, 110)][i % 3])

    def s_abo(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 300, 1880, 0.9, t)
        C.grand_tel(ctx, 700, 900, 0.7, "TikTok", couleur=(20, 20, 26), contenu=lambda c, *a: ecran_abo(c, *a, t), t=t)

    def s_fond(ctx, t, lt):
        I.accueil(ctx, t)
        agent.draw(ctx, 640, 1700, 0.85, t)
        I.guichet(ctx, 640, 1330)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (12, 14, 26), 0.62)

    def carte_loi(ctx, t, t0, titre, sous, lignes_):
        k = back((t - t0) / 0.3)
        ctx.save()
        ctx.translate(540 + 16 * math.sin(t * 1.6), 620 + 18 * math.sin(t * 1.1))
        ctx.rotate(0.015 * math.sin(t * 1.3))
        ctx.scale(k, k)
        rrect(ctx, -420, -260, 840, 520, 24)
        paint(ctx, (252, 250, 244), 6, shade=0.95)
        rrect(ctx, -420, -260, 840, 120, 24)
        paint(ctx, (200, 40, 50), 6, shade=0.95)
        ecrit(ctx, titre, 0, -200, 60, (255, 255, 255), big=True)
        ecrit(ctx, sous, 0, -95, 30, (110, 110, 120))
        for i, l in enumerate(lignes_):
            ecrit(ctx, l, 0, -10 + i * 80, 50, INK, big=True)
        ctx.restore()

    def s_loi1(ctx, t, lt):
        s_fond(ctx, t, lt)
        if t < L(16, 0):
            carte_loi(ctx, t, L(15, 0), "Art. 199 quater F", "Code général des impôts",
                      ["Enfant scolarisé", "= impôt en moins"])
        else:
            n = 1 + (t >= W(16, "cent")) + (t >= W(16, "cent", 1) - 0.1)
            I.tableau(ctx, 540 + 16 * math.sin(t * 1.4), 700, 1.2, n, t)
            if t >= W(16, "sans"):
                ui.panneau(ctx, 540, 1100, "SANS FACTURE", t - W(16, "sans"), rot=-0.04, size=80, fond=(70, 205, 115),
                           bord=INK, col=INK)

    def s_case(ctx, t, lt):
        s_guichet(ctx, t, lt)
        if L(17, 0) <= t < L(18, 0) and t >= W(17, "personne"):
            ui.panneau(ctx, 540, 520, "PERSONNE NE COCHE LA CASE", t - W(17, "personne"), rot=-0.04, size=58)
        if L(18, 0) <= t < L(19, 0) and t >= W(18, "l'erreur"):
            ui.bulle(ctx, 600, 760, "L'erreur est chez vous.", t - W(18, "l'erreur"), size=48, cote=-1)

    def s_faux(ctx, t, lt):
        s_fond(ctx, t, lt)
        ui.panneau(ctx, 540, 800, "FAUX.", lt, rot=-0.06, size=180)

    def s_loi2(ctx, t, lt):
        s_fond(ctx, t, lt)
        carte_loi(ctx, t, L(20, 0), "RÉCLAMATION", "Livre des procédures fiscales, art. R*196-1",
                  ["Déclaration validée ?", "Tu as 2 ans pleins", "(jusqu'au 31/12)" if t >= W(21, "deux") else ""])

    def s_compte(ctx, t, lt):
        f_t[0] = t
        s_fond(ctx, t, lt)
        for i, (li, annee, rev, val) in enumerate(((23, 2026, "Revenus 2025 · Première", "+153 €"),
                                                    (24, 2025, "Revenus 2024 · Seconde", "+153 €"),
                                                    (25, 2024, "Revenus 2023 · Collège", "+61 €"))):
            if t >= L(li, 0):
                k = ease((t - L(li, 0)) / 0.35)
                I.avis(ctx, 300 + i * 240, 760 + i * 60 + 900 * (1 - k), 0.62, annee, rev, valeur=val,
                       rot=-0.08 + i * 0.08)
        if t >= W(26, "trois") - 0.1:
            ui.panneau(ctx, 540, 1250, "TOTAL : 367 €", t - W(26, "trois") + 0.1, rot=-0.04, size=100,
                       fond=(255, 210, 40), bord=INK, col=INK)
        if t >= L(27, 0):
            I.calendrier(ctx, 860, 380, 0.6, 42, t)
            ui.panneau(ctx, 300, 380, "LE 61 € EXPIRE", t - L(27, 0), rot=0.05, size=56)

    def s_rdv(ctx, t, lt):
        s_guichet(ctx, t, lt)
        if t >= L(29, 0):
            ui.bulle(ctx, 600, 760, "Pas besoin de rendez-vous.", t - L(29, 0), size=48, cote=-1)

    def s_reclam(ctx, t, lt):
        f_t[0] = t
        s_fond(ctx, t, lt)
        n = 1 + (t >= L(31, 0)) + (t >= L(32, 0))
        I.reclamation(ctx, 540 + 14 * math.sin(t * 1.3), 820, 1.0 * back(lt / 0.3), n, t)

    def s_objection(ctx, t, lt):
        s_guichet(ctx, t, lt)
        if L(33, 0) <= t < L(34, 0):
            ui.bulle(ctx, 600, 760, "Elle paie des impôts ?", t - L(33, 0), size=44, cote=-1)

    def s_limite(ctx, t, lt):
        s_fond(ctx, t, lt)
        carte_loi(ctx, t, L(34, 0), "LA LIMITE", "Réduction ≠ crédit d'impôt",
                  ["Pas d'impôt payé ?", "= rien de remboursé", "Sa mère en paie : OK" if t >= L(36, 0) else ""])

    def s_preuve(ctx, t, lt):
        s_guichet(ctx, t, lt)
        if L(37, 0) <= t < L(38, 0):
            ui.bulle(ctx, 600, 760, "Vous pouvez le prouver ?", t - L(37, 0), size=44, cote=-1)
        if t >= L(39, 0):
            k = ease((t - L(39, 0)) / 0.4)
            I.certificats(ctx, 540, 760 + 1000 * (1 - k), 0.8, 3, t)

    # ── plans : grammaire La Ficelle (champ / contrechamp, panoramique éclair entre personnages, réactions,
    #    gros plan sur chaque mot clé, une coupe toutes les ~1,6 s) ──
    LARGE = (540, 1150, 1.0)
    CAG = (640, 1080, 1.5)          # plan moyen sur l'agent (taille → tête)
    CKV = (320, 1210, 1.5)           # plan moyen sur Kévin
    CAL = (470, 1170, 2.3)            # gros plan calendrier
    TAG = (770, 1250, 2.4)            # gros plan étiquette 367 €
    plan(0, s_hook, (None, *LARGE), (0.8, 600, 1200, 1.9), (W(0, "trois") - 0.05, *TAG),
         (L(1, 0), *CAG, "pan"), (W(1, "et") - 0.05, *CAL), (L(2, 0), *CKV, "pan"),
         (W(3, "avant") - 0.05, *CAG, "pan"), (W(3, "réveillon"), *CKV, "pan"))
    plan(4, s_rideau, (None, *LARGE), (W(4, "un") - 0.05, 290, 1160, 1.8), (W(4, "que", 1), *LARGE),
         (L(5, 0), 640, 1050, 1.35), (W(5, "céder") - 0.05, *CAG, "pan"))
    plan(6, s_urgence, (None, *LARGE), (W(6, "un"), *CAL), (W(6, "perdu") - 0.05, 540, 820, 1.4),
         (W(6, "sans"), *CKV, "pan"))
    plan(7, s_pause, (None, 540, 1150, 1.0), (W(7, "avec"), 560, 1150, 1.12), (L(8, 0), 760, 1120, 1.55, "pan"),
         (W(8, "cent") - 0.05, 640, 820, 1.5), (W(8, "par"), 360, 1150, 1.55, "pan"))
    plan(9, s_avis, (None, 540, 1100, 1.0), (W(9, "l'avis"), 720, 1000, 1.45), (L(10, 0), 720, 1050, 1.9),
         (L(11, 0), 300, 1240, 1.7), (W(11, "kévin"), 640, 1050, 1.2), (L(12, 0), 700, 1080, 1.8),
         (L(13, 0), 300, 1090, 2.1))
    plan(14, s_abo, (None, 300, 1200, 1.7), (W(14, "kévin"), 540, 1050, 1.0), (W(14, "où"), 700, 860, 1.55, "pan"))
    plan(15, s_loi1, (None, 540, 760, 1.0), (W(15, "un"), 540, 680, 1.25), (L(16, 0), 540, 740, 1.05),
         (W(16, "cent") - 0.05, 540, 770, 1.3), (W(16, "cent", 1) - 0.05, 540, 860, 1.4), (W(16, "sans"), 540, 1000, 1.25))
    plan(17, s_case, (None, *LARGE), (W(17, "personne"), 540, 760, 1.3), (L(18, 0), *CAG, "pan"),
         (W(18, "l'erreur"), 620, 900, 1.35))
    plan(19, s_faux, (None, 540, 820, 1.25))
    plan(20, s_loi2, (None, 540, 760, 1.0), (L(21, 0), 540, 680, 1.25), (W(21, "deux"), 540, 760, 1.45))
    plan(22, s_compte, (None, 540, 900, 1.0), (L(23, 0) + 0.3, 300, 800, 1.6), (L(24, 0) + 0.3, 540, 860, 1.6, "pan"),
         (L(25, 0) + 0.3, 780, 920, 1.6, "pan"), (L(26, 0), 540, 1000, 1.05), (W(26, "trois"), 540, 1220, 1.6),
         (L(27, 0), 860, 420, 1.8), (W(27, "expire"), 300, 400, 1.7, "pan"))
    plan(28, s_rdv, (None, *CKV), (L(29, 0), *CAG, "pan"), (W(29, "rendez-vous"), 600, 820, 1.5))
    plan(30, s_reclam, (None, 540, 820, 1.0), (W(30, "un"), 540, 520, 1.6), (L(31, 0), 540, 600, 1.7),
         (L(32, 0), 540, 820, 1.7), (W(32, "l'article"), 540, 1000, 1.25))
    plan(33, s_objection, (None, *CAG), (W(33, "au"), 600, 820, 1.4))
    plan(34, s_limite, (None, 540, 760, 1.0), (L(35, 0), 540, 700, 1.3), (W(35, "si"), 540, 760, 1.45),
         (L(36, 0), 540, 860, 1.45))
    plan(37, s_preuve, (None, *CAG), (W(37, "lycée"), 600, 820, 1.4), (L(38, 0), *LARGE),
         (W(38, "grâce"), 300, 1160, 1.7, "pan"), (L(39, 0), 540, 860, 1.3), (W(39, "pour"), 540, 760, 1.6))

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "CE QUE L'ÉTAT DOIT À SA MÈRE",
                                       [(0, 0), (L(23, 0) + 0.4, 153), (L(24, 0) + 0.4, 306), (L(25, 0) + 0.4, 367)],
                                       apparition=L(6, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(0.25, "whoosh", 0.6), (W(0, "trois"), "impact", 0.7), (W(5, "céder"), "rate", 0.6),
                       (W(6, "perdu"), "tampon", 0.6), (W(8, "cent"), "pop", 0.5), (L(10, 0), "rate", 0.5),
                       (L(12, 0), "rate", 0.5), (L(14, 0) + 0.3, "succes", 0.6), (L(15, 0), "pop", 0.5),
                       (W(16, "sans"), "pop", 0.5), (L(19, 0), "impact", 0.8), (L(23, 0), "pop", 0.5),
                       (L(24, 0), "pop", 0.5), (L(25, 0), "pop", 0.5), (W(26, "trois"), "succes", 0.8),
                       (L(29, 0), "pop", 0.5), (L(31, 0), "pop", 0.5), (L(32, 0), "pop", 0.5),
                       (L(36, 0), "succes", 0.5), (L(39, 0), "tampon", 0.7)]:
        f.son(tt, son, g)
    f.secousse(L(19, 0), 12)
    f.dur = L(39, 0, fin=False) + (len(voice) / voix.SR - L(39, 0))          # coupe nette en fin de phrase (boucle)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/ficelle_scolarite.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_ficelle1"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
