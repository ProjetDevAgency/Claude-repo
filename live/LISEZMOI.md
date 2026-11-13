# Live « Fauché-les-Oies »

Le village en direct pour un live TikTok. Les règles sont les mêmes que sur les lives « village » :
- 1 abonné = 1 habitant ;
- 1 like = 1 € de budget ;
- chaque cadeau construit un bâtiment selon son prix :

| Cadeau | Bâtiment |
|---|---|
| 1 pièce | un arbre |
| 5+ pièces | une cabane |
| 30+ pièces | une maison |
| 100+ pièces | une grande maison |
| 500+ pièces | un immeuble |
| 2000+ pièces | un monument |

- classement « Top bâtisseurs » ;
- objectif 10 000 habitants ;
- les commentaires s'affichent en bulle au-dessus du bonhomme de la personne ;
- un narrateur parle de temps en temps ;
- cycle jour/soir de 8 minutes, avec une musique de jour et une musique de nuit (originales, générées par ElevenLabs) ;
  volume dans `config.json` → `"musique"` (0 = coupée, 1 = fort ; 0.8 par défaut).

Le village repart de zéro à chaque lancement (0 habitant, objectif 10 000) : il n'est pas relié au vrai nombre
d'abonnés du compte. Les bâtiments des épisodes restent dans la rue comme décor. La page de pilotage a un bouton
« Remettre le village à zéro ».

## Mode « Le Quiz du Million » (mode par défaut)
- Les spectateurs écrivent **A, B, C ou D** en commentaire ; 20 s par question, seule la 1ʳᵉ réponse compte.
- Leur photo de profil apparaît dans la case qu'ils ont choisie.
- 10 paliers de 6 questions, thème tiré au sort à chaque palier ; une bonne réponse rapporte de 1 000 € (palier 1)
  à 60 000 € (palier 10) : tout juste = 1 000 000 € (argent fictif).
- Abonné = +20 % sur ses gains · cadeau 1+ = joker (1 erreur pardonnée) · 30+ = x2 sur le palier (1 fois par partie)
  · 100+ = 50/50 pour tout le monde.
- Une partie dure environ 30 min, puis une nouvelle commence. 156 questions dans `public/questions.json`
  (on peut en ajouter : relancer `make_voix.py` pour enregistrer leur lecture).
- Pour changer de mode pendant le live : page de pilotage → Mode du live.

## Mode « Villageois vs Zombies »
Un deuxième jeu, à lancer depuis la page de pilotage (bouton « 🧟 Villageois vs Zombies ») :
- commentaire **1** = rejoindre les villageois, **2** = les zombies (ton bonhomme entre sur le terrain) ;
- cadeau = renforts dans ton équipe : 1 pièce 1 combattant, 5 → 3, 30 → un champion, 100 → 5 + un champion,
  500 → un géant, 2000 → attaque spéciale ;
- like = répare le camp de ton équipe ; abonnement = un combattant offert ;
- manches de 4 minutes ; des combattants automatiques font vivre la bataille même avec peu de monde.

## Avec un ordinateur (LIVE Studio)
1. Installer Node.js (nodejs.org, version LTS).
2. Dans ce dossier `live/` : `npm install` (une seule fois).
3. Mettre ton pseudo TikTok dans `config.json` → `"tiktok": "ton_pseudo"`.
4. Double-cliquer sur `lancer_live.bat` (Windows) ou `lancer_live.command` (Mac).
   Ça démarre le serveur, qui se branche tout seul dès que ton live démarre, et ouvre le village
   dans une fenêtre Chrome où **le son se lance sans cliquer**.
5. Dans LIVE Studio, ajouter le village comme source :
   - avec une source « Lien » ou « Navigateur » si LIVE Studio en propose une
     (adresse http://localhost:3000 ; le son y démarre tout seul) ;
   - sinon, ajouter une « Capture de fenêtre » de la fenêtre Chrome ouverte à l'étape 4.
   Format vertical 1080×1920.
6. Page de pilotage : http://localhost:3000/admin. Elle montre l'état de la connexion et contient des boutons de test.

Tester sans être en live : `npm run demo` (faux événements en continu).

## Avec le téléphone seul (Android, « Jeu mobile »)
1. Installer Termux (depuis F-Droid), puis dans Termux :
   `pkg install nodejs git`, récupérer ce dossier, `npm install`, `npm start`.
2. Ouvrir http://localhost:3000 dans **Firefox** : menu → Paramètres → Autorisations du site →
   Lecture automatique → « Autoriser l'audio et la vidéo ». Le son se lance alors sans toucher l'écran.
   (Chrome sur Android bloque le son tant qu'on n'a pas touché l'écran une fois : il n'a pas de réglage pour ça.)
3. Dans TikTok : LIVE → « Jeu mobile » → partager l'écran, puis revenir sur Firefox.
4. Mettre le téléphone en Ne pas déranger, et le brancher.

## Changer les dessins ou les phrases
- Dessins : `python3 live/make_sprites.py` (repris des façades des vidéos).
- Phrases du narrateur : `live/make_voix.py` (ElevenLabs). Pour refaire une phrase, supprimer son mp3 puis relancer.
