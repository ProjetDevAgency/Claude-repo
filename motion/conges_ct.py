"""Tes droits : congés pas pris = payés au départ (Code du travail, L3141-28). Format « le méchant », publication 12 h."""
from cartoon import GREEN, RED, WHITE, YEL
from demission_ct import entrepot_bg
from mechant_ct import Mechant

PATRON = dict(shirt=(60, 60, 70), pants=(40, 40, 50), hair=(50, 40, 30), glasses=True, tie=True)

C = dict(
    nom="droits_conges", script="scripts/modele/11_conges.txt", voix="output/_work_droits_conges/voice_duo.wav",
    fond=entrepot_bg, look=PATRON, badge="LE PATRON", compteur="DÛ PAR LE PATRON", montant=1140,
    hook_bulle=["T'AVAIS QU'À LES POSER,", "ESPÈCE D'IDIOT"], hook_tag="12 JOURS DE CONGÉS PERDUS ?",
    faux_sous="QUE LE PATRON VA LUI PAYER",
    setup_pose="neutre", setup_tags=[("3 ANS DANS SON ENTREPÔT", WHITE, 0.0), ("IL DÉMISSIONNE", YEL, 1.2),
                                     ("IL RESTE 12 JOURS DE CONGÉS", GREEN, 2.6)],
    m1=["TU TE CASSES ?", "ALORS TU TE CASSES", "LES POCHES VIDES"],
    m2=["T'ES UN TRAÎTRE.", "RENDS TON BADGE", "ET DISPARAIS"],
    m3=["UN MEC COMME TOI,", "ÇA GAGNE", "JAMAIS RIEN"],
    sarah=["LÂCHE", "L'AFFAIRE…"],
    notif="Congés pas pris : tes droits",
    regle=("LA RÈGLE", [("Congés pas pris au départ", 0.5, False), ("= payés par le patron", 1.2, True),
                        ("démission, rupture, faute", 2.4, False)], "CODE DU TRAVAIL · L3141-28"),
    lettre=("MAIL AU PATRON", "3 PHRASES", [("1. Date de départ", "", 0.3, False), ("2. 12 jours restants", "", 0.8, False),
                                            ("3. Article L3141-28", "", 1.3, True)]),
    m4=["TON PETIT MAIL,", "PAPIER TOILETTE"],
    riposte="TRIBUNAL",
    calcul=("SES CONGÉS", [("12 jours × 95 €", 0.6, False), ("= 1 140 €", 1.4, True)]),
    gain_phrase="virement",
    notif_fin=("Banque", "Virement reçu", "EMPLOYEUR · +1 140,00 €", (60, 110, 230)),
    question="ET TOI, TON PATRON T'A FAIT LE COUP ?",
    chute="« LES POCHES VIDES »", chute_sous="PAYÉS. SANS UN MOT.",
    mention="CAS TYPE · CODE DU TRAVAIL L3141-28 · CECI N'EST PAS UN CONSEIL",
    reperes=[("hook", "Tes douze jours"), ("faux", "Faux. Et ce patron"), ("setup", "Trois ans que Kévin"),
             ("m1", "Tu te casses"), ("m2", "Les congés, c'est pour"), ("m3", "Va pleurer aux"),
             ("sarah", "Même Sarah"), ("abonne", "Sauf que heureusement"), ("regle", "Retiens bien"),
             ("lettre", "Kévin lui envoie"), ("m4", "Ton petit mail"), ("riposte", "Alors Kévin ajoute"),
             ("calcul", "Fais le calcul"), ("partage", "Et c'est là que Kévin envoie"),
             ("fin", "Quarante-huit heures"), ("chute", "Lui pensait")],
)

if __name__ == "__main__":
    Mechant(C).fabriquer()
