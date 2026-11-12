"""Génère les phrases du narrateur du live (ElevenLabs) → live/public/voix/*.mp3 + voix.json.

Usage : ELEVENLABS_API_KEY=… ELEVENLABS_VOICE_ID=… python3 live/make_voix.py
Les fichiers déjà présents ne sont pas régénérés (supprime-les pour refaire une phrase).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.tts import synthesize_elevenlabs  # noqa: E402

OUT = Path(__file__).resolve().parent / "public" / "voix"
OUT.mkdir(parents=True, exist_ok=True)

PHRASES = {
    "arrivee": [
        "Une nouvelle famille arrive au village !",
        "Un nouvel habitant ! Bienvenue à Fauché-les-Oies !",
        "Bienvenue ! Ta maison t'attend.",
        "Encore un nouveau voisin. Le village grandit !",
    ],
    "construction": [
        "Et une nouvelle construction ! Merci pour le cadeau !",
        "Ça construit à Fauché-les-Oies ! Merci !",
        "Le village s'agrandit. Merci beaucoup !",
    ],
    "discute": [
        "Ça discute bien dans le village ce soir !",
        "Il y a du monde dans les rues aujourd'hui !",
    ],
    "soir": ["Le soir tombe sur Fauché-les-Oies… C'est magnifique."],
    "matin": ["Le soleil se lève sur Fauché-les-Oies. Bonne journée, les habitants !"],
    "appel": [
        "Abonne-toi, et tu deviens un habitant du village !",
        "Partage le live à tes potes : plus on est, plus le village grandit !",
        "Chaque like, c'est un euro pour le village. Allez, on tapote !",
        "Envoie un cadeau, et ta maison apparaît dans la rue !",
    ],
    "monument": ["Oh ! Un monument ! Merci, c'est énorme !"],
}

index = {}
for cat, lignes in PHRASES.items():
    index[cat] = []
    for i, txt in enumerate(lignes):
        f = OUT / f"{cat}_{i}.mp3"
        if not f.exists():
            synthesize_elevenlabs(txt, f, model="eleven_v4", stability=0.5, style=0.35)
            print("✓", f.name, "·", txt)
        index[cat].append(f"voix/{f.name}")
(OUT / "voix.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
print(sum(len(v) for v in index.values()), "phrases")
