# Machine à vidéos (repost amélioré)

Pipeline perso : vidéo source → script → voix → montage 61-63 s prêt à poster.

```
library/raw/*.mp4  ──►  script (tes 2 prompts)  ──►  voix IA ou ta voix
                                                      │  silences coupés
                                                      │  vitesse ajustée
                                                      ▼
        sortie 1080x1920, 61-63 s  ◄──  miroir + étalonnage + sous-titres mot à mot + bandeau
```

## Installation (une fois)

```bash
# ffmpeg doit être installé (brew install ffmpeg / apt install ffmpeg)
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # facultatif, pour que les scripts s'écrivent tout seuls
```

## Utilisation

### 1. Récupérer tes vidéos (> 1 minute)
```bash
python -m pipeline.download                       # compte défini dans config.yaml
python -m pipeline.download --account https://www.tiktok.com/@toncompte --limit 20
```
Les vidéos vont dans `library/raw/`. `library/index.json` note celles déjà utilisées.

### 2. Trouver des sujets et écrire le script
```bash
python -m pipeline.script sujets                  # prompt « Machine à sujets » → 20 sujets
python -m pipeline.script ecrire --sujet "..." --hook "..." \
       --video library/raw/XXXX.mp4 --out scripts/mon_script.txt
python -m pipeline.script verifier scripts/mon_script.txt   # contrôle des règles du moteur
```
`ecrire` envoie le moteur H1 complet (`prompts/moteur_script.txt`) avec 6 images
de la vidéo, pour que le script ne contredise jamais l'image. Sans clé API :
colle les PDF dans claude.ai et mets le script obtenu dans `scripts/`.

Le vérificateur contrôle : longueur 1 350 à 1 500 caractères, ponctuation interdite,
le symbole €, les chiffres, les négations en « ne », les anglicismes et les appels à
l'action, les phrases de plus de 25 mots, le nombre de points d'exclamation.

### 3. Fabriquer la vidéo
```bash
python make_video.py --script scripts/vache_abattoir.txt --video library/raw/7702891546923863326.mp4 \
       --title "Son fils voulait envoyer sa vache à l'abattoir mais j'ai trouvé la vraie raison ..."

python make_video.py --script scripts/x.txt --random-video          # pioche une vidéo pas encore utilisée
python make_video.py --script scripts/x.txt --video v.mp4 --voice-file ma_voix.wav   # ta vraie voix
python make_video.py --sujet "..." --hook "..." --random-video     # tout automatique (API)
```
La sortie est dans `output/<nom>.mp4`, avec le fichier de sous-titres `.ass` à côté.

## Ce que fait chaque étape

| Étape | Détail | Réglages (`config.yaml`) |
|---|---|---|
| Voix | Voix neuronale gratuite Microsoft (`fr-FR-RemyMultilingualNeural`) ou ton fichier | `voice.tts_voice`, `voice.tts_rate` |
| Silences | Chaque silence de plus de 0,15 s est ramené à 0,09 s ; début et fin coupés | `silence_threshold_db`, `min_silence`, `keep_silence` |
| Vitesse | Voix accélérée (sans changer la hauteur) pour tenir dans 61-63 s, max x1,35 | `max_speedup`, `min_speed` |
| Coupe | Vidéo coupée à la durée de la voix + 0,35 s, bornée à 61-63 s | `edit.target_min/max`, `skip_start` |
| Miroir | Flip horizontal | `edit.mirror` |
| Couleur | Contraste, saturation, gamma, teinte chaude, vignette, léger zoom | `edit.color`, `edit.zoom` |
| Sous-titres | Whisper donne le timing de chaque mot, le texte vient du script (zéro faute). Un mot à la fois, majuscules, contour noir, montants en jaune | `subtitles.*` (`position_y: 0.5` = centre exact) |
| Bandeau | Encadré blanc arrondi en haut pendant 5,5 s, comme sur ta vidéo modèle | `title.*` ou `--title` / `--no-title` |
| Son | Voix seule normalisée à -14 LUFS ; option ambiance d'origine ou musique (`assets/music/`) | `original_audio_volume`, `music_volume` |

## Changer de voix
```bash
python -m pipeline.tts          # liste toutes les voix françaises disponibles
```
Ou enregistre-toi et utilise `--voice-file` : le pipeline coupe tes silences et ajuste ta vitesse pareil.

## Arborescence
```
config.yaml            tous les réglages
make_video.py          commande principale
pipeline/download.py   récupération des vidéos (yt-dlp)
pipeline/script.py     sujets, écriture et vérification des scripts (API Claude)
pipeline/tts.py        voix IA
pipeline/audio.py      silences + vitesse + normalisation
pipeline/subtitles.py  transcription Whisper + alignement + fichier .ass
pipeline/edit.py       montage ffmpeg
prompts/               tes deux prompts en texte
scripts/               un fichier .txt par script
assets/fonts/          Montserrat ExtraBold (licence OFL)
```
