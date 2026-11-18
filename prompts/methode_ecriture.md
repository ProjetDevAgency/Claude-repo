# Méthode d'écriture « Où va ton argent ? » — v3 (15 nov. 2026)

Repartie de zéro à partir du moteur H1 (`prompts/methode/moteur_script_H1.pdf`), adapté à notre format :
dessin animé, **Kévin raconte à la première personne** (voix narrateur), **le méchant parle avec sa propre voix** (M:).
Cette méthode REMPLACE le « Format Kévin v2 » de `consignes_eco.md` (formules La Ficelle recopiées = robot).

## Ce qui ne bouge jamais
- **Français parlé.** Négation sans « ne ». Présent de narration. Mots courts. Fragments (« Pas un mot. »).
  « il me fait », « il me sort », « il en rajoute une couche ». Jamais « déclara », jamais de connecteurs d'écrit
  (néanmoins, cependant, ainsi, en effet). Phrases de 6 à 15 mots, jamais plus de 25.
- **Ponctuation : point, virgule, ? et !** (un seul ! maximum). Pas de deux-points, pas de guillemets, pas de « … »,
  pas de tiret. Une réplique s'annonce par « il me fait, » puis la ligne M:.
- **Montants en toutes lettres.** 2 ou 3 chiffres par script, pas un calcul de comptable.
- **Zéro appel au spectateur.** Pas d'« abonne-toi », pas d'« envoie ça à… », pas de « écris-le », pas de question au
  spectateur, pas de nom du compte dans l'histoire. Le script s'arrête sur le dernier mot de la chute.
- **Pas de « Faux », pas d'insulte** (idiot, pigeon, abruti…). Le mépris passe par ce que le méchant dit de la
  personne et de sa vie (« un gamin qui fait des burgers »).
- **Pas de formule toute faite répétée d'un script à l'autre** (« fais le calcul avec Kévin », « on en a tous un »,
  « retiens bien », « il le sait pas encore, mais »). Chaque script trouve ses propres mots.

## L'ordre d'un script (60 à 65 s, 1 450 à 1 550 caractères)
1. **Hook en 3 couches** (0–10 s) : le choc (de préférence le mépris dit par le méchant ; le prix est facultatif), le verrou (de préférence
   « C'est ce que X m'a sorti… », la phrase avant de savoir qui la dit), la couture (le lieu, l'objet, le moment).
2. **Montée sincère** (20 %) : Kévin est content, il a un projet. Aucun signe avant-coureur.
3. **Le conflit, deux coups** : coup 1 sur la chose (le permis, le contrat, la démarche), coup 2 sur la personne
   (sa vie, son âge, son job), séparés par un geste. Kévin ne répond pas (« Je dis rien. »). Puis **un écho** de
   2 à 5 mots du coup, seul entre deux points.
4. **La règle** (notre « bloc technique ») : racontée comme une histoire, avec 1 à 3 problèmes concrets
   (« Sauf que… », « Mais alors… ? » avec sa réponse dans la foulée) et UN « ce que les gens savent pas, c'est que ».
   La référence exacte va à l'écran et dans la description, pas forcément dans la voix.
5. **Le doute** : Kévin admet une demi-raison au méchant en une phrase.
6. **Twist et chute** : le twist referme une phrase posée au début (jamais un événement qui tombe du ciel), puis la
   punchline, avec le montant du hook à l'identique. Les deux dernières phrases font 3 à 8 mots. Rien après.

## Le méchant
Le plus fort : un proche (mère, père, frère, belle-famille) ou quelqu'un qui a un vrai pouvoir sur Kévin (patron,
proprio, gérant, banquier). Jamais un inconnu sans pouvoir. Il a toujours une petite part de raison.

## Règle du 16 nov. : uniquement des sujets 8/8
Avant d'écrire, chaque sujet passe les 8 critères de la machine à sujets (prompts/methode/machine_a_sujets.pdf) :
client précis · prix précis et crédible · choc (une des 5 façons) · cohérence · tiers absent qui crée l'enjeu ·
deadline réelle · zone grise morale (geste discutable de Kévin) · pas un sujet banal / « client normalement pénible ».
Un seul critère manquant → on retravaille le sujet ou on le jette. Jamais de vidéo sous 8/8.

## Contrôle avant de faire une vidéo (obligatoire, dans cet ordre)
1. **Le sujet passe les 8 critères** (machine à sujets), notés dans l'en-tête du .dial.
2. **La règle de loi est vérifiée** dans au moins 2 sources, et la référence est notée dans l'en-tête.
3. **Le prix dans l'accroche est FACULTATIF** (règle du 18 nov. : le moteur ne l'impose pas, c'est un des 9 chocs).
   S'il y en a un : DANS la 1re phrase, jamais en 1er mot, avant l'objet (« J'ai réparé … pour [prix] »), et repris
   à l'identique dans la chute. Sans prix, la chute prend une autre forme (maxime, geste, coda, réplique d'un tiers).
   ✗ « Mille cent quarante euros de prime ? » → ✓ « Tu veux ta prime de mille cent quarante euros ? »
4. **Le hook est clair en 2 secondes** : qui parle, de quoi, combien, compréhensible SANS contexte.
   ✗ « 1 400 € la robe ? » (quelle robe ?) → ✓ « 1 400 € la robe de mariée de ta sœur ? »
5. **`python3 scripts/verifier_script.py <fichier.dial>`** : longueur, ponctuation, négations, phrases longues,
   s'il y a un prix : pas en 1er mot, avant l'objet, repris dans la chute. Tout doit être ✅.
6. **Planche d'aperçu** (APERCU=…) : aucun texte sur un visage, aucun texte coupé, personnages reconnaissables.
7. **Vérification du rendu final** : une image toutes les 5 s.

## Le modèle gagnant (analyse du 18 nov., à réviser chaque semaine par la boucle)
Tiré des 2 vidéos qui ont décollé (Anthropic 48,8 k, permis candidat libre 27,5 k) contre toutes les autres (< 2,3 k) :
1. **Accroche = ultimatum méprisant du méchant, avec sa voix** : « [Tu me paies / Tu mets] X €, sinon [ta vie est
   fichue] », puis « C'est ce que [proche / autorité] m'a sorti, devant [témoin] ». Le prix est facultatif, l'ultimatum non.
2. **Une étape de vie de jeune adulte** que tout le monde a vécue ou va vivre : permis, premier appart, premier job,
   épargne, première voiture, études. Jamais un cas rare (robe de mariée dans la soute, vase cassé).
3. **Kévin gagne en faisant autrement, pas en réclamant** : une astuce légale que peu de gens connaissent, qui fait
   économiser une grosse somme, ou un piège qu'il évite. C'est ce qui se partage et s'enregistre (permis : 190 partages,
   369 enregistrements). Les histoires de réclamation (« la loi oblige X à te rembourser ») plafonnent sous 600 vues.
4. **Méchant proche (TIER S) ou qui a du pouvoir (TIER A)**, jamais un inconnu au comptoir (TIER F : 16–19 s de
   temps moyen, contre 24–26 s).
5. **La fin referme l'ultimatum** : Kévin passe devant l'agence au volant ; le frère lui demande d'avancer son loyer.
