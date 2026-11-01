"""Fabrique une vidéo finale de 61 à 63 secondes.

Exemples :
    python make_video.py --script scripts/cheval_abattoir.txt --video library/raw/7702891546923863326.mp4
    python make_video.py --script scripts/x.txt --random-video          # pioche une vidéo non utilisée
    python make_video.py --script scripts/x.txt --video v.mp4 --voice-file ma_voix.wav
    python make_video.py --sujet "..." --hook "..." --random-video     # script écrit par Claude (API)
"""
import argparse
import json
import random
import re
import shutil
import time
from pathlib import Path

from pipeline import audio, edit, subtitles, tts
from pipeline.common import ROOT, duration, load_config
from pipeline.script import check, write_script


def pick_video(min_dur):
    idx_path = ROOT / "library" / "index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else {}
    vids = [p for p in (ROOT / "library" / "raw").glob("*.mp4")
            if not idx.get(p.stem, {}).get("used") and duration(p) > min_dur]
    if not vids:
        raise SystemExit("Aucune vidéo disponible : lance d'abord  python -m pipeline.download")
    return random.choice(vids)


def mark_used(video, out):
    idx_path = ROOT / "library" / "index.json"
    if not idx_path.exists():
        return
    idx = json.loads(idx_path.read_text())
    if video.stem in idx:
        idx[video.stem]["used"] = True
        idx[video.stem].setdefault("outputs", []).append(str(out.relative_to(ROOT)))
        idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2))


def default_title(script):
    first = re.split(r"(?<=[.?!])\s+", script.strip())[0].rstrip(".")
    words = first.split()
    return " ".join(words[:14]) + (" ..." if len(words) > 14 else " ...")


def main():
    cfg = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="fichier texte du script")
    ap.add_argument("--sujet", help="sujet (génère le script via l'API Claude)")
    ap.add_argument("--hook", default="")
    ap.add_argument("--video", help="vidéo source")
    ap.add_argument("--random-video", action="store_true")
    ap.add_argument("--voice-file", help="ta propre voix (wav/mp3) à la place de la voix IA")
    ap.add_argument("--elevenlabs", action="store_true", help="forcer la voix ElevenLabs")
    ap.add_argument("--title", help="texte du bandeau du haut (par défaut : début du hook)")
    ap.add_argument("--no-title", action="store_true")
    ap.add_argument("--skip-start", type=float, help="secondes à sauter au début de la source")
    ap.add_argument("--name", help="nom du fichier de sortie")
    ap.add_argument("--whisper", default="small", help="taille du modèle Whisper (base, small, medium)")
    args = ap.parse_args()

    e = cfg["edit"]
    if args.skip_start is not None:
        e["skip_start"] = args.skip_start
    video = Path(args.video) if args.video else pick_video(e["target_min"])
    print(f"▶ vidéo source : {video}")

    # 1. Script
    if args.script:
        script = Path(args.script).read_text(encoding="utf-8").strip()
    elif args.sujet:
        print("▶ écriture du script (Claude)…")
        script = write_script(args.hook, args.sujet, video=video)
        Path(ROOT / "scripts").mkdir(exist_ok=True)
        (ROOT / "scripts" / f"auto_{int(time.time())}.txt").write_text(script + "\n", encoding="utf-8")
    else:
        raise SystemExit("Donne --script ou --sujet")
    ok, issues, info = check(script, real_voice=bool(args.voice_file))
    print("▶ script : " + " | ".join(info))
    for i in issues:
        print(f"   ⚠ {i}")

    name = args.name or (Path(args.script).stem if args.script else f"video_{int(time.time())}")
    work = ROOT / "output" / f"_work_{name}"
    work.mkdir(parents=True, exist_ok=True)

    # 2. Voix
    if args.voice_file:
        raw_voice = Path(args.voice_file)
        print(f"▶ voix : fichier {raw_voice}")
    elif cfg["voice"].get("provider") == "elevenlabs" or args.elevenlabs:
        print("▶ voix IA : ElevenLabs")
        el = cfg["voice"].get("elevenlabs", {})
        raw_voice = tts.synthesize_elevenlabs(script, work / "voice_raw.mp3",
                                              el.get("voice_id") or None,
                                              el.get("model", "eleven_multilingual_v2"))
    else:
        print(f"▶ voix IA : {cfg['voice']['tts_voice']}")
        raw_voice = tts.synthesize(script, work / "voice_raw.mp3",
                                   cfg["voice"]["tts_voice"], cfg["voice"]["tts_rate"])

    # 3. Silences + accélération : la voix doit finir avant 63 s (petite marge de fin)
    tail = 0.35
    mid = (e["target_min"] + e["target_max"]) / 2
    voice, vdur, factor = audio.process_voice(
        raw_voice, work, cfg["voice"], target_voice=mid - tail,
        window=(e["target_min"] + 0.2 - tail, e["target_max"] - 0.3 - tail))
    final_dur = min(max(vdur + tail, e["target_min"]), e["target_max"])
    if vdur + tail < e["target_min"]:
        print(f"   ⚠ voix courte ({vdur:.1f}s) : la vidéo dure {final_dur:.1f}s, "
              "la fin reste sans voix. Allonge un peu le script.")
    print(f"▶ durée finale : {final_dur:.2f}s")

    # 4. Sous-titres mot à mot
    print("▶ sous-titres : transcription + alignement…")
    words = subtitles.transcribe_words(voice, args.whisper)
    aligned = subtitles.align(tts.prepare_text(script), words)
    ass = subtitles.write_ass(aligned, work / "subs.ass", cfg["subtitles"],
                              e["width"], e["height"], final_dur)

    # 5. Bandeau titre
    title_png = None
    if cfg["title"]["enabled"] and not args.no_title:
        title_png = edit.render_title(args.title or default_title(script), work / "title.png",
                                      e["width"], cfg["subtitles"]["font_file"],
                                      cfg["title"]["font_size"])

    # 6. Montage
    music_files = sorted((ROOT / "assets" / "music").glob("*.mp3")) + \
        sorted((ROOT / "assets" / "music").glob("*.wav"))
    music = random.choice(music_files) if music_files else None
    out = ROOT / "output" / f"{name}.mp4"
    print("▶ montage (miroir, étalonnage, sous-titres)…")
    edit.build(video, voice, ass, out, cfg, final_dur, title_png, music)
    shutil.copy(ROOT / "output" / f"_work_{name}" / "subs.ass", ROOT / "output" / f"{name}.ass")
    mark_used(video, out)
    print(f"✅ {out}  ({duration(out):.2f}s)")


if __name__ == "__main__":
    main()
