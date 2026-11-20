# La boucle quotidienne « Où va ton argent ? » — consignes complètes

Lancée chaque matin par une tâche programmée. Elle doit tenir seule : tout ce qu'il faut savoir est ici et dans les
fichiers cités. Compte TikTok : @souslesabot (cartoon, héros Kévin, voix narrateur + voix du méchant).

## 0. À lire avant tout
1. `prompts/methode_ecriture.md` — la méthode, ses règles et **le modèle gagnant** (fin du fichier).
2. `prompts/methode/moteur_script_H1.pdf` — le moteur d'écriture (il fait foi pour tout le script).
3. `prompts/methode/machine_a_sujets.pdf` — les 8 critères d'un sujet.
4. `prompts/stats_ouvatonargent.md` (carnet d'expériences) et `prompts/videos_index.csv` (une ligne par vidéo).
5. `prompts/actu_argent.md` (calendrier de l'actu) et `prompts/sujets_concurrents.md`.

## Règles du client (jamais d'exception)
- Uniquement des sujets **8/8** (machine à sujets). La loi est vérifiée dans **2 sources**, une officielle si possible.
- **Jamais d'insulte** (idiot, pigeon, abruti, radin…) ni de « Faux ». Le méchant est violent par ce qu'il dit de la vie
  de Kévin, pas par des gros mots.
- **Aucune question au spectateur dans la voix.** La question va dans la description et dans le commentaire épinglé.
- Prix dans l'accroche **facultatif** ; s'il y en a un : dans la 1re phrase, jamais en 1er mot, avant l'objet, repris à
  l'identique dans la chute.
- Un **geste discutable de Kévin** (zone grise) **et** un **doute** dans chaque script. Le geste reste légal.
- Vidéo de **61 s minimum** (monétisation) : script de 1 450 à 1 500 caractères.
- Aucun texte sur un visage, aucun texte coupé, méchant reconnaissable (jamais le sosie de Kévin).
- Thème différent de la veille.

## 1. Analyse (10 min)
1. Metricool : `getAnalyticsDataByMetrics`, brandId **8206232**, métriques TKPO02, TKPO03, TKPO07, TKPO08 (j'aime), TKPO09,
   TKPO10, TKPO11 (portée), TKPO15, TKPO16. TKPO13 (vue en entier) donne des valeurs incohérentes (0,3 % quand TikTok
   Studio affiche 16 %) : ne pas l'utiliser. Enregistrements, rétention à 0:01 et récompenses : captures du client seulement. sur les 30 derniers jours (heures en UTC : +1 h pour Paris).
2. Mettre à jour `prompts/videos_index.csv` (vues, partages, commentaires, temps moyen, % « Pour toi », date du relevé).
3. Lire la vidéo d'hier à 24 h (temps moyen, partages, « Pour toi ») et celle de J-3 pour les vues définitives.
4. Diagnostic (moteur 7.3) :
   | Signal | Cause | Changement |
   |---|---|---|
   | temps moyen < 18 s ET < 72 % à 0:01 (capture client) | on part au hook | changer le type de choc (prix ↔ mépris), plus concret |
   | départ 5–15 s (temps moyen 18–22 s) | couture ou dette du hook | revoir la promesse du hook |
   | temps moyen ≥ 24 s mais peu de vues | sujet pas assez universel | appliquer plus strictement le filtre n° 1 (étape 2) |
   | 0 partage, 0 enregistrement | gain pas assez clair | chiffrer le gain de Kévin dès l'ouverture (astuce OU réclamation) |
   | 0 commentaire | pas de débat | geste de Kévin plus discutable, accroche T5 |
   | « Pour toi » < 85 % | diffusion | description et hashtags |
5. **Une seule variable changée par vidéo.** Une tendance devient une règle après 2–3 confirmations seulement.
6. Écrire le résultat et la décision du jour dans `prompts/stats_ouvatonargent.md` (section datée).
7. **Le lundi : analyse de la semaine** (7 dernières vidéos, par catégorie de l'index : accroche, tier, sujet, étape de
   vie, twist). Réviser « le modèle gagnant » dans la méthode si une tendance est confirmée. Demander au client une
   capture TikTok Studio (enregistrements, vue en entier, récompenses : Metricool ne les donne pas).

## 2. Sujet (10 min)
- **D'abord la veille (client, 20 nov.)** : `python3 scripts/veille_actu.py` → lire `prompts/veille_actu.md`. Ce sont
  les sujets des comptes d'actu que regardent nos spectateurs (HugoDécrypte, TF1 Info, BFMTV, Franceinfo, Le Parisien,
  Loopsider…). Choisir en priorité une actu argent de la veille (la plus vue, qui touche les 18–25 ans), la raconter
  avec Kévin et le méchant / le frère. On reprend le SUJET, vérifié dans 2 sources, jamais leurs images ni leur texte.
- Autres sources : actu (service-public.fr, Légifrance, economie.gouv.fr, franceinfo, BFM Éco, Capital, Selectra, Que Choisir +
  `prompts/actu_argent.md`), concurrents (`prompts/sujets_concurrents.md`), ou invention.
- Le sujet suit **le modèle gagnant** et passe les 8 critères. Vérifier la règle dans 2 sources ; noter références et
  sources dans l'en-tête du `.dial`.
- **Filtre n° 1, avant les 8 critères : « est-ce qu'un 18–25 ans l'ENVERRAIT à un pote ou l'ENREGISTRERAIT ? »**
  Oui seulement si : actu chaude que tout le monde voit passer (IPO, prix, nouvelle loi), OU envie / dépense que presque
  tous les 18–25 ans ont (permis, premier appart, premier salaire, voiture, épargne). Un cas de niche (robe de mariée,
  vase cassé, taxes d'aéroport, frais d'agence pour un seul public) = non, même s'il est 8/8. Relevé du 19 nov. : la
  rétention des 1res secondes est la même sur les succès et les flops (78–83 % à 0:01) ; ce qui sépare 48 k de 300 vues,
  ce sont les partages et enregistrements, donc le sujet.
- **Test en cours (depuis le 20 nov.) : le feuilleton du grand frère** — lire `prompts/feuilleton_grand_frere.md`.
  Une vidéo sur deux est un épisode (sam. 21 = épisode 4, dim. 22 = sans frère, lun. 23 = épisode 5…). Respecter la
  bible et la continuité, ajouter l'épisode à la liste du fichier. Colonne `format` de l'index : `feuilleton ep N` ou
  `hors feuilleton`. Le test de la « promesse après l'accroche » est suspendu pendant ce test.
- Proposer mentalement 3 accroches (PRIX, MÉPRIS, ENJEU) et garder la plus conforme au modèle gagnant et aux stats.

## 3. Script (15 min)
- Écrire `scripts/modele/NN_slug.dial` (NN = numéro suivant ; `M:` méchant, `N:` Kévin), en-tête complet : sources,
  transgression, verrou, entrée, axe, twist, chute, mot-enjeu, tier, 8/8, zone grise.
- `python3 scripts/verifier_script.py scripts/modele/NN_slug.dial` → **zéro ❌**. Relire à la main : casting, dette du
  hook, twist qui referme une prémisse, test de la banane.

## 4. Voix (5 min)
```
export ELEVENLABS_API_KEY=proxy          # la vraie clé est injectée par le proxy de l'environnement
export ELEVENLABS_VOICE_ID=rlqCQzyNTVyUMPGBqC31
# méchante (voix féminine) : MECHANT_VOICE_ID=O31r762Gb3WFygrEOGh0 ; méchant (défaut) : Paul K
python3 motion/voix_duo.py scripts/modele/NN_slug.dial output/_work_b_slug/voice_duo.wav
```
Si ElevenLabs échoue 3 fois (vérifier https://status.elevenlabs.io), **arrêter** et prévenir le client.

## 5. Vidéo (30 min) — style « chantier visuel » du 19 nov. (modèle : `motion/boucle/anthropic_ouverture_v2_ct.py`)
- Créer `motion/boucle/slug_ct.py` : décors et classe `V2` de `motion/semaine_ct.py`, `recit(..., dynamique=True)`
  (coupes avec zoom qui claque + flou de mouvement, sous-titres discrets), et le module `motion/dynamique.py`.
- **Règle d'or (client) : ce qu'on voit = ce qui est dit.** Chaque phrase qui parle d'un objet, d'un chiffre ou d'une
  action a son illustration animée : courbe (`graphique`), écran de prix (`defile_prix`), appli (`insert_appli`),
  notification (`insert_notif`), devis / lettre / bail (`insert_document`), calendrier (`insert_calendrier`),
  étiquette de prix (`insert_etiquette`), compte à rebours (`insert_compte`), livret (`livret`), billets qui
  s'envolent (`billets_envoles`), vapeur d'un plat (`vapeur_devant`). En créer de nouveaux si le sujet l'exige.
  Jamais de logo de marque réelle : le nom, un symbole, un objet générique.
- **Ouverture** : `D.sequence` en 3 plans calés sur la voix (≥ 1,1 s chacun ; regarder les temps des mots dans
  `output/_work_<nom>/subs.ass` après un premier aperçu) : l'objet du sujet avec le montant → le méchant en gros plan
  → Kévin qui réagit (`D.reaction`). Pas plus rapide (le client a trouvé 4 plans en 2,6 s trop rapide).
- **Dialogues vivants** : `D.dialogue` (caméra qui glisse vers celui qui parle, gestes liés au texte : téléphone
  montré, plat servi, fourchette, parents qui réagissent), `D.gp_vivant` (méchant qui gesticule en parlant),
  `D.echo_vivant`. Aucune scène de plus de 6 s sans changement de plan ou d'objet.
- Aperçu : `APERCU=<png> python3 motion/boucle/slug_ct.py` → regarder la planche (règles d'image ci-dessus).
- Rendu : `python3 motion/boucle/slug_ct.py` (≈ 7–10 min) → vérifier une image toutes les 5 s
  (`ffmpeg -i out.mp4 -vf "fps=1/5,scale=180:320,tile=13x1" -frames:v 1 planche.png`) et la durée (≥ 61 s).
- Mesurer : `python3 scripts/mesure_mouvement.py output/<nom>.mp4` (cible : ≥ 6 % de l'image qui bouge, ≤ 15 %
  d'images figées) ; noter les deux chiffres dans le compte rendu.
- Copier dans `output/a_publier_finance/NN_slug.mp4`.

## 6. Publication (5 min)
1. Mise en ligne temporaire : `curl -sS -F "files[]=@output/a_publier_finance/NN_slug.mp4" https://uguu.se/upload`
   → URL dans `files[0].url` (le lien expire en 3 h, Metricool copie la vidéo chez lui).
2. Metricool `createScheduledPost`, blogId 8206232, **le lendemain à 18 h (Europe/Paris)** (mode sécurité : le client a
   24 h pour corriger), providers tiktok, `tiktokData` : title (obligatoire, ≤ 90 car.), privacyOption
   PUBLIC_TO_EVERYONE, **isAigc true**, autoPublish true. Texte = description TikTok (accroche courte, 4 ✅ avec
   références, question de débat 👇, « Cas type, montants indicatifs. », 5 hashtags).
3. Ajouter la ligne de la vidéo dans `prompts/videos_index.csv` (catégories remplies, stats vides).

## 7. Compte rendu au client
- `git add` des fichiers créés/modifiés (scripts, motion/boucle, prompts) → commit → `git push -u origin ccr-dd26f1b1-ihm967`.
- Envoyer au client (SendUserFile, status proactive) la vidéo + un message court : sujet, date de publication,
  script complet, description, **commentaire à épingler**, ce que l'analyse a appris, ce qui a changé et pourquoi.
- En cas d'échec à n'importe quelle étape : ne rien publier, dire au client ce qui bloque.
