"""Tes droits : la caution que le proprio garde (style cartoon plat)."""
import argparse

from PIL import ImageDraw

from cartoon import (GREEN, GREY, INK, NADIA, PROPRIO, RED, WHITE, YEL, CartoonVideo, back, big_number, bubble,
                     card, character, dim, ease, notif, phone_big, room, shot, tag)

NX, PX, BASE = 330, 760, 1560   # Nadia, proprio, sol


def stage(kind="appart", nadia=None, proprio=None, z=1.0, fy=0.33):
    """Décor + personnages, cadré. nadia / proprio : dict de pose, ou None pour ne pas les dessiner."""
    big = room(kind).copy()
    d = ImageDraw.Draw(big)
    if nadia is not None:
        character(d, nadia.pop("x", NX), BASE, **{**NADIA, **nadia})
    if proprio is not None:
        character(d, proprio.pop("x", PX), BASE, **{**PROPRIO, **proprio})
    return shot(big, z, fy)


def s_hook(lt, dur):
    img = stage(nadia=dict(mouth="flat", brows="triste"), proprio=dict(mouth="grin"))
    big_number(img, (540, 320), "600 €", 170, YEL, "DE CAUTION", k=1.0, strike=ease((lt - 0.4) / 0.4))
    big_number(img, (540, 570), "720 €", 140, GREEN, "QU'IL VA LUI RENDRE", k=(lt - 1.2) / 0.4, rot=3)
    tag(img, 540, 170, "3 MOIS SANS NOUVELLES", 40, RED, WHITE, rot=-3, k=(lt - 0.2) / 0.3)
    return img


def s_nickel(lt, dur):
    img = stage(nadia=dict(x=540, mouth="grin", arm=ease(lt / 0.4) * 0.6), z=1.05)
    d = ImageDraw.Draw(img)
    for j, (x, y) in enumerate([(240, 520), (860, 600), (700, 380), (380, 700)]):
        k = back((lt - 0.2 - 0.15 * j) / 0.3)
        if k > 0:
            r = 26 * k
            d.polygon([(x, y - 2 * r), (x + r * .5, y - r * .5), (x + 2 * r, y), (x + r * .5, y + r * .5), (x, y + 2 * r),
                       (x - r * .5, y + r * .5), (x - 2 * r, y), (x - r * .5, y - r * .5)], fill=YEL)
    tag(img, 330, 300, "0 TROU", 52, GREEN, INK, rot=-5, k=(lt - 0.6) / 0.3)
    tag(img, 750, 300, "0 TRACE", 52, GREEN, INK, rot=4, k=(lt - 1.0) / 0.3)
    return img


def s_edl(lt, dur):
    img = stage(nadia=dict(mouth="smile"), proprio=dict(mouth="grin", clipboard=True), z=1.08, fy=0.6)
    bubble(img, 690, 330, ["JE TE VIRE ÇA", "TRÈS VITE"], 50, (lt - 0.6) / 0.3, tail_x=740)
    return img


def s_edl2(lt, dur):
    img = stage(nadia=dict(mouth="smile"), proprio=dict(mouth="grin", arm=0.5), z=1.08, fy=0.6)
    bubble(img, 600, 300, ["T'INQUIÈTE, JE SUIS PAS", "DU GENRE À GARDER", "L'ARGENT DES GENS"], 44,
           (lt - 0.2) / 0.3, tail_x=760)
    return img


def s_attente(lt, dur):
    img = stage(nadia=dict(x=540, phone=True, mouth="flat", brows="triste"), z=1.1, fy=0.7)
    steps = [("1 MOIS", "RIEN", 0.0), ("2 MOIS", "VU, PAS DE RÉPONSE", 1.3), ("3 MOIS", "MESSAGERIE", 3.2)]
    cur = [s for s in steps if lt >= s[2]]
    if cur:
        a, b, t0 = cur[-1]
        big_number(img, (540, 400), a, 170, WHITE, k=(lt - t0) / 0.3)
        tag(img, 540, 640, b, 46, RED, WHITE, rot=-3, k=(lt - t0 - 0.3) / 0.3)
    if lt > 1.6 and lt < 3.2:
        notif(img, 540, 120, "Messages", "Moi", "Bonjour, pour ma caution ?  Vu", (lt - 1.6) / 0.4)
    if lt > 4.3:
        tag(img, 540, 780, "UN AVOCAT ?", 50, YEL, INK, rot=4, k=(lt - 4.3) / 0.3)
    return img


def s_compte(lt, dur):
    img = dim(stage(nadia=dict(x=540, phone=True, mouth="sad", brows="triste"), z=1.1, fy=0.7), 0.8)
    phone_big(img, 540, 820, lt, "21:47", [("Banque", "Solde", "Aucun virement reçu", (60, 110, 230))])
    return img


def s_echo(lt, dur):
    img = dim(stage(proprio=dict(x=540, mouth="grin"), z=1.15, fy=0.6), 0.6)
    tag(img, 540, 620, "« TRÈS VITE »", 90, YEL, INK, rot=-4, k=lt / 0.3)
    return img


def s_loi(lt, dur):
    img = dim(stage(nadia=dict(), proprio=dict()), ease(lt / 0.4))
    big_number(img, (540, 260), "LA LOI", 120, YEL, "JOUE POUR ELLE", k=lt / 0.3)
    card(img, 540, 900, "LOI DU 6 JUILLET 1989", "ARTICLE 22", [
        ("État des lieux conforme", "1 mois", 1.6, True),
        ("Dégâts constatés", "2 mois", 4.0, True),
        ("Preuves", "factures, devis", 5.4, False)], lt - 0.6)
    return img


def s_calcul(lt, dur):
    img = dim(stage(nadia=dict(x=540, mouth="o"), z=1.05), 0.7)
    tag(img, 540, 250, "FAIS LE CALCUL", 56, YEL, INK, rot=-4, k=lt / 0.3)
    big_number(img, (540, 520), "10 %", 160, WHITE, "DU LOYER PAR MOIS DE RETARD", k=(lt - 1.0) / 0.3)
    big_number(img, (540, 840), "600 € × 10 % × 2", 86, WHITE, k=(lt - 4.0) / 0.3)
    big_number(img, (540, 1060), "+120 €", 170, GREEN, "DE PÉNALITÉ", k=(lt - 5.6) / 0.3, rot=-3)
    return img


def s_piege(lt, dur):
    img = dim(stage(nadia=dict(), proprio=dict(mouth="grin")), 0.75)
    big_number(img, (540, 280), "SANS ADRESSE", 100, RED, "PAS DE PÉNALITÉ", k=lt / 0.3)
    card(img, 540, 900, "ÉTAT DES LIEUX DE SORTIE", "SIGNÉ LE JOUR DES CLÉS", [
        ("Murs, sols, cuisine", "conforme", 0.3, False),
        ("Nouvelle adresse", "écrite", 3.6, True)], lt - 2.4, rot=-2)
    return img


def s_demi(lt, dur):
    img = stage(proprio=dict(x=540, mouth="o", arm=0.9), z=1.12, fy=0.6)
    tag(img, 540, 330, "UN OUBLI ?", 64, WHITE, INK, rot=-4, k=lt / 0.3)
    tag(img, 540, 520, "LA LOI S'EN FICHE", 56, RED, WHITE, rot=3, k=(lt - 1.6) / 0.3)
    return img


def s_lettre(lt, dur):
    img = dim(stage(nadia=dict(x=540, mouth="flat")), 0.8)
    card(img, 540, 760, "LETTRE RECOMMANDÉE AR", "MISE EN DEMEURE", [
        ("État des lieux conforme", "", 0.4, False),
        ("Art. 22, loi du 6 juillet 1989", "", 1.0, False),
        ("720 € sous 8 jours", "", 1.8, True),
        ("Sinon, le tribunal", "", 2.6, False)], lt, stamp="ENVOYÉ", stamp_t=3.6)
    return img


def s_virement(lt, dur):
    img = dim(stage(nadia=dict(x=540, phone=True, mouth="grin")), 0.75)
    phone_big(img, 540, 820, lt, "09:12", [("Banque", "Virement reçu", "PROPRIO  +720,00 €", (60, 110, 230))])
    return img


def s_chute(lt, dur):
    img = stage(nadia=dict(x=540, mouth="grin", arm=ease(lt / 0.4)), z=1.05)
    tag(img, 540, 260, "PAS UN MOT D'EXCUSE", 50, WHITE, INK, rot=-3, k=lt / 0.3)
    big_number(img, (540, 560), "720 €", 220, YEL, k=(lt - 0.5) / 0.3)
    if lt > 0.8:
        tag(img, 540, 1760, "CAS TYPE · CECI N'EST PAS UN CONSEIL JURIDIQUE", 26, (40, 40, 50), WHITE, rot=0,
            k=(lt - 0.8) / 0.3)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-file")
    a = ap.parse_args()
    v = CartoonVideo("droits_caution", "scripts/modele/2_caution.txt", "", "", corner="LOGEMENT")
    v.hook_head_start = 0.0
    v.voice(a.voice_file)
    v.scene("Six cents euros de caution", s_hook)
    v.scene("L'appart est nickel", s_nickel)
    v.scene("À l'état des lieux", s_edl)
    v.scene("Et en empochant", s_edl2)
    v.scene("Un mois. Rien", s_attente)
    v.scene("Nadia regarde son compte", s_compte)
    v.scene("Très vite", s_echo, after=v.at("Nadia regarde son compte"))
    v.scene("Et pourtant, la loi", s_loi)
    v.scene("Mais alors, s'il traîne", s_calcul)
    v.scene("Sauf qu'il y a un piège", s_piege)
    v.scene("Honnêtement, le proprio", s_demi)
    v.scene("Nadia envoie une lettre", s_lettre)
    v.scene("Six jours plus tard", s_virement)
    v.scene("Pas un mot d'excuse", s_chute)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
