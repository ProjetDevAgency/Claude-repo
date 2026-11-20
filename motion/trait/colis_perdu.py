"""Colis jamais reçu (script 28, scripts/modele/28_colis_perdu.dial, méthode d'écriture du compte, 8/8, loi vérifiée)
mis en dessin animé avec le moteur « trait ». Kévin = Yann, le père = Paul K. Voix v4 accélérée à 64 s (réglage par défaut).

    python3 motion/trait/colis_perdu.py                 → output/trait/colis_perdu.mp4
    python3 motion/trait/colis_perdu.py --stills 1,10
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
import decors_piscine as P  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, rrect  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/28_colis_perdu.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "pere": (os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT"), voix.REGLAGES_YANN)}   # Paul K

# marques de couleur des sous-titres : [jaune] {rouge}. Le texte, lui, est celui du .dial, mot pour mot (vérifié).
MARQUES = {0: [("mille deux cents euros", "[{}]")], 2: [("livré", "[{}]"), ("personne a sonné", "{{{}}}")],
           5: [("Sonnez fort", "[{}]")], 7: [("petits dessins", "{{{}}}")], 11: [("petits dessins", "{{{}}}")],
           13: [("le risque est pour le vendeur", "[{}]")], 14: [("prouver", "[{}]"), ("il rembourse", "[{}]")],
           17: [("le site rembourse", "[{}]"), ("14 personnes", "[{}]")], 20: [("Mille deux cents euros", "[{}]")]}


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


KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
PERE = dict(cheveux="court", couleur_cheveux=(150, 150, 156), peau=(220, 160, 120), haut="uni",
            couleur_haut=(130, 90, 60), bas=(60, 60, 72), chaussures=(40, 36, 40), moustache=True, lunettes=True,
            seed=10)
COLLEGUE = dict(cheveux="chignon", couleur_cheveux=(90, 60, 40), peau=(236, 190, 156), haut="uni",
                couleur_haut=(60, 140, 150), bas=(50, 50, 70), seed=11)


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.15, cible=voix.CIBLE)   # silences serrés : dialogue
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        """Temps du k-ième mot de la réplique li (0 = 1re réplique du .dial)."""
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    kev, pere, coll = Perso(**KEVIN), Perso(**PERE), Perso(**COLLEGUE)
    kev.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)
    pere.objet = lambda ctx, x, y, s: (D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1) if pose_pere(f_t[0]) != "devis"
                                       else devis(ctx, x, y - 120))
    f_t = [0.0]

    def devis(ctx, x, y):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.05)
        rrect(ctx, -130, -170, 260, 340, 6)
        from dessin import paint
        paint(ctx, (252, 252, 248), 5, shade=0.95)
        ecrit(ctx, "DEVIS", 0, -120, 46, INK, big=True)
        ecrit(ctx, "Kévin, graphiste", 0, -70, 22, INK)
        C.croissant(ctx, 0, 20, 0.5)
        ctx.restore()

    def pose_pere(t):
        return "devis" if L(4, 0) <= t < L(5, 0) else "tel"

    # ── poses et émotions ──
    pere.pose(0, "telephone").emotion(0, "malin")
    pere.pose(L(4, 0), "objet").emotion(L(4, 0), "content")
    pere.pose(L(7, 0), "telephone").emotion(L(7, 0), "content").emotion(L(9, 0), "colere")
    pere.pose(L(18, 0), "repos").emotion(L(18, 0), "triste")
    kev.pose(0, "telephone").emotion(0, "choc").emotion(L(3, 0), "content").pose(L(3, 0), "repos")
    kev.emotion(L(9, 7), "triste").emotion(L(16, 0), "triste")
    kev.pose(L(17, 0), "leve").emotion(L(17, 0), "content").pose(L(20, 0), "telephone")
    coll.emotion(0, "content")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    # ── scènes ──
    def s_pere(ctx, t, lt):
        f_t[0] = t
        C.cuisine(ctx, t)
        pere.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "pere"))
        if t >= L(0, 3) and t < L(1, 0):
            ui.panneau(ctx, 540, 1800 - 0.95 * 1180, "1 200 €", t - L(0, 3), rot=-0.04, size=110,
                       fond=(255, 210, 40), bord=INK, col=INK)
        if L(7, 7) <= t < L(8, 0):
            ui.panneau(ctx, 560, 760, "DES PETITS DESSINS", t - L(7, 7), rot=0.04, size=70)
        if L(8, 0) <= t < L(9, 0):
            ui.panneau(ctx, 760, 420, "+ 1 HEURE", t - L(8, 0), rot=0.05, size=64, fond=(255, 210, 40), bord=INK,
                       col=INK)
        if L(9, 0) <= t < L(10, 0):
            traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, t - L(9, 0))

    def ecran_papa(c, x0, y0, w, h, t):
        y = y0 + 30
        y += C.bulle_msg(c, x0, y, w, "Tu me dois 1 200 € pour un ordi que t'es même pas capable de réceptionner.",
                         False, ease((t - L(0, 9) + 0.3) / 0.3))
        if t >= L(6, 3):
            y += C.bulle_msg(c, x0, y, w, "Papa, je te rembourse avec la mission", True, ease((t - L(6, 3)) / 0.3))
        if t >= L(6, 10):
            y += C.vocal(c, x0, y, w, t - L(6, 10), ease((t - L(6, 10)) / 0.3))
        if t >= L(18, 10):
            C.bulle_msg(c, x0, y + 20, w, "Et pour le colis de ta mère, on fait comment ?", False,
                        ease((t - L(18, 10)) / 0.3), size=40)

    def fond_flou(ctx, t, decor):
        decor(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)

    def s_tel_papa(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Papa", contenu=lambda c, *a: ecran_papa(c, *a, t), t=t)

    def s_kevin(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"), regard=0.2)
        if L(1, 0) <= t < L(2, 0):
            traits_choc(ctx, 540, 1800 - 0.95 * 880, 150, t - L(1, 0))

    def ecran_suivi(c, x0, y0, w, h, t):
        etapes = [("Commandé", True), ("Expédié", True), ("En cours de livraison", True), ("LIVRÉ  14 h 00", True)]
        for i, (lab, _) in enumerate(etapes):
            y = y0 + 80 + i * 160
            vis = i < 3 or t >= L(2, 8)
            col = (40, 170, 90) if vis else (200, 200, 206)
            from dessin import circle
            circle(c, x0 + 80, y, 34)
            flat(c, col)
            if i < 3:
                c.rectangle(x0 + 76, y + 34, 8, 92)
                flat(c, col)
            ecrit(c, lab, x0 + 140, y, 40 if i == 3 else 34, INK if vis else (160, 160, 168), ax=0, big=(i == 3))
        if t >= L(2, 12):
            ui.panneau(c, x0 + w / 2, y0 + 760, "PERSONNE A SONNÉ", t - L(2, 12), rot=-0.05, size=52, s=1)
        if L(14, 0) <= t < L(14, 8):
            ecrit(c, "?", x0 + w - 90, y0 + 560, 220, (232, 52, 60), big=True, scale=back((t - L(14, 0)) / 0.3))

    def s_suivi(ctx, t, lt):
        fond_flou(ctx, t, C.palier)
        C.grand_tel(ctx, 540, 900, 0.95, "Suivi de colis", couleur=(40, 110, 200),
                    contenu=lambda c, *a: ecran_suivi(c, *a, t), t=t)

    def s_palier(ctx, t, lt):
        C.palier(ctx, t, mot=t >= L(5, 0), colis=0)

    def s_bureau_kev(ctx, t, lt):
        f_t[0] = t
        C.chambre(ctx, t)
        kev.draw(ctx, 540, 1900, 1.0, t, bouche=bouche(t, "nar"))
        C.bureau_vide(ctx, t, 540, 1330)
        for t0, t1 in ((L(3, 0), L(4, 0)), (L(15, 0), 1e9)):
            if t0 <= t < t1:
                D.calendrier(ctx, 850, 520, 0.9 * back((t - t0) / 0.3), "1re MISSION", "LUN")

    def s_bureau_pere(ctx, t, lt):
        f_t[0] = t
        P.bureau(ctx, t)
        coll.draw(ctx, 780, 1740, 0.85, t)
        pere.draw(ctx, 330, 1740, 0.9, t, regard=0.5)

    def s_echo(ctx, t, lt):
        C.chambre(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (10, 10, 30), 0.35)
        ctx.save()
        ctx.translate(540, 960)
        ctx.rotate(-0.05)
        rrect(ctx, -380, -260, 760, 520, 8)
        from dessin import paint
        paint(ctx, (250, 250, 245), 6, shade=1)
        C.croissant(ctx, 0, 0, 2.2)
        ecrit(ctx, "BOULANGERIE", 0, 190, 64, INK, big=True)
        ctx.restore()

    def ecran_site(c, x0, y0, w, h, t):
        y = y0 + 30
        y += C.bulle_msg(c, x0, y, w, "Bonjour, mon colis est marqué livré mais j'ai rien reçu.", True, 1.0)
        C.bulle_msg(c, x0, y, w, "Voyez avec le transporteur.", False, ease((t - L(12, 7)) / 0.3), size=44,
                    couleur=(255, 220, 220))

    def s_site(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "MégaShop · aide", couleur=(200, 70, 60),
                    contenu=lambda c, *a: ecran_site(c, *a, t), t=t)

    t_carte = L(13, 0)

    def s_regle(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))

    def h_regle(ctx, t, lt):
        ui.carte_regle(ctx, t - t_carte, "LA RÈGLE", [
            (0.15, "Achat à distance", "à distance"),
            (L(13, 11) - t_carte, "Pas de colis en main ?\nRisque pour le vendeur", "le vendeur"),
            (L(14, 8) - t_carte, "Au vendeur de prouver\nla livraison", "prouver"),
            (L(14, 17) - t_carte, "Sinon, il rembourse", "rembourse"),
        ], y0=300)
        ecrit(ctx, "Code de la consommation, art. L216-4 et L221-15", 540, 1150, 30, (230, 230, 236))

    def ecran_mail(c, x0, y0, w, h, t):
        k = ease((t - L(15, 4)) / 1.2)
        lignes_mail = ["À : service client MégaShop", "Objet : colis jamais reçu", "",
                       "Colis marqué livré, jamais reçu.", "Art. L216-4 : le risque reste", "au vendeur.",
                       "Merci de me rembourser."]
        for i, l in enumerate(lignes_mail[:int(len(lignes_mail) * k) + 1]):
            ecrit(c, l, x0 + 40, y0 + 70 + i * 70, 32, INK, ax=0)
        if t >= L(15, 6, fin=True):
            ui.panneau(c, x0 + w - 150, y0 + 780, "ENVOYÉ", t - L(15, 6, fin=True), rot=0.06, size=50,
                       fond=(70, 205, 115), bord=INK, col=INK)

    def s_mail(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Nouveau mail", couleur=(60, 90, 170),
                    contenu=lambda c, *a: ecran_mail(c, *a, t), t=t)

    def s_kevin_rembourse(ctx, t, lt):
        s_kevin(ctx, t, lt)

    def h_rembourse(ctx, t, lt):
        ui.notif(ctx, t - L(17, 0) - 0.2, 540, 330, "MégaShop", "Remboursement effectué", "1 200,00 € sur ton compte",
                 couleur=(200, 70, 60))

    def ecran_groupe(c, x0, y0, w, h, t):
        y = y0 + 30
        k = ease((t - L(17, 4)) / 0.3)
        if k > 0:
            from dessin import paint
            sc = back(k)
            c.save()
            c.translate(x0 + w - 40, y)
            c.scale(sc, sc)
            rrect(c, -420, 0, 420, 330, 24)
            flat(c, (210, 246, 200))
            rrect(c, -400, 20, 380, 140, 12)
            paint(c, (255, 255, 255), 3, shade=1)
            ecrit(c, "Remboursé 1 200 €", -210, 90, 32, (40, 150, 80), big=True)
            rrect(c, -400, 175, 380, 130, 12)
            flat(c, (255, 255, 255))
            ecrit(c, "Papa : t'es même pas capable", -390, 220, 22, INK, ax=0)
            ecrit(c, "de réceptionner.", -390, 260, 22, INK, ax=0)
            c.restore()
            y += 350
        for i, (nom, txt) in enumerate([("Tata Sophie", "Ah quand même !"), ("Tonton Marc", "Bien joué Kévin"),
                                         ("Mamie", "Il a raison le petit")]):
            ti = L(17, 16) + 0.5 + i * 0.5
            if t >= ti:
                ecrit(c, nom, x0 + 30, y + 14, 22, (200, 80, 120), ax=0)
                y += 26 + C.bulle_msg(c, x0, y + 20, w, txt, False, ease((t - ti) / 0.3), size=32)

    def s_groupe(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        C.grand_tel(ctx, 540, 900, 0.95, "Famille (14)", contenu=lambda c, *a: ecran_groupe(c, *a, t), t=t)
        if t >= L(17, 16):
            ui.panneau(ctx, 540, 1250, "14 PERSONNES", t - L(17, 16), rot=-0.04, size=70, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def s_pere_silence(ctx, t, lt):
        f_t[0] = t
        C.cuisine(ctx, t * 4)                       # l'horloge file : la journée passe
        pere.draw(ctx, 540, 1800, 0.95, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (40, 30, 80), 0.25 * ease(lt / 2.0))

    def s_colis(ctx, t, lt):
        f_t[0] = t
        n = min(11, 1 + int(max(0.0, t - L(19, 0)) / 0.32))
        C.palier(ctx, t, mot=True, colis=n)
        kev.draw(ctx, 900, 1780, 0.75, t, bouche=bouche(t, "nar"))

    def s_final(ctx, t, lt):
        f_t[0] = t
        C.palier(ctx, t, mot=True, colis=11)
        kev.draw(ctx, 600, 1800, 0.95, t, bouche=bouche(t, "nar"))
        ui.panneau(ctx, 600, 560, "1 200 €", t - L(20, 0), rot=-0.04, size=120, fond=(255, 210, 40), bord=INK, col=INK)

    # ── plans ──
    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731
    f.plan(0, s_pere, [(0, *tete(540, 1800, 0.95), 1.55), (2.0, *tete(540, 1810, 0.95), 1.7)], fouet=False)
    f.plan(L(0, 9), s_tel_papa, [(0, 540, 860, 1.1), (1.5, 540, 780, 1.4)])
    f.plan(L(1, 0), s_kevin, [(0, *tete(540, 1800, 0.95), 1.7), (2.0, *tete(540, 1810, 0.95), 1.85)])
    f.plan(L(2, 0), s_suivi, [(0, 540, 900, 1.0), (2.0, 540, 940, 1.3)])
    f.plan(L(2, 12), s_palier, [(0, 560, 1000, 1.05), (1.5, 560, 1020, 1.12)])
    f.plan(L(3, 0), s_bureau_kev, [(0, 560, 1080, 1.1), (2.5, 560, 1100, 1.2)])
    f.plan(L(4, 0), s_bureau_pere, [(0, 540, 1150, 1.1), (2.5, 520, 1120, 1.2)])
    f.plan(L(5, 0), s_palier, [(0, 540, 760, 1.6), (2.0, 540, 760, 1.75)])
    f.plan(L(6, 0), s_tel_papa, [(0, 540, 800, 1.05), (2.0, 540, 900, 1.3)])
    f.plan(L(7, 0), s_pere, [(0, *tete(540, 1800, 0.95), 1.6), (2.0, *tete(540, 1810, 0.95), 1.7)])
    f.plan(L(8, 0), s_pere, [(0, 430, 320, 2.2), (1.2, 430, 320, 2.4)])
    f.plan(L(9, 0), s_pere, [(0, *tete(540, 1790, 0.95), 1.9), (1.0, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(9, 7), s_kevin, [(0, 540, 1150, 0.95), (1.5, 540, 1150, 1.0)])
    f.plan(L(10, 0), s_kevin, [(0, *tete(540, 1800, 0.95), 2.1), (1.0, *tete(540, 1800, 0.95), 2.2)])
    f.plan(L(11, 0), s_echo, [(0, 540, 960, 1.0), (1.2, 540, 960, 1.1)])
    f.plan(L(12, 0), s_site, [(0, 540, 820, 1.05), (2.5, 540, 900, 1.35)])
    f.plan(L(13, 0), s_regle, [(0, 540, 960, 1.0), (5, 600, 1000, 1.25)], hud=h_regle)
    f.plan(L(14, 0), s_suivi, [(0, 540, 760, 1.3), (1.5, 540, 760, 1.36)])
    f.plan(L(14, 8), s_regle, [(0, 480, 920, 1.25), (4, 540, 960, 1.0)], hud=h_regle)
    f.plan(L(15, 0), s_bureau_kev, [(0, 700, 760, 1.5), (1.2, 700, 760, 1.6)])
    f.plan(L(15, 4), s_mail, [(0, 540, 820, 1.05), (1.5, 540, 900, 1.3)])
    f.plan(L(16, 0), s_kevin, [(0, 600, 1000, 1.2), (3.0, 620, 980, 1.35)])
    f.plan(L(17, 0), s_kevin_rembourse, [(0, 540, 1100, 1.0), (1.5, 540, 1090, 1.08)], hud=h_rembourse)
    f.plan(L(17, 4), s_groupe, [(0, 540, 820, 1.05), (3.0, 540, 960, 1.3)])
    f.plan(L(18, 0), s_pere_silence, [(0, 500, 1000, 1.1), (2.0, 480, 900, 1.25)])
    f.plan(L(18, 6), s_tel_papa, [(0, 540, 700, 1.25), (2.0, 540, 820, 1.55)])
    f.plan(L(19, 0), s_colis, [(0, 560, 1250, 1.0), (2.5, 560, 1250, 1.08)])
    f.plan(L(20, 0), s_final, [(0, 600, 1000, 1.25), (2.0, 600, 990, 1.35)])

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "REMBOURSÉ À KÉVIN", [(0, 0), (L(17, 3), 1200)],
                                       apparition=L(1, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(L(0, 3), "pop", 0.7), (L(0, 9), "notif", 0.8), (L(2, 8), "pop", 0.6), (L(2, 12), "rate", 0.6),
                       (L(5, 4), "pop", 0.6), (L(6, 3), "notif", 0.6), (L(6, 10), "notif", 0.6),
                       (L(7, 7), "impact", 0.7), (L(9, 0), "impact", 0.8), (L(12, 7), "rate", 0.6),
                       (L(13, 11), "pop", 0.5), (L(14, 8), "pop", 0.5), (L(14, 17), "pop", 0.5),
                       (L(15, 6), "tampon", 0.6), (L(17, 0) + 0.2, "succes", 0.8), (L(17, 3), "ticks", 0.6),
                       (L(17, 16), "pop", 0.7), (L(18, 10), "notif", 0.8), (L(20, 0), "succes", 0.6)]:
        f.son(tt, son, g)
    for i in range(10):
        f.son(L(19, 0) + 0.32 * (i + 1), "pop", 0.3)
    f.secousse(L(9, 0), 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/colis_perdu.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_colis"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
