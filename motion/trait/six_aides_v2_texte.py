"""Texte de « 6 aides avant le 31 décembre » v2 : MÊME accroche, MÊME déroulé et MÊME rythme que la vidéo de
La Ficelle (demande du client, 20 nov.), réécrit avec nos mots, Kévin à la 1re personne, nos personnages.
Faits : voir scripts/modele/40_six_aides_31_decembre.dial (sources) ; compte à rebours 6 → 1 comme l'original."""
NAR = ("rlqCQzyNTVyUMPGBqC31", {"stability": 0.42, "similarity_boost": 0.8, "style": 0.25})
PAT = ("5l4ttmr4SKNgi0HnOelT", {"stability": 0.38, "similarity_boost": 0.8, "style": 0.35})
VOIX = {"nar": NAR, "pat": PAT}
# vitesse par ligne : accroche à vitesse normale (même rythme que l'original), le reste un peu plus vite
VITESSES = [1.0] + [1.17] * 17
LIGNES = [
    ("nar", "[Six aides] à récupérer avant le [31 décembre]. La plus grosse vaut jusqu'à [1 000 euros], et ton patron se gardera bien de t'en {parler}."),
    ("nar", "Lundi matin, je fais le plein avant d'aller au garage. [90 euros] pour 20 kilomètres de route."),
    ("nar", "Numéro six, l'aide carburant. Si tu roules pour bosser, avec un revenu fiscal sous [22 770 euros] par part, l'État te verse [100 euros]."),
    ("nar", "Sur le site des impôts, je rentre ma plaque et ma carte grise. Dix jours après, [100 euros] tombent sur mon compte. Le formulaire ferme le [31 décembre]."),
    ("nar", "Le soir, chez ma pote Inès, il fait [16 degrés]. Elle garde son manteau sur le canapé. Elle me fait, le chauffage, je l'allume plus."),
    ("nar", "Numéro cinq, le chèque énergie. Inès y a droit, mais depuis qu'elle a déménagé, elle l'a jamais reçu. Il suit pas ton adresse, il faut le réclamer."),
    ("nar", "Revenu fiscal sous [11 000 euros] seul, [16 500] en couple. Avec son numéro fiscal et le numéro du compteur, elle fait la demande en ligne. [48 euros]."),
    ("nar", "J'envoie direct le lien à ma cousine, qui a déménagé en mars."),
    ("nar", "Le lendemain, j'emmène Inès à la mairie. Numéro quatre, le centre d'action sociale. Selon la ville, il aide à payer le chauffage, ou il offre un colis de Noël. Et beaucoup bouclent leurs dossiers dès début décembre."),
    ("nar", "Trois papiers. L'avis d'impôt, un justificatif de domicile, la dernière facture. {Dossier déposé.}"),
    ("nar", "Chez moi, ma mère emballe les cadeaux et hésite devant un don à une asso d'aide alimentaire. Elle me fait, cent euros cette année, c'est trop."),
    ("nar", "Numéro trois, le don. Pour une asso qui aide les personnes en difficulté, l'État te rend [75 %] du don sur ton impôt. Elle donne [100 euros], ça lui en coûte [25]. Il faut payer l'impôt, garder le reçu, et donner avant le 31. Un don du premier janvier compte pour l'année d'après."),
    ("nar", "Jeudi, au garage, je regarde mon solde de congés. Trois RTT pas encore pris. Numéro deux, le rachat des RTT. Dans beaucoup de boîtes, un RTT pas pris au 31 est perdu. Mais jusqu'à fin 2026, tu peux le revendre à ton patron, payé comme une heure sup. [25 %] de plus, sans impôt. Mes trois jours valent [450 euros]. Il faut l'accord du patron, alors j'envoie ma demande par écrit."),
    ("nar", "Le patron passe la tête par la porte, il ricane."),
    ("pat", "Racheter tes RTT ? Et puis quoi, une {prime de Noël} tant que t'y es ?"),
    ("nar", "Justement. Numéro un, la prime transport. Depuis un décret du 20 octobre, et jusqu'au 31 décembre, un patron peut verser jusqu'à [1 000 euros] à chaque salarié pour ses trajets, sans payer de cotisations. {Rien l'oblige.}"),
    ("nar", "Alors je lui fais le calcul. [1 000 euros] d'augmentation vous coûteraient bien plus, avec les charges. La prime, c'est [1 000 euros] pile. Il refait le calcul, et il signe pour tout l'atelier."),
    ("nar", "Total, [1 673 euros] récupérés avant le 31."),
]
