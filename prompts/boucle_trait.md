# Boucle quotidienne @souslesabot — moteur « trait » (consignes du 20 nov. 2026, soir)

Lancée chaque matin par une tâche programmée, dans la session qui a construit le moteur (branche
`ccr-a57d9e9e-flymhr`). **Objectif du jour : trois vidéos publiées à 10 h, 15 h et 20 h (Europe/Paris), sur TikTok (Metricool puis manuel), YouTube (Zapier) et Facebook (Windsor puis Zapier).**
Ces consignes REMPLACENT `prompts/boucle_consignes.md` (ancien moteur, publication le lendemain 18 h) pour cette boucle.

## Règles du client (jamais d'exception)
- **TROIS vidéos par jour (décision du 21 nov.), créneaux 10 h, 15 h et 20 h (Europe/Paris), écartés de 5 h (décision du client, 21 nov.)**, chacune publiée à son
  créneau sur TikTok, YouTube et Facebook. Fabrication dans l'ordre des créneaux (10 h d'abord). Une vidéo qui n'est
  pas prête ET vérifiée 20 min avant son créneau saute ce créneau : on ne programme rien pour lui, on passe à la
  suivante et on prévient le client (jamais de vidéo bâclée, jamais d'heure de remplacement sans son accord).
- Les 3 vidéos du jour : 3 sujets et 3 thèmes différents (ex. travail, conso, logement), jamais le même méchant.
- TikTok : Metricool tant que le compteur du mois est sous 20 (section 5 ter), puis paquet manuel envoyé au client
  pour chaque vidéo (il poste lui-même).
- **Ne jamais toucher aux autres publications du planning** (le client a passé les anciennes en brouillon).
- Sujet **universel** (filtre n° 1 ci-dessous) **et 8/8** (machine à sujets). Loi vérifiée dans **2 sources**, une officielle.
- Script selon `prompts/methode_ecriture.md` (moteur H1 adapté au compte) : Kévin raconte à la 1re personne, le méchant
  parle avec sa voix, 1 450 à 1 550 caractères, `python3 scripts/verifier_script.py` → zéro ❌.
- Pas d'insulte, pas de « Faux », aucune question ni appel au spectateur dans la voix (la question va dans la description
  et le commentaire épinglé). Thème différent de la veille.
- 2 à 3 entités par histoire (moteur 4.2) ; les autres personnages ne sont que des figurants muets.
- Contenu IA toujours déclaré (`isAigc true`).

## 1. Analyse (≈ 10 min) — Windsor.ai d'abord, Metricool en secours
0. **Source n° 1 : Windsor.ai** (connecteur « Windsor.ai for Social Media » ; ESSAI jusqu'au 20 déc. 2026, puis formule gratuite = 1 source / 1 compte :
   à partir du 21 déc., on ne garde sur Windsor QUE tiktok_organic, et Facebook repasse sur Zapier), connector
   `tiktok_organic`, `get_data` avec les champs : video_create_datetime, video_duration, video_views_count,
   video_likes, video_shares, **video_favorites (enregistrements)**, video_comments, video_average_time_watched,
   video_full_watched_rate (déjà en fraction : 0,34 = 34 %), video_new_followers, video_caption. Chiffres à jour
   (comme TikTok Studio, vérifié le 21 nov.). Pour comprendre un décrochage : video_view_retention_second +
   video_view_retention_percentage (rétention seconde par seconde) et video_impression_sources_* (« Pour toi »,
   profil, recherche). Si Windsor ne répond pas ou si l'essai est fini : Metricool comme ci-dessous.
   Repère du 21 nov. : les 2 succès ont 383 et 401 enregistrements, les autres 0 à 7 → les enregistrements sont le
   signal n° 1 à suivre avec les partages.
1. `getAnalyticsDataByMetrics`, brandId 8206232, du 1er nov. à aujourd'hui, métriques
   TKPO02 (date), TKPO05 (description), TKPO06 (durée), TKPO07 (vues), TKPO08 (j'aime), TKPO09 (commentaires),
   TKPO10 (partages), TKPO11 (portée), TKPO15 (temps moyen regardé), TKPO16 (« Pour toi »), TKPO20 (profil), TKPO21 (recherche).
   + TKPO13 (vue en entier) : **fiable mais à multiplier par 10 000 pour avoir un %** (0,000558 = 5,6 % ; vérifié
     avec TikTok Studio les 20 et 21 nov.).
   Une vidéo apparaît dans Metricool jusqu'à ~24 h après sa sortie, et **ses chiffres peuvent rester figés sur une photo
   prise tôt** (21 nov. : 82 vues dans Metricool contre 595 en direct sur TikTok). Donc : AUCUNE conclusion sur une vidéo
   de moins de 48 h à partir de Metricool ; les décisions se prennent sur J-3 ; une capture du profil ou de TikTok Studio
   envoyée par le client fait foi quand elle est plus récente.
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

## Apprentissage accéléré (priorité n° 1 du client, 21 nov. : « le plus important, c'est l'analyse et l'amélioration »)
1. **Fiche par vidéo** dans `prompts/videos_trait.csv` (une ligne par vidéo, remplie à la fabrication) : date, créneau,
   slug, thème, type de hook (prix / mépris / enjeu…), prix dans le hook (oui/non), méchant (lien + tier), twist,
   durée, variable testée (n° du test ou « témoin »). Les chiffres à 48 h sont ajoutés ensuite : vues, enregistrements,
   partages, j'aime, commentaires, temps moyen, vue en entier, % « Pour toi », abonnés gagnés (TikTok via Windsor),
   + vues YouTube et Facebook (Windsor `youtube` / `facebook_organic` si disponibles).
2. **Tests avec témoins le même jour** : sur les 3 vidéos du jour, 1 ou 2 portent la variable du test en cours, les
   autres sont des témoins (même jour, créneaux alternés d'un jour à l'autre pour neutraliser l'heure). Un test se
   conclut sur 6 à 9 vidéos (2 à 3 jours) : confirmé seulement si les vidéos testées battent leurs témoins du jour sur
   le signal visé (enregistrements + partages d'abord, puis vues et temps moyen) dans la grande majorité des
   comparaisons, sans dégrader le reste. Toujours UN seul test à la fois.
3. **Diagnostic par la rétention** : pour chaque vidéo à 48 h, lire video_view_retention_second / _percentage (Windsor),
   repérer la plus forte chute après la 3e seconde et la relier à la phrase du script prononcée à cet instant (temps des
   mots du .dial). Noter « décroche à Xs sur : <phrase> » dans la fiche. Une chute qui revient au même endroit sur
   plusieurs vidéos (couture, bloc technique, doute…) devient l'hypothèse du test suivant.
4. **Lundi : bilan sur les 21 vidéos de la semaine** dans `prompts/stats_souslesabot.md` : comparer les combinaisons de
   la fiche (thème × hook × méchant × twist), sortir les 3 meilleures et les 3 pires, choisir les 1 ou 2 prochains tests,
   et proposer au client les règles confirmées pour `prompts/methode_ecriture.md`.

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

## 5 ter. Limite Metricool gratuit : 20 publications PUBLIÉES par mois (toutes plateformes Metricool confondues)
- Avant de programmer TikTok, compter les publications Metricool du mois dans `prompts/publications_metricool.md`
  (une ligne par publication partie). Seules les publications réellement publiées comptent, pas les brouillons.
- Si le compte du mois atteint 20 (ou si Metricool refuse pour cause de limite) : NE PAS programmer sur Metricool.
  Envoyer au client, en `SendUserFile` status proactive, le « paquet TikTok » : la vidéo, la miniature et un message
  avec la description et le commentaire à épingler prêts à copier, l'heure conseillée (12 h) et le rappel « cocher
  contenu généré par IA ». YouTube et Facebook partent comme d'habitude.
- Le 1er du mois, repartir à zéro (nouvelle section datée dans le fichier).
- Décisions du client (21 nov.) : pas de Make, pas de Composio (trop long), Windsor ne publie pas sur TikTok.
  Seul Metricool publie TikTok automatiquement ; Metricool Starter (~16 €/mois) lèverait la limite.

## 5 bis. YouTube à 12 h (Zapier, chaîne « Où va ton argent ? » @ouvatonargent) — décision du client du 21 nov.
Zapier publie IMMÉDIATEMENT (la programmation YouTube est réservée aux chaînes partenaires) et n'arrive pas à lire
les liens uguu : on passe par le dépôt public.
1. Le matin, après la programmation TikTok : copier la vidéo (≤ 10 Mo si possible, sinon telle quelle) dans
   `publication/<slug>.mp4` sur la branche, commit + push, vérifier que
   `https://raw.githubusercontent.com/ProjetDevAgency/Claude-repo/ccr-a57d9e9e-flymhr/publication/<slug>.mp4`
   répond 200.
2. Programmer un réveil PAR CRÉNEAU : `send_later` à **10:00, 15:00 et 20:00 Europe/Paris** (un par vidéo prête) (format `AAAA-MM-JJT12:00:00[Europe/Paris]`) avec
   le message « Publie sur YouTube et Facebook la vidéo du jour <slug> (titre, description et tags dans
   scripts/trait/<slug>_description.txt), puis retire publication/ ».
3. À midi : Zapier `YouTubeV4CLIAPI` / `upload_video` (tool_name `youtube_upload_video`, connexion par défaut), params :
   title (≤ 100 caractères, finit par « #shorts »), description (= description TikTok + « Vidéo d'animation créée avec
   l'IA. »), video = l'URL raw ci-dessus, privacy_status « public », made_for_kids « false », notify_subscribers
   « true », tags (5 à 8 mots que les gens cherchent), default_language « fr », default_audio_language « fr ».
   **Pas de miniature** tant que la chaîne n'est pas vérifiée par téléphone (sinon erreur… et la vidéo part quand
   même : ne JAMAIS relancer l'envoi après une erreur sans avoir vérifié la liste des vidéos de la chaîne,
   `video_in_playlist` avec playlist_id `UUQKeRa6PWJMVmp1jylEM54w`, sinon doublon).
3 bis. Juste après YouTube, Facebook EN REEL via Windsor.ai (jusqu'au 20 déc. 2026 ; à partir du 21 déc., directement Zapier) : `execute_action`, connector `facebook_organic`,
   account « 1439579452576065 », action `create_reel`, params video_url = la même URL raw, description = la
   description TikTok + « Vidéo d'animation créée avec l'aide de l'IA. » (Reel : 3 à 90 s, 9:16 : nos vidéos de 64 s
   conviennent). Si Windsor échoue (essai fini, erreur) et seulement après avoir vérifié que rien n'est parti :
   secours Zapier `FacebookV2CLIAPI` / `page_video` (tool_name
   `facebook_pages_create_page_video`, connexion par défaut), params : page « 1439579452576065 » (page « Où va ton
   argent ? », la SEULE page autorisée), source = la même URL raw, title = le titre sans « #shorts », description =
   la description TikTok + « Vidéo d'animation créée avec l'aide de l'IA. ». Facebook ne propose pas de brouillon pour
   une vidéo : l'envoi publie directement. Même règle anti-doublon : après une erreur, vérifier la page avant de
   relancer (`page_stream` en lecture).
4. Vérifier que la vidéo est en ligne sur YouTube et Facebook, puis `git rm -r publication` + commit + push. Noter l'ID de la vidéo
   YouTube dans `scripts/trait/<slug>_description.txt`.
5. Zapier : vérifier chaque jour le compteur avec `show_task_usage_info` (tâches utilisées / limite / coût par appel).
   Relevé du 21 nov. : essai Pro 1 000 tâches jusqu'au 5 déc., puis gratuit 100 tâches/mois ; 2 tâches par appel,
   et Zapier annonce 0 tâche par appel à partir du 23 nov. (à confirmer le 23). À 3 vidéos par jour, si un envoi
   coûte encore des tâches après le 5 déc., la limite gratuite ne tient pas : prévenir le client AVANT d'atteindre
   80 % de la limite, et ne jamais laisser un envoi échouer en silence. Si Zapier signale la limite, ne rien forcer et
   prévenir le client.
6. Un sujet déjà publié sur YouTube dans l'ancien style (ex. colis, salaire en retard le 19 nov.) est quand même publié
   dans sa nouvelle version, sauf avis contraire du client.

## 6. Compte rendu au client
- `git add` (scripts, motion/trait, prompts) → commit → `git push -u origin ccr-a57d9e9e-flymhr`.
- Envoyer au client (SendUserFile, status proactive) la vidéo et la miniature, avec un message court : la règle apprise
  s'il y en a une (en premier), l'état du test en cours, ce que l'analyse a appris, le sujet et pourquoi, l'heure de publication, la description, le commentaire à épingler, les mesures
  (durée, mouvement, prononciation).
- En cas d'échec à n'importe quelle étape : ne rien publier, dire au client ce qui bloque et ce qu'il faut de lui.

## Suivi du rythme à 3 vidéos par jour (à partir du 22 nov.)
- Dans l'analyse quotidienne, comparer la part « Pour toi » (video_impression_sources) et les vues médianes des jours à
  3 vidéos avec la période 15-19 nov. (1 à 2 vidéos par jour). Si la part « Pour toi » baisse nettement 3 jours de
  suite (repère : 20 nov., 3 vidéos, 61-79 % contre 83-96 %), le signaler en tête du compte rendu : c'est au client de
  décider s'il revient à moins de vidéos.
- Compte rendu : un seul message par jour après la vidéo de 20 h (ou après la dernière vidéo prête), avec les 3 vidéos,
  plus un message à chaque paquet TikTok manuel.
