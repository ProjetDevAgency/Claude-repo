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

## Le modèle gagnant (analyse du 18 nov., réconciliée le 19 nov. avec les 52 vidéos de La Ficelle)
Tiré de nos 2 vidéos qui ont décollé (Anthropic 48,8 k, permis 27,5 k) contre les autres (< 2,3 k), puis confronté au
concurrent La Ficelle (`prompts/analyse_concurrent_laficelle.md`, 15 vidéos à plus de 100 k sur 43 depuis le 25 oct.) :
1. **Accroche = la réplique du méchant, avec sa voix** (ultimatum ou mépris) : « [Tu me paies / Tu mets] X €, sinon
   [ta vie est fichue] ». Chez La Ficelle : réplique du méchant en 1re phrase, médiane 41 k vues contre 24 k sans ; un
   montant en 1re phrase, 44 k contre 14,5 k. Le prix reste facultatif (décision du client) mais il est **recommandé**.
2. **Un sujet universel** : une situation que presque tout le monde a vécue ou redoute (permis, premier appart, salaire,
   colis, CAF, caution, épargne, actu que tout le monde voit passer). Les étapes de vie en font partie, mais ne sont pas
   obligatoires (colis perdu 1,5 M, salaire en retard 590 k). Jamais un cas rare (robe de mariée, vase cassé) : les
   mêmes sujets de niche échouent chez eux comme chez nous (tenue de travail, argent prêté, vice caché).
3. **Un gain clair et chiffré pour Kévin** : astuce légale peu connue, piège évité OU réclamation qui aboutit. *Corrigé
   le 19 nov.* : on avait écrit que les réclamations plafonnent sous 600 vues ; chez La Ficelle, les réclamations font
   400 k à 1,5 M (colis, caution, salaire, CAF). Ce qui plafonnait chez nous, c'était l'exécution, pas le type.
4. **Méchant de préférence proche (TIER S) ou avec du pouvoir (TIER A)** : chez nous, TIER F = 16–19 s de temps moyen
   contre 24–26 s. Mais un vendeur ou un service client peut marcher si le sujet est universel (colis, 1,5 M chez eux).
5. **La fin referme l'ultimatum** : Kévin passe devant l'agence au volant ; le frère lui demande d'avancer son loyer.

## Mise en image (chantier visuel du 19 nov., obligatoire)
- **Ce qu'on voit = ce qui est dit** : chaque objet, chiffre ou action du texte a son illustration animée
  (`motion/dynamique.py`). Écrire le script en pensant à ce qu'on montrera : des objets concrets (devis, livret,
  appli, calendrier, notification, plat, billets) plutôt que des idées abstraites.
- Ouverture en 3 plans calés sur la voix : un VISAGE dès la 1re image (le méchant qui parle, le chiffre au-dessus de sa
  tête) → l'objet du sujet → la réaction de Kévin. Jamais un chiffre ou un objet seul en ouverture.
- Dialogues vivants : caméra vers celui qui parle, gestes que le texte décrit.
- Jamais de logo de marque réelle.
- Mesure : ≥ 6 % de l'image qui bouge, ≤ 15 % d'images figées (`scripts/mesure_mouvement.py`).
Détails techniques : `prompts/boucle_consignes.md`, étape 5.

## Règles apprises par la boucle
Ajoutées par la boucle quotidienne quand un test de `prompts/tests_boucle.md` est confirmé 3 fois sur 3. Chaque règle :
date, règle, chiffres, numéro du test. Le client peut en refuser une : elle est alors retirée.

(aucune pour l'instant)
