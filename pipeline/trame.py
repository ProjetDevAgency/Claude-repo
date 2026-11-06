"""Trame minutée d'une vidéo source : quand le créateur parle, ce qu'il constate,
quand il se tait (moments d'action), et ce qu'on voit à l'image.

    python -m pipeline.trame library/raw/7621673039805123870.mp4
    python -m pipeline.trame library/raw/XXX.mp4 --start 5 --duration 62

Sortie : output/trames/<id>.md (créneaux PAROLE / PAUSE, avec budget de
caractères par créneau) et output/trames/<id>.png (une image toutes les 2 s).
On écrit ensuite le script dans les créneaux PAROLE (nos mots, nos faits
vérifiés à l'image, notre histoire) et on laisse les PAUSES au bruit de travail.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np

from .common import ROOT

CHARS_PER_S = 15.5      # débit de la voix ElevenLabs v4, silences coupés


def _audio16(video):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def slots(video, start=0.0, duration=62.0, min_pause=1.5):
    from faster_whisper import WhisperModel
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    a = _audio16(video)
    win = a[int(start * 16000): int((start + duration) * 16000)]
    opts = VadOptions(threshold=0.4, min_silence_duration_ms=int(min_pause * 1000), speech_pad_ms=150)
    speech = [(r["start"] / 16000, r["end"] / 16000) for r in get_speech_timestamps(win, opts)]
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(win, language="en", vad_filter=True)
    lines = [(s.start, s.end, s.text.strip()) for s in segs]

    def db(t0, t1):
        x = win[int(t0 * 16000): int(t1 * 16000)]
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else -99

    out, cur = [], 0.0
    for s0, s1 in speech:
        if s0 - cur >= 0.5:
            out.append(("PAUSE", cur, s0, db(cur, s0), ""))
        # chaque phrase va au créneau qu'elle recouvre le plus
        said = " ".join(t for (l0, l1, t) in lines
                        if max(speech, key=lambda r: min(r[1], l1) - max(r[0], l0)) == (s0, s1))
        out.append(("PAROLE", s0, s1, db(s0, s1), said))
        cur = s1
    if duration - cur >= 0.5:
        out.append(("PAUSE", cur, duration, db(cur, duration), ""))
    return out


def contact_sheet(video, start, duration, png):
    font = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
    vf = (f"fps=0.5,scale=150:-1,drawtext=text='%{{pts\\:hms}}':fontsize=20:fontcolor=yellow:"
          f"box=1:boxcolor=black:x=3:y=3:fontfile={font},tile=8x4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start}", "-t", f"{duration}", "-i", str(video),
                    "-vf", vf, "-frames:v", "1", str(png)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=62.0)
    args = ap.parse_args()
    video = Path(args.video)
    outdir = ROOT / "output" / "trames"
    outdir.mkdir(parents=True, exist_ok=True)
    stem = video.stem
    rows = slots(video, args.start, args.duration)
    contact_sheet(video, args.start, args.duration, outdir / f"{stem}.png")
    md = [f"# Trame {stem} (de {args.start:.0f} s à {args.start + args.duration:.0f} s)\n",
          "| Créneau | De | À | Durée | Budget | Son | Ce que dit le créateur (faits à reprendre avec nos mots) |",
          "|---|---|---|---|---|---|---|"]
    talk = 0.0
    for kind, t0, t1, lvl, said in rows:
        d = t1 - t0
        budget = f"~{int(d * CHARS_PER_S)} car." if kind == "PAROLE" else "bruit de travail"
        talk += d if kind == "PAROLE" else 0
        md.append(f"| {kind} | {t0:.1f} | {t1:.1f} | {d:.1f} s | {budget} | {lvl:.0f} dB | {said} |")
    md.append(f"\nParole : {talk:.0f} s sur {args.duration:.0f} s → budget total ≈ {int(talk * CHARS_PER_S)} caractères.")
    (outdir / f"{stem}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
