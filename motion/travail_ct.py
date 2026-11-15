"""Où va ton argent ? — deux vidéos travail, méthode v3 (Kévin raconte, le chef a sa voix).
    python3 motion/travail_ct.py tenue    → l'entretien de la tenue obligatoire (scripts/modele/15_tenue_travail.dial)
    python3 motion/travail_ct.py avance   → l'arrivée en avance imposée (scripts/modele/16_arriver_avance.dial)
"""
import sys

from cartoon import FA, bubble, card, flash, room, shake
from heures_sup_ct import boutique_bg
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, RED, SS, WHITE, YEL, ImageDraw, Recit, W, big_number, dim, echo,
                   gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from vol_ct import badge, carte_sombre

POLO = dict(shirt=(200, 40, 40), hood=None)                     # Kévin en polo rouge du fast-food
GERANT = dict(shirt=(40, 40, 48), pants=(36, 36, 44), hair=(60, 45, 30), tie=False, glasses=True)
RESP = dict(shirt=(30, 70, 140), pants=(36, 36, 44), hair=(35, 30, 25), tie=True)
COLLEGUE = [dict(shirt=(200, 40, 40), pants=(40, 40, 50), hair=(30, 25, 20), mouth="flat", sc=0.85),
            dict(shirt=(200, 40, 40), pants=(40, 40, 50), hair=(110, 70, 40), long_hair=True, mouth="flat", sc=0.85)]
VENDEUR = [dict(shirt=(250, 250, 250), pants=(40, 40, 50), hair=(30, 25, 20), mouth="flat", sc=0.85),
           dict(shirt=(250, 250, 250), pants=(40, 40, 50), hair=(120, 60, 30), long_hair=True, mouth="flat", sc=0.85)]
_bg = {}


# ───── décors ─────

def fastfood_bg():
    if "f" not in _bg:
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        for y in range(380, 1180, 60):                    # carrelage rouge et blanc
            for x in range(0, W, 60):
                d.rectangle([x * s, y * s, (x + 58) * s, (y + 58) * s],
                            fill=(235, 70, 60) if (x // 60 + y // 60) % 2 else (250, 245, 240))
        _bg["f"] = im
    return _bg["f"]


def comptoir_ff(d, t):
    s = SS
    d.rectangle([540 * s, 1180 * s, W * s, 1500 * s], fill=(70, 70, 80))
    d.rectangle([540 * s, 1180 * s, W * s, 1212 * s], fill=(180, 180, 190))
    d.rounded_rectangle([880 * s, 1080 * s, 1040 * s, 1180 * s], radius=12 * s, fill=(50, 50, 60))  # caisse
    d.rectangle([900 * s, 1100 * s, 1020 * s, 1140 * s], fill=(120, 220, 160))


def comptoir_mag(d, t):
    s = SS
    d.rectangle([560 * s, 1180 * s, W * s, 1500 * s], fill=(120, 80, 56))
    d.rectangle([560 * s, 1180 * s, W * s, 1210 * s], fill=(150, 104, 74))


def badgeuse(img, x, y, heure, col=(240, 80, 80), k=1.0):
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 170, y - 110, x + 170, y + 110], radius=24, fill=(70, 74, 86), outline=INK, width=6)
    d.rounded_rectangle([x - 140, y - 80, x + 140, y + 10], radius=12, fill=(15, 20, 25))
    d.text((x, y - 35), heure, font=FA(70), fill=col, anchor="mm")
    d.text((x, y + 55), "BADGEUSE", font=FA(30), fill=(200, 200, 210), anchor="mm")


# ═════════════ 1. la tenue de travail ═════════════

def ff(t, kpose="neutre", gerant=None, equipe=True, z=1.0, center=(540, 1000), **kx):
    autres = [(560, COLLEGUE[0], {}, 1.3, BASE - 60), (680, COLLEGUE[1], {}, 2.1, BASE - 60)] if equipe else ()
    return plan(fastfood_bg, t, kpose, mechant=gerant or dict(mouth="flat"), look=GERANT, mx=860, autres=autres,
                devant=comptoir_ff, z=z, center=center, **{**POLO, **kx})


def t_hook(lt, dur):
    img = gros_plan_mechant(fastfood_bg, GERANT, lt, dur, arm=0.5, devant=comptoir_ff)
    badge(img, 540, 1190, "LE GÉRANT DU FAST-FOOD")
    bubble(img, 540, 570, ["720 € DE LESSIVE ?", "C'EST TON PROBLÈME,", "PAS LE MIEN"], 60, (lt + 0.3) / 0.3, tail_x=660)
    return shake(img, lt)


def t_couture(lt, dur):
    img = ff(lt, "neutre", dict(mouth="grin", arm=0.3), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "DEVANT TOUTE L'ÉQUIPE", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    tag(img, 540, 560, "POLO OBLIGATOIRE · LAVÉ CHEZ LUI", 44, WHITE, INK, rot=2, k=(lt - 2.6) / 0.3)
    return flash(img, lt)


def t_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=540, z=push(lt, dur, 1.0, 1.08), center=(540, 1000), **POLO)
    for i, (txt, col, t0) in enumerate([("SON PREMIER CDI", YEL, 0.2), ("FIER DE SON POLO", GREEN, 1.6)]):
        tag(img, 540, 420 + i * 140, txt, 56, col, INK, rot=(-4, 3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def t_demande(lt, dur):
    img = ff(lt, "parle", dict(mouth="grin" if lt > 1.4 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "ET POUR LA LESSIVE ?", 56, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def t_coup1(lt, dur):
    img = gros_plan_mechant(fastfood_bg, GERANT, lt, dur, 1.95, 2.15, arm=0.4, devant=comptoir_ff)
    bubble(img, 540, 560, ["C'EST UN POLO,", "PAS UNE ROBE", "DE MARIÉE"], 64, lt / 0.25, tail_x=660)
    return flash(img, lt)


def t_geste(lt, dur):
    img = ff(lt, "triste", dict(mouth="grin", arm=0.8), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def t_coup2(lt, dur):
    img = gros_plan_mechant(fastfood_bg, GERANT, lt, dur, 2.2, 2.4, arm=0.8, devant=comptoir_ff)
    bubble(img, 540, 560, ["PAS CONTENT ?", "J'AI QUINZE CV", "SUR MON BUREAU"], 64, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def t_silence(lt, dur):
    return ff(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def t_echo(lt, dur):
    img = dim(gros_plan_kevin(fastfood_bg, lt, dur, devant=comptoir_ff, **POLO), 0.75)
    echo(img, "QUINZE CV SUR SON BUREAU")
    return img


def t_regle(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **POLO), 0.9)
    carte_sombre(img, "LA RÈGLE", [("Tenue imposée par le patron", 0.3, False), ("= entretien payé par lui", 1.8, True),
                                   ("Indemnité ou remboursement", 3.2, False)], lt, y0=470,
                 sous="COUR DE CASSATION · 21 MAI 2008")
    return img


def t_calcul(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **POLO), 0.9)
    carte_sombre(img, "CE QUE ÇA COÛTE", [("1 machine par jour de boulot", 0.3, False),
                                          ("≈ 1 € : lessive, eau, électricité", 1.6, False),
                                          ("= 240 € par an", 3.0, True)], lt, y0=470)
    return img


def t_trois(lt, dur):
    img = dim(plan(salon_bg, lt, "neutre", kx=540, **POLO), 0.85)
    big_number(img, (540, 560), "240 € × 3 ANS", 110, YEL, "ÇA SE RÉCLAME SUR 3 ANS", k=lt / 0.3)
    return img


def t_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000), **POLO)
    tag(img, 540, 420, "PASSER POUR UN RADIN ?", 54, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def t_mail(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540, **POLO), 0.85)
    card(img, 540, 760, "MAIL AU GÉRANT", "3 PHRASES", [("1. Tenue obligatoire", "", 0.3, False),
                                                       ("2. Cass. soc. 21/05/2008", "", 1.0, False),
                                                       ("3. Remboursement sur 3 ans", "", 1.7, True)], lt, rot=2)
    return img


def t_twist(lt, dur):
    img = plan(fastfood_bg, lt, "victoire", autres=[(560, COLLEGUE[0], dict(arms_up=True, mouth="grin"), 1.3, BASE - 60),
                                                    (720, COLLEGUE[1], dict(arms_up=True, mouth="grin"), 2.1, BASE - 60)],
               z=1.0, center=(540, 1000), **POLO)
    d = ImageDraw.Draw(img)
    k = min(1.0, lt / 0.3)
    if k > 0:
        d.rectangle([280, 380, 800, 600], fill=(252, 252, 248), outline=INK, width=6)
        d.text((540, 440), "PRIME D'ENTRETIEN", font=FA(52), fill=INK, anchor="mm")
        d.text((540, 520), "POUR TOUTE L'ÉQUIPE", font=FA(40), fill=RED, anchor="mm")
        d.ellipse([520, 375, 560, 415], fill=(220, 40, 40), outline=INK, width=4)
    if lt > 2.0:
        tag(img, 540, 690, "12 POLOS, 12 PRIMES", 50, GREEN, INK, rot=-3, k=(lt - 2.0) / 0.3)
    return flash(img, lt)


def t_gerant(lt, dur):
    img = ff(lt, "neutre", dict(mouth="o", brows="triste"), z=push(lt, dur, 1.05, 1.1))
    tag(img, 540, 420, "IL DIT PLUS RIEN", 56, WHITE, INK, rot=-3, k=(lt - 0.6) / 0.3)
    return img


def t_chute(lt, dur):
    img = dim(plan(fastfood_bg, lt, devant=comptoir_ff, z=1.1, center=(700, 1100)), 0.6)   # pas de visage sous le texte
    big_number(img, (540, 470), "720 €", 150, GREEN, "C'EST LUI QUI PAIE LA MACHINE", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · COUR DE CASSATION, 21 MAI 2008, N° 06-44.044", lt)
    return img


TENUE = (Recit("droits_tenue", "scripts/modele/15_tenue_travail.txt", "output/_work_droits_tenue/voice_duo.wav",
               compteur=dict(label="DÛ PAR LE GÉRANT", depart=0, montant=720, phrase="se réclame sur trois")),
         [("T'as dépensé", t_hook, ("impact", 1.0)), ("C'est ce que le gérant", t_couture, ("whoosh", 0.6)),
          ("Et pourtant j'étais fier", t_montee, ("pop", 0.8)), ("Je demande juste", t_demande, None),
          ("C'est un polo", t_coup1, ("impact", 0.8)), ("Et en refermant", t_geste, ("whoosh", 0.5)),
          ("Pas content", t_coup2, ("impact", 1.0)), ("Je dis rien", t_silence, None),
          ("Quinze CV sur son bureau", t_echo, ("rate", 0.6)), ("Sauf que ce polo", t_regle, ("pop", 0.8)),
          ("Mais alors ça fait combien", t_calcul, ("ticks", 0.6)), ("Ce que presque personne", t_trois, None),
          ("Honnêtement", t_doute, None), ("Alors j'envoie un mail", t_mail, ("notif", 0.7)),
          ("Le lundi, une feuille", t_twist, ("succes", 0.8)), ("Le gérant passe", t_gerant, None),
          ("Sept cent vingt euros de lessive, et", t_chute, ("impact", 0.9))])


# ═════════════ 2. l'arrivée en avance ═════════════

def mag(t, kpose="neutre", resp=None, equipe=True, z=1.0, center=(540, 1000), **kx):
    autres = [(540, VENDEUR[0], {}, 1.3, BASE - 60), (660, VENDEUR[1], {}, 2.1, BASE - 60)] if equipe else ()
    return plan(boutique_bg, t, kpose, mechant=resp or dict(mouth="flat"), look=RESP, mx=860, autres=autres,
                devant=comptoir_mag, z=z, center=center, **kx)


def a_hook(lt, dur):
    img = gros_plan_mechant(boutique_bg, RESP, lt, dur, arm=0.5, devant=comptoir_mag)
    badge(img, 540, 1190, "LE RESPONSABLE DU MAGASIN")
    bubble(img, 540, 570, ["UN QUART D'HEURE GRATUIT", "TOUS LES MATINS,", "SINON LA PORTE"], 58, (lt + 0.3) / 0.3,
           tail_x=660)
    return shake(img, lt)


def a_couture(lt, dur):
    img = mag(lt, "neutre", dict(mouth="grin", arm=0.3), z=push(lt, dur, 1.0, 1.06))
    tag(img, 540, 420, "BRIEFING À 8 H 45", 56, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    badgeuse(img, 540, 650, "09:00", k=(lt - 2.4) / 0.3)
    return flash(img, lt)


def a_montee(lt, dur):
    img = plan(salon_bg, lt, "victoire", kx=540, z=push(lt, dur, 1.0, 1.08), center=(540, 1000))
    for i, (txt, col, t0) in enumerate([("SON PREMIER VRAI POSTE", YEL, 0.2), ("IL VEUT BIEN FAIRE", GREEN, 1.6)]):
        tag(img, 540, 420 + i * 140, txt, 56, col, INK, rot=(-4, 3)[i], k=(lt - t0) / 0.3)
    return flash(img, lt)


def a_demande(lt, dur):
    img = mag(lt, "parle", dict(mouth="grin" if lt > 1.4 else "flat"), z=push(lt, dur, 1.05, 1.12))
    tag(img, 540, 420, "CE QUART D'HEURE EST PAYÉ ?", 50, WHITE, INK, rot=-3, k=(lt - 0.2) / 0.3)
    return flash(img, lt)


def a_coup1(lt, dur):
    img = gros_plan_mechant(boutique_bg, RESP, lt, dur, 1.95, 2.15, arm=0.4, devant=comptoir_mag)
    bubble(img, 540, 560, ["UN QUART D'HEURE, C'EST RIEN.", "TU VAS PAS PLEURER", "POUR UN CAFÉ"], 56, lt / 0.25, tail_x=660)
    return flash(img, lt)


def a_geste(lt, dur):
    img = mag(lt, "triste", dict(mouth="grin", arm=0.8), z=push(lt, dur, 1.1, 1.2))
    tag(img, 540, 420, "IL EN RAJOUTE", 56, RED, WHITE, rot=-3, k=(lt - 0.4) / 0.3)
    return flash(img, lt)


def a_coup2(lt, dur):
    img = gros_plan_mechant(boutique_bg, RESP, lt, dur, 2.2, 2.4, arm=0.8, devant=comptoir_mag)
    bubble(img, 540, 560, ["LES GARS QUI COMPTENT", "LEURS MINUTES, ÇA FINIT", "JAMAIS CHEF"], 58, lt / 0.25, tail_x=660)
    return shake(flash(img, lt), lt)


def a_silence(lt, dur):
    return mag(lt, "triste", dict(mouth="grin"), z=push(lt, dur, 1.0, 1.04))


def a_echo(lt, dur):
    img = dim(gros_plan_kevin(boutique_bg, lt, dur, devant=comptoir_mag), 0.75)
    echo(img, "ÇA FINIT JAMAIS CHEF")
    return img


def a_regle(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "C'EST DU TRAVAIL SI…", [("Tu es là, à sa disposition", 0.3, False), ("Tu suis ses ordres", 1.4, False),
                                               ("Tu ne peux pas partir", 2.5, False), ("= payé", 3.6, True)], lt, y0=440,
                 sous="CODE DU TRAVAIL · ARTICLE L3121-1")
    return img


def a_preuve(lt, dur):
    img = mag(lt, "telephone", dict(mouth="flat"), equipe=False, z=push(lt, dur, 1.0, 1.06))
    badgeuse(img, 540, 520, "09:00", k=1.0)
    if lt > 2.6:
        tag(img, 540, 720, "PHOTO DE L'HORLOGE · CHAQUE MATIN", 42, YEL, INK, rot=-3, k=(lt - 2.6) / 0.3)
    return img


def a_calcul(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.9)
    carte_sombre(img, "LE CALCUL", [("15 min × 5 jours × 47 semaines", 0.3, False), ("= 58 h par an", 1.4, False),
                                    ("Réclamable sur 3 ans", 2.6, True)], lt, y0=470, sous="CODE DU TRAVAIL · L3245-1")
    return img


def a_doute(lt, dur):
    img = plan(salon_bg, lt, "triste", kx=540, z=push(lt, dur, 1.1, 1.18), center=(540, 1000))
    tag(img, 540, 420, "C'EST QUE 15 MINUTES ?", 54, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
    return img


def a_mail(lt, dur):
    img = dim(plan(salon_bg, lt, "telephone", kx=540), 0.85)
    card(img, 540, 760, "MAIL AU RESPONSABLE", "3 PHRASES", [("1. Briefing imposé à 8 h 45", "", 0.3, False),
                                                            ("2. Photos de l'horloge", "", 1.0, False),
                                                            ("3. Rappel de salaire sur 3 ans", "", 1.7, True)], lt, rot=2)
    return img


def a_twist(lt, dur):
    img = mag(lt, "victoire", dict(mouth="flat"), z=1.0)
    badgeuse(img, 540, 560, "08:45", col=(90, 230, 120), k=lt / 0.3)
    tag(img, 540, 760, "POUR TOUT LE MONDE", 54, GREEN, INK, rot=-3, k=(lt - 1.0) / 0.3)
    return flash(img, lt)


def a_chef(lt, dur):
    img = mag(lt, "parle", dict(mouth="o", brows="triste"), z=push(lt, dur, 1.05, 1.1))
    tag(img, 540, 420, "KÉVIN · RESPONSABLE DU BRIEFING", 46, YEL, INK, rot=-3, k=(lt - 0.3) / 0.3)
    return img


def a_chute(lt, dur):
    img = dim(plan(boutique_bg, lt, devant=comptoir_mag, z=1.1, center=(700, 1100)), 0.6)   # pas de visage sous le texte
    big_number(img, (540, 470), "2 100 €", 150, GREEN, "POUR LE GARS QUI COMPTAIT SES MINUTES", k=lt / 0.25, rot=-3)
    mention(img, "CAS TYPE · CODE DU TRAVAIL L3121-1 ET L3245-1 · SMIC BRUT", lt)
    return img


AVANCE = (Recit("droits_avance", "scripts/modele/16_arriver_avance.txt", "output/_work_droits_avance/voice_duo.wav",
                compteur=dict(label="DÛ PAR LE MAGASIN", depart=0, montant=2100, phrase="se réclame sur trois")),
          [("Tu me fais cadeau", a_hook, ("impact", 1.0)), ("C'est ce que le responsable", a_couture, ("whoosh", 0.6)),
           ("Et pourtant j'étais content", a_montee, ("pop", 0.8)), ("Je demande juste", a_demande, None),
           ("Un quart d'heure, c'est rien", a_coup1, ("impact", 0.8)), ("Et en éteignant", a_geste, ("whoosh", 0.5)),
           ("Les gars qui comptent", a_coup2, ("impact", 1.0)), ("Je dis rien", a_silence, None),
           ("Ça finit jamais chef", a_echo, ("rate", 0.6)), ("Sauf que le Code", a_regle, ("pop", 0.8)),
           ("Mais alors comment je prouve", a_preuve, ("ticks", 0.6)), ("Cinquante-huit heures", a_calcul, None),
           ("Honnêtement", a_doute, None), ("Alors j'envoie un mail", a_mail, ("notif", 0.7)),
           ("Le lundi suivant", a_twist, ("succes", 0.8)), ("Et c'est moi qu'il met", a_chef, None),
           ("Deux mille cent euros", a_chute, ("impact", 0.9))])

if __name__ == "__main__":
    rec, beats = {"tenue": TENUE, "avance": AVANCE}[sys.argv[1]]
    rec.fabriquer(beats)
