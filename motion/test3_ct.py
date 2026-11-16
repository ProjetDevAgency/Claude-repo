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


# ═════════════ 2. CONCURRENT : la valise cassée ═════════════

AGENTE = dict(shirt=(30, 60, 130), pants=(30, 30, 40), hair=(40, 30, 25), long_hair=True, tie=True)
FILE = [dict(shirt=(90, 140, 90), pants=(40, 40, 50), hair=(60, 40, 30), mouth="flat", sc=0.8),
        dict(shirt=(200, 160, 60), pants=(40, 40, 50), hair=(30, 25, 20), long_hair=True, mouth="flat", sc=0.8),
        dict(shirt=(120, 120, 130), pants=(40, 40, 50), hair=(150, 150, 150), mouth="flat", sc=0.8)]


def comptoir_bag(d, t):
    s = SS
    d.rectangle([560 * s, 1180 * s, W * s, 1500 * s], fill=(200, 205, 215))
    d.rectangle([560 * s, 1180 * s, W * s, 1210 * s], fill=(230, 232, 238))
    d.rounded_rectangle([600 * s, 1230 * s, 1020 * s, 1300 * s], radius=10 * s, fill=(30, 60, 130))
    d.text((810 * s, 1265 * s), "BAGAGES", font=FA(40 * s), fill=WHITE, anchor="mm")


def valise(d, t, x=150, y=1520):
    s = SS
    d.rounded_rectangle([(x - 90) * s, (y - 300) * s, (x + 90) * s, (y - 20) * s], radius=24 * s, fill=(230, 120, 160), outline=INK, width=4 * s)
    d.line([((x - 70) * s, (y - 240) * s), ((x + 10) * s, (y - 160) * s), ((x - 30) * s, (y - 80) * s)], fill=INK, width=6 * s)
    d.rectangle([(x - 30) * s, (y - 340) * s, (x + 30) * s, (y - 300) * s], fill=(80, 80, 90))
    d.ellipse([(x + 50) * s, (y - 30) * s, (x + 80) * s, y * s], fill=INK)            # une seule roue


def comptoir(t, kpose="neutre", agente=None, file=False, z=1.0, center=(540, 1000)):
    autres = [(420 + k * 90, FILE[k], {}, 0.7 * k, BASE - 60) for k in range(3)] if file else ()
    return plan(aeroport_bg, t, kpose, kx=270, mechant=agente or dict(mouth="flat"), look=AGENTE, mx=860, autres=autres,
                devant=lambda d, tt: (comptoir_bag(d, tt), valise(d, tt)), z=z, center=center)


def v_hook(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, arm=0.5, devant=comptoir_bag)
    badge(img, 540, 1190, "L'AGENTE DU COMPTOIR BAGAGES")
    bubble(img, 540, 570, ["220 € POUR TA VALISE ?", "ELLE ÉTAIT DÉJÀ ABÎMÉE,", "ON REMBOURSE RIEN"], 58, (lt + 0.3) / 0.3,
           tail_x=660)
    return shake(img, lt)


def v_couture(lt, dur):
    img = comptoir(lt, "choc", dict(mouth="grin", arm=0.4), file=True, z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "DEVANT TOUTE LA FILE", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "LA ROUE ARRACHÉE", 50, RED, WHITE, rot=2, k=(lt - 2.6) / 0.3)
    return flash(img, lt)


def v_montee(lt, dur):
    img = plan(aeroport_bg, lt, "victoire", kx=380, autres=[(700, LEA, dict(mouth="grin", arm=0.9), 1.2)],
               z=push(lt, dur, 1.0, 1.08))
    tag(img, 540, 420, "SES PREMIÈRES VRAIES VACANCES", 48, YEL, INK, rot=-3, k=(lt - 0.2) / 0.3)
    tag(img, 540, 560, "PAYÉES AVEC SES HEURES SUP", 46, GREEN, INK, rot=2, k=(lt - 1.8) / 0.3)
    return flash(img, lt)


def v_demande(lt, dur):
    img = comptoir(lt, "parle", dict(mouth="flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "UN FORMULAIRE, S'IL VOUS PLAÎT", 46, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def v_coup1(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, 1.95, 2.15, arm=0.4, devant=comptoir_bag)
    bubble(img, 540, 560, ["UN FORMULAIRE POUR UNE ROUE ?", "LES ROUES, ÇA CASSE,", "C'EST L'USURE"], 54, lt / 0.25, tail_x=660)
    return flash(img, lt)


def v_geste(lt, dur):
    img = comptoir(lt, "triste", dict(mouth="grin", arm=0.8), file=True, z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "ELLE EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def v_coup2(lt, dur):
    img = gros_plan_mechant(aeroport_bg, AGENTE, lt, dur, 2.2, 2.4, arm=0.8, devant=comptoir_bag)
    bubble(img, 540, 560, ["LES GENS COMME TOI,", "ÇA DEVRAIT VOYAGER", "AVEC UN SAC DE SPORT"], 58, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def v_silence(lt, dur):
    return plan(aeroport_bg, lt, "triste", kx=540, devant=lambda d, t: valise(d, t, x=760), z=push(lt, dur, 1.0, 1.05))


def v_echo(lt, dur):
    img = dim(gros_plan_kevin(aeroport_bg, lt, dur), 0.75)
    echo(img, "UN SAC DE SPORT")
    return img


def v_regle(lt, dur):
    img = dim(plan(aeroport_bg, lt, "neutre", kx=540), 0.9)
    carte_sombre(img, "VALISE ABÎMÉE EN SOUTE", [("La compagnie est responsable", 0.4, False),
                                                 ("L'usure ? À ELLE de la prouver", 2.0, True)], lt, y0=470,
                 sous="CONVENTION DE MONTRÉAL · ARTICLE 17")
    return img


def v_demitour(lt, dur):
    img = comptoir(lt, "parle", dict(mouth="o", brows="triste"), file=True, z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "LE CONSTAT AU COMPTOIR", 54, YEL, INK, rot=-3, k=(lt - 2.4) / 0.3)
    return flash(img, lt)


def v_file(lt, dur):
    img = comptoir(lt, "neutre", dict(mouth="flat"), file=True, z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "20 PERSONNES · 15 MINUTES", 52, RED, WHITE, rot=-3, k=(lt - 0.2) / 0.3)
    return img


def v_doute(lt, dur):
    img = plan(aeroport_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000))
    tag(img, 540, 420, "TOUT ÇA POUR UNE VALISE ?", 52, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def v_reclam(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.85)
    card(img, 540, 760, "RÉCLAMATION", "SOUS 7 JOURS", [("1. Le constat du comptoir", "", 0.3, False),
                                                        ("2. Les photos", "", 1.0, False),
                                                        ("3. La facture de la valise", "", 1.7, True)], lt, rot=2)
    return img


def v_twist(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=300)
    phone_big(img, 620, 920, lt, "09:15", [("Mail", "Remboursement", "+220,00 €", (60, 110, 230))])
    return flash(img, lt)


def v_fin(lt, dur):
    img = dim(plan(aeroport_bg, lt, z=1.0), 0.6)
    big_number(img, (540, 470), "220 €", 150, GREEN, "POUR UNE VALISE « DÉJÀ ABÎMÉE »", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CONVENTION DE MONTRÉAL ART. 17 ET 31", lt)
    return img


VALISE = (Recit("test_valise", "scripts/modele/22_valise_cassee.txt", "output/_work_test_valise/voice_duo.wav",
                compteur=dict(label="REMBOURSÉ À KÉVIN", depart=0, montant=220, phrase="Dix jours après")),
          [("Deux cent vingt euros", v_hook, ("impact", 1.0)), ("C'est ce que l'agente", v_couture, ("whoosh", 0.6)),
           ("Et pourtant je revenais", v_montee, ("pop", 0.8)), ("Je lui demande juste", v_demande, None),
           ("Un formulaire pour", v_coup1, ("impact", 0.8)), ("Et en appelant", v_geste, ("whoosh", 0.5)),
           ("Les gens comme toi", v_coup2, ("impact", 1.0)), ("Je dis rien", v_silence, None),
           ("Un sac de sport", v_echo, ("rate", 0.6)), ("Sauf que la loi", v_regle, ("pop", 0.8)),
           ("Mais alors comment", v_demitour, ("whoosh", 0.6)), ("Vingt personnes", v_file, ("impact", 0.6)),
           ("Honnêtement", v_doute, None), ("Le soir même", v_reclam, ("notif", 0.7)),
           ("Dix jours après", v_twist, ("succes", 0.8)), ("Deux cent vingt euros, pour", v_fin, ("impact", 0.9))])


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
