# Histoires 3D « à toi de choisir » (thème tueur)

Vidéos verticales 1080x1920 en 3D low-poly : une histoire de survie qui s'arrête sur un
choix, le public vote en commentaire, l'épisode suivant suit le vote.

```
scripts/mon_loup_p1.txt  (script du moteur S1, format NARRATEUR > …)
episodes/mon_loup_p1.json  (voix, bruitages, plan caméra par réplique)
        │
     audio.py ──► build/audio.wav + build/timeline.json   (voix ElevenLabs, minutage mot à mot)
        │
  scene.html (Three.js) ◄── caméra, sous-titres mot à mot, texto, carton de règle, flèches du choix
        │
     render.js ──► output/mon_loup_p1.mp4
```

## Installation (une fois)

```bash
pip install numpy
cd tueur && npm install && npx playwright install chromium
export ELEVENLABS_API_KEY=...   # inutile dans l'environnement cloud « Tiktok », la clé y est déjà
```
ffmpeg doit être installé.

## Fabriquer un épisode

```bash
python tueur/verifier.py tueur/scripts/mon_loup_p1.txt   # le script respecte les règles ?
python tueur/audio.py tueur/episodes/mon_loup_p1.json    # voix + bruitages + timeline (~1 min)
node tueur/render.js --preview 0.3,10,30                 # quelques images pour vérifier (secondes)
node tueur/render.js                                     # la vidéo complète (~35 min pour 70 s)
```

Les voix sont toujours faites avec ElevenLabs. Chaque réplique est mise en cache dans
`build/tts_cache` : relancer `audio.py` ne consomme rien tant que le texte ne change pas.
Un épisode coûte environ 1 000 caractères.

## La fiche épisode (`episodes/*.json`)

| Champ | Rôle |
|---|---|
| `script` | Le script du moteur, dans `scripts/` |
| `tts.voix` | Une voix ElevenLabs par personnage. `effet` : `porte` (étouffée, derrière la porte) ou `telephone`. `texto: true` : la réplique s'affiche en texto au lieu des sous-titres. |
| `rythme` | Silences entre répliques, durée d'une `[PAUSE]`, tenue de l'écran final, durée minimum (les pauses s'allongent toutes seules pour ne jamais passer sous 61 s) |
| `bruitages` | Ce que donne chaque `[BRUITAGE]` du script : `knock3`, `buzz`, `creak`, `steps`, `sting`, et combien de temps il prend |
| `plans` | Un plan caméra par réplique, dans l'ordre. Les plans existants sont dans `PRESETS` de `scene.html` |
| `marques` | Les répliques où il se passe quelque chose (le héros marche, les pieds apparaissent, le texto, le retournement, le choix) |
| `hud`, `regle`, `texto`, `choix` | L'heure et la partie en haut, le carton de règle, la conversation de texto, les deux étiquettes du choix |
| `rouge` | Les mots qui passent en rouge dans les sous-titres. Sinon le mot le plus long du morceau |

Pour la partie 2 : nouveau script, nouvelle fiche, et de nouveaux plans dans `PRESETS` si la
caméra va ailleurs (salle de bain, cage d'escalier…).
