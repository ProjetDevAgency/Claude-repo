# La boucle quotidienne « Où va ton argent ? » — consignes complètes

Lancée chaque matin par une tâche programmée. Elle doit tenir seule : tout ce qu'il faut savoir est ici et dans les
fichiers cités. Compte TikTok : @souslesabot (cartoon, héros Kévin, voix narrateur + voix du méchant).

## 0. À lire avant tout
1. `prompts/methode_ecriture.md` — la méthode, ses règles et **le modèle gagnant** (fin du fichier).
2. `prompts/methode/moteur_script_H1.pdf` — le moteur d'écriture (il fait foi pour tout le script).
3. `prompts/methode/machine_a_sujets.pdf` — les 8 critères d'un sujet.
4. `prompts/stats_ouvatonargent.md` (carnet d'expériences) et `prompts/videos_index.csv` (une ligne par vidéo).
5. `prompts/actu_argent.md` (calendrier de l'actu) et `prompts/sujets_concurrents.md`.

## MODE ACTUEL (décision du client, 20 nov. soir) : REMAKE QUOTIDIEN de la dernière vidéo de La Ficelle
Ce mode REMPLACE les étapes 2 (sujet), 3 (script), 4 (voix) et 5 (vidéo) ci-dessous. Les étapes 1 (analyse),
6 (publication) et 7 (compte rendu) restent valables. Règle : `prompts/regle_remake.md` (l'original fait foi ; les
« 7 points » ne s'appliquent pas). Modèle complet : `motion/trait/remake_aides.py` + `motion/trait/remake_aides_texte.py`
+ `prompts/remakes/aides_31dec_decoupage.md`.
1. **Choisir la vidéo** : `yt-dlp --flat-playlist -J https://www.tiktok.com/@laficelle_off` → la plus récente qui
   n'est pas dans `prompts/remakes/journal.md`. La télécharger (yt-dlp). Si TikTok la bloque : prendre la précédente
   accessible, ou demander au client de la déposer sur son Drive. Une vidéo « actu / photos / interview » qui ne se
   refait pas en dessin animé : la sauter et le dire dans le compte rendu.
2. **Découper** : coupes (`ffmpeg … select='gt(scene,0.22)'`), une image par seconde, transcription horodatée
   (faster_whisper « small », audio en numpy). Écrire `prompts/remakes/<slug>_decoupage.md` : chaque plan avec son
   temps, son décor, ce qui bouge, les textes à l'écran.
3. **Texte** : une phrase à nous en face de chaque phrase de l'original, même idée, même longueur, au même instant
   (`motion/trait/<slug>_texte.py`, liste PHRASES (t0, voix, texte)). Leurs personnages → les nôtres (Marc → Kévin ;
   seconds rôles : Yanis, Sarah, Léa ; le patron). Chaque chiffre vérifié dans 2 sources ; un chiffre non vérifiable
   est remplacé par nos sources ou retiré, et noté dans l'en-tête. Jamais leur nom, ni « abonné à La Ficelle ».
4. **Voix** : Yann (rlqCQzyNTVyUMPGBqC31), modèle **eleven_v4, SANS balise d'émotion** ; `voix.build_cale(…, vmax=2.0)`
   (chaque phrase posée à l'instant de l'original). Personnages : voix distinctes (Hugo, Victoire, Paul K).
5. **Images** : `motion/trait/<slug>.py` sur le modèle de remake_aides.py : chaque plan au même instant, même décor,
   même cadrage, mêmes objets qui racontent (tailles, progressions, compteurs, cartes, fiches, récapitulatif).
   Décors dessinés pour la vidéo ; plans photo de l'original → photos libres de droits (Openverse, licence cc0/pdm,
   via curl), aucune marque lisible, sources dans `assets/photos_libres/SOURCES.md`. **Caméra calme**
   (`VIE = {"pousse": 0.02, "derive": 8, "roulis": 0}`), **coupes nettes** (fouet=False). Rendu `--jobs 4`.
6. **Vérifier et corriger** (règle du client du 20 nov. : sur leur 1re image, le héros est bien visible) : **la 1re image compte double** — même place, même taille de personnage (en pied, ≈ la moitié de la hauteur), mêmes objets visibles et déjà en mouvement que l'original ; le comparer côte à côte à 0,2 s avant tout le reste. Puis : planches original / remake à la même seconde (1 image/s, voir la méthode du
   20 nov.), lister chaque écart (cadrage, objet manquant, texte trop petit ou caché, marque visible, personnage
   coupé), corriger, refaire la planche. Mesure `scripts/mesure_mouvement.py` : au moins le niveau de l'original.
   Aucun texte sur un visage, aucun texte coupé.
7. **Miniature** comme La Ficelle (modèle fixe, `motion/trait/miniature.py`, tout dans la zone visible 3:4 : y 240 à 1680) : bandeau jaune avec la question du sujet en haut (« AIDES AVANT LE 31/12 ? »), gros plan d'un personnage qui réagit (larmes / choc), bandeau sombre avec la phrase choc, puis « 0 € barré → gain en vert » en bas → `output/trait/miniature_<slug>.jpg`, passée dans `videoThumbnailUrl` (uguu) au moment de programmer.
8. **Publier** (étape 6) : description à nous (accroche, 4 à 6 ✅ avec références, question 👇, « Cas type, montants
   indicatifs. », 5 hashtags), isAigc true, lendemain 18 h. Ajouter la ligne dans `prompts/remakes/journal.md`
   (date, vidéo d'origine, slug, durée, mouvement, post Metricool) et dans `prompts/videos_index.csv`.
9. **Compte rendu** : la vidéo + la planche de comparaison + la liste des écarts corrigés et de ceux qui restent.

## Règles du client (jamais d'exception)
- Uniquement des sujets **8/8** (machine à sujets). La loi est vérifiée dans **2 sources**, une officielle si possible.
- **Jamais d'insulte** (idiot, pigeon, abruti, radin…) ni de « Faux ». Le méchant est violent par ce qu'il dit de la vie
  de Kévin, pas par des gros mots.
- **Aucune question au spectateur dans la voix.** La question va dans la description et dans le commentaire épinglé.
- Prix dans l'accroche **facultatif** ; s'il y en a un : dans la 1re phrase, jamais en 1er mot, avant l'objet, repris à
  l'identique dans la chute.
- Un **geste discutable de Kévin** (zone grise) **et** un **doute** dans chaque script. Le geste reste légal.
- Vidéo de **61 s minimum** (monétisation) : script de 1 450 à 1 800 caractères (62 à 75 s ; le squelette du 20 nov.
  demande plus de place : escalade, étapes, calcul).
- Aucun texte sur un visage, aucun texte coupé, méchant reconnaissable (jamais le sosie de Kévin).
- Thème différent de la veille.
- **Chaque vidéo crée son propre décor** (20 nov.) : pas de décor réutilisé tel quel d'une vidéo à l'autre.
- **Dessin animé uniquement** : jamais de photo ni d'image IA dans la vidéo.

## Les 7 points du 20 nov. (validés par le client, à appliquer à CHAQUE vidéo)
Issus du contre-audit de La Ficelle à dates égales (`prompts/analyse_concurrent_laficelle.md`) ; détail dans
`prompts/methode_ecriture.md` (« Les 7 points » et « L'ordre d'un script »).
1. Sujet universel avec **un méchant à battre et un gain chiffré**.
2. **1re phrase = réplique du méchant adressée à « tu »** (ligne M:) ; jamais une question au spectateur ni un sujet
   abstrait.
3. **Promesse juste après l'accroche**, dans nos mots (ce que le méchant va perdre / ce que Kévin va récupérer).
4. **Au moins 6 montants** dans le script (frais qui s'empilent, calcul qui monte).
5. **Dessin animé, jamais de photo ni d'image IA.**
6. **L'image montre ce dont parle la phrase en cours** (lieu déduit, méchant, objet avec son prix collé dessus, geste
   du verbe), **un changement fort toutes les 1 à 1,5 s**.
7. **Le squelette** accroche → promesse → escalade → règle → étapes → calcul → résolution est le minimum.
Le compte rendu au client dit, pour chacun des 7 points, comment la vidéo du jour l'applique.

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
- **Décision du client (20 nov.) : chaque jour, on refait un sujet de La Ficelle.** Prendre dans
  `prompts/sujets_laficelle.md` le sujet le mieux classé qui n'a pas encore été refait dans le NOUVEAU style (même s'il
  a déjà été traité chez nous dans l'ancien style), en sautant les sujets « culture éco » du bas du tableau. Noter
  « refait le JJ/MM » dans la dernière colonne. On reprend le sujet et les faits (vérifiés dans 2 sources), jamais leur
  texte, leurs personnages ni leurs images : script écrit par nous, moteur H1, Kévin et nos méchants. Le grand frère
  peut être le méchant quand le sujet s'y prête (le test du feuilleton en alternance est suspendu).
- La veille actu (`python3 scripts/veille_actu.py` → `prompts/veille_actu.md`) sert seulement à donner un angle
  d'actualité au sujet du jour, si une actu de la veille s'y rattache.
- Autres sources : actu (service-public.fr, Légifrance, economie.gouv.fr, franceinfo, BFM Éco, Capital, Selectra, Que Choisir +
  `prompts/actu_argent.md`), concurrents (`prompts/sujets_concurrents.md`), ou invention.
- Le sujet suit **le modèle gagnant** et passe les 8 critères. Vérifier la règle dans 2 sources ; noter références et
  sources dans l'en-tête du `.dial`.
- **Point 1 du 20 nov.** : le sujet doit avoir un méchant à battre ET un gain chiffré pour Kévin. Sans méchant (couple,
  conseil d'épargne) ou avec un gain éparpillé, on change d'angle ou de sujet (ce sont les flops de La Ficelle).
- **Filtre n° 1, avant les 8 critères : « est-ce qu'un 18–25 ans l'ENVERRAIT à un pote ou l'ENREGISTRERAIT ? »**
  Oui seulement si : actu chaude que tout le monde voit passer (IPO, prix, nouvelle loi), OU envie / dépense que presque
  tous les 18–25 ans ont (permis, premier appart, premier salaire, voiture, épargne). Un cas de niche (robe de mariée,
  vase cassé, taxes d'aéroport, frais d'agence pour un seul public) = non, même s'il est 8/8. Relevé du 19 nov. : la
  rétention des 1res secondes est la même sur les succès et les flops (78–83 % à 0:01) ; ce qui sépare 48 k de 300 vues,
  ce sont les partages et enregistrements, donc le sujet.
- Feuilleton du grand frère (`prompts/feuilleton_grand_frere.md`) : test en alternance SUSPENDU le 20 nov. (décision du
  client : sujets de La Ficelle chaque jour). Si le frère est le méchant, respecter la bible et la continuité.
- Proposer mentalement 3 accroches (PRIX, MÉPRIS, ENJEU) et garder la plus conforme au modèle gagnant et aux stats.

## 3. Script (15 min)
- Écrire `scripts/modele/NN_slug.dial` (NN = numéro suivant ; `M:` méchant, `N:` Kévin), en-tête complet : sources,
  transgression, verrou, entrée, axe, twist, chute, mot-enjeu, tier, 8/8, zone grise, **promesse**.
- Suivre « L'ordre d'un script » (squelette du 20 nov.) : la 1re ligne est la réplique du méchant à « tu » (M:), la
  promesse arrive dans les 3 phrases suivantes, au moins 6 montants, des étapes (« D'abord… Ensuite… La dernière… »),
  un calcul qui monte.
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
- **Avant de coder, écrire la liste des images** (point 6 du 20 nov.) : pour chaque phrase du script, le LIEU
  (déduit : « où ça se passerait si on le filmait ? »), le MÉCHANT, l'OBJET avec son PRIX COLLÉ DESSUS, le GESTE du
  verbe ; une date → calendrier / compte à rebours ; un message → notification. Le décor du lieu est créé pour la
  vidéo (pas de décor réutilisé tel quel).
- **Ouverture** : `D.sequence` en 3 plans calés sur la voix (≥ 1,1 s chacun ; temps des mots : voir la méthode dans
  `motion/boucle/frere_plateforme_ct.py`) : **1) le méchant qui dit sa réplique DANS le lieu de la phrase**, visage
  visible dès la 1re image (correction du client, 20 nov.), avec l'objet du conflit et son prix collé dessus (panneau
  du lieu, étiquette, facture, affiche ; `D.visage_chiffre` seulement si aucun objet ne porte le prix) → 2) le geste du
  verbe (l'objet tombe, l'affiche se colle, les pages s'envolent…) → 3) Kévin qui réagit (`D.reaction`).
- **Dialogues vivants** : `D.dialogue` (caméra qui glisse vers celui qui parle, gestes liés au texte : téléphone
  montré, plat servi, fourchette, parents qui réagissent), `D.gp_vivant` (méchant qui gesticule en parlant),
  `D.echo_vivant`. **Un changement fort à l'image toutes les 1 à 1,5 s** (coupe, zoom, objet qui arrive, geste) ;
  aucune scène de plus de 3 s sans changement.
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
  script complet, description, **commentaire à épingler**, ce que l'analyse a appris, ce qui a changé et pourquoi,
  et **comment la vidéo applique chacun des 7 points du 20 nov.**
- En cas d'échec à n'importe quelle étape : ne rien publier, dire au client ce qui bloque.
