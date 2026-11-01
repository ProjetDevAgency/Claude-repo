"""Génération de la voix off (TTS neuronale Microsoft Edge, gratuite).

Si tu préfères ta vraie voix, passe --voice-file mon_enregistrement.wav à
make_video.py : cette étape est alors sautée.
"""
import asyncio
import json
import os
import re
import urllib.request

import edge_tts
import edge_tts.communicate as _comm

from .common import ssl_context


def prepare_text(script: str) -> str:
    """Nettoie le script pour la synthèse : un seul bloc, pas de retours inutiles."""
    text = re.sub(r"\s*\n+\s*", " ", script.strip())
    return re.sub(r"\s{2,}", " ", text)


async def _speak(text, voice, rate, out_path):
    await edge_tts.Communicate(text, voice, rate=rate).save(str(out_path))


def synthesize(script: str, out_path, voice="fr-FR-RemyMultilingualNeural", rate="+0%"):
    _comm._SSL_CTX = ssl_context()  # compatible avec les proxys d'entreprise
    asyncio.run(_speak(prepare_text(script), voice, rate, out_path))
    return out_path


def synthesize_elevenlabs(script: str, out_path, voice_id=None, model="eleven_multilingual_v2",
                          stability=0.45, similarity=0.8, style=0.15):
    """Voix ElevenLabs. La clé est lue dans la variable d'environnement
    ELEVENLABS_API_KEY (jamais écrite dans le code ni dans config.yaml)."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID")
    if not key or not voice_id:
        raise RuntimeError("ELEVENLABS_API_KEY et ELEVENLABS_VOICE_ID doivent être définis.")
    body = json.dumps({
        "text": prepare_text(script),
        "model_id": model,
        "voice_settings": {"stability": stability, "similarity_boost": similarity,
                           "style": style, "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_192",
        data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, context=ssl_context(), timeout=180) as r:
            open(out_path, "wb").write(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"ElevenLabs a répondu {e.code} : {e.read()[:300]!r}") from None
    return out_path


async def _list():
    return [v for v in await edge_tts.list_voices() if v["Locale"].startswith("fr-")]


def list_french_voices():
    _comm._SSL_CTX = ssl_context()
    return asyncio.run(_list())


if __name__ == "__main__":
    for v in list_french_voices():
        print(v["ShortName"], v["Gender"])
