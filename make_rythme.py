"""Fabrique une vidéo en mode « respiration » à partir d'un script YAML.

    python make_rythme.py scripts/rythme/femme_amant.yaml
    python make_rythme.py scripts/rythme/femme_amant.yaml --voice-file voix.mp3
"""
import argparse
from pathlib import Path

import yaml

from pipeline import edit, rythme, subtitles, tts
from pipeline.common import ROOT, duration, load_config


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--voice-file")
    ap.add_argument("--name")
    args = ap.parse_args()

    spec = yaml.safe_load(open(args.script, encoding="utf-8"))
    segs = spec["segments"]
    dur = float(spec.get("duration", 62.0))
    video = ROOT / spec["video"]
    name = args.name or Path(args.script).stem + "_rythme"
    work = ROOT / "output" / f"_work_{name}"
    work.mkdir(parents=True, exist_ok=True)
    full = " ".join(s["text"].strip() for s in segs)
    print(f"▶ {name} : {len(full)} caractères, {len(segs)} segments, {dur}s")

    if args.voice_file:
        raw = Path(args.voice_file)
    elif cfg["voice"].get("provider") == "elevenlabs":
        el = cfg["voice"].get("elevenlabs", {})
        raw = tts.synthesize_elevenlabs(full, work / "voice_raw.mp3", el.get("voice_id") or None,
                                        el.get("model", "eleven_v4"))
    else:
        raw = tts.synthesize(full, work / "voice_raw.mp3", cfg["voice"]["tts_voice"], cfg["voice"]["tts_rate"])

    skip = float(spec.get("skip_start", 0.0))
    voice, words, speed = rythme.build_audio(raw, segs, video, skip, dur, work, cfg["voice"])
    e = cfg["edit"]
    e["skip_start"] = skip
    e["original_audio_volume"] = 0.0          # le son d'origine est déjà dans le mix
    ass = subtitles.write_ass(words, work / "subs.ass", cfg["subtitles"], e["width"], e["height"],
                              dur, hold_max=0.35)
    title = None
    if cfg["title"]["enabled"] and spec.get("title"):
        title = edit.render_title(spec["title"], work / "title.png", e["width"],
                                  cfg["subtitles"]["font_file"], cfg["title"]["font_size"])
    out = ROOT / "output" / f"{name}.mp4"
    edit.build(video, voice, ass, out, cfg, dur, title, None)
    print(f"✅ {out} ({duration(out):.2f}s)")


if __name__ == "__main__":
    main()
