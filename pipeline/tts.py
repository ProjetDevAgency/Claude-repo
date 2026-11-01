"""Génération de la voix off (TTS neuronale Microsoft Edge, gratuite).

Si tu préfères ta vraie voix, passe --voice-file mon_enregistrement.wav à
make_video.py : cette étape est alors sautée.
"""
import asyncio
import re

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


async def _list():
    return [v for v in await edge_tts.list_voices() if v["Locale"].startswith("fr-")]


def list_french_voices():
    _comm._SSL_CTX = ssl_context()
    return asyncio.run(_list())


if __name__ == "__main__":
    for v in list_french_voices():
        print(v["ShortName"], v["Gender"])
