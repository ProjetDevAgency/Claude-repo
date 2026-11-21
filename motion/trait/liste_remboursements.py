"""« 5 remboursements que tu laisses filer » : vidéo LISTE au format La Ficelle (démo du 21 nov.), moteur « trait ».
Script : scripts/modele/50_liste_remboursements.dial. Kévin = Yann, le père = Paul K. Voix v4 accélérée ×1,25.

    python3 motion/trait/liste_remboursements.py                 → output/trait/liste_remboursements.mp4
    python3 motion/trait/liste_remboursements.py --stills 1,10
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
import decors_liste as L_  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, paint, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/50_liste_remboursements.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "pere": (os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT"), voix.REGLAGES_YANN)}
VITESSE = 1.25

MARQUES = {0: [("Cinq remboursements", "[{}]")], 1: [("six cents euros", "[{}]")],
           2: [("quarante-cinq minutes", "{{{}}}")], 4: [("un quart du billet", "[{}]")],
           5: [("quinze euros", "[{}]")], 7: [("périmés", "{{{}}}")], 9: [("quinze jours", "[{}]")],
           10: [("Soixante-douze euros", "[{}]")], 11: [("Cent vingt euros", "{{{}}}")],
           13: [("huit euros", "[{}]"), ("quatre-vingts euros", "[{}]")], 14: [("Quarante euros", "[{}]")],
           15: [("Vingt mois", "{{{}}}")], 16: [("un an", "{{{}}}")], 19: [("deux ans", "[{}]")],
           20: [("Deux cent quatre-vingt-dix euros", "[{}]")], 21: [("quatre heures de retard", "{{{}}}")],
           24: [("trois heures", "[{}]")], 25: [("quatre cents euros", "[{}]")],
           27: [("huit cent dix-sept euros", "[{}]")]}

KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
SOFIA = dict(cheveux="chignon", couleur_cheveux=(40, 28, 24), peau=(226, 170, 130), haut="uni",
             couleur_haut=(230, 120, 60), bas=(60, 60, 90), seed=80)
VENDEUR = dict(cheveux="court", couleur_cheveux=(200, 160, 90), peau=(240, 200, 170), haut="polo",
               couleur_haut=(150, 70, 170), bas=(40, 40, 50), seed=81)
PERE = dict(cheveux="plaque", couleur_cheveux=(120, 110, 100), peau=(198, 138, 98), haut="chemise",
            couleur_haut=(200, 200, 220), bas=(50, 50, 64), moustache=True, seed=82)
MERE = dict(cheveux="chignon", couleur_cheveux=(60, 46, 40), peau=(205, 145, 105), haut="gilet",
            couleur_haut=(190, 90, 110), bas=(70, 60, 90), seed=83)
HOTESSE = dict(cheveux="chignon", couleur_cheveux=(160, 110, 60), peau=(240, 200, 170), haut="uni",
               couleur_haut=(40, 60, 120), bas=(40, 60, 120), seed=84)


def lignes():
    out = []
    for ligne in open(DIAL, encoding="utf-8"):
        if ligne[:2] not in ("M:", "N:"):
            continue
        txt = ligne[2:].strip()
        for a, motif in MARQUES.get(len(out), []):
            assert a in txt, (len(out), a)
            txt = txt.replace(a, motif.format(a), 1)
        out.append(("pere" if ligne[0] == "M" else "nar", txt))
    return out


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.2, speed=VITESSE)
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    def W(li, prefixe, n=0, fin=False):
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t1" if fin else "t0"]

    kev, sofia, vendeur = Perso(**KEVIN), Perso(**SOFIA), Perso(**VENDEUR)
    pere, mere, hotesse = Perso(**PERE), Perso(**MERE), Perso(**HOTESSE)
    f_t = [0.0]

    def objet_kev(ctx, x, y, s):
        t = f_t[0]
        D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)

    kev.objet = objet_kev
    sofia.objet = lambda ctx, x, y, s: L_.releve(ctx, x, y - 90, 0.22, 15, -1, 99)
    pere.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.8, rot=-0.1)

    kev.pose(0, "pointe").emotion(0, "malin").pose(L(1, 0), "repos")
    kev.pose(L(2, 0), "mains_hanches").emotion(L(2, 0), "triste").pose(L(5, 0), "telephone").emotion(L(5, 0), "content")
    kev.pose(L(7, 0), "repos").emotion(L(7, 0), "choc").emotion(L(10, 0), "content").pose(L(10, 0), "leve_d")
    kev.pose(L(15, 0), "telephone").emotion(L(15, 0), "choc").pose(L(16, 0), "repos").emotion(L(16, 0), "colere")
    kev.pose(L(17, 0), "telephone").emotion(L(17, 0), "malin").pose(L(20, 0), "leve").emotion(L(20, 0), "content")
    kev.pose(L(21, 0), "repos").emotion(L(21, 0), "neutre").emotion(L(22, 0), "triste")
    kev.pose(L(25, 0), "telephone").emotion(L(25, 0), "malin").pose(L(27, 0), "leve").emotion(L(27, 0), "content")
    sofia.pose(0, "objet").emotion(0, "choc").emotion(L(14, 0), "content").pose(L(14, 0), "leve_d")
    vendeur.pose(0, "haussement").emotion(0, "malin")
    pere.pose(0, "repos").emotion(0, "malin").pose(L(22, 0), "pointe_g").emotion(L(22, 0), "content")
    pere.emotion(L(25, 0), "choc").pose(L(26, 0), "telephone").emotion(L(26, 0), "triste")
    mere.pose(0, "repos").emotion(0, "neutre").emotion(L(26, 0), "content")
    hotesse.pose(0, "mains_hanches").emotion(0, "malin")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    def fond_flou(ctx, t, decor):
        decor(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)

    # ── scènes ──
    ENV = [("15 €", "train"), ("72 €", "ticket"), ("40 €", "banque"), ("290 €", "tel"), ("600 €", "avion")]

    def s_hook(ctx, t, lt):
        f_t[0] = t
        import decors_ville as V
        V.ville_nuit(ctx, t)
        kev.draw(ctx, 190, 1860, 0.9, t, bouche=bouche(t, "nar"))
        pos = [(420, 1180, 0.42), (600, 1180, 0.5), (780, 1180, 0.58), (520, 1620, 0.66), (840, 1660, 0.8)]
        for i, (m, ic) in enumerate(ENV):
            ti = 0.15 + i * 0.32
            if lt < ti:
                continue
            x, y, s0 = pos[i]
            k = back((lt - ti) / 0.3)
            L_.enveloppe(ctx, x, y, s0 * k, m, ic, lueur=(1.0 if i == 4 and t >= L(1, 0) else 0.0),
                         rot=0.04 * math.sin(t * 2 + i))
        if t >= W(1, "six") - 0.1:
            ui.panneau(ctx, 640, 520, "LE PLUS GROS : 600 €", t - W(1, "six") + 0.1, rot=-0.04, size=74,
                       fond=(255, 210, 40), bord=INK, col=INK)

    def s_quai(ctx, t, lt):
        f_t[0] = t
        x = 1500 - 1400 * ease(lt / 3.0)
        L_.quai(ctx, t, train_x=x, retard=t >= W(2, "le") - 0.2)
        kev.draw(ctx, 300, 1900, 0.85, t, bouche=bouche(t, "nar"))
        if t >= W(2, "quarante") - 0.1:
            ui.panneau(ctx, 640, 560, "+45 MIN", t - W(2, "quarante") + 0.1, rot=-0.05, size=100)

    def carte(n, titre, montant):
        def sc(ctx, t, lt):
            L_.carte_numero(ctx, t, lt, n, titre, montant)
        return sc

    t_r5 = L(4, 0)

    def s_regle_fond(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))
        L_.rayons(ctx, 540, 700, t, (120, 200, 190), alpha=0.06)
        L_.pieces_flottantes(ctx, t)

    def h_r5(ctx, t, lt):
        ui.carte_regle(ctx, t - t_r5, "GARANTIE 30 MIN", [
            (0.15, "Retard de 30 min à 2 h :\n25 % du billet", "25 %"),
            (W(4, "la", 1) - t_r5, "De 2 h à 3 h : 50 %", "50 %"),
            (W(4, "les") - t_r5, "Plus de 3 h : 75 %", "75 %"),
        ], y0=300)
        ecrit(ctx, "TGV INOUI et Intercités · garantie SNCF Voyageurs", 540, 1150, 26, (230, 230, 236))

    def ecran_form(c, x0, y0, w, h, t):
        ecrit(c, "Garantie 30 min", x0 + w / 2, y0 + 60, 44, INK, big=True)
        for k, lab in enumerate(("N° de dossier", "Train du 21/11", "Retard : 45 min")):
            rrect(c, x0 + 40, y0 + 130 + k * 110, w - 80, 80, 14)
            paint(c, (255, 255, 255), 3, shade=1)
            ecrit(c, lab, x0 + 70, y0 + 170 + k * 110, 34, (80, 80, 90), ax=0)
        if t >= W(5, "quinze") - 0.1:
            k = back((t - W(5, "quinze") + 0.1) / 0.3)
            rrect(c, x0 + 60, y0 + 520, w - 120, 160, 24)
            flat(c, (70, 205, 115))
            ecrit(c, "15 €", x0 + w / 2, y0 + 580, 80, INK, big=True, scale=k)
            ecrit(c, "bon d'achat", x0 + w / 2, y0 + 650, 32, INK)
        if t >= W(5, "virement") - 0.2:
            ecrit(c, "> 1 h de retard = virement", x0 + w / 2, y0 + 760, 32, (40, 80, 160), big=True)

    def s_form(ctx, t, lt):
        fond_flou(ctx, t, lambda c, tt: L_.quai(c, tt, train_x=100, retard=True))
        C.grand_tel(ctx, 540, 900, 0.95, "SNCF Connect", couleur=(130, 40, 90),
                    contenu=lambda c, *a: ecran_form(c, *a, t), t=t)

    def ecran_partage(c, x0, y0, w, h, t):
        ecrit(c, "aujourd'hui 22:41", x0 + w / 2, y0 + 30, 24, (120, 120, 130))
        C.bulle_msg(c, x0, y0 + 70, w, "Regarde ça, toi qui fais Paris-Lille tous les week-ends 👇", True,
                    ease((t - L(6, 0)) / 0.3), size=36)
        if t >= W(6, "vidéo") - 0.1:
            rrect(c, x0 + w - 380, y0 + 300, 340, 420, 20)
            paint(c, (30, 30, 40), 4, shade=1)
            ecrit(c, "▶", x0 + w - 210, y0 + 480, 90, (255, 255, 255), big=True)
            ecrit(c, "5 remboursements…", x0 + w - 210, y0 + 660, 26, (255, 255, 255), big=True)
        if t >= W(6, "week") + 0.3:
            C.bulle_msg(c, x0, y0 + 760, w, "Merci !!! 😱", False, ease((t - W(6, "week") - 0.3) / 0.3), size=40)

    def s_partage(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Clara (sœur)", couleur=(40, 160, 90),
                    contenu=lambda c, *a: ecran_partage(c, *a, t), t=t)

    def s_bureau(ctx, t, lt):
        f_t[0] = t
        L_.bureau(ctx, t, tiroir=ease(lt / 0.8))
        kev.draw(ctx, 380, 1900, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(7, "huit") - 0.1:
            for i in range(8):
                ti = W(7, "huit") - 0.1 + i * 0.08
                if t < ti:
                    break
                k = ease((t - ti) / 0.3)
                L_.ticket_resto(ctx, 840 + (i % 2) * 40 - 60, 1240 - k * (240 + i * 34), 0.8,
                                rot=math.sin(i * 1.7) * 0.2, perime=t >= W(7, "périmés"))

    t_r4 = L(9, 0)

    def h_r4(ctx, t, lt):
        ui.carte_regle(ctx, t - t_r4, "TICKETS PÉRIMÉS", [
            (0.15, "Tu les rends\nà ton employeur", "à ton employeur"),
            (W(9, "dans") - t_r4, "Dans les 15 jours après\nla fin de validité", "15 jours"),
            (W(9, "gratuitement") - t_r4, "Échangés gratuitement\ncontre des neufs", "gratuitement"),
        ], y0=300)
        ecrit(ctx, "Code du travail, art. R3262-5 · tickets papier", 540, 1150, 26, (230, 230, 236))

    def s_tickets(ctx, t, lt):
        f_t[0] = t
        D.fond_sombre(ctx, t, (40, 34, 30))
        L_.rayons(ctx, 540, 700, t, (255, 210, 40), alpha=0.07)
        for i in range(8):
            ti = i * 0.12
            if lt < ti:
                break
            L_.ticket_resto(ctx, 300 + (i % 4) * 160, 560 + (i // 4) * 170, 0.75 * back((lt - ti) / 0.3),
                            rot=math.sin(i * 2.3) * 0.12)
        if t >= W(10, "soixante") - 0.1:
            ui.panneau(ctx, 540, 1000, "8 × 9 € = 72 €", t - W(10, "soixante") + 0.1, rot=-0.04, size=96,
                       fond=(70, 205, 115), bord=INK, col=INK)

    def s_sofia(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        sofia.draw(ctx, 250, 1880, 0.85, t)
        L_.releve(ctx, 720, 860, 0.62, 15, W(11, "quinze") - 0.2, t,
                  total="120 €" if t >= W(11, "cent") - 0.2 else None)
        if t >= W(11, "sofia"):
            ui.badge(ctx, 250, 1880 - 0.85 * 1150, "SOFIA, SA COLOC", t - W(11, "sofia"))

    t_r3 = L(13, 0)

    def h_r3(ctx, t, lt):
        ui.carte_regle(ctx, t - t_r3, "FRAIS BANCAIRES", [
            (0.15, "Commission d'intervention :\nplafonnée", "plafonnée"),
            (W(13, "huit") - t_r3, "8 € par opération", "8 €"),
            (W(13, "quatre") - t_r3, "80 € par mois maximum", "80 €"),
        ], y0=300)
        ecrit(ctx, "Décret n° 2013-931 · C. monétaire et financier, R312-4-1", 540, 1150, 26, (230, 230, 236))

    def s_calcul_banque(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        sofia.draw(ctx, 250, 1880, 0.85, t)
        k = back(lt / 0.3)
        ctx.save()
        ctx.translate(700, 760)
        ctx.scale(k, k)
        rrect(ctx, -320, -260, 640, 520, 30)
        paint(ctx, (250, 248, 240), 6, shade=0.95)
        ecrit(ctx, "Prélevé : 120 €", 0, -170, 54, INK, big=True)
        ecrit(ctx, "Plafond : 80 €", 0, -60, 54, (40, 110, 200), big=True)
        if t >= W(14, "quarante") - 0.2:
            ecrit(ctx, "= 40 € rendus", 0, 110, 76, (40, 150, 80), big=True,
                  scale=back((t - W(14, "quarante") + 0.2) / 0.3))
        ctx.restore()

    def s_ecran_noir(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 540, 1860, 0.95, t, bouche=bouche(t, "nar"))
        if t >= W(15, "vingt") - 0.1:
            ui.panneau(ctx, 540, 520, "20 MOIS APRÈS L'ACHAT", t - W(15, "vingt") + 0.1, rot=-0.04, size=66)

    def s_boutique(ctx, t, lt):
        f_t[0] = t
        D.boutique(ctx, t)
        vendeur.draw(ctx, 760, 1760, 0.9, t)
        D.comptoir(ctx, 760, 1380)
        kev.draw(ctx, 250, 1900, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(16, "la") - 0.1:
            ui.bulle(ctx, 700, 520, "La garantie, c'était 1 an !", t - W(16, "la") + 0.1, size=50, cote=-1)

    def ecran_abo(c, x0, y0, w, h, t):
        ecrit(c, "@souslesabot", x0 + w / 2, y0 + 80, 44, INK, big=True)
        ecrit(c, "Où va ton argent ?", x0 + w / 2, y0 + 140, 34, (90, 90, 100))
        k = ease((t - L(17, 0) - 0.4) / 0.3)
        rrect(c, x0 + 80, y0 + 220, w - 160, 100, 50)
        flat(c, (60, 170, 100) if k > 0.5 else (230, 40, 80))
        ecrit(c, "Abonné ✓" if k > 0.5 else "S'abonner", x0 + w / 2, y0 + 270, 44, (255, 255, 255), big=True)
        for i in range(6):
            rrect(c, x0 + 30 + (i % 3) * 178, y0 + 380 + (i // 3) * 260, 166, 240, 10)
            flat(c, [(70, 90, 140), (200, 120, 60), (60, 150, 110)][i % 3])

    def s_abo(ctx, t, lt):
        fond_flou(ctx, t, D.boutique)
        C.grand_tel(ctx, 540, 900, 0.95, "TikTok", couleur=(20, 20, 26),
                    contenu=lambda c, *a: ecran_abo(c, *a, t), t=t)

    t_r2 = L(19, 0)

    def h_r2(ctx, t, lt):
        ui.carte_regle(ctx, t - t_r2, "GARANTIE LÉGALE", [
            (0.15, "Produit neuf, chez un pro :\n2 ans par la loi", "2 ans"),
            (W(19, "quoi") - t_r2, "Quoi que dise\nle fabricant", "le fabricant"),
            (W(19, "c'est") - t_r2, "Au vendeur de prouver\nque c'est ta faute", "Au vendeur"),
        ], y0=300)
        ecrit(ctx, "Code de la consommation, art. L217-3 et L217-7", 540, 1150, 26, (230, 230, 236))

    def s_reparation(ctx, t, lt):
        f_t[0] = t
        D.boutique(ctx, t)
        vendeur.emotion(L(20, 0), "triste").pose(L(20, 0), "repos")
        vendeur.draw(ctx, 760, 1760, 0.9, t)
        D.comptoir(ctx, 760, 1380)
        kev.draw(ctx, 250, 1900, 0.9, t, bouche=bouche(t, "nar"))
        ui.panneau(ctx, 540, 480, "RÉPARATION GRATUITE", lt, rot=-0.04, size=70, fond=(70, 205, 115), bord=INK,
                   col=INK)
        if t >= W(20, "deux") - 0.1:
            ui.panneau(ctx, 560, 640, "290 € ÉCONOMISÉS", t - W(20, "deux") + 0.1, rot=0.04, size=70,
                       fond=(255, 210, 40), bord=INK, col=INK)

    def s_dejeuner(ctx, t, lt, gros=False):
        f_t[0] = t
        L_.salle_a_manger(ctx, t)
        mere.draw(ctx, 180, 1720, 0.75, t)
        pere.draw(ctx, 540, 1700, 0.8, t, bouche=bouche(t, "pere"))
        kev.draw(ctx, 900, 1720, 0.78, t, bouche=bouche(t, "nar"))
        L_.table(ctx, 540, 1250)

    def s_repas(ctx, t, lt):
        s_dejeuner(ctx, t, lt)
        if L(21, 0) <= t < L(22, 0) and t >= W(21, "vol") - 0.1:
            k = ease((t - W(21, "vol") + 0.1) / 1.5)
            L_.avion(ctx, -200 + 1300 * k, 420 - 120 * k, 0.6, rot=-0.1)
            if t >= W(21, "quatre"):
                ui.panneau(ctx, 540, 640, "4 H DE RETARD", t - W(21, "quatre"), rot=-0.04, size=80)
        if L(25, 0) <= t < L(26, 0) and t >= W(25, "quatre") - 0.1:
            ui.panneau(ctx, 540, 560, "2 000 KM → 400 €", t - W(25, "quatre") + 0.1, rot=-0.04, size=80,
                       fond=(70, 205, 115), bord=INK, col=INK)
        if t >= L(26, 0):
            ui.notif(ctx, t - L(26, 0) - 0.6, 540, 300, "Banque", "Virement reçu : + 400,00 €", "Compagnie aérienne",
                     couleur=(40, 110, 200))
            if t >= W(26, "son") - 0.1:
                ui.bulle(ctx, 540, 760, "Tu m'envoies le lien ?", t - W(26, "son") + 0.1, size=50, cote=-1)

    def s_pere(ctx, t, lt):
        f_t[0] = t
        L_.salle_a_manger(ctx, t)
        pere.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "pere"))
        L_.table(ctx, 540, 1420, w=900)
        traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, lt)
        if t >= W(22, "ils"):
            ui.panneau(ctx, 540, 480, "« ILS TE DONNERONT RIEN »", t - W(22, "ils"), rot=0.04, size=60)

    t_r1 = L(24, 0)

    def h_r1(ctx, t, lt):
        ui.carte_regle(ctx, t - t_r1, "RETARD D'AVION ≥ 3 H", [
            (0.15, "Moins de 1 500 km :\n250 €", "250 €"),
            (W(24, "six") - t_r1 - 0.6, "De 1 500 à 3 500 km :\n400 €", "400 €"),
            (W(24, "six") - t_r1, "Plus de 3 500 km :\n600 €", "600 €"),
        ], y0=300)
        ecrit(ctx, "Règlement (CE) 261/2004 · sauf circonstances extraordinaires", 540, 1150, 26, (230, 230, 236))

    def s_total(ctx, t, lt):
        f_t[0] = t
        import decors_ville as V
        V.ville_nuit(ctx, t)
        kev.draw(ctx, 540, 1880, 0.95, t, bouche=bouche(t, "nar"))
        for i, (m, ic) in enumerate(ENV):
            m2 = "400 €" if i == 4 else m
            L_.enveloppe(ctx, 140 + i * 200, 820, 0.5 * back((lt - i * 0.1) / 0.3) if lt > i * 0.1 else 0.001, m2,
                         ic, couleur=(220, 250, 220))
        if t >= W(27, "huit") - 0.1:
            ui.panneau(ctx, 540, 380, "TOTAL : 817 €", t - W(27, "huit") + 0.1, rot=-0.04, size=110,
                       fond=(255, 210, 40), bord=INK, col=INK)

    # ── plans ──
    f.plan(0, s_hook, [(0, 540, 1000, 1.0), (2.5, 560, 1040, 1.06), (5.0, 600, 1000, 1.1)], fouet=False)
    f.plan(L(2, 0), s_quai, [(0, 540, 1050, 1.0), (2.5, 480, 1150, 1.15), (4.5, 400, 1200, 1.25)])
    f.plan(L(3, 0), carte(5, "La garantie 30 minutes", "15 €"), [(0, 540, 900, 1.0), (1.5, 540, 900, 1.1)],
           son="impact")
    f.plan(L(4, 0), s_regle_fond, [(0, 540, 960, 1.0), (3, 620, 1000, 1.25), (6, 480, 930, 1.12), (9, 560, 980, 1.2)],
           hud=h_r5)
    f.plan(L(5, 0), s_form, [(0, 540, 760, 1.0), (2.5, 560, 900, 1.3), (5.0, 520, 1000, 1.2)])
    f.plan(L(6, 0), s_partage, [(0, 540, 760, 1.0), (2.0, 540, 900, 1.25), (4.0, 520, 960, 1.15)])
    f.plan(L(7, 0), s_bureau, [(0, 540, 1100, 1.0), (2.0, 700, 1050, 1.25), (4.0, 760, 1000, 1.35)])
    f.plan(L(8, 0), carte(4, "Les tickets resto périmés", "72 €"), [(0, 540, 900, 1.0), (1.5, 540, 900, 1.1)],
           son="impact")
    f.plan(L(9, 0), s_regle_fond, [(0, 540, 960, 1.0), (3, 620, 1000, 1.25), (6, 480, 930, 1.12), (9, 560, 980, 1.2)],
           hud=h_r4)
    f.plan(L(10, 0), s_tickets, [(0, 540, 760, 1.15), (2.0, 540, 900, 1.0), (3.5, 540, 960, 1.15)])
    f.plan(L(11, 0), s_sofia, [(0, 540, 1100, 1.0), (2.5, 680, 900, 1.25), (5.0, 720, 1000, 1.35)])
    f.plan(L(12, 0), carte(3, "Le plafond des frais bancaires", "40 €"), [(0, 540, 900, 1.0), (1.5, 540, 900, 1.1)],
           son="impact")
    f.plan(L(13, 0), s_regle_fond, [(0, 540, 960, 1.0), (3, 620, 1000, 1.25), (6, 480, 930, 1.12), (9, 560, 980, 1.2)],
           hud=h_r3)
    f.plan(L(14, 0), s_calcul_banque, [(0, 600, 1000, 1.0), (2.0, 680, 860, 1.2), (4.0, 640, 900, 1.1)])
    f.plan(L(15, 0), s_ecran_noir, [(0, *tete(540, 1860, 0.95), 1.4), (2.0, *tete(540, 1860, 0.95), 1.6)])
    f.plan(L(16, 0), s_boutique, [(0, 540, 1100, 1.0), (2.0, 640, 1000, 1.2), (3.5, 700, 950, 1.3)])
    f.plan(L(17, 0), s_abo, [(0, 540, 760, 1.0), (1.5, 540, 860, 1.25), (3.0, 540, 900, 1.15)])
    f.plan(L(18, 0), carte(2, "La garantie légale", "290 €"), [(0, 540, 900, 1.0), (1.5, 540, 900, 1.1)],
           son="impact")
    f.plan(L(19, 0), s_regle_fond, [(0, 540, 960, 1.0), (3, 620, 1000, 1.25), (6, 480, 930, 1.12), (9, 560, 980, 1.2)],
           hud=h_r2)
    f.plan(L(20, 0), s_reparation, [(0, 540, 1000, 1.0), (2.0, 520, 900, 1.15), (4.0, 500, 1000, 1.2)])
    f.plan(L(21, 0), s_repas, [(0, 540, 1100, 1.0), (3.0, 540, 1000, 1.12), (6.0, 700, 1050, 1.25)])
    f.plan(L(22, 0), s_pere, [(0, *tete(540, 1800, 0.95), 1.6), (2.0, *tete(540, 1800, 0.95), 1.85)])
    f.plan(L(23, 0), carte(1, "Le retard d'avion", "jusqu'à 600 €"), [(0, 540, 900, 1.0), (1.5, 540, 900, 1.1)],
           son="impact")
    f.plan(L(24, 0), s_regle_fond, [(0, 540, 960, 1.0), (3, 620, 1000, 1.25), (6, 480, 930, 1.12), (9, 560, 980, 1.2)],
           hud=h_r1)
    f.plan(L(25, 0), s_repas, [(0, 900, 1150, 1.2), (2.5, 700, 1050, 1.1), (5.0, 540, 1000, 1.0)])
    f.plan(L(26, 0), s_repas, [(0, 540, 900, 1.0), (2.0, 560, 980, 1.15), (4.0, 540, 1000, 1.05)])
    f.plan(L(27, 0), s_total, [(0, 540, 1000, 1.0), (2.0, 540, 980, 1.08), (4.0, 540, 960, 1.12)])

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ PAR KÉVIN ET SES PROCHES",
                                       [(0, 0), (W(5, "quinze") + 0.3, 15), (W(10, "soixante") + 0.3, 87),
                                        (W(14, "quarante") + 0.3, 127), (W(20, "deux") + 0.3, 417),
                                        (W(25, "quatre") + 0.3, 817)], apparition=L(2, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(0.15, "pop", 0.4), (0.47, "pop", 0.4), (0.79, "pop", 0.4), (1.11, "pop", 0.4),
                       (1.43, "impact", 0.6), (W(2, "quarante"), "rate", 0.5), (W(5, "quinze"), "succes", 0.6),
                       (L(6, 0), "notif", 0.6), (W(7, "périmés"), "tampon", 0.6), (W(10, "soixante"), "succes", 0.6),
                       (W(11, "cent"), "impact", 0.6), (W(14, "quarante"), "succes", 0.6),
                       (W(15, "vingt"), "rate", 0.5), (W(16, "la"), "pop", 0.5), (L(17, 0) + 0.8, "succes", 0.5),
                       (W(20, "deux"), "succes", 0.7), (L(22, 0), "impact", 0.7), (W(25, "quatre"), "succes", 0.6),
                       (L(26, 0) + 0.6, "notif", 0.8), (W(27, "huit"), "tampon", 0.8)]:
        f.son(tt, son, g)
    f.secousse(L(22, 0), 12)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/liste_remboursements.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_liste"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
