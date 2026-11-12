"""Tes droits : voiture d'occasion chez un pro, garantie légale de conformité (L217-7). Format « le méchant », 18 h."""
from PIL import Image, ImageDraw

import facades
from cartoon import GREEN, RED, SS, WHITE, YEL
from engine import H, W
from mechant_ct import Mechant

VENDEUR = dict(shirt=(170, 40, 40), pants=(40, 40, 50), hair=(30, 25, 20), tie=False, glasses=False)
_bg = {}


def garage_bg():
    """Garage d'occasions : murs gris, panneau, voiture en vitrine, sol en béton."""
    if "g" in _bg:
        return _bg["g"]
    s = SS
    im = Image.new("RGB", (W * s, H * s), (150, 155, 165))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * s, 260 * s], fill=(120, 125, 135))
    for x in range(0, W, 180):                                   # bardage
        d.rectangle([x * s, 260 * s, (x + 8) * s, 1380 * s], fill=(135, 140, 150))
    d.rounded_rectangle([240 * s, 90 * s, 840 * s, 190 * s], radius=20 * s, fill=(30, 30, 36))   # enseigne, hors des gros plans
    d.text((540 * s, 140 * s), "GARAGE · OCCASIONS", font=facades.FA(int(52 * s)), fill=(255, 206, 0), anchor="mm")
    d.rectangle([0, 1380 * s, W * s, H * s], fill=(95, 98, 105))       # sol
    d.rectangle([0, 1380 * s, W * s, 1395 * s], fill=(70, 72, 80))
    facades.voiture(d, 540)                                      # la voiture en vitrine, au fond
    _bg["g"] = im
    return im


C = dict(
    nom="droits_occasion", script="scripts/modele/12_occasion.txt", voix="output/_work_droits_occasion/voice_duo.wav",
    fond=garage_bg, look=VENDEUR, badge="LE VENDEUR", compteur="PAYÉ PAR LE GARAGE", montant=2400,
    hook_bulle=["PAS MON PROBLÈME,", "PIGEON"], hook_tag="BOÎTE DE VITESSES : 2 400 €",
    faux_sous="DE RÉPARATION, GRATUITE",
    setup_pose="neutre", setup_tags=[("VOITURE D'OCCASION : 6 000 €", WHITE, 0.0), ("TOUTES SES ÉCONOMIES", YEL, 1.4),
                                     ("3 SEMAINES PLUS TARD : EN PANNE", RED, 3.0)],
    m1=["VENDU EN L'ÉTAT.", "T'AS SIGNÉ", "SANS LIRE"],
    m2=["T'AS PERDU.", "VA PLEURER", "CHEZ TA MÈRE"],
    m3=["REMETS UN PIED ICI", "ET J'APPELLE", "LES FLICS"],
    sarah=["PAIE LA", "RÉPARATION…"],
    notif="Occasion : la garantie légale",
    regle=("LA RÈGLE", [("Occasion achetée chez un pro", 0.5, False), ("panne < 12 mois", 1.4, True),
                        ("= au vendeur de prouver", 2.2, False), ("« vendu en l'état » n'annule rien", 3.4, True)],
           "CODE DE LA CONSOMMATION · L217-7"),
    lettre=("LETTRE RECOMMANDÉE", "3 PHRASES", [("1. Date d'achat", "", 0.3, False), ("2. La panne", "", 0.8, False),
                                                 ("3. Garantie légale L217-7", "", 1.3, True)]),
    m4=["TA LETTRE ?", "MON CHIEN L'A MANGÉE"],
    riposte="DEVIS JOINT",
    calcul=("LA RÉPARATION", [("Boîte de vitesses : 2 400 €", 0.6, False), ("Payé par Kévin : 0 €", 1.4, True)]),
    gain_phrase="la voiture est réparée",
    notif_fin=("Garage", "Votre véhicule est prêt", "RÉPARATION · 0,00 €", (40, 160, 90)),
    question="ET TOI, UN VENDEUR T'A FAIT LE COUP ?",
    chute="« PIGEON »", chute_sous="RÉPARÉS GRATUITEMENT",
    mention="CAS TYPE · CODE DE LA CONSO. L217-7 · CECI N'EST PAS UN CONSEIL",
    reperes=[("hook", "Ta boîte de vitesses"), ("faux", "Faux. Et ce garagiste"), ("setup", "Kévin achète une voiture"),
             ("m1", "Vendu en l'état"), ("m2", "Une occasion, c'est"), ("m3", "Remets un pied"),
             ("sarah", "Même Sarah"), ("abonne", "Sauf que heureusement"), ("regle", "Retiens bien"),
             ("lettre", "Kévin envoie une lettre"), ("m4", "Ta lettre, je l'ai"), ("riposte", "Alors Kévin ajoute"),
             ("calcul", "Fais le calcul"), ("partage", "Et c'est là que Kévin envoie"),
             ("fin", "Dix jours plus tard"), ("chute", "Lui pensait")],
)

if __name__ == "__main__":
    Mechant(C).fabriquer()
