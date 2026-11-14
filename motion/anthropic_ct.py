"""Où va ton argent ? — l'entrée en bourse d'Anthropic (19 nov. 2026), méthode v3. Script : scripts/modele/14_ipo_anthropic.dial
Ton neutre, pas d'incitation : « Ceci n'est pas un conseil en investissement » à l'écran."""
from cartoon import FA, bubble, flash, phone_big, shake
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, ImageDraw, Recit, W, barres, big_number, dim, echo,
                   gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from vol_ct import badge, carte_sombre

FRERE = dict(shirt=(40, 40, 50), pants=(50, 50, 60), hair=(25, 20, 15), hood=(30, 30, 38))
MERE = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
PERE = dict(shirt=(70, 110, 160), pants=(50, 50, 60), hair=(150, 150, 150), glasses=True)


def table(d, t):
    """La table du repas du dimanche : nappe, assiettes, plat de gratin, le téléphone du frère avec la courbe."""
    s = SS
    d.rectangle([0, 1230 * s, W * s, 1520 * s], fill=(235, 232, 225))
    d.rectangle([0, 1230 * s, W * s, 1262 * s], fill=(250, 248, 244))
    for x in (230, 470, 640, 860):
        d.ellipse([(x - 80) * s, 1236 * s, (x + 80) * s, 1262 * s], fill=WHITE, outline=(200, 200, 205), width=3 * s)
    d.rounded_rectangle([480 * s, 1196 * s, 630 * s, 1250 * s], radius=14 * s, fill=(225, 160, 70))
    d.rounded_rectangle([960 * s, 1190 * s, 1040 * s, 1250 * s], radius=8 * s, fill=(20, 20, 26))
    pts = [(968, 1240), (985, 1228), (1000, 1232), (1015, 1214), (1032, 1200)]
    d.line([(x * s, y * s) for x, y in pts], fill=(60, 220, 120), width=4 * s)


def repas(t, kpose="neutre", frere=None, parents=True, z=1.0, center=(540, 1000)):
    autres = [(420, PERE, dict(mouth="flat"), 1.1, BASE - 30), (650, MERE, dict(mouth="flat"), 2.3, BASE - 30)] if parents else ()
    return plan(salon_bg, t, kpose, kx=190, mechant=frere or dict(mouth="flat"), look=FRERE, mx=890, autres=autres,
                devant=table, z=z, center=center)


def s_hook(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, arm=0.5, devant=table)
    badge(img, 540, 1190, "SON GRAND FRÈRE")
    bubble(img, 540, 560, ["TES 4 000 € SUR ANTHROPIC,", "SINON T'ES FAUCHÉ À VIE"], 56, (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def s_couture(lt, dur):
    img = repas(lt, "neutre", dict(mouth="grin", phone=True), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE REPAS DU DIMANCHE", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "L'APPLI DE BOURSE OUVERTE", 46, WHITE, INK, rot=2, k=(lt - 2.4) / 0.3)
    return flash(img, lt)


def s_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=540, z=push(lt, dur, 1.0, 1.08), center=(540, 1000))
    for i, (txt, col, t0) in enumerate([("2 ANS D'ÉCONOMIES", YEL, 0.3), ("SUR SON LIVRET", WHITE, 1.4),
                                        ("POUR SON 1ER APPART", GREEN, 2.6)]):
        tag(img, 540, 420 + i * 140, txt, 54, col, INK, rot=(-4, 3, -3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def s_rire(lt, dur):
    return flash(repas(lt, "neutre", dict(mouth="grin", arm=0.3), z=push(lt, dur, 1.05, 1.1)), lt)


def s_coup1(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 1.95, 2.15, arm=0.4, devant=table)
    if lt < 2.6:
        bubble(img, 540, 545, ["TON LIVRET ?", "ÇA RAPPORTE MÊME PAS", "L'INFLATION"], 60, lt / 0.25, tail_x=660)
    else:
        bubble(img, 540, 560, ["MOI J'AI DÉJÀ TOUT MIS.", "TOUT CE QUE J'AVAIS"], 60, (lt - 2.6) / 0.25, tail_x=660)
    return flash(img, lt)


def s_gratin(lt, dur):
    img = repas(lt, "triste", dict(mouth="grin", arm=0.8), z=push(lt, dur, 1.1, 1.18))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def s_coup2(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 2.2, 2.4, arm=0.8, devant=table)
    bubble(img, 540, 545, ["TU FINIRAS COMME PAPA,", "AVEC TON PETIT", "LIVRET"], 60, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def s_silence(lt, dur):
    return repas(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def s_echo(lt, dur):
    img = dim(gros_plan_kevin(salon_bg, lt, dur, devant=table), 0.75)
    echo(img, "TON PETIT LIVRET")
    return img


def s_ipo(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "ENTRÉE EN BOURSE", [("Anthropic, l'entreprise de Claude", 0.3, False),
                                           ("Le 19 novembre, au Nasdaq", 1.6, False),
                                           ("Entre 70 et 78 $ l'action", 3.0, True)], lt, y0=470,
                 sous="FOURCHETTE DE PRIX ANNONCÉE")
    return img


def s_croissance(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    barres(img, "SON CHIFFRE D'AFFAIRES", [("2024", 0.386, "386 M$", (120, 120, 140), 0.3),
                                           ("2025", 4.6, "4,6 MD$", (60, 200, 110), 1.2)], lt, sous="× 12 EN UN AN")
    return img


def s_prix(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.85)
    big_number(img, (540, 560), "≈ 1 000 MILLIARDS $", 96, YEL, "CE QU'ELLE VAUT AU PRIX D'ENTRÉE", k=lt / 0.3)
    tag(img, 540, 820, "LA CROISSANCE EST DÉJÀ DANS LE PRIX", 44, WHITE, INK, rot=-2, k=(lt - 2.2) / 0.3)
    return img


def s_piege(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    barres(img, "LE PIÈGE", [("INTRODUCTION", 78, "78 $", (60, 200, 110), 0.3),
                             ("OUVERTURE", 110, "? $", (230, 80, 80), 1.6)], lt, sous="SI L'ACTION OUVRE PLUS HAUT")
    return img


def s_impots(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "SI ÇA MONTE", [("PEA : impossible", 0.3, False), ("Compte-titres : oui", 1.3, False),
                                      ("Impôt sur le gain : 31,4 %", 2.4, True)], lt, y0=470, sous="FLAT TAX 2026")
    return img


def s_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000))
    tag(img, 540, 420, "IL A PEUT-ÊTRE RAISON ?", 54, WHITE, INK, rot=-3, k=(lt - 0.5) / 0.3)
    return img


def s_choix(lt, dur):
    img = plan(salon_bg, lt, "neutre", kx=540, z=push(lt, dur, 1.0, 1.06), center=(540, 1000))
    tag(img, 540, 420, "LA CAUTION RESTE AU CHAUD", 52, GREEN, INK, rot=-3, k=(lt - 0.2) / 0.3)
    tag(img, 540, 560, "IL MET CE QU'IL PEUT PERDRE", 46, WHITE, INK, rot=2, k=(lt - 1.4) / 0.3)
    return flash(img, lt)


def s_appel(lt, dur):
    img = plan(salon_bg, lt, "telephone", kx=300)
    phone_big(img, 600, 920, lt, "19:08", [("Messages", "Grand frère", "Tu peux m'avancer mon loyer ?", (60, 160, 230))])
    tag(img, 540, 420, "MERCREDI", 56, YEL, INK, rot=-3, k=lt / 0.25)
    return img


def s_tout(lt, dur):
    img = plan(salon_bg, lt, "choc", kx=540, z=push(lt, dur, 1.2, 1.3), center=(540, 1000))
    tag(img, 540, 420, "IL AVAIT VRAIMENT TOUT MIS", 54, RED, WHITE, rot=-3, k=lt / 0.25)
    return shake(flash(img, lt), lt)


def s_chute(lt, dur):
    img = dim(plan(salon_bg, lt, devant=table, z=1.1, center=(540, 1150)), 0.6)   # pas de visage sous le texte
    big_number(img, (540, 470), "4 000 €", 150, GREEN, "TOUJOURS SUR SON LIVRET", k=lt / 0.25, rot=-3)
    tag(img, 540, 700, "ET C'EST LUI QUI EMPRUNTE", 50, YEL, INK, rot=2, k=(lt - 0.8) / 0.3)
    mention(img, "CECI N'EST PAS UN CONSEIL EN INVESTISSEMENT · CAS TYPE", lt)
    return img


REC = Recit("droits_anthropic", "scripts/modele/14_ipo_anthropic.txt", "output/_work_droits_anthropic/voice_duo.wav",
            compteur=dict(label="ÉPARGNE DE KÉVIN", depart=4000, montant=4000, phrase=None))

BEATS = [
    ("Tu mets tes quatre", s_hook, ("impact", 1.0)),
    ("C'est ce que mon grand frère", s_couture, ("whoosh", 0.6)),
    ("Et pourtant j'étais fier", s_montee, ("pop", 0.8)),
    ("Il rigole et il me fait", s_rire, None),
    ("Ton livret", s_coup1, ("impact", 0.8)),
    ("Et en se resservant", s_gratin, ("whoosh", 0.5)),
    ("Toi, tu finiras", s_coup2, ("impact", 1.0)),
    ("Je dis rien", s_silence, None),
    ("Ton petit livret", s_echo, ("rate", 0.6)),
    ("Anthropic, c'est", s_ipo, ("pop", 0.8)),
    ("Mais alors pourquoi", s_croissance, ("ticks", 0.6)),
    ("Sauf qu'à ce prix", s_prix, ("impact", 0.7)),
    ("Ce que mon frère sait pas", s_piege, ("pop", 0.7)),
    ("Une action américaine", s_impots, ("pop", 0.7)),
    ("Honnêtement", s_doute, None),
    ("Je garde ma caution", s_choix, ("succes", 0.6)),
    ("Mercredi, il m'appelle", s_appel, ("notif", 0.9)),
    ("Il avait vraiment tout mis", s_tout, ("rate", 0.8)),
    ("Quatre mille euros. Et", s_chute, ("impact", 0.9)),
]

if __name__ == "__main__":
    REC.fabriquer(BEATS)
