# Boucle quotidienne @souslesabot — moteur « trait » (consignes du 20 nov. 2026, soir)

Lancée chaque matin par une tâche programmée, dans la session qui a construit le moteur (branche
`ccr-a57d9e9e-flymhr`). **Objectif du jour : une vidéo publiée à 12 h (Europe/Paris) le jour même.**
Ces consignes REMPLACENT `prompts/boucle_consignes.md` (ancien moteur, publication le lendemain 18 h) pour cette boucle.

## Règles du client (jamais d'exception)
- **Une vidéo par jour, programmée à 12 h le jour même** dans Metricool (brand 8206232), publication automatique.
  Si elle n'est pas prête et vérifiée à **11 h 40**, on ne programme RIEN et on prévient le client (jamais de vidéo bâclée,
  jamais d'heure de remplacement sans son accord).
- **Ne jamais toucher aux autres publications du planning** (le client a passé les anciennes en brouillon).
- Sujet **universel** (filtre n° 1 ci-dessous) **et 8/8** (machine à sujets). Loi vérifiée dans **2 sources**, une officielle.
- Script selon `prompts/methode_ecriture.md` (moteur H1 adapté au compte) : Kévin raconte à la 1re personne, le méchant
  parle avec sa voix, 1 450 à 1 550 caractères, `python3 scripts/verifier_script.py` → zéro ❌.
- Pas d'insulte, pas de « Faux », aucune question ni appel au spectateur dans la voix (la question va dans la description
  et le commentaire épinglé). Thème différent de la veille.
- 2 à 3 entités par histoire (moteur 4.2) ; les autres personnages ne sont que des figurants muets.
- Contenu IA toujours déclaré (`isAigc true`).

## 1. Analyse Metricool (≈ 10 min)
1. `getAnalyticsDataByMetrics`, brandId 8206232, du 1er nov. à aujourd'hui, métriques
   TKPO02 (date), TKPO05 (description), TKPO06 (durée), TKPO07 (vues), TKPO08 (j'aime), TKPO09 (commentaires),
   TKPO10 (partages), TKPO11 (portée), TKPO15 (temps moyen regardé), TKPO16 (« Pour toi »), TKPO20 (profil), TKPO21 (recherche).
   + TKPO13 (vue en entier) : **fiable**, vérifié par le client le 20 nov. (0,13 point d'écart avec TikTok Studio).
   Une vidéo apparaît dans Metricool jusqu'à ~24 h après sa sortie.
2. Mettre à jour `prompts/stats_souslesabot.md` : une section datée avec la vidéo de la veille (à ~24 h), celle de
   J-3 (vues quasi définitives), et ce qu'on en tire. Repères établis le 21 nov. (`prompts/stats_souslesabot_21nov.md`) :
   le **sujet** décide ; temps moyen ≥ 24 s nécessaire mais pas suffisant ; les **partages** séparent les succès ;
   l'heure ne joue pas ; la recherche ramène une longue traîne.
3. Mettre à jour `prompts/tests_boucle.md` (journal des tests, voir « Apprentissage » plus bas) avec les chiffres des
   vidéos qui appartiennent à un test en cours.
4. Diagnostic (une seule variable changée par vidéo) :
   | Signal | Changement pour la vidéo du jour |
   |---|---|
   | temps moyen < 18 s | changer le type de choc du hook (prix ↔ mépris), plus concret |
   | temps moyen 18-22 s | revoir la couture et la dette du hook |
   | temps moyen ≥ 24 s mais < 1 000 vues | sujet pas assez universel : filtre n° 1 plus strict |
   | 0 partage | gain de Kévin plus clair et chiffré dès l'ouverture |
   | « Pour toi » < 85 % | description et hashtags (mots que les gens cherchent) |
   | vue en entier en baisse avec un temps moyen stable | la fin traîne : twist plus tôt, chute plus courte |
5. Le **lundi** : bilan de la semaine (voir « Apprentissage »).

## 2. Sujet (≈ 15 min)
1. **Filtre n° 1 : « est-ce qu'un 18-30 ans l'ENVERRAIT à un pote ou l'ENREGISTRERAIT ? »** Oui seulement si c'est
   une actu chaude que tout le monde voit passer (bourse, prix, nouvelle loi, grève, fêtes), OU une situation que presque
   tout le monde a vécue ou redoute (colis, permis, premier appart, caution, salaire, CAF, impôts, banque, voiture,
   forfait, Noël). Un cas de niche (robe de mariée, vase cassé…) = non, même 8/8.
2. Sources, dans cet ordre :
   - `prompts/sujets_laficelle.md` : sujets classés par vues chez le concurrent. On reprend le SUJET et les FAITS,
     jamais leur texte, leurs personnages ni leurs images.
   - l'actu du jour (service-public.fr, Légifrance, economie.gouv.fr, franceinfo, Que Choisir, Capital) pour un angle
     d'actualité ou un sujet chaud ;
   - les scripts déjà écrits et jamais publiés de `scripts/modele/*.dial` (vérifier qu'ils passent encore le filtre).
   - les sujets qui ont ramené de la recherche dans Metricool (TKPO21 élevé) : les décliner.
3. Jamais un sujet déjà fait dans `prompts/sujets_faits_trait.md` ; y ajouter le sujet du jour (date, slug, source).
4. Passer les 8 critères de la machine à sujets ; vérifier la loi dans 2 sources ; noter références et sources en tête du `.dial`.

## 3. Script (≈ 15 min)
- `scripts/modele/NN_slug.dial` (NN = numéro suivant ; `M:` méchant, `N:` Kévin), en-tête complet (sources, 8/8,
  transgression, verrou, twist, chute, tier, zone grise). Écrire en pensant à ce qu'on MONTRERA (objets concrets :
  téléphone, document, appli, calendrier, notification, billets, cartons…).
- `python3 scripts/verifier_script.py scripts/modele/NN_slug.dial` → zéro ❌ ; relire casting, dette du hook, twist qui
  referme une prémisse, test de la banane.

## 4. Vidéo (≈ 60 min) — moteur `motion/trait/` (notice : `motion/trait/LISEZMOI.md`)
- **Modèle à copier : `motion/trait/colis_perdu.py`** (lit le `.dial`, marques de couleur des sous-titres, plans calés
  sur les mots avec `L(réplique, n° du mot)`, compteur, sons). Créer `motion/trait/<slug>.py`, et un module de décors
  `motion/trait/decors_<slug>.py` si le sujet en demande de nouveaux (réutiliser d'abord `decors.py`, `decors_colis.py`,
  `decors_piscine.py`, `decors_ville.py`, `ui.py`).
- Voix : réglage par défaut (`voix.YANN` pour Kévin, Paul K `5l4ttmr4SKNgi0HnOelT` pour un méchant homme,
  `O31r762Gb3WFygrEOGh0` pour une méchante), modèle v4, vitesse normale, accélérée au montage avec `cible=voix.CIBLE`
  (64 s, ×1,35 max) ; si ça dépasse, `gap=0.15` puis raccourcir le script.
- `voix.verifier(...)` : corriger tout mot mal prononcé (régénérer la réplique, ou réécrire le mot) avant le rendu.
- Règles d'image : un VISAGE dès la 1re image (le méchant qui parle, le chiffre au-dessus de sa tête), puis l'objet, puis
  la réaction de Kévin ; ce qu'on voit = ce qui est dit ; un plan toutes les 1 à 3 s ; aucun texte sur un visage ni coupé ;
  zone des sous-titres (y ≈ 1 330) libre ; jamais de logo de marque réelle.
- Contrôle : `--stills` toutes les 2,2 s → planche ; corriger ; rendu ; `python3 scripts/mesure_mouvement.py` →
  **≥ 6 % de l'image qui bouge, ≤ 15 % d'images figées** (sinon : téléphones qui flottent, caméra qui glisse, objets animés).
- Miniature : copier `motion/trait/miniature_colis.py` ; titres et visages dans la zone sûre du recadrage 3:4
  (y de 240 à 1 680), vérifier avec le cadre rouge.

## 5. Publication à 12 h (≈ 5 min)
1. Mise en ligne temporaire (le lien expire en 3 h, Metricool copie les fichiers chez lui) :
   `curl -sS -F "files[]=@output/trait/<slug>.mp4" https://uguu.se/upload` → `files[0].url` ; pareil pour la miniature.
   Si uguu échoue : déposer les fichiers dans `publication/` sur la branche (dépôt public), utiliser
   `https://raw.githubusercontent.com/ProjetDevAgency/Claude-repo/ccr-a57d9e9e-flymhr/publication/<fichier>`, programmer,
   puis retirer `publication/` dans un commit.
2. Metricool `createScheduledPost`, blogId 8206232, date **aujourd'hui 12:00 Europe/Paris**, providers tiktok, autoPublish
   true, `media` = URL vidéo, `videoThumbnailUrl` = URL miniature, `firstCommentText` = commentaire à épingler,
   `tiktokData` : title (≤ 90 caractères), privacyOption PUBLIC_TO_EVERYONE, **isAigc true**.
   Texte = description : accroche courte avec le montant, 4 ✅ avec références, question de débat 👇,
   « Cas type, montants indicatifs. » (+ limite de la règle si besoin), **5 hashtags** dont des mots que les gens cherchent.
3. Vérifier avec `getScheduledPosts` que la publication est bien là, à 12 h, non brouillon. Ne toucher à aucune autre.
4. Enregistrer `scripts/trait/<slug>_description.txt` (description, commentaire, réglages).

## Apprentissage : comment la boucle s'améliore seule
1. **Journal des tests** (`prompts/tests_boucle.md`) : UN test en cours à la fois. Chaque test = une hypothèse
   (« chiffrer le gain dans la 1re phrase fait monter les partages »), la variable changée, les vidéos testées, les
   vidéos témoins, le résultat chiffré, la décision. Pas de nouveau test tant que le précédent n'est pas conclu
   (3 vidéos testées maximum, ou 7 jours).
2. **Conclusion** : confirmé si l'effet va dans le même sens sur 3 vidéos sur 3 et dépasse l'écart habituel (la médiane
   hors succès tourne autour de 400 vues : un « succès » d'une seule vidéo ne prouve rien). Sinon : infirmé ou non
   concluant, et on passe au test suivant.
3. **Règle confirmée → elle entre dans `prompts/methode_ecriture.md`**, section « Règles apprises par la boucle »
   (date, règle, chiffres qui la prouvent, numéro du test), et elle est signalée en tête du compte rendu au client.
   Le client peut la refuser : on la retire alors et on le note dans le journal.
4. **Ce qu'on ne modifie jamais** : le moteur H1 (`prompts/moteur_script.txt`, PDF de méthode), les règles du client
   en haut de ce fichier. On adapte la méthode d'écriture et les choix de sujet, pas la référence.
5. **Le lundi** : bilan des 7 dernières vidéos dans `prompts/stats_souslesabot.md` (par sujet, type de hook, méchant,
   twist), état du test en cours, prochain test choisi, et demande au client d'une capture TikTok Studio (rétention
   seconde par seconde, enregistrements : Metricool ne les donne pas) pour la meilleure et la pire vidéo de la semaine.

## 6. Compte rendu au client
- `git add` (scripts, motion/trait, prompts) → commit → `git push -u origin ccr-a57d9e9e-flymhr`.
- Envoyer au client (SendUserFile, status proactive) la vidéo et la miniature, avec un message court : la règle apprise
  s'il y en a une (en premier), l'état du test en cours, ce que l'analyse a appris, le sujet et pourquoi, l'heure de publication, la description, le commentaire à épingler, les mesures
  (durée, mouvement, prononciation).
- En cas d'échec à n'importe quelle étape : ne rien publier, dire au client ce qui bloque et ce qu'il faut de lui.
