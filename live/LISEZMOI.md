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
- cycle jour/soir de 8 minutes.

Le village est sauvegardé dans `etat.json` et continue d'un live à l'autre.

## Avec un ordinateur (LIVE Studio)
1. Installer Node.js (nodejs.org, version LTS).
2. Dans ce dossier `live/` : `npm install` (une seule fois).
3. Mettre ton pseudo TikTok dans `config.json` → `"tiktok": "ton_pseudo"`.
4. `npm start`. Le serveur se branche tout seul dès que ton live démarre.
5. Dans LIVE Studio, ajouter la page http://localhost:3000 comme source :
   - avec une source « Lien » ou « Navigateur » si LIVE Studio en propose une ;
   - sinon, ouvrir la page dans Chrome et ajouter une « Capture de fenêtre ».
   Format vertical 1080×1920.
6. Page de pilotage : http://localhost:3000/admin. Elle montre l'état de la connexion et contient des boutons de test.

Tester sans être en live : `npm run demo` (faux événements en continu).

## Avec le téléphone seul (Android, « Jeu mobile »)
1. Installer Termux (depuis F-Droid), puis dans Termux :
   `pkg install nodejs git`, récupérer ce dossier, `npm install`, `npm start`.
2. Ouvrir http://localhost:3000 dans Chrome et toucher l'écran une fois pour le son.
3. Dans TikTok : LIVE → « Jeu mobile » → partager l'écran, puis revenir sur Chrome.
4. Mettre le téléphone en Ne pas déranger, et le brancher.

## Changer les dessins ou les phrases
- Dessins : `python3 live/make_sprites.py` (repris des façades des vidéos).
- Phrases du narrateur : `live/make_voix.py` (ElevenLabs). Pour refaire une phrase, supprimer son mp3 puis relancer.
