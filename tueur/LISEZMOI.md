# Histoires 3D « à toi de choisir » (thème tueur)

Vidéos verticales 1080x1920 en 3D low-poly : une histoire de survie qui s'arrête sur un
choix (A ou B), le public vote en commentaire, l'épisode suivant suit le vote.

```
episodes/ep1.json ──► audio.py ──► build/audio.wav + build/timeline.json
                                         │
                       scene.html (Three.js) ◄┘  caméra, sous-titres et événements calés sur la voix
                                         │
                       render.js ──► output/tueur_ep1.mp4
```

## Installation (une fois)

```bash
pip install edge-tts numpy          # voix gratuite Microsoft
cd tueur && npm install && npx playwright install chromium
```
ffmpeg doit être installé.

## Fabriquer un épisode

```bash
python tueur/audio.py tueur/episodes/ep1.json      # voix + bruitages + timeline (~10 s)
node tueur/render.js output/tueur_ep1.mp4          # rendu image par image (~10-15 min)
node tueur/render.js --preview 3,9.5,19            # quelques images pour vérifier (secondes)
```

## Ce qu'on change dans `episodes/*.json`

| Champ | Rôle |
|---|---|
| `lines` | Les phrases. `text` en blanc, `hi` en orange (la phrase-choc), `say` = ce que la voix lit si différent. `gap` = silence après. |
| `sfx` | Bruitages calés sur une phrase : `knock`, `buzz`, `creak`, `sting` (fabriqués par le code, aucun droit). |
| `hud` | Bandeau en haut : épisode, horloge de départ, lieu. |
| `choice` | Les deux choix affichés à la fin (A / B). |

Les `id` des phrases (`porte`, `judas`, `ombre`, `tel`, `message`, `choix`, `cta`) pilotent
les plans de caméra dans `scene.html` (fonction `shots()`). Un nouvel épisode avec un
nouveau décor = nouvelle scène à ajouter dans `scene.html`.
