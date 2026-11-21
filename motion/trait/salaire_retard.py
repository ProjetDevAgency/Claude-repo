"""Salaire en retard (script 29, scripts/modele/29_salaire_retard.dial, hook du test T1) en dessin animé, moteur
« trait ». Kévin plombier = Yann, le beau-père patron = Paul K. Voix v4 accélérée à 64 s (réglage par défaut).

    python3 motion/trait/salaire_retard.py                 → output/trait/salaire_retard.mp4
    python3 motion/trait/salaire_retard.py --stills 1,10
"""
import argparse
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_chantier as K  # noqa: E402
import decors_colis as C  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, rrect  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

DIAL = ROOT / "scripts/modele/29_salaire_retard.dial"
VOIX = {"nar": (os.environ.get("YANN_VOICE_ID", voix.YANN), voix.REGLAGES_YANN),
        "pere": (os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT"), voix.REGLAGES_YANN)}

MARQUES = {0: [("quatre-vingt-dix euros", "[{}]")], 2: [("Douze jours", "[{}]"), ("Le loyer rejeté", "{{{}}}")],
           3: [("tout garder par écrit", "[{}]")], 6: [("trois sous", "{{{}}}")], 10: [("Trois sous", "{{{}}}")],
           11: [("des intérêts", "[{}]"), ("mise en demeure écrite", "[{}]")], 12: [("sa mauvaise foi", "[{}]")],
           15: [("6 gars", "[{}]")], 18: [("la même lettre", "[{}]")], 20: [("Quatre-vingt-dix euros", "[{}]")]}


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


KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="uni",
             couleur_haut=(40, 90, 160), bas=(40, 90, 160), chaussures=(60, 50, 40), seed=1)
BEAUPERE = dict(cheveux="chauve", couleur_cheveux=(170, 170, 176), peau=(232, 178, 140), haut="uni",
                couleur_haut=(52, 62, 92), bas=(56, 56, 66), chaussures=(30, 30, 36), moustache=True, seed=12)
GARS = [dict(cheveux="court", couleur_cheveux=(60, 40, 30), peau=(230, 180, 140), haut="uni", couleur_haut=c,
             bas=(70, 70, 80), seed=20 + i) for i, c in enumerate([(230, 140, 40), (90, 150, 90), (160, 60, 60),
                                                                    (90, 90, 160), (200, 190, 60)])]
VIEUX = dict(cheveux="chauve", couleur_cheveux=(200, 200, 204), peau=(214, 160, 120), haut="uni",
             couleur_haut=(120, 110, 90), bas=(70, 70, 80), barbe=True, seed=30)
CLIENT = dict(cheveux="chignon", couleur_cheveux=(120, 80, 50), peau=(240, 196, 160), haut="uni",
              couleur_haut=(200, 120, 160), bas=(80, 80, 110), seed=31)


def construire(work):
    voice, words = voix.build(lignes(), VOIX, work, gap=0.2, cible=voix.CIBLE)
    f = Film(voice, words)

    def L(li, k=0, fin=False):
        ws = [w for w in words if w["line"] == li]
        return ws[k]["t1" if fin else "t0"]

    def W(li, prefixe, n=0, fin=False):
        """Temps du n-ième mot de la réplique li qui commence par `prefixe`."""
        ws = [w for w in words if w["line"] == li and
              re.sub(r"[^\w'-]", "", w["w"].lower()).startswith(prefixe.lower())]
        return ws[n]["t1" if fin else "t0"]

    kev, bp, vieux, cliente = Perso(**KEVIN), Perso(**BEAUPERE), Perso(**VIEUX), Perso(**CLIENT)
    gars = [Perso(**g) for g in GARS]
    kev.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.9, rot=-0.1)
    vieux.objet = lambda ctx, x, y, s: (rrect(ctx, x - 60, y - 40, 120, 50, 20), flat(ctx, (230, 190, 120)))

    # poses et émotions
    bp.pose(0, "mains_hanches").emotion(0, "malin")
    bp.pose(L(5, 0), "haussement").emotion(L(6, 0), "content").emotion(L(8, 0), "colere")
    kev.emotion(0, "content").pose(L(9, 0), "repos").emotion(L(9, 0), "triste")
    kev.emotion(L(11, 0), "neutre").emotion(L(13, 0), "triste")
    kev.pose(L(15, 0), "telephone").emotion(L(15, 0), "malin")
    kev.pose(L(19, 0), "leve").emotion(L(19, 0), "content")
    vieux.pose(0, "objet").emotion(0, "content").emotion(L(17, 0), "choc")
    cliente.emotion(0, "content")
    for g in gars:
        g.emotion(0, "content")
    for g in gars[:3]:
        g.emotion(L(16, 0), "choc")

    def bouche(t, qui):
        return f.bouche(t, qui) * (0.7 if qui == "nar" else 1.0)

    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731

    # ── scènes ──
    def s_hook(ctx, t, lt):
        K._T[0] = t
        K.exterieur(ctx, t, camion_x=760)
        bp.draw(ctx, 420, 1800, 0.95, t, bouche=bouche(t, "pere"))
        ui.badge(ctx, 420, 1800 - 0.95 * 1150, "BEAU-PÈRE ET PATRON", lt - 0.2)
        if t >= W(0, "quatre") - 0.1:
            ui.panneau(ctx, 590, 470, "90 €", t - W(0, "quatre") + 0.1, rot=0.05, size=120, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def ecran_vocal(c, x0, y0, w, h, t):
        y = y0 + 30
        y += C.bulle_msg(c, x0, y, w, "Ce message a été supprimé", False, 1.0, size=32, couleur=(230, 230, 230))
        if t >= W(1, "gardé") - 0.2:
            ecrit(c, "Enregistré par Kévin", x0 + 30, y + 10, 24, (40, 140, 80), ax=0)
            C.vocal(c, x0, y + 30, w, t - W(1, "gardé"), ease((t - W(1, "gardé") + 0.2) / 0.3))

    def ecran_lecture(c, x0, y0, w, h, t):
        y = y0 + 30
        ecrit(c, "Enregistrement du 3 novembre", x0 + 30, y + 10, 26, (90, 90, 100), ax=0)
        C.vocal(c, x0, y + 40, w, t - L(16, 0) + 2, 1.0)
        C.bulle_msg(c, x0, y + 200, w, "Je les paie le 12, ça me fait de la trésorerie.", False,
                    ease((t - L(16, 0)) / 0.4), size=40, couleur=(255, 235, 200))

    def fond_flou(ctx, t, decor):
        decor(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (16, 18, 30), 0.6)

    def s_vocal(ctx, t, lt):
        fond_flou(ctx, t, K.salle_de_bain)
        C.grand_tel(ctx, 540, 900, 0.95, "Beau-père", contenu=lambda c, *a: ecran_vocal(c, *a, t), t=t)

    def s_lecture(ctx, t, lt):
        fond_flou(ctx, t, lambda c, tt: K.exterieur(c, tt, camion_x=760))
        C.grand_tel(ctx, 540, 900, 0.95, "Dictaphone", couleur=(200, 60, 60),
                    contenu=lambda c, *a: ecran_lecture(c, *a, t), t=t)

    def ecran_banque(c, x0, y0, w, h, t):
        jours = min(12, 1 + int(max(0.0, t - L(2, 0)) * 6))
        ecrit(c, "Salaire de novembre", x0 + 40, y0 + 60, 32, INK, ax=0)
        ecrit(c, f"pas reçu · J+{jours}", x0 + 40, y0 + 110, 44, (210, 40, 50), big=True, ax=0)
        if t >= W(2, "loyer") - 0.1:
            k = ease((t - W(2, "loyer") + 0.1) / 0.3)
            rrect(c, x0 + 20, y0 + 200, w - 40, 260, 20)
            flat(c, (255, 235, 235), k)
            ecrit(c, "Prélèvement loyer", x0 + 50, y0 + 250, 32, INK, ax=0, alpha=k)
            ecrit(c, "REJETÉ", x0 + 50, y0 + 310, 56, (210, 40, 50), big=True, ax=0, alpha=k)
            ecrit(c, "Frais de rejet : - 90,00 €", x0 + 50, y0 + 400, 34, (210, 40, 50), ax=0, alpha=k)

    def s_banque(ctx, t, lt):
        fond_flou(ctx, t, K.salle_de_bain)
        C.grand_tel(ctx, 540, 900, 0.95, "Ma banque", couleur=(30, 90, 160),
                    contenu=lambda c, *a: ecran_banque(c, *a, t), t=t)

    def s_sdb(ctx, t, lt):
        K.salle_de_bain(ctx, t)
        kev.draw(ctx, 560, 1800, 0.95, t, bouche=bouche(t, "nar"))
        K.caisse_outils(ctx, 860, 1760, 1.1)
        if t >= W(3, "tout") - 0.1 and t < L(4, 0):
            ui.panneau(ctx, 560, 660, "TOUT GARDER PAR ÉCRIT", t - W(3, "tout") + 0.1, rot=-0.04, size=60,
                       fond=(255, 210, 40), bord=INK, col=INK)

    def s_client(ctx, t, lt):
        K.salle_de_bain(ctx, t)
        cliente.draw(ctx, 220, 1760, 0.85, t)
        bp.draw(ctx, 540, 1760, 0.9, t)
        kev.draw(ctx, 850, 1760, 0.85, t, bouche=0.0)
        ui.panneau(ctx, 760, 600, "« MON FUTUR GENDRE »", lt - 0.3, rot=0.04, size=54)

    def s_arrivee(ctx, t, lt):
        K._T[0] = t
        x = 1500 - 740 * (1 - (1 - min(1.0, lt / 1.2)) ** 3)
        K.exterieur(ctx, t, camion_x=x)
        kev.draw(ctx, 260, 1780, 0.85, t, bouche=bouche(t, "nar"))
        if lt > 1.2:
            bp.draw(ctx, 560, 1780, 0.85, t)

    def s_bp(ctx, t, lt):
        K._T[0] = t
        K.exterieur(ctx, t, camion_x=860)
        for i, g in enumerate(gars[:3]):
            g.draw(ctx, 650 + i * 150, 1480, 0.5, t)
        bp.draw(ctx, 420, 1800, 0.95, t, bouche=bouche(t, "pere"))
        if t >= L(8, 0):
            traits_choc(ctx, 420, 1800 - 0.95 * 880, 160, t - L(8, 0))
        if t >= W(6, "trois") - 0.1 and t < L(7, 0):
            ui.panneau(ctx, 440, 560, "TROIS SOUS ?", t - W(6, "trois") + 0.1, rot=-0.05, size=70)
        if t >= W(8, "ma") - 0.05 and t < L(9, 0):
            ui.panneau(ctx, 430, 560, "« MA FILLE PAIE POUR TOI »", t - W(8, "ma") + 0.05, rot=0.04, size=40)

    def s_camion(ctx, t, lt):
        K._T[0] = t
        K.exterieur(ctx, t, camion_x=620)
        bp.draw(ctx, 300, 1760, 0.85, t)

    def s_kev_silence(ctx, t, lt):
        K.salle_de_bain(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t)
        K.caisse_outils(ctx, 760, 1640 - 120 * ease((t - W(9, "je")) / 0.6), 1.0)

    def s_echo(ctx, t, lt):
        D.fond_sombre(ctx, t, (40, 30, 30))
        K.pieces(ctx, 540, 1000, t, 7)
        ecrit(ctx, "3 SOUS", 540, 760, 160, (255, 210, 40), big=True, scale=back(lt / 0.3))

    t_carte = L(11, 0)

    def s_regle(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))

    def h_regle(ctx, t, lt):
        ui.carte_regle(ctx, t - t_carte, "LA RÈGLE", [
            (0.15, "Salaire en retard :\ndes intérêts", "des intérêts"),
            (W(11, "dès") - t_carte, "Dès la mise en demeure\nécrite, automatique", "mise en demeure"),
            (W(12, "il") - t_carte, "Frais de banque :\npréjudice à part", "préjudice"),
            (W(12, "et") - t_carte, "+ sa mauvaise foi\nà prouver", "mauvaise foi"),
        ], y0=300)
        ecrit(ctx, "Code civil, art. 1231-6 · Cass. soc. 6 mai 2025, n° 23-17.005", 540, 1150, 26,
              (230, 230, 236))

    def s_doute(ctx, t, lt):
        K.salle_de_bain(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"))
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (30, 20, 70), 0.3)

    def s_pause(ctx, t, lt):
        K._T[0] = t
        K.exterieur(ctx, t, camion_x=760)
        for i, g in enumerate(gars):
            g.draw(ctx, 520 + (i % 3) * 170, 1560 + (i // 3) * 140, 0.55, t)
        vieux.draw(ctx, 980, 1640, 0.6, t)
        kev.draw(ctx, 220, 1800, 0.9, t, bouche=bouche(t, "nar"))
        if t >= W(15, "6"):
            ui.panneau(ctx, 560, 640, "6 GARS", t - W(15, "6"), rot=-0.04, size=80, fond=(255, 210, 40), bord=INK,
                       col=INK)

    def s_vieux(ctx, t, lt):
        K._T[0] = t
        K.exterieur(ctx, t, camion_x=760)
        vieux.draw(ctx, 540, 1800, 0.95, t)
        traits_choc(ctx, 540, 1800 - 0.95 * 880, 160, lt)

    def ecran_appel(c, x0, y0, w, h, t):
        ecrit(c, "Appel en cours · 0:42", x0 + w / 2, y0 + 60, 30, (90, 90, 100))
        if t >= W(18, "6") - 0.2:
            C.bulle_msg(c, x0, y0 + 140, w, "Les 6 gars ont envoyé la même lettre !", False,
                        ease((t - W(18, "6") + 0.2) / 0.3), size=40)

    def s_soir(ctx, t, lt):
        fond_flou(ctx, t, C.chambre)
        if t < W(18, "sauf"):
            C.grand_tel(ctx, 540, 900, 0.95, "Léa", couleur=(200, 80, 140),
                        contenu=lambda c, *a: ecran_appel(c, *a, t), t=t)
        else:
            K.lettres(ctx, 540, 1150, 6, 1.4)
            ui.panneau(ctx, 540, 520, "TOUT PAR ÉCRIT", t - W(18, "sauf"), rot=-0.04, size=80, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def h_paie(ctx, t, lt):
        ui.notif(ctx, lt - 0.1, 540, 330, "Ma banque", "Salaire reçu + 90,00 €", "Remboursement des frais de rejet",
                 couleur=(30, 90, 160))

    def s_final(ctx, t, lt):
        K.salle_de_bain(ctx, t)
        kev.draw(ctx, 540, 1800, 0.95, t, bouche=bouche(t, "nar"))
        if t >= L(20, 0):
            ui.panneau(ctx, 540, 520, "90 €", t - L(20, 0), rot=-0.04, size=130, fond=(255, 210, 40), bord=INK,
                       col=INK)

    # ── plans ──
    f.plan(0, s_hook, [(0, *tete(420, 1800, 0.95), 1.45), (2.0, *tete(420, 1800, 0.95), 1.6)], fouet=False)
    f.plan(L(1, 0), s_vocal, [(0, 540, 860, 1.05), (2.0, 540, 900, 1.3)])
    f.plan(L(2, 0), s_banque, [(0, 540, 820, 1.05), (2.5, 540, 900, 1.3)])
    f.plan(L(3, 0), s_sdb, [(0, 700, 1000, 1.3), (2.0, 560, 1100, 1.05), (4.0, 560, 1060, 1.2)])
    f.plan(L(4, 0), s_client, [(0, 540, 1100, 1.05), (2.0, 540, 1080, 1.15)])
    f.plan(L(5, 0), s_arrivee, [(0, 540, 1150, 1.0), (3.0, 500, 1100, 1.15)])
    f.plan(L(6, 0), s_bp, [(0, *tete(420, 1800, 0.95), 1.7), (2.0, *tete(420, 1810, 0.95), 1.85)])
    f.plan(L(7, 0), s_camion, [(0, 460, 1150, 1.1), (2.0, 460, 1130, 1.2)])
    f.plan(L(8, 0), s_bp, [(0, *tete(420, 1790, 0.95), 1.95), (2.0, *tete(420, 1800, 0.95), 2.1)])
    f.plan(L(9, 0), s_kev_silence, [(0, *tete(540, 1800, 0.95), 1.9), (1.5, *tete(540, 1800, 0.95), 2.05)])
    f.plan(L(10, 0), s_echo, [(0, 540, 960, 1.0), (1.2, 540, 960, 1.1)])
    f.plan(L(11, 0), s_regle, [(0, 540, 960, 1.0), (3, 620, 1010, 1.3), (6, 480, 930, 1.12), (9, 560, 980, 1.25)], hud=h_regle)
    f.plan(L(13, 0), s_doute, [(0, 540, 1150, 1.0), (2.0, *tete(540, 1800, 0.95), 1.7), (5.0, *tete(560, 1800, 0.95), 2.0)])
    f.plan(L(15, 0), s_pause, [(0, 560, 1200, 1.0), (2.5, 600, 1200, 1.1)])
    f.plan(L(16, 0), s_lecture, [(0, 540, 820, 1.05), (2.0, 540, 900, 1.3)])
    f.plan(L(17, 0), s_vieux, [(0, *tete(540, 1800, 0.95), 1.8), (1.0, *tete(540, 1800, 0.95), 1.95)])
    f.plan(L(18, 0), s_soir, [(0, 540, 860, 1.05), (4.0, 540, 900, 1.25)])
    f.plan(L(19, 0), s_final, [(0, 540, 1100, 1.0), (1.5, 540, 1090, 1.08)], hud=h_paie)
    f.plan(L(20, 0), s_final, [(0, *tete(540, 1800, 0.95), 1.5), (2.0, *tete(540, 1800, 0.95), 1.65)])

    # ── compteur, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "RÉCUPÉRÉ PAR KÉVIN", [(0, 0), (L(19, 0) + 0.3, 90)],
                                       apparition=L(1, 0)))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for tt, son, g in [(W(0, "quatre"), "pop", 0.7), (L(1, 0), "notif", 0.6), (W(2, "loyer"), "rate", 0.7),
                       (W(3, "tout"), "pop", 0.5), (L(4, 0) + 0.3, "pop", 0.5), (L(5, 0), "whoosh", 0.4),
                       (W(6, "trois"), "impact", 0.7), (L(8, 0), "impact", 0.8), (L(10, 0), "ticks", 0.5),
                       (W(11, "dès"), "pop", 0.5), (W(12, "il"), "pop", 0.5), (W(12, "et"), "pop", 0.5),
                       (W(15, "6"), "pop", 0.6), (L(16, 0), "notif", 0.6), (L(17, 0), "impact", 0.6),
                       (W(18, "sauf"), "tampon", 0.7), (L(19, 0), "succes", 0.8), (L(20, 0), "succes", 0.5)]:
        f.son(tt, son, g)
    f.secousse(L(8, 0), 14)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/salaire_retard.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_salaire"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
