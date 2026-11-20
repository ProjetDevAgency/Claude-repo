"""VERSION COURTE DE COMPARAISON (script raccourci à 1 158 caractères, voix à vitesse normale). La référence est
piscine_dauphin.py.

Histoire du pisciniste (script écrit avec la machine à sujets + le moteur H1, scripts/trait/piscine_dauphin_court.txt),
mise en dessin animé avec le moteur « trait », voix ElevenLabs « Yann ».

    python3 motion/trait/piscine_dauphin.py                    → output/trait/piscine_dauphin.mp4
    python3 motion/trait/piscine_dauphin.py --stills 1,10,30
"""
import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import decors_piscine as P  # noqa: E402
import decors_ville as V  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, flat, halo, rrect, stroke  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

YANN = os.environ.get("YANN_VOICE_ID", "nr2EGJNe96rzn9FRlTId")          # « Yann » dans ElevenLabs
VOIX = {"nar": (YANN, {"stability": 0.5, "similarity_boost": 0.75})}   # vitesse normale, aucun réglage d'émotion

# Le texte est celui de scripts/trait/piscine_dauphin_court.txt (vérifié par pipeline.script verifier),
# avec seulement les marques de couleur des sous-titres : [jaune] {rouge}.
LIGNES = [
    "[Six mille euros], c'est ce qu'une dame de [quatre-vingt-un ans] m'a payé pour remplir une piscine abandonnée.",
    "Vide depuis vingt ans, et elle se baigne même plus.",
    "Un bassin carrelé à la main, des feuilles jusqu'aux genoux, une {fissure} sur tout le fond.",
    "Elle veut que ce soit fini pour le [quatorze juillet]. "
    "Et elle me dit juste, le [dauphin] au fond, vous y touchez pas.",
    "Le deuxième jour, c'est son fils qui m'appelle. Il me fait, six mille balles pour un trou "
    "où personne va nager, t'as pas honte de {plumer une vieille}. Et avant de raccrocher il ajoute, "
    "ma mère sait même plus quel jour on est.",
    "Je dis rien. Je redescends dans le bassin.",
    "{Plumer une vieille.}",
    "Ce que les gens savent pas, c'est qu'un bassin vide depuis vingt ans, {ça bouge.}",
    "Mais alors pourquoi payer tout ça pour une eau où elle ira jamais ? Peut-être qu'il avait raison.",
    "Le quatorze juillet, le fils débarque avec une petite de [sept ans.] "
    "Il s'arrête au bord, il voit le dauphin, et il dit plus rien. "
    "Sa mère me glisse, c'est lui qui l'a posé avec son père, à l'âge de sa fille. "
    "Il était pas revenu depuis {l'enterrement.}",
    "Elle savait très bien quel jour on était.",
    "[Six mille euros] pour revoir son fils.",
]

MOI = dict(cheveux="court", couleur_cheveux=(96, 62, 40), peau=(236, 184, 146), haut="polo",
           couleur_haut=(40, 120, 200), bas=(50, 60, 84), chaussures=(240, 240, 240), seed=4)
DAME = dict(cheveux="chignon", couleur_cheveux=(206, 206, 212), peau=(242, 200, 170), haut="uni",
            couleur_haut=(170, 110, 170), bas=(90, 80, 110), chaussures=(230, 230, 236), lunettes=True, seed=5)
FILS = dict(cheveux="court", couleur_cheveux=(52, 38, 32), peau=(230, 180, 140), haut="chemise",
            couleur_haut=(214, 224, 238), bas=(40, 44, 62), chaussures=(30, 30, 36), barbe=True, seed=6)
PETITE = dict(cheveux="chignon", couleur_cheveux=(110, 70, 40), peau=(236, 186, 150), haut="uni",
              couleur_haut=(250, 200, 60), bas=(230, 120, 150), chaussures=(255, 255, 255), seed=7)
PERE = dict(cheveux="court", couleur_cheveux=(70, 50, 40), peau=(230, 180, 140), haut="uni",
            couleur_haut=(60, 90, 140), bas=(60, 90, 140), moustache=True, seed=8)
GAMIN = dict(cheveux="court", couleur_cheveux=(52, 38, 32), peau=(230, 180, 140), haut="uni",
             couleur_haut=(230, 80, 70), bas=(60, 70, 110), seed=9)


def construire(work):
    voice, words = voix.build([("nar", l) for l in LIGNES], VOIX, work, model="eleven_v4", gap=0.3)
    f = Film(voice, words)
    T = f.t
    moi, dame, fils, petite = Perso(**MOI), Perso(**DAME), Perso(**FILS), Perso(**PETITE)
    pere, gamin = Perso(**PERE), Perso(**GAMIN)

    # qui parle quand (les répliques citées font bouger la bouche du personnage)
    PAROLE = {
        "dame": [(T("juste") + 0.25, T("pas", 0, fin=True)), (T("c'est", 3), T("fille", 0, fin=True))],
        "fils": [(T("six", 1), T("vieille", 0, fin=True)), (T("mère") - 0.25, T("est", 0, fin=True))],
    }

    def bouche(t, qui):
        if qui == "moi":
            if any(a <= t <= b for r in PAROLE.values() for a, b in r):
                return 0.0
            return f.bouche(t, "nar") * 0.8
        return f.bouche(t, "nar") if any(a <= t <= b for a, b in PAROLE[qui]) else 0.0

    # ── poses et émotions ──
    t_app, t_2j = T("veut"), T("deuxième")
    dame.pose(0, "objet").emotion(0, "content")
    dame.pose(t_app, "oreille").emotion(t_app, "neutre")
    dame.pose(T("Mais"), "repos").emotion(T("glisse"), "content").emotion(T("savait"), "malin")

    def objet_dame(ctx, x, y, s):
        if f_now[0] < t_app:
            P.cheque(ctx, x, y - 175, 0.95)
        else:
            D.telephone(ctx, x + 35, y - 95, 0.7, rot=0.35)
    dame.objet = objet_dame
    fils.objet = lambda ctx, x, y, s: D.telephone(ctx, x + 35, y - 95, 0.7, rot=0.35)
    fils.pose(0, "oreille").emotion(0, "colere").emotion(T("raccrocher"), "malin")
    fils.pose(T("fils", 1), "repos").emotion(T("fils", 1), "colere").emotion(T("bord"), "neutre")
    fils.emotion(T("rien", 1), "triste")
    moi.emotion(0, "neutre").emotion(T("Je"), "triste").emotion(T("savent"), "neutre")
    moi.emotion(T("Mais"), "triste").emotion(T("fils", 1), "neutre").emotion(T("Six", 2), "content")
    petite.emotion(0, "content").pose(T("Six", 2), "leve")
    gamin.pose(0, "objet").emotion(0, "content")
    gamin.objet = lambda ctx, x, y, s: (rrect(ctx, x - 40, y - 40, 80, 80, 8), flat(ctx, (40, 120, 220)))
    f_now = [0.0]

    # ── état de la piscine dans le temps ──
    Tsav, Tv, Tm = T("savent"), T("vingt", 1), T("Mais")

    def etat(t, **forcer):
        e = dict(feuilles=1.0 - ease((t - T("redescends")) / (T("savent") - T("redescends"))) if t < T("savent")
                 else 0.0,
                 fissure=ease((t - T("fissure")) / 0.9),
                 resine=ease((t - Tv) / 0.7),                       # réparation en accéléré sur « ça bouge »
                 eau=0.95 * ease((t - Tv - 0.6) / max(0.8, Tm - Tv - 0.6)) + 0.05 * ease((t - Tm) / 3),
                 propre=ease((t - Tv - 1.0) / 1.2))
        e.update(forcer)
        return e

    def jardin(ctx, t, cast=(), soir=0.0, devant=None, **forcer):
        f_now[0] = t
        P.jardin(ctx, t, soir)
        P.piscine(ctx, t, **etat(t, **forcer))
        for p, x, y, s, qui in cast:
            p.draw(ctx, x, y, s, t, bouche=bouche(t, qui) if qui else 0.0)
        if devant:
            devant(ctx, t)
        if soir:
            ctx.rectangle(-600, -600, 2400, 3200)
            flat(ctx, (30, 20, 70), 0.3 * soir)

    # ── scènes ──
    def s_dame(ctx, t, lt):
        jardin(ctx, t, [(dame, 540, 1780, 0.92, "dame")])
        if t >= T("quatre"):
            ui.badge(ctx, 540, 1780 - 0.92 * 1150, "81 ANS", t - T("quatre"))

    def s_piscine_large(ctx, t, lt):
        jardin(ctx, t, [(dame, 150, 1660, 0.6, "dame")], fissure=0.0)
        if t >= T("Vide"):
            ui.panneau(ctx, 560, 1010, "VIDE DEPUIS 20 ANS", t - T("Vide"), rot=-0.04, size=64)

    def s_bassin(ctx, t, lt):
        jardin(ctx, t, [(moi, 700, 1390, 0.5, "moi")],
               devant=lambda c, tt: P.tas_feuilles(c, 700, 1395, 190, tt))

    def s_tel_dame(ctx, t, lt):
        jardin(ctx, t, [(dame, 360, 1760, 0.95, "dame")])
        if t >= T("quatorze"):
            D.calendrier(ctx, 800, 820, 1.2 * back((t - T("quatorze")) / 0.3), "JUILLET", "14")

    def s_dauphin_sale(ctx, t, lt):
        jardin(ctx, t, feuilles=0.25)
        halo(ctx, *P.DAUPHIN, 260, (255, 240, 160), 0.25 + 0.1 * math.sin(t * 5))
        if t >= T("touchez"):
            ui.panneau(ctx, 540, 1150, "VOUS Y TOUCHEZ PAS", t - T("touchez"), rot=0.04, size=46, s=0.9)

    def s_bureau(ctx, t, lt):
        P.bureau(ctx, t)
        fils.draw(ctx, 430, 1720, 0.95, t, bouche=bouche(t, "fils"))
        ui.badge(ctx, 430, 1720 - 0.95 * 1150, "LE FILS", lt - 0.2)
        if t >= T("six", 1):
            traits_choc(ctx, 430, 1720 - 0.95 * 880, 150, t - T("six", 1))
        if t >= T("plumer"):
            ui.panneau(ctx, 560, 600, "PLUMER UNE VIEILLE", t - T("plumer"), rot=-0.05, size=66)

    def ecran_banque(ctx, w, h):
        ctx.rectangle(0, 0, w, h)
        flat(ctx, (246, 247, 250))
        ctx.rectangle(0, 0, w, 34)
        flat(ctx, (30, 90, 160))
        ecrit(ctx, "MA BANQUE", w / 2, 18, 10, (255, 255, 255), big=True)
        ecrit(ctx, "Virement émis", w / 2, 62, 9, (90, 90, 100))
        ecrit(ctx, "- 6 000,00 €", w / 2, 92, 17, (210, 40, 50), big=True)
        ecrit(ctx, "Piscines du Midi", w / 2, 122, 8, INK)
        for i in range(3):
            rrect(ctx, 10, 140 + i * 18, w - 20, 12, 4)
            flat(ctx, (220, 224, 234))

    def s_banque(ctx, t, lt):
        P.bureau(ctx, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (20, 24, 40), 0.55)
        D.telephone(ctx, 540, 1000, 4.4 * back(lt / 0.3), ecran_banque, rot=0.03 * math.sin(t))

    def s_moi_bassin(ctx, t, lt):
        jardin(ctx, t, [(moi, 700, 1390, 0.5, "moi")], soir=0.4 if t >= T("plumer", 1) else 0.0,
               devant=lambda c, tt: P.tas_feuilles(c, 700, 1395, 190, tt) if tt < T("savent") else None)

    def s_coupe(ctx, t, lt):
        D.fond_sombre(ctx, t, (24, 34, 50))
        P.coupe(ctx, t, ease((lt - 0.6) / 1.0), ease((lt - 1.7) / 0.5), y=960)
        ui.panneau(ctx, 540, 470, "CE QUE LES GENS SAVENT PAS", lt, rot=0, size=50, fond=(255, 210, 40), bord=INK,
                   col=INK)
        if lt >= 1.8:
            ui.panneau(ctx, 540, 1480, "ÇA BOUGE", lt - 1.8, rot=-0.04, size=80)

    def s_reparation(ctx, t, lt):
        jardin(ctx, t, devant=lambda c, tt: P.tuyau(c, tt, 360, 1160) if lt > 0.6 else None)
        ui.panneau(ctx, 300, 1000, "RÉSINE ÉPOXY", lt - 0.1, rot=-0.06, size=56, fond=(255, 210, 40), bord=INK,
                   col=INK)
        if lt > 0.6:
            ui.panneau(ctx, 760, 1010, "GOUTTE-À-GOUTTE", lt - 0.6, rot=0.05, size=50, fond=(255, 210, 40),
                       bord=INK, col=INK)

    def s_goutte(ctx, t, lt):
        jardin(ctx, t, devant=lambda c, tt: P.tuyau(c, tt, 360, 1160))

    def s_brosse(ctx, t, lt):
        jardin(ctx, t)
        x = 540 + 50 * math.sin(t * 16)
        P.brosse(ctx, x, 1300, 1.0, 0.5 + 0.1 * math.sin(t * 16))
        if t >= T("brosse"):
            for i in range(5):
                k = ((t - T("brosse")) * 1.5 + i / 5) % 1
                a = i * 1.3
                ctx.save()
                ctx.translate(540 + math.cos(a) * 150 * k, 1300 + math.sin(a) * 80 * k)
                ctx.scale(1 - k, 1 - k)
                ctx.move_to(0, -26)
                ctx.line_to(6, -6)
                ctx.line_to(26, 0)
                ctx.line_to(6, 6)
                ctx.line_to(0, 26)
                ctx.line_to(-6, 6)
                ctx.line_to(-26, 0)
                ctx.line_to(-6, -6)
                ctx.close_path()
                flat(ctx, (255, 255, 255))
                ctx.restore()

    def s_doute(ctx, t, lt):
        jardin(ctx, t, [(moi, 900, 1640, 0.62, "moi")], soir=0.85)

    def s_portail(ctx, t, lt):
        jardin(ctx, t)
        x = 1500 - 520 * (1 - (1 - min(1.0, lt / 1.0)) ** 3)
        V.voiture(ctx, x, 905, 0.42, (200, 70, 60))
        D.calendrier(ctx, 640, 640, 0.9 * back(lt / 0.35), "JUILLET", "14")

    def s_arrivee(ctx, t, lt):
        jardin(ctx, t, [(fils, 300, 1700, 0.82, "fils"), (petite, 470, 1720, 0.46, None)])
        ui.badge(ctx, 300, 1700 - 0.82 * 1150, "LE FILS", lt - 0.2)

    def s_arnaqueur(ctx, t, lt):
        jardin(ctx, t, [(moi, 800, 1700, 0.85, "moi")])
        ui.panneau(ctx, 800, 640, "L'ARNAQUEUR", lt - 0.15, rot=0.05, size=70)

    def s_bord(ctx, t, lt):
        jardin(ctx, t, [(fils, 470, 1640, 0.8, "fils"), (petite, 640, 1660, 0.45, None)])

    def s_glisse(ctx, t, lt):
        jardin(ctx, t, [(dame, 370, 1720, 0.85, "dame"), (moi, 700, 1720, 0.85, "moi")])

    def s_souvenir(ctx, t, lt):
        P.jardin(ctx, t)
        P.piscine(ctx, t, feuilles=0, fissure=0, resine=0, eau=0, propre=1)
        pere.draw(ctx, 660, 1400, 0.52, t)
        gamin.draw(ctx, 470, 1410, 0.32, t)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (150, 110, 60), 0.38)
        ctx.rectangle(-600, -600, 2400, 3200)
        flat(ctx, (255, 240, 210), 0.12)
        ui.panneau(ctx, 540, 1010, "SOUVENIR", lt - 0.1, rot=-0.03, size=56, fond=(250, 240, 220), bord=INK, col=INK)

    def s_final(ctx, t, lt):
        jardin(ctx, t, [(dame, 160, 1640, 0.6, "dame"), (moi, 920, 1640, 0.6, "moi"),
                        (fils, 400, 1700, 0.72, "fils"), (petite, 600, 1720, 0.42, None)])
        if t >= T("Six", 2):
            ui.panneau(ctx, 540, 1000, "6 000 €", t - T("Six", 2), rot=-0.03, size=110, fond=(255, 210, 40),
                       bord=INK, col=INK)

    # ── plans (caméra : centre x, centre y, zoom) ──
    tete = lambda x, y, s: (x, y - s * 880)          # noqa: E731
    f.plan(0, s_dame, [(0, 540, 1180, 1.3), (1.2, 540, 1160, 1.38)], fouet=False)
    f.plan("quatre", s_dame, [(0, 540, 1040, 1.8), (1.2, 540, 1030, 1.95)])
    f.plan("piscine", s_piscine_large, [(0, 540, 1180, 1.0), (1.5, 540, 1200, 1.06)])
    f.plan("Vide", s_piscine_large, [(0, 560, 1200, 1.35), (2.2, 560, 1220, 1.45)])
    f.plan("bassin", s_bassin, [(0, 660, 1270, 1.7), (1.6, 660, 1280, 1.8)])
    f.plan("fissure", s_bassin, [(0, 470, 1290, 1.8), (1.4, 480, 1300, 1.95)])
    f.plan("veut", s_tel_dame, [(0, 400, 1080, 1.3), (1.6, 420, 1070, 1.38)])
    f.plan("quatorze", s_tel_dame, [(0, 600, 1000, 1.2), (1.2, 610, 990, 1.28)])
    f.plan("dauphin", s_dauphin_sale, [(0, 540, 1280, 2.0), (1.5, 540, 1290, 2.2)])
    f.plan("deuxième", s_bureau, [(0, 480, 1100, 1.2), (1.5, 470, 1090, 1.28)])
    f.plan(("six", 1), s_bureau, [(0, *tete(430, 1720, 0.95), 2.0), (1.5, *tete(430, 1740, 0.95), 2.1)])
    f.plan("plumer", s_bureau, [(0, 470, 920, 1.5), (1.0, 470, 920, 1.55)])
    f.plan("raccrocher", s_bureau, [(0, 470, 1080, 1.35), (2.5, 460, 1060, 1.5)])
    f.plan("Je", s_moi_bassin, [(0, 680, 1250, 1.6), (1.6, 690, 1240, 1.75)])
    f.plan(("plumer", 1), s_moi_bassin, [(0, *tete(700, 1390, 0.5), 3.2), (1.2, *tete(700, 1400, 0.5), 3.4)])
    f.plan("savent", s_coupe, [(0, 540, 960, 1.0), (4, 540, 960, 1.06)])
    f.plan(("vingt", 1), s_reparation, [(0, 540, 1220, 1.3), (2.0, 540, 1250, 1.45)])
    f.plan("Mais", s_doute, [(0, 760, 1240, 1.2), (4.0, 780, 1230, 1.32)])
    f.plan(("quatorze", 1), s_portail, [(0, 860, 820, 1.4), (2.5, 880, 820, 1.5)])
    f.plan(("fils", 1), s_arrivee, [(0, 380, 1160, 1.25), (1.5, 390, 1150, 1.32)])
    f.plan("s'arrête", s_bord, [(0, 540, 1260, 1.1), (2.5, 540, 1270, 1.22)])
    f.plan(("rien", 1), s_bord, [(0, *tete(470, 1640, 0.8), 2.2), (1.2, *tete(470, 1650, 0.8), 2.35)])
    f.plan("glisse", s_glisse, [(0, 530, 1080, 1.3), (1.0, 530, 1070, 1.36)])
    f.plan("posé", s_souvenir, [(0, 560, 1300, 1.5), (2.5, 560, 1300, 1.62)])
    f.plan("l'ent", s_bord, [(0, *tete(470, 1660, 0.8), 2.4), (1.5, *tete(470, 1660, 0.8), 2.55)])
    f.plan("savait", s_glisse, [(0, *tete(370, 1740, 0.85), 2.0), (1.5, *tete(370, 1740, 0.85), 2.12)])
    f.plan(("Six", 2), s_final, [(0, 540, 1250, 1.0), (2.5, 540, 1240, 1.08)])

    # ── compte à rebours, sous-titres, sons ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "MISE EN EAU AVANT LE 14/07", [
        (0, 12), (T("deuxième"), 11), (Tsav, 8), (Tv, 4), (Tm, 1), (T("quatorze", 1), 0)],
        apparition=T("quatorze"), prefixe="J-", suffixe=""))
    groupes = ui.decouper(words)
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes, y=1330))
    for mot, son, g in [("quatre", "pop", 0.6), ("Vide", "pop", 0.6), ("fissure", "rate", 0.5),
                        ("quatorze", "pop", 0.7), ("touchez", "pop", 0.6), ("deuxième", "notif", 0.8),
                        ("six", "impact", 0.0), ("plumer", "impact", 0.9), ("bouge", "rate", 0.6),
                        (("vingt", 1), "tampon", 0.6), (("quatorze", 1), "pop", 0.7), (("Six", 2), "succes", 0.7)]:
        if g:
            f.son(T(*mot) if isinstance(mot, tuple) else mot, son, g)
    f.secousse("plumer", 14)
    f.secousse("bouge", 10)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/piscine_dauphin_court.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_piscine"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
