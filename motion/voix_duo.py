"""Voix à deux : le narrateur (ta voix ElevenLabs) + le méchant (une 2e voix, grave et méprisante).

Le dialogue s'écrit dans un fichier .dial, une réplique par ligne :
    M: Tes douze jours de congés ? T'avais qu'à les poser, espèce d'idiot.
    N: Faux. Et ce patron le sait pas encore…
(M = méchant, N = narrateur). Le script texte (.txt) utilisé pour les sous-titres est écrit à côté.

Usage : python3 motion/voix_duo.py scripts/modele/11_conges.dial output/_work_xxx/voice_raw.wav
Variables : ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID (narrateur), MECHANT_VOICE_ID (sinon Paul K, grave, français).
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.tts import synthesize_elevenlabs  # noqa: E402

MECHANT = os.environ.get("MECHANT_VOICE_ID", "5l4ttmr4SKNgi0HnOelT")   # « Paul K — Deep French Narrator »
SR = 48000


def lire_dial(chemin):
    lignes = []
    for brut in Path(chemin).read_text(encoding="utf-8").splitlines():
        brut = brut.strip()
        if not brut or brut.startswith("#"):
            continue
        qui, _, texte = brut.partition(":")
        lignes.append((qui.strip().upper(), texte.strip()))
    return lignes


def main():
    dial, sortie = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    lignes = lire_dial(dial)
    # le texte complet (sous-titres et repérage des scènes)
    dial.with_suffix(".txt").write_text(" ".join(t for _, t in lignes) + "\n", encoding="utf-8")
    morceaux = sortie.parent / "repliques"
    morceaux.mkdir(parents=True, exist_ok=True)
    wavs = []
    for i, (qui, texte) in enumerate(lignes):
        mp3 = morceaux / f"{i:02d}_{qui}.mp3"
        if not mp3.exists() or mp3.with_suffix(".txt").read_text(encoding="utf-8") != texte:
            if qui == "M":
                synthesize_elevenlabs(texte, mp3, MECHANT, "eleven_v4", stability=0.3, similarity=0.85, style=0.8)
            else:
                synthesize_elevenlabs(texte, mp3, None, "eleven_v4")
            mp3.with_suffix(".txt").write_text(texte, encoding="utf-8")
        wav = morceaux / f"{i:02d}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR),
                        "-af", "loudnorm=I=-16:TP=-1.5", str(wav)], check=True)
        wavs.append(wav)
    liste = morceaux / "liste.txt"
    blanc = morceaux / "blanc.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", "0.15",
                    str(blanc)], check=True)
    liste.write_text("".join(f"file '{w}'\nfile '{blanc}'\n" for w in wavs))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-ac", "1",
                    "-ar", str(SR), str(sortie)], check=True)
    print("✅", sortie, "·", len(lignes), "répliques")


if __name__ == "__main__":
    main()
