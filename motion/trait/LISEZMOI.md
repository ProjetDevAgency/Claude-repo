# Moteur « trait » : dessin animé vectoriel, rythme rapide, objets qui bougent

Le style vient de l'étude de @laficelle_off (3 vidéos décortiquées image par image, dont « colis perdu » à 1,6 M de vues).
On reprend leurs **principes** : traits épais, aplats avec un ombrage doux, décor sombre et chargé, lumière en faisceau,
compteur en haut à gauche, mots-clés surlignés dans les sous-titres, panneaux qui claquent, coupe toutes les 1 à 3 s.
On ne reprend **pas** leur look : ni leurs personnages (Marc, sweat orange), ni leurs couleurs, ni leurs décors, ni leur nom.

```bash
pip install pycairo                                   # une fois
python3 motion/trait/exemple_forfait.py               # → output/trait/exemple_forfait.mp4 (≈ 2 min de rendu)
python3 motion/trait/exemple_forfait.py --stills 1,5,12   # quelques images pour vérifier un plan
python3 scripts/mesure_mouvement.py output/trait/exemple_forfait.mp4
```

Mesure de la vidéo exemple : 7,2 % de l'image bouge, 14 % d'images figées
(cible de l'analyse : au moins 6 % et au plus 15 % ; La Ficelle : 5 à 8 % et 4 à 27 %).

## Les fichiers
| Fichier | Rôle |
|---|---|
| `voix.py` | ElevenLabs **avec le temps de chaque mot** (`/with-timestamps`, sans Whisper). Plusieurs voix (narrateur + méchant). `[mots]` = surlignés en jaune, `{mots}` = en rouge. Les appels sont mis en cache. |
| `dessin.py` | Primitives Cairo : `paint()` (aplat + ombre à droite + contour d'encre), `tube()`, faisceaux, halos, vignette, textes (Montserrat / Anton). Courbes `ease`, `back` (pop), `spring`. |
| `perso.py` | Personnage articulé : 10 poses (`repos`, `pointe`, `leve`, `telephone`, `facepalm`…), 6 émotions (`choc`, `malin`, `colere`…), cheveux (`boucles`, `court`, `plaque`, `chauve`, `chignon`), hauts (`sweat`, `polo`, `chemise`, `gilet`). Respiration, balancement, clignement, bouche calée sur la voix, petit saut quand il est choqué. `traits_choc()`. |
| `decors.py` | Boutique d'opérateur (écrans qui changent), salon le soir (fenêtres qui s'allument, lampe), fond sombre quadrillé pour les cartes. Objets : téléphone, contrat + tampon, étiquette qui se balance, calendrier, ampoule. |
| `ui.py` | Compteur permanent qui défile, sous-titres par groupes de 1 à 3 mots, panneau incliné, badge de rôle, carte « LA RÈGLE » cochée, notification, bulle de message. |
| `film.py` | Montage : un plan démarre **sur un mot** (`f.plan("pars", scene, cam=[...])`), caméra qui glisse et zoome, coup de fouet + whoosh à chaque coupe, secousses, bruitages de `motion/sfx.py`, rendu ffmpeg 1080x1920 30 i/s, son à -14 LUFS. |

## Faire une nouvelle vidéo
Copier `exemple_forfait.py`, puis changer dans l'ordre :
1. `LIGNES` : le texte, ligne par ligne, avec la voix de chaque ligne.
2. Le casting (`Perso(...)`) et ses poses / émotions calées sur des mots : `kev.emotion(T("pars"), "choc")`.
3. Les scènes : une fonction `scene(ctx, t, lt)` qui dessine le décor, les personnages et les objets du sujet.
4. Les plans : `f.plan(mot, scene, cam=[(temps, centre x, centre y, zoom), ...], hud=...)`. Viser un plan toutes les 1 à 3 s.
5. Les sons (`f.son`), secousses (`f.secousse`) et le compteur.

`T("mot", n)` = début du n-ième mot qui commence par « mot ». Attention aux mots courts (« Le » trouve aussi « le »).

## Réglage par défaut de la voix (choix du client, 20 nov.)
Comparaison faite sur l'histoire du pisciniste : **script complet + voix accélérée au montage** a été préféré à
« script raccourci + voix à vitesse normale ». Donc, par défaut :
1. Script complet selon le moteur H1 (`prompts/moteur_script.txt`, bloc 7) : 1 450 à 1 500 caractères,
   contrôlé par `python3 -m pipeline.script verifier`.
2. Voix « Yann » (`voix.YANN`), modèle `eleven_v4`, générée à vitesse normale, aucune indication d'émotion.
3. `voix.build(..., cible=voix.CIBLE)` : la voix est accélérée au montage (sans changer la hauteur) juste ce qu'il
   faut pour tenir 64 s, jamais plus de ×1,35. Si ça ne suffit pas, le moteur prévient : raccourcir le script.
4. `voix.verifier(voice, words, work)` : retranscription et liste des mots mal prononcés, à corriger avant le rendu.

Exemple complet : `piscine_dauphin.py` (+ `miniature_piscine.py` pour la couverture). Version courte pour
comparaison : `piscine_dauphin_court.py`.
