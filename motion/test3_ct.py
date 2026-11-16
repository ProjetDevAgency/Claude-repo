"""Où va ton argent ? — le test des 3 sources (méthode v3 + geste clivant + doute).
    python3 motion/test3_ct.py spacex   → ACTU : SpaceX, avant l'entrée en bourse d'Anthropic (21_spacex_avant_anthropic.dial)
    python3 motion/test3_ct.py valise   → CONCURRENT : la valise cassée (22_valise_cassee.dial)
    python3 motion/test3_ct.py cdd      → INVENTÉ : la prime de fin de CDD (23_cdd_precarite.dial)
"""
import sys

from anthropic_ct import FRERE
from cartoon import FA, bubble, card, flash, phone_big, room, shake
from demission_ct import bureau_bg, entrepot_bg
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, H, Image, ImageDraw, Recit, W, barres, big_number, dim,
                   echo, gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from vie_ct import LEA, aeroport_bg as _aero


def aeroport_bg():
    return _aero("ARRIVÉES · BAGAGES")
from vol_ct import badge, carte_sombre

MAMAN = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)


def cuisine_fg(d, t):
    s = SS
    d.rectangle([0, 1250 * s, W * s, 1520 * s], fill=(150, 104, 74))
    d.rectangle([0, 1250 * s, W * s, 1280 * s], fill=(175, 125, 90))
    for x in (300, 760):                                                   # deux tasses de café
        d.rounded_rectangle([(x - 30) * s, 1195 * s, (x + 30) * s, 1255 * s], radius=10 * s, fill=WHITE, outline=INK, width=3 * s)


def courbe(img, lt, y0=470):
    """La courbe de SpaceX : 135 $ à l'introduction, 150 $ à l'ouverture, le plus haut, puis la chute de moitié."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([70, y0, 1010, y0 + 720], radius=34, fill=(28, 28, 36))
    d.text((540, y0 + 60), "SPACEX EN BOURSE", font=FA(56), fill=YEL, anchor="mm")
    d.text((540, y0 + 115), "JUIN → FIN JUILLET 2026", font=FA(30), fill=(170, 170, 185), anchor="mm")
    pts = [(140, 135), (240, 150), (330, 161), (430, 185), (520, 200), (620, 160), (720, 130), (820, 110), (930, 100)]
    k = max(0.0, min(1.0, lt / 3.0))
    n = max(2, int(len(pts) * k) + 1)
    xy = [(x, y0 + 640 - (v - 80) * 3.4) for x, v in pts[:n]]
    d.line(xy, fill=(60, 200, 110) if n <= 5 else (230, 80, 80), width=10, joint="curve")
    for (x, v), lab in ((pts[0], "135 $"), (pts[1], "150 $")):
        y = y0 + 640 - (v - 80) * 3.4
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=WHITE)
        d.text((x, y + 44), lab, font=FA(34), fill=WHITE, anchor="mm")
    if lt > 3.0:
        d.text((800, y0 + 250), "− 50 %", font=FA(84), fill=(240, 90, 90), anchor="mm")
        d.text((800, y0 + 320), "DEPUIS LE PLUS HAUT", font=FA(28), fill=(240, 90, 90), anchor="mm")


# ═════════════ 1. ACTU : SpaceX avant Anthropic ═════════════

def maison(t, kpose="neutre", frere=None, z=1.0, center=(540, 1000)):
    return plan(salon_bg, t, kpose, mechant=frere or dict(mouth="flat"), look=FRERE, devant=cuisine_fg, z=z, center=center)


def s_hook(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, arm=0.5, phone=True, devant=cuisine_fg)
    badge(img, 540, 1190, "SON GRAND FRÈRE")
    bubble(img, 540, 570, ["JEUDI, 6 000 €", "SUR ANTHROPIC.", "ET CETTE FOIS TU ME SUIS"], 58, (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def s_couture(lt, dur):
    img = maison(lt, "neutre", dict(mouth="grin", phone=True), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE MÊME QUI LUI DOIT SON LOYER", 46, RED, WHITE, rot=-3, k=(lt - 2.6) / 0.3)
    return flash(img, lt)


def s_montee(lt, dur):
    img = maison(lt, "parle", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "TOUT LE MONDE EN PARLE", 54, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "JEUDI 19 NOVEMBRE", 50, WHITE, INK, rot=2, k=(lt - 1.4) / 0.3)
    return flash(img, lt)


def s_demande(lt, dur):
    img = maison(lt, "parle", dict(mouth="grin" if lt > 1.6 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "ET SI ÇA BAISSE ?", 56, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def s_coup1(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 1.95, 2.15, arm=0.4, devant=cuisine_fg)
    bubble(img, 540, 560, ["ÇA BAISSE PAS.", "REGARDE SPACEX,", "COMME ÇA A DÉCOLLÉ"], 62, lt / 0.25, tail_x=660)
    return flash(img, lt)


def s_geste(lt, dur):
    img = maison(lt, "triste", dict(mouth="grin", arm=0.8), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def s_coup2(lt, dur):
    img = gros_plan_mechant(salon_bg, FRERE, lt, dur, 2.2, 2.4, arm=0.8, devant=cuisine_fg)
    bubble(img, 540, 560, ["T'AS JAMAIS RIEN RISQUÉ.", "C'EST POUR ÇA", "QUE T'AS RIEN"], 60, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def s_silence(lt, dur):
    return maison(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def s_echo(lt, dur):
    img = dim(gros_plan_kevin(salon_bg, lt, dur, devant=cuisine_fg), 0.75)
    echo(img, "JAMAIS RIEN RISQUÉ")
    return img


def s_spacex(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "SPACEX · JUIN 2026", [("Prix d'entrée : 135 $", 0.4, False), ("1er jour : ouvre à 150 $", 2.0, True),
                                             ("Tout le monde s'emballe", 3.6, False)], lt, y0=470, sous="NASDAQ · SPCX")
    return img


def s_chute_spx(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    courbe(img, lt)
    return img


def s_gros(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    barres(img, "QUI A LE PRIX D'ENTRÉE ?", [("LES GROS", 135, "135 $", (60, 200, 110), 0.6),
                                            ("TOI, APRÈS", 160, "+ CHER", (230, 80, 80), 2.6)], lt,
           sous="L'ACTION, TU L'ACHÈTES APRÈS L'OUVERTURE")
    return img


def s_groupe(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=300), 0.85, blur=6, dark=0.6)
    phone_big(img, 600, 900, lt, "22:41", [("Famille", "Groupe Famille", "Kévin : une image", (40, 160, 90)),
                                           ("Famille", "Groupe Famille", "Regarde SpaceX", (40, 160, 90))])
    return img


def s_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000))
    tag(img, 540, 420, "DEVANT TOUTE LA FAMILLE…", 50, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    tag(img, 540, 560, "PERSONNE NE SAIT POUR JEUDI", 46, YEL, INK, rot=2, k=(lt - 3.0) / 0.3)
    return img


def s_maman(lt, dur):
    img = dim(plan(salon_bg, lt, "victoire", kx=300), 0.85, blur=6, dark=0.6)
    phone_big(img, 600, 900, lt, "22:43", [("Famille", "Maman", "Rends d'abord", (220, 80, 140)),
                                           ("Famille", "Maman", "son loyer à Kévin", (220, 80, 140))])
    return img


def s_fin(lt, dur):
    img = dim(plan(salon_bg, lt, devant=cuisine_fg, z=1.1, center=(540, 1150)), 0.6)
    big_number(img, (540, 470), "6 000 €", 150, YEL, "POUR JEUDI, ET TOUJOURS PAS SON LOYER", k=lt / 0.25, rot=-3)
    mention(img, "CECI N'EST PAS UN CONSEIL EN INVESTISSEMENT · CAS TYPE", lt)
    return img


SPACEX = (Recit("test_spacex", "scripts/modele/21_spacex_avant_anthropic.txt", "output/_work_test_spacex/voice_duo.wav",
                compteur=dict(label="CE QUE LUI DOIT SON FRÈRE", depart=800, montant=800, phrase=None)),
          [("Jeudi, je mets", s_hook, ("impact", 1.0)), ("C'est ce que mon grand frère", s_couture, ("whoosh", 0.6)),
           ("Et pourtant, cette fois", s_montee, ("pop", 0.8)), ("Je lui demande juste", s_demande, None),
           ("Ça baisse pas", s_coup1, ("impact", 0.8)), ("Et en rangeant", s_geste, ("whoosh", 0.5)),
           ("Toi, t'as jamais", s_coup2, ("impact", 1.0)), ("Je dis rien", s_silence, None),
           ("Jamais rien risqué", s_echo, ("rate", 0.6)), ("Le soir, je regarde", s_spacex, ("ticks", 0.6)),
           ("Mais alors ceux qui", s_chute_spx, ("rate", 0.8, 3.0)), ("Ce que presque personne", s_gros, ("pop", 0.7)),
           ("Alors j'envoie la courbe", s_groupe, ("notif", 0.8)), ("Honnêtement", s_doute, None),
           ("Deux minutes après", s_maman, ("notif", 0.9)), ("Six mille euros pour jeudi", s_fin, ("impact", 0.9))])


# ═════════════ 2. CONCURRENT reconstruit (8/8) : la robe de mariée dans la soute ═════════════

AGENTE = dict(shirt=(30, 60, 130), pants=(30, 30, 40), hair=(40, 30, 25), long_hair=True, tie=True)
SOEUR = dict(shirt=(230, 120, 160), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
MARIEE = dict(shirt=(252, 252, 250), pants=(252, 252, 250), hair=(110, 70, 40), long_hair=True)
RETOUCHEUSE = dict(shirt=(120, 90, 160), pants=(40, 40, 50), hair=(180, 180, 185), glasses=True)
FILE = [dict(shirt=(90, 140, 90), pants=(40, 40, 50), hair=(60, 40, 30), mouth="flat", sc=0.8),
        dict(shirt=(200, 160, 60), pants=(40, 40, 50), hair=(30, 25, 20), long_hair=True, mouth="flat", sc=0.8),
        dict(shirt=(120, 120, 130), pants=(40, 40, 50), hair=(150, 150, 150), mouth="flat", sc=0.8)]


def comptoir_bag(d, t):
    s = SS
    d.rectangle([560 * s, 1180 * s, W * s, 1500 * s], fill=(200, 205, 215))
    d.rectangle([560 * s, 1180 * s, W * s, 1210 * s], fill=(230, 232, 238))
    d.rounded_rectangle([600 * s, 1230 * s, 1020 * s, 1300 * s], radius=10 * s, fill=(30, 60, 130))
    d.text((810 * s, 1265 * s), "BAGAGES", font=FA(40 * s), fill=WHITE, anchor="mm")


def robe(d, x, y, sc=1.0, tache=True):
    """La robe de mariée (sur cintre), avec la tache de graisse."""
    s = SS

    def P(a, b):
        return ((x + a * sc) * s, (y + b * sc) * s)
    d.line([P(-40, -330), P(0, -360), P(40, -330)], fill=(120, 120, 130), width=int(6 * s))
    d.polygon([P(-55, -330), P(55, -330), P(45, -200), P(-45, -200)], fill=(252, 252, 250), outline=INK)
    d.polygon([P(-45, -200), P(45, -200), P(150, 40), P(-150, 40)], fill=(250, 250, 248), outline=INK)
    for k in range(-2, 3):
        d.line([P(k * 20, -195), P(k * 55, 35)], fill=(225, 225, 230), width=int(3 * s))
    if tache:
        d.ellipse([P(-10, -120), P(80, -40)], fill=(70, 55, 40))
        d.ellipse([P(40, -60), P(100, 0)], fill=(85, 68, 50))


def valise_ouverte(d, t, x=330, y=1530):
    s = SS
    d.rounded_rectangle([(x - 170) * s, (y - 120) * s, (x + 170) * s, y * s], radius=20 * s, fill=(230, 120, 160), outline=INK, width=4 * s)
    d.line([((x - 150) * s, (y - 110) * s), ((x - 40) * s, (y - 30) * s), ((x + 30) * s, (y - 100) * s)], fill=INK, width=6 * s)
    robe(d, x, y - 110, 0.55)


def comptoir(t, kpose="neutre", agente=None, file=False, z=1.0, center=(540, 1000)):
    autres = [(420 + k * 90, FILE[k], {}, 0.7 * k, BASE - 60) for k in range(3)] if file else ()
    return plan(aeroport_bg, t, kpose, kx=270, mechant=agente or dict(mouth="flat"), look=AGENTE, mx=860, autres=autres,
                devant=comptoir_bag, z=z, center=center)


def v_hook(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, arm=0.5, devant=comptoir_bag)
    badge(img, 540, 1190, "L'AGENTE DU COMPTOIR BAGAGES")
    bubble(img, 540, 570, ["1 400 € LA ROBE ?", "LE CONTENU, ON REMBOURSE PAS.", "FALLAIT LA PRENDRE EN CABINE"], 54,
           (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def v_couture(lt, dur):
    img = plan(aeroport_bg, lt, "choc", kx=760, devant=valise_ouverte, z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LA ROBE DE MARIÉE DE SA SŒUR", 48, YEL, INK, rot=-3, k=(lt - 2.2) / 0.3)
    if lt > 4.6:
        tag(img, 540, 560, "TACHÉE DE GRAISSE", 54, RED, WHITE, rot=2, k=(lt - 4.6) / 0.3)
    return flash(img, lt)


def v_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=380, autres=[(720, SOEUR, dict(mouth="grin", arm=0.9), 1.2)],
               z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "LA MISSION DE SA VIE", 54, YEL, INK, rot=-3, k=(lt - 0.6) / 0.3)
    tag(img, 540, 560, "LE MARIAGE EST SAMEDI", 50, GREEN, INK, rot=2, k=(lt - 2.6) / 0.3)
    return flash(img, lt)


def v_demande(lt, dur):
    img = comptoir(lt, "parle", dict(mouth="flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "UN CONSTAT, S'IL VOUS PLAÎT", 48, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def v_coup1(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, 1.95, 2.15, arm=0.4, devant=comptoir_bag)
    bubble(img, 540, 560, ["UNE ROBE EN SOUTE ?", "FALLAIT RÉFLÉCHIR AVANT,", "C'EST PAS MON PROBLÈME"], 56, lt / 0.25,
           tail_x=660)
    return flash(img, lt)


def v_geste(lt, dur):
    img = comptoir(lt, "triste", dict(mouth="grin", arm=0.8), file=True, z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "ELLE EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def v_coup2(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, 2.2, 2.4, arm=0.8, devant=comptoir_bag)
    bubble(img, 540, 560, ["TA SŒUR S'ACHÈTERA", "UNE ROBE CHEZ ZARA,", "COMME TOUT LE MONDE"], 60, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def v_silence(lt, dur):
    return plan(aeroport_bg, lt, "triste", kx=760, devant=valise_ouverte, z=push(lt, dur, 1.0, 1.05))


def v_echo(lt, dur):
    img = dim(gros_plan_kevin(aeroport_bg, lt, dur), 0.75)
    echo(img, "COMME TOUT LE MONDE")
    return img


def v_regle(lt, dur):
    img = dim(plan(aeroport_bg, lt, "neutre", kx=540), 0.9)
    carte_sombre(img, "VALISE EN SOUTE", [("La compagnie paie la valise", 0.4, False),
                                          ("ET ce qu'il y a dedans", 2.0, True),
                                          ("Jusqu'à + de 1 500 €", 3.4, False)], lt, y0=470,
                 sous="CONVENTION DE MONTRÉAL · ARTICLES 17 ET 22")
    return img


def v_demitour(lt, dur):
    img = comptoir(lt, "parle", dict(mouth="o", brows="triste"), file=True, z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE CONSTAT, AVANT DE PARTIR", 50, YEL, INK, rot=-3, k=(lt - 1.6) / 0.3)
    tag(img, 540, 560, "IL NE BOUGE PLUS", 50, WHITE, INK, rot=2, k=(lt - 4.0) / 0.3)
    return flash(img, lt)


def v_retouche(lt, dur):
    img = plan(salon_bg, lt, "neutre", kx=260, autres=[(820, RETOUCHEUSE, dict(mouth="flat", arm=0.5), 0.8)],
               devant=lambda d, t: robe(d, 540, 1480, 1.1, tache=t < 3.0), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "3 NUITS · 400 € DE SA POCHE", 50, YEL, INK, rot=-3, k=(lt - 1.0) / 0.3)
    return img


def v_secret(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=300), 0.85, blur=6, dark=0.6)
    phone_big(img, 620, 900, lt, "21:12", [("Messages", "Ma sœur", "Ma robe est arrivée ?", (220, 80, 140)),
                                           ("Messages", "Moi", "Oui, elle est parfaite", (40, 160, 90))])
    return img


def v_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000))
    tag(img, 540, 420, "ELLE AVAIT LE DROIT DE SAVOIR ?", 48, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def v_mariage(lt, dur):
    tl = REC_VALISE.T.get("gain", 99) - REC_VALISE.T["v_mariage"]
    img = plan(salon_bg, lt, "victoire", kx=300, autres=[(700, MARIEE, dict(mouth="grin", arm=0.6), 1.2)],
               devant=lambda d, t: robe(d, 700, 1580, 0.95, tache=False), z=1.0)
    tag(img, 540, 420, "SAMEDI", 66, YEL, INK, rot=-3, k=lt / 0.3)
    if lt > tl:
        tag(img, 540, 560, "LUNDI : +400 € REMBOURSÉS", 50, GREEN, INK, rot=2, k=(lt - tl) / 0.3)
    return flash(img, lt)


def v_fin(lt, dur):
    img = dim(plan(salon_bg, lt, z=1.0), 0.6)
    big_number(img, (540, 470), "1 400 €", 150, GREEN, "ET ELLE A JAMAIS SU", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CONVENTION DE MONTRÉAL ART. 17, 22 ET 31", lt)
    return img


REC_VALISE = Recit("test_valise", "scripts/modele/22_valise_cassee.txt", "output/_work_test_valise/voice_duo.wav",
                   compteur=dict(label="REMBOURSÉ À KÉVIN", depart=0, montant=400, phrase="la compagnie me rembourse"))
VALISE = (REC_VALISE,
          [("Mille quatre cents euros la robe", v_hook, ("impact", 1.0)), ("C'est ce que l'agente", v_couture, ("whoosh", 0.6)),
           ("Et pourtant j'étais", v_montee, ("pop", 0.8)), ("Je lui demande juste", v_demande, None),
           ("Une robe dans", v_coup1, ("impact", 0.8)), ("Et en appelant", v_geste, ("whoosh", 0.5)),
           ("Ta sœur s'achètera", v_coup2, ("impact", 1.0)), ("Je dis rien", v_silence, None),
           ("Comme tout le monde", v_echo, ("rate", 0.6)), ("Sauf que ce que presque", v_regle, ("pop", 0.8)),
           ("Mais alors il faut quoi", v_demitour, ("whoosh", 0.6)), ("Le soir, je trouve", v_retouche, ("ticks", 0.6)),
           ("Et à ma sœur", v_secret, ("notif", 0.7)), ("Honnêtement", v_doute, None),
           ("Samedi, elle remonte", v_mariage, ("succes", 0.8)), ("Mille quatre cents euros de robe", v_fin, ("impact", 0.9))])


# ═════════════ 3. INVENTÉ : la prime de fin de CDD ═════════════

DRH = dict(shirt=(60, 60, 70), pants=(36, 36, 44), hair=(90, 80, 70), glasses=True, tie=True)
GARS = [dict(shirt=(230, 120, 40), pants=(40, 40, 60), hair=(30, 25, 20), mouth="flat", sc=0.85),
        dict(shirt=(230, 120, 40), pants=(40, 40, 60), hair=(120, 70, 30), mouth="flat", sc=0.85)]
GILET = dict(shirt=(230, 120, 40))


def quai(t, kpose="neutre", drh=None, gars=True, z=1.0, center=(540, 1000)):
    autres = [(560, GARS[0], {}, 1.3, BASE - 60), (680, GARS[1], {}, 2.1, BASE - 60)] if gars else ()
    return plan(entrepot_bg, t, kpose, mechant=drh or dict(mouth="flat"), look=DRH, mx=860, autres=autres, z=z,
                center=center, **GILET)


def c_hook(lt, dur):
    img = gros_plan_mechant(entrepot_bg, DRH, lt, dur, arm=0.5)
    badge(img, 540, 1190, "LE DRH DE L'ENTREPÔT")
    bubble(img, 540, 570, ["1 140 € DE PRIME ?", "T'AVAIS QU'À SIGNER", "LE CDI. C'EST ZÉRO"], 60, (lt + 0.3) / 0.3,
           tail_x=660)
    return shake(img, lt)


def c_couture(lt, dur):
    img = quai(lt, "choc", dict(mouth="grin", arm=0.4), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE DERNIER JOUR DU CDD", 54, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "AUCUN CDI PROPOSÉ", 52, RED, WHITE, rot=2, k=(lt - 3.0) / 0.3)
    return flash(img, lt)


def c_montee(lt, dur):
    img = quai(lt, "victoire", dict(mouth="flat"), gars=True, z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "6 MOIS · JAMAIS UN RETARD", 52, GREEN, INK, rot=-3, k=(lt - 0.2) / 0.3)
    tag(img, 540, 560, "MÊME LES SAMEDIS DE DÉCEMBRE", 44, YEL, INK, rot=2, k=(lt - 1.8) / 0.3)
    return flash(img, lt)


def c_demande(lt, dur):
    img = quai(lt, "parle", dict(mouth="grin" if lt > 1.4 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "MA PRIME DE FIN DE CONTRAT ?", 48, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def c_coup1(lt, dur):
    img = gros_plan_mechant(entrepot_bg, DRH, lt, dur, 1.95, 2.15, arm=0.4)
    bubble(img, 540, 560, ["LA PRIME, C'EST POUR", "CEUX QUI LA MÉRITENT.", "TOI, T'AS CRACHÉ DESSUS"], 56, lt / 0.25,
           tail_x=660)
    return flash(img, lt)


def c_geste(lt, dur):
    img = plan(bureau_bg, lt, "triste", mechant=dict(mouth="grin", arm=0.8), look=DRH, mx=820, z=push(lt, dur, 1.1, 1.2),
               **GILET)
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def c_coup2(lt, dur):
    img = gros_plan_mechant(bureau_bg, DRH, lt, dur, 2.2, 2.4, arm=0.8)
    bubble(img, 540, 560, ["UN CDD DE PLUS OU DE MOINS,", "PERSONNE VA TE", "REGRETTER ICI"], 56, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def c_silence(lt, dur):
    return quai(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def c_echo(lt, dur):
    img = dim(gros_plan_kevin(entrepot_bg, lt, dur, **GILET), 0.75)
    echo(img, "PERSONNE VA TE REGRETTER")
    return img


def c_regle(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **GILET), 0.9)
    carte_sombre(img, "FIN DE CDD", [("10 % de tout ce que tu as gagné", 0.4, True),
                                     ("Sauf si tu as refusé un vrai CDI", 2.6, False),
                                     ("proposé AVANT la fin du contrat", 3.8, False)], lt, y0=470,
                 sous="CODE DU TRAVAIL · L1243-8 ET L1243-10")
    return img


def c_preuve(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **GILET), 0.85)
    for i, (txt, t0) in enumerate([("PAS UN MAIL", 0.8), ("PAS UNE LETTRE", 1.6), ("RIEN", 2.4)]):
        tag(img, 540, 520 + i * 150, txt, 66, RED, WHITE, rot=(-3, 2, -2)[i], k=(lt - t0) / 0.25)
    return img


def c_calcul(lt, dur):
    img = dim(plan(salon_bg, lt, "neutre", kx=540, **GILET), 0.9)
    carte_sombre(img, "LE CALCUL", [("6 mois × 1 900 € brut", 0.3, False), ("= 11 400 €", 1.2, False),
                                    ("× 10 % = 1 140 €", 2.2, True)], lt, y0=470)
    return img


def c_copie(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **GILET), 0.85)
    card(img, 540, 760, "LETTRE RECOMMANDÉE", "COPIE : 7 COLLÈGUES", [("1. Fin de CDD le 30", "", 0.3, False),
                                                                    ("2. Aucun CDI proposé", "", 1.0, False),
                                                                    ("3. Prime de 10 % · L1243-8", "", 1.7, True)], lt, rot=2)
    return img


def c_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000), **GILET)
    tag(img, 540, 420, "LUI DÉCLARER LA GUERRE ?", 52, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def c_twist(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=300, **GILET)
    phone_big(img, 620, 920, lt, "11:02", [("Banque", "Virement reçu", "+1 140,00 €", (60, 110, 230)),
                                           ("Appel", "DRH Entrepôt", "Appel entrant…", (40, 160, 90))])
    return flash(img, lt)


def c_fin(lt, dur):
    img = dim(plan(entrepot_bg, lt, z=1.0), 0.6)
    big_number(img, (540, 470), "1 140 €", 150, GREEN, "ET CETTE FOIS, C'EST LUI QUI REFUSE", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CODE DU TRAVAIL L1243-8 ET L1243-10", lt)
    return img


CDD = (Recit("test_cdd", "scripts/modele/23_cdd_precarite.txt", "output/_work_test_cdd/voice_duo.wav",
             compteur=dict(label="DÛ PAR L'ENTREPÔT", depart=0, montant=1140, phrase="Six mois à mille")),
       [("Mille cent quarante euros de prime", c_hook, ("impact", 1.0)), ("C'est ce que le DRH", c_couture, ("whoosh", 0.6)),
        ("Et pourtant j'avais", c_montee, ("pop", 0.8)), ("Je lui demande juste", c_demande, None),
        ("La prime, c'est pour", c_coup1, ("impact", 0.8)), ("Et en refermant", c_geste, ("whoosh", 0.5)),
        ("Un CDD de plus", c_coup2, ("impact", 1.0)), ("Je dis rien", c_silence, None),
        ("Personne va te regretter", c_echo, ("rate", 0.6)), ("Sauf qu'à la fin", c_regle, ("pop", 0.8)),
        ("Mais alors comment il prouve", c_preuve, ("impact", 0.6)), ("Six mois à mille", c_calcul, ("ticks", 0.6)),
        ("Alors j'envoie la lettre", c_copie, ("notif", 0.7)), ("Honnêtement", c_doute, None),
        ("Deux semaines après", c_twist, ("succes", 0.8)), ("Mille cent quarante euros, et", c_fin, ("impact", 0.9))])

if __name__ == "__main__":
    rec, beats = {"spacex": SPACEX, "valise": VALISE, "cdd": CDD}[sys.argv[1]]
    rec.fabriquer(beats)
