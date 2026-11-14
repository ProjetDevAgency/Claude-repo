"""Où va ton argent ? — permis en candidat libre (méthode v3, Kévin raconte). Script : scripts/modele/13_candidat_libre.dial"""
import facades
from auto_ecole_ct import voiture_bg, voiture_fg
from cartoon import FA, bubble, card, flash, room, shake, shock_lines
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, H, Image, ImageDraw, Recit, W, big_number, dim, echo,
                   gros_plan_kevin, gros_plan_mechant, mention, parle, plan, push, tag)  # noqa: F401
from recit import calque_kevin_tete
from vol_ct import badge, carte_sombre

GERANT = dict(shirt=(130, 32, 44), pants=(36, 36, 44), hair=(120, 120, 125), tie=True)
MERE = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
PERE = dict(shirt=(70, 110, 160), pants=(50, 50, 60), hair=(150, 150, 150))
_bg = {}


def agence_bg():
    """L'agence : mur, panneau AUTO-ÉCOLE."""
    if "a" not in _bg:
        im = room("vide").copy()
        _bg["a"] = im
    return _bg["a"]


def comptoir(d, t):
    """Le comptoir devant le gérant, le contrat et le stylo posé dessus."""
    s = SS
    d.rectangle([540 * s, 1180 * s, W * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([540 * s, 1180 * s, W * s, 1212 * s], fill=(150, 104, 74))
    d.polygon([(600 * s, 1196 * s), (860 * s, 1186 * s), (880 * s, 1206 * s), (612 * s, 1214 * s)], fill=WHITE)
    d.rectangle([630 * s, 1240 * s, 960 * s, 1440 * s], fill=(245, 245, 240))
    d.text((795 * s, 1290 * s), "CONTRAT", font=FA(40 * s), fill=INK, anchor="mm")
    d.text((795 * s, 1370 * s), "1 800 €", font=FA(64 * s), fill=RED, anchor="mm")
    d.line([700 * s, 1420 * s, 880 * s, 1400 * s], fill=(30, 60, 160), width=10 * s)


def rue_bg():
    """Devant l'agence : façade AUTO-ÉCOLE, trottoir, route."""
    if "r" not in _bg:
        im = Image.new("RGB", (W * SS, H * SS), (150, 205, 245))
        d = ImageDraw.Draw(im)
        facades.boutique(d, cx=540, nom="AUTO-ÉCOLE", mur=(240, 236, 228), enseigne=(30, 90, 200), store=(30, 90, 200))
        d.rectangle([0, 1380 * SS, W * SS, 1470 * SS], fill=(190, 190, 196))
        d.rectangle([0, 1470 * SS, W * SS, H * SS], fill=(70, 72, 80))
        for x in range(0, W, 200):
            d.rectangle([(x + 40) * SS, 1690 * SS, (x + 140) * SS, 1704 * SS], fill=WHITE)
        _bg["r"] = im
    return _bg["r"]


VOITURE = None


def voiture_calque():
    global VOITURE
    if VOITURE is None:
        VOITURE = facades.calque("voiture").resize((int(W * 0.78), int(H * 0.78)), Image.LANCZOS)
    return VOITURE


def agence(t, kpose="neutre", gerant=None, mere=False, z=1.0, center=(540, 1000)):
    autres = [(110, MERE, dict(mouth="flat"), 1.3)] if mere else ()
    return plan(agence_bg, t, kpose, kx=KX + (60 if mere else 0), mechant=gerant or dict(mouth="flat"), look=GERANT,
                autres=autres, devant=comptoir, z=z, center=center)


def dans_la_voiture(t, kpose="parle", pere=None, z=1.0, center=None):
    from cartoon import kevin, character, idle
    big = voiture_bg().copy()
    d = ImageDraw.Draw(big)
    kevin(d, 330, BASE, kpose, t)
    bob, blink = idle(t, 2.1)
    character(d, 760, BASE + bob, **{**PERE, "blink": blink, **(pere or dict(mouth="smile"))})
    voiture_fg(d)
    from cartoon import shot
    import rue
    return rue.contour_aretes(shot(big, z, center=center), seuil=90, w=3)


# ───── scènes, dans l'ordre du script ─────

def s_hook(lt, dur):
    img = gros_plan_mechant(agence_bg, GERANT, lt, dur, arm=0.5, devant=comptoir)
    badge(img, 540, 1190, "LE GÉRANT DE L'AUTO-ÉCOLE")
    bubble(img, 540, 570, ["1 800 € TON PERMIS,", "SINON TU RESTES À PIED"], 60, (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def s_couture(lt, dur):
    img = agence(lt, "neutre", gerant=dict(mouth="grin", arm=0.3), mere=True, z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "DEVANT SA MÈRE", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "LE CONTRAT EST PRÊT", 50, WHITE, INK, rot=2, k=(lt - 2.2) / 0.3)
    return flash(img, lt)


def s_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=540, z=push(lt, dur, 1.0, 1.08), center=(540, 1000))
    for i, (txt, col, t0) in enumerate([("PREMIER JOB EN MARS", YEL, 0.0), ("IL FAUT LE PERMIS", WHITE, 1.6),
                                        ("TOUT L'ÉTÉ AU SNACK", GREEN, 3.0)]):
        tag(img, 540, 420 + i * 140, txt, 54, col, INK, rot=(-4, 3, -3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def s_demande(lt, dur):
    img = agence(lt, "parle", gerant=dict(mouth="grin" if lt > 1.2 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "ET AVEC MON PÈRE ?", 56, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def s_coup1(lt, dur):
    img = gros_plan_mechant(agence_bg, GERANT, lt, dur, 1.95, 2.15, arm=0.4, devant=comptoir)
    if lt < 2.4:
        bubble(img, 540, 545, ["TON PÈRE ?", "IL SAIT MÊME PAS", "FAIRE UN CRÉNEAU"], 62, lt / 0.25, tail_x=660)
    else:
        bubble(img, 540, 560, ["ICI C'EST 20 H MINIMUM,", "C'EST LA LOI"], 62, (lt - 2.4) / 0.25, tail_x=660)
    return flash(img, lt)


def s_stylo(lt, dur):
    img = agence(lt, "triste", gerant=dict(mouth="grin", arm=0.8), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def s_coup2(lt, dur):
    img = gros_plan_mechant(agence_bg, GERANT, lt, dur, 2.2, 2.4, arm=0.8, devant=comptoir)
    bubble(img, 540, 545, ["UN GAMIN QUI FAIT", "DES BURGERS, ÇA A", "PAS LES MOYENS"], 60, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def s_silence(lt, dur):
    img = agence(lt, "triste", gerant=dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))
    return img


def s_echo(lt, dur):
    img = dim(gros_plan_kevin(agence_bg, lt, dur), 0.75)
    echo(img, "ÇA A PAS LES MOYENS")
    return img


def s_regle(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "LA RÈGLE", [("Auto-école : pas obligatoire", 0.3, False), ("20 h minimum : leur règle", 1.8, False),
                                   ("Candidat libre : 0 minimum", 3.4, True)], lt, y0=470,
                 sous="SERVICE-PUBLIC · ARRÊTÉ DU 22/12/2009")
    return img


def s_pere(lt, dur):
    img = dans_la_voiture(lt, "parle", dict(mouth="smile"), z=push(lt, dur, 1.0, 1.06), center=(540, 1000))
    tag(img, 540, 420, "SON PÈRE", 60, YEL, INK, rot=-3, k=(lt - 0.6) / 0.3)
    tag(img, 540, 560, "PERMIS DEPUIS + DE 5 ANS · PAS PAYÉ", 44, WHITE, INK, rot=2, k=(lt - 1.8) / 0.3)
    return flash(img, lt)


def s_double(lt, dur):
    img = dans_la_voiture(lt, "neutre", dict(mouth="flat"), z=push(lt, dur, 1.05, 1.12), center=(540, 1050))
    tag(img, 540, 420, "1 SEULE PÉDALE DE FREIN", 52, RED, WHITE, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "DOUBLE COMMANDE · 20 €/H", 50, GREEN, INK, rot=2, k=(lt - 2.0) / 0.3)
    return flash(img, lt)


def s_depenses(lt, dur):
    tg = REC.T["gain"] - REC.T["s_depenses"]
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.88)
    carte_sombre(img, "SON PERMIS SEUL", [("Code : 30 €", 0.4, False), ("Location : 25 h × 20 € = 500 €", 1.6, False),
                                          ("Voiture de l'examen : 120 €", 2.8, False), ("Total : 650 €", tg, True)],
                 lt, y0=470, sous="INSCRIPTION SEUL SUR L'ANTS · EXAMEN SUR RDVPERMIS")
    return img


def s_doute(lt, dur):
    img = dans_la_voiture(lt, "triste", dict(mouth="smile"), z=push(lt, dur, 1.1, 1.18), center=(450, 1000))
    tag(img, 540, 420, "3 MOIS SANS MONITEUR", 54, WHITE, INK, rot=-3, k=(lt - 1.2) / 0.3)
    return img


def s_twist(lt, dur):
    from cartoon import character, idle
    big = rue_bg().copy()
    d = ImageDraw.Draw(big)
    bob, blink = idle(lt, 0.6)
    silence = lt > 3.2
    character(d, 860, 1440 + bob, sc=0.78, **{**GERANT, "blink": blink, "mouth": "o" if silence else "flat",
                                               "brows": "triste" if silence else "colere"})
    from cartoon import shot
    import rue
    img = rue.contour_aretes(shot(big, 1.0), seuil=90, w=3).convert("RGBA")
    car = voiture_calque()
    x = int(-760 + 820 * min(1.0, lt / 2.2))           # la voiture arrive et s'arrête devant l'agence
    img.alpha_composite(car, (x, 420))
    calque_kevin_tete(img, x + int(540 * 0.78) - 90, 420 + int((1380 - 40 - 360) * 0.78), 1.0)
    img = img.convert("RGB")
    tag(img, 540, 420, "AU VOLANT", 66, GREEN, INK, rot=-3, k=(lt - 1.6) / 0.3)
    if silence:
        tag(img, 540, 560, "LE GÉRANT NE DIT PLUS RIEN", 46, WHITE, INK, rot=2, k=(lt - 3.2) / 0.3)
    return img


def s_chute(lt, dur):
    img = dim(plan(agence_bg, lt, devant=comptoir, z=1.15, center=(700, 1100)), 0.6)   # pas de visage sous le texte
    big_number(img, (540, 420), "1 800 €", 130, RED, k=lt / 0.25, strike=ease_((lt - 0.5) / 0.3))
    big_number(img, (540, 590), "PERMIS OBTENU", 90, GREEN, "SANS LUI", k=(lt - 0.9) / 0.25, rot=-3)
    mention(img, "CANDIDAT LIBRE · SERVICE-PUBLIC.FR · CAS TYPE", lt)
    return img


def ease_(k):
    return max(0.0, min(1.0, k))


REC = Recit("droits_candidat_libre", "scripts/modele/13_candidat_libre.txt",
            "output/_work_droits_candidat_libre/voice_duo.wav",
            compteur=dict(label="GARDÉ PAR KÉVIN", depart=0, montant=1150, phrase="Six cent cinquante"))

BEATS = [
    ("Tu me paies", s_hook, ("impact", 1.0)),
    ("C'est ce que le gérant", s_couture, ("whoosh", 0.6)),
    ("Et pourtant j'étais content", s_montee, ("pop", 0.8)),
    ("Je demande juste", s_demande, None),
    ("Ton père", s_coup1, ("impact", 0.8)),
    ("Et en rangeant son stylo", s_stylo, ("whoosh", 0.5)),
    ("Un gamin qui retourne", s_coup2, ("impact", 1.0)),
    ("Je dis rien", s_silence, None),
    ("Ça a pas les moyens", s_echo, ("rate", 0.6)),
    ("Sauf que rien en France", s_regle, ("pop", 0.8)),
    ("Mais alors qui s'assoit", s_pere, ("whoosh", 0.5)),
    ("Sauf que sa Clio", s_double, ("pop", 0.7)),
    ("Je m'inscris seul", s_depenses, ("notif", 0.7)),
    ("Honnêtement", s_doute, None),
    ("Trois mois après", s_twist, ("whoosh", 0.8)),
    ("Mille huit cents euros pour", s_chute, ("impact", 0.9)),
]

if __name__ == "__main__":
    REC.fabriquer(BEATS)
