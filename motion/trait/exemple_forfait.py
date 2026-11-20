"""Vidéo exemple du style « trait » : le forfait mobile qui augmente → on part sans frais (art. L224-33).

    python3 motion/trait/exemple_forfait.py                 # vidéo complète → output/trait/exemple_forfait.mp4
    python3 motion/trait/exemple_forfait.py --stills 1,4,9  # quelques images seulement (contrôle rapide)
"""
import argparse
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import decors as D  # noqa: E402
import ui  # noqa: E402
import voix  # noqa: E402
from dessin import INK, ROOT, back, ease, ecrit, rrect, flat, paint, stroke, LW, halo  # noqa: E402
from film import Film  # noqa: E402
from perso import Perso, traits_choc  # noqa: E402

NARRATEUR = os.environ.get("ELEVENLABS_VOICE_ID", "cDpfdjuqlrxqLRo3BMFC")
MECHANT = os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT")      # Paul K, grave
VOIX = {"mechant": (MECHANT, {"stability": 0.38, "similarity_boost": 0.8, "style": 0.35}),
        "nar": (NARRATEUR, {"stability": 0.45, "similarity_boost": 0.8, "style": 0.2})}

# [mots] = surlignés en jaune, {mots} = en rouge
LIGNES = [
    ("mechant", "Ton forfait passe de [15 à 22 euros]. Et si tu pars, tu paies tes {8 mois} d'engagement."),
    ("nar", "Il le sait pas encore, mais cette phrase va lui coûter un client."),
    ("nar", "Kévin relit son contrat. [7 euros] de plus par mois, ça fait [84 euros] par an. "
            "Et pour partir, 8 mois à 22 euros, {176 euros} de frais."),
    ("nar", "Sauf qu'il y a une règle que presque personne ne connaît."),
    ("nar", "Quand ton opérateur augmente un prix qui n'était pas prévu dans ton contrat, "
            "il doit te prévenir [un mois avant]."),
    ("nar", "Et pendant [4 mois] après la hausse, tu peux partir sans payer {un seul euro} de frais. "
            "Même si t'es engagé."),
    ("nar", "C'est écrit dans le Code de la consommation, article L deux cent vingt-quatre, trente-trois."),
    ("nar", "Kévin envoie un message au service client. Le lendemain, résiliation acceptée. [Zéro euro] de frais."),
    ("nar", "[176 euros] gardés, et [84 euros] par an en moins. Le vendeur, lui, vient de perdre un client."),
    ("nar", "Alors regarde bien le dernier mail de ton opérateur, avant qu'il te dise"),
]

# ───────────── casting (original : ni le look ni les personnages d'un autre compte) ─────────────
KEVIN = dict(cheveux="boucles", couleur_cheveux=(30, 24, 30), peau=(198, 138, 98), haut="sweat",
             couleur_haut=(46, 170, 120), bas=(56, 70, 120), chaussures=(245, 245, 245), seed=1)
VENDEUR = dict(cheveux="plaque", couleur_cheveux=(44, 36, 44), peau=(242, 196, 160), haut="polo",
               couleur_haut=(150, 70, 170), bas=(40, 40, 52), chaussures=(30, 30, 36), moustache=True, seed=2)


def construire(work):
    voice, words = voix.build(LIGNES, VOIX, work)
    f = Film(voice, words)
    T = f.t

    kev = Perso(**KEVIN)
    ven = Perso(**VENDEUR)
    kev_salon = Perso(**KEVIN)

    # ── poses et émotions calées sur les mots ──
    ven.pose(0, "mains_hanches").emotion(0, "malin")
    ven.pose(T("pars"), "pointe_g").emotion(T("pars"), "colere")
    ven.pose(T("8"), "haussement").emotion(T("8"), "malin")
    kev.emotion(T("22"), "choc")
    kev.emotion(T("Il"), "malin")
    kev.emotion(T("Sauf"), "neutre").emotion(T("règle"), "content").pose(T("règle"), "leve_d")
    ven.pose(T("vendeur"), "facepalm").emotion(T("vendeur"), "colere")

    def tel_ecran(ok):
        def e(ctx, w, h):
            flat_bg = (230, 240, 236) if ok else (236, 238, 246)
            ctx.rectangle(0, 0, w, h)
            flat(ctx, flat_bg)
            for i in range(4):
                rrect(ctx, 10 + (i % 2) * 24, 20 + i * 42, 60, 26, 10)
                flat(ctx, (40, 140, 240) if i % 2 else (200, 204, 214))
        return e

    kev_salon.objet = lambda ctx, x, y, s: D.telephone(ctx, x - 10, y - 60, 0.9, tel_ecran(False), rot=-0.1)
    kev_salon.pose(0, "telephone").emotion(0, "malin")
    kev_salon.emotion(T("lendemain"), "content").pose(T("lendemain"), "leve")
    kev_salon.pose(T("Alors"), "pointe_cam").emotion(T("Alors"), "content")

    # ── scène : la boutique ──
    def boutique(ctx, t, lt):
        D.boutique(ctx, t)
        ven.draw(ctx, 650, 1560, 0.75, t, bouche=f.bouche(t, "mechant"))
        D.comptoir(ctx, 650, 1255)
        hv = (650, 1560 - 0.75 * 1030)
        ui.badge(ctx, hv[0], hv[1] - 40, "LE VENDEUR", t - 0.3)
        # étiquette de prix : 15 € puis 22 € qui claque
        if T("15") - 0.1 <= t < T("Il"):
            prix = "22 €" if t >= T("22") else "15 €"
            col = (232, 52, 60) if t >= T("22") else (255, 214, 60)
            k = back((t - (T("22") if t >= T("22") else T("15"))) / 0.25)
            D.etiquette(ctx, 900, 720, 0.8 * k, prix, t - T("15"), col, (255, 255, 255) if t >= T("22") else INK)
        if T("8") <= t < T("Il"):
            ui.panneau(ctx, 860, 560, "8 MOIS", t - T("8"), rot=0.07, size=80)
        if t >= T("vendeur"):
            traits_choc(ctx, hv[0], hv[1] + 60, 150, t - T("vendeur"))
            ui.panneau(ctx, 650, 560, "- 1 CLIENT", t - T("vendeur") - 0.3, size=90)
        kev.draw(ctx, 250, 1760, 0.95, t, bouche=0.0, regard=0.6)
        hk = (250, 1760 - 0.95 * 880)
        if T("22") <= t < T("Il"):
            traits_choc(ctx, hk[0], hk[1], 150, t - T("22"))
        if T("règle") <= t < T("Quand"):
            D.ampoule(ctx, hk[0] + 10, hk[1] - 210, back((t - T("règle")) / 0.3) * 0.8, t)

    # ── scène : le contrat ──
    def contrat(ctx, t, lt):
        D.fond_sombre(ctx, t)
        k = back(lt / 0.35)
        lignes = [("Forfait XL 100 Go", INK), ("", None), ("Prix : 15,00 € / mois", INK), ("", None)]
        D.contrat(ctx, 540, 830, 2.1 * k, rot=-0.04 + math.sin(t) * 0.01, lignes=lignes, tampon="+7 €/MOIS",
                  tampon_k=max(0, (t - T("7")) / 0.6) if t >= T("7") else 0)
        if t >= T("84"):
            ui.panneau(ctx, 540, 1335, "7 € × 12 = 84 € / AN", t - T("84"), rot=0.03, size=72,
                       fond=(255, 210, 40), bord=INK, col=INK)

    # ── scène : 8 mois de frais (pages de calendrier qui tombent) ──
    MOIS = ["DÉC", "JANV", "FÉVR", "MARS", "AVR", "MAI", "JUIN", "JUIL"]

    def frais(ctx, t, lt):
        D.fond_sombre(ctx, t, (44, 26, 34))
        t176 = T("176")
        n = min(8, int(lt / max(0.2, (t176 - f.plans_t0("frais")) / 8.5)) + 1)
        for i in range(n):
            a = (lt * 3 + i) if i < n - 1 else 0
            if i < n - 1:
                y = 900 + (lt - i * 0.18) * 900
                D.calendrier(ctx, 540 + math.sin(i * 2.1) * 260, y, 1.2, MOIS[i], "22 €")
        D.calendrier(ctx, 540, 740, 2.0, MOIS[n - 1], "22 €")
        ecrit(ctx, f"{n} / 8 MOIS", 540, 1100, 70, (255, 255, 255), big=True)
        if t >= t176:
            ui.panneau(ctx, 540, 1460, "176 € DE FRAIS", t - t176, rot=-0.05, size=100)

    # ── scène : le mail de l'opérateur (téléphone en gros plan) ──
    def mail(ctx, t, lt):
        D.salon(ctx, t)
        halo(ctx, 540, 1000, 700, (120, 160, 255), 0.18)

        def ecran(c, w, h):
            c.rectangle(0, 0, w, h)
            flat(c, (244, 246, 250))
            rrect(c, 6, 8, w - 12, 30, 8)
            flat(c, (150, 70, 170))
            ecrit(c, "Boîte de réception", w / 2, 23, 9, (255, 255, 255))
            for i in range(6):
                rrect(c, 8, 48 + i * 24, w - 16, 18, 5)
                flat(c, (220, 224, 234))
        D.telephone(ctx, 540, 1000, 4.6, ecran, rot=0.03 * math.sin(t))

    def mail_hud(ctx, t, lt):
        ui.notif(ctx, t - T("prévenir"), 540, 360, "MOBI+", "Modification de votre offre",
                 "Votre forfait passe à 22 €/mois…")
        if t >= T("avant"):
            D.calendrier(ctx, 860, 1470, 1.0 * back((t - T("avant")) / 0.3), "PRÉAVIS", "J-30")

    # ── scène : la règle (carte cochée) ──
    def regle(ctx, t, lt):
        D.fond_sombre(ctx, t, (26, 40, 44))

    def regle_hud(ctx, t, lt):
        t0 = f.plans_t0("regle")
        ui.carte_regle(ctx, lt, "LA RÈGLE", [
            (0.15, "Hausse non prévue :\nprévenu 1 mois avant", "1 mois avant"),
            (T("4") - t0, "4 mois pour partir\naprès la hausse", "4 mois"),
            (T("sans") - t0, "0 € de frais\nde résiliation", "0 €"),
            (T("Même") - t0, "Même si tu es\nencore engagé", "engagé"),
        ], y0=300)

    # ── scène : le texte de loi surligné ──
    def loi(ctx, t, lt):
        D.fond_sombre(ctx, t, (34, 34, 40))
        k = back(lt / 0.35)
        ctx.save()
        ctx.translate(540, 980)
        ctx.scale(k, k)
        ctx.rotate(0.02)
        rrect(ctx, -440, -560, 880, 1120, 16)
        paint(ctx, (250, 248, 240), LW, shade=0.94)
        ecrit(ctx, "CODE DE LA CONSOMMATION", 0, -480, 46, INK, big=True)
        ecrit(ctx, "Article L224-33", 0, -400, 56, (200, 40, 50))
        txt = ["Tout projet de modification", "des conditions contractuelles", "est communiqué au consommateur",
               "au moins un mois avant", "son entrée en vigueur. […]", "Le consommateur peut résilier",
               "le contrat sans pénalité de", "résiliation […] dans un délai", "de quatre mois après l'entrée",
               "en vigueur de la modification."]
        surl = {3: 0.35, 5: 1.0, 6: 1.2, 7: 1.4, 8: 1.6}
        for i, l in enumerate(txt):
            y = -300 + i * 78
            if i in surl:
                p = ease((lt - surl[i]) / 0.35)
                if p > 0:
                    rrect(ctx, -390, y - 30, 780 * p, 60, 8)
                    flat(ctx, (255, 210, 40), 0.85)
            ecrit(ctx, l, -380, y, 44, INK, ax=0)
        ctx.restore()

    # ── scène : le salon (Kévin envoie le message, reçoit la réponse) ──
    def salon(ctx, t, lt):
        D.salon(ctx, t)
        kev_salon.draw(ctx, 540, 1760, 1.0, t, regard=-0.3)
        if T("Kévin", 1) <= t < T("lendemain"):
            ui.bulle(ctx, 720, 640, "Je résilie (art. L224-33)", t - T("Kévin", 1) - 0.6, size=38)

    def salon_hud(ctx, t, lt):
        if t >= T("résiliation"):
            ui.notif(ctx, t - T("résiliation"), 540, 330, "MOBI+", "Résiliation acceptée",
                     "Frais de résiliation : 0,00 €", couleur=(150, 70, 170))

    def bilan_hud(ctx, t, lt):
        ui.panneau(ctx, 540, 520, "+176 € GARDÉS", lt, rot=-0.04, size=86, fond=(70, 205, 115), bord=INK, col=INK)
        if t >= T("84", 1):
            ui.panneau(ctx, 560, 700, "+84 € / AN", t - T("84", 1), rot=0.04, size=86, fond=(255, 210, 40),
                       bord=INK, col=INK)

    # ── plans (caméra : centre x, centre y, zoom) ──
    f.plans_t0 = lambda nom: {"frais": T("partir"), "regle": T("pendant")}[nom]
    vend = (650, 900)
    tete_k = (250, 960)
    f.plan(0, boutique, [(0, 540, 1000, 1.0), (1.0, 560, 980, 1.08)], fouet=False)
    f.plan("15", boutique, [(0, vend[0] + 80, vend[1] + 40, 1.7), (1.5, vend[0] + 80, vend[1] + 40, 1.85)])
    f.plan("pars", boutique, [(0, tete_k[0] + 120, tete_k[1] + 80, 1.75), (1.0, tete_k[0] + 120, tete_k[1] + 60, 1.9)])
    f.plan("8", boutique, [(0, 720, 860, 1.5), (1.0, 720, 860, 1.6)])
    f.plan("Il", boutique, [(0, tete_k[0] + 60, tete_k[1] + 60, 2.2), (2.5, tete_k[0] + 60, tete_k[1] + 40, 2.5)])
    f.plan("Kévin", contrat, [(0, 540, 960, 1.0), (3, 540, 1000, 1.1)])
    f.plan("84", contrat, [(0, 540, 1180, 1.3), (2, 540, 1180, 1.36)])
    f.plan("partir", frais, [(0, 540, 960, 1.0), (3, 540, 960, 1.12)])
    f.plan("Sauf", boutique, [(0, tete_k[0] + 80, tete_k[1] - 40, 1.8), (2.5, tete_k[0] + 80, tete_k[1] - 60, 2.0)])
    f.plan("Quand", mail, [(0, 540, 1000, 1.0), (4, 540, 1000, 1.12)], hud=mail_hud)
    f.plan("prévenir", mail, [(0, 540, 760, 1.5), (3, 540, 760, 1.6)], hud=mail_hud)
    f.plan("pendant", regle, hud=regle_hud)
    f.plan("C'est", loi, [(0, 540, 960, 0.95), (1.2, 540, 960, 1.0), (4.5, 540, 760, 1.25)])
    f.plan(("Kévin", 1), salon, [(0, 540, 1100, 1.0), (2.5, 600, 1050, 1.25)], hud=salon_hud)
    f.plan("lendemain", salon, [(0, 540, 1000, 1.25), (2.5, 540, 1000, 1.35)], hud=salon_hud)
    f.plan(("176", 1), salon, [(0, 540, 1050, 1.1), (2, 540, 1050, 1.2)], hud=bilan_hud)
    f.plan("vendeur", boutique, [(0, vend[0], vend[1] + 20, 1.6), (2.5, vend[0], vend[1], 1.8)])
    f.plan("Alors", salon, [(0, 540, 950, 1.6), (3, 540, 930, 1.85)])

    # ── chiffres animés, bruitages, secousses ──
    f.ecran(lambda ctx, t: ui.compteur(ctx, t, "ÉCONOMISÉ PAR KÉVIN",
                                       [(0, 0), (T("Zéro"), 176), (T("84", 1), 260)], apparition=T("Il")))
    f.ecran(lambda ctx, t: ui.sous_titres(ctx, t, groupes))
    groupes = ui.decouper(words)
    for mot, son, g in [("15", "pop", 0.7), ("22", "impact", 0.9), ("8", "pop", 0.8), ("7", "tampon", 0.9),
                        ("84", "pop", 0.7), ("176", "rate", 0.8), ("règle", "succes", 0.6), ("prévenir", "notif", 0.9),
                        ("4", "pop", 0.6), ("sans", "pop", 0.6), ("Même", "pop", 0.6), ("résiliation", "notif", 0.9),
                        ("Zéro", "succes", 0.9), (("84", 1), "ticks", 0.6), ("vendeur", "impact", 0.8)]:
        f.son(mot, son, g)
    f.son(f.t("partir"), "ticks", 0.5)
    for mot in ("22", "176", "vendeur"):
        f.secousse(mot, 16)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--out", default=str(ROOT / "output/trait/exemple_forfait.mp4"))
    a = ap.parse_args()
    work = ROOT / "output/trait/_work_forfait"
    f = construire(work)
    print(f"durée {f.dur:.1f} s, {len(f.plans)} plans")
    if a.stills:
        f.stills([float(x) for x in a.stills.split(",")], work / "stills")
    else:
        print("→", f.render(a.out))


if __name__ == "__main__":
    main()
