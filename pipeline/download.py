"""Télécharge toutes les vidéos d'un compte TikTok qui durent plus de N secondes.

Usage :
    python -m pipeline.download                 # utilise config.yaml
    python -m pipeline.download --account https://www.tiktok.com/@moncompte --min 60

Les vidéos vont dans library/raw/<id>.mp4 et un index library/index.json
garde la durée, la description et l'état (utilisée ou non).
"""
import argparse
import json
import subprocess
import sys

from .common import ROOT, load_config

INDEX = ROOT / "library" / "index.json"


def load_index():
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {}


def save_index(idx):
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")


def list_account(url):
    out = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--flat-playlist", "--print",
         "%(id)s\t%(duration)s\t%(title)s", url],
        capture_output=True, text=True)
    if out.returncode != 0 and not out.stdout:
        raise RuntimeError(out.stderr[-2000:])
    items = []
    for line in out.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        vid, dur = parts[0], parts[1]
        try:
            dur = float(dur)
        except ValueError:
            continue
        items.append({"id": vid, "duration": dur, "title": parts[2] if len(parts) > 2 else ""})
    return items


def main():
    cfg = load_config()["download"]
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", default=cfg["account_url"])
    ap.add_argument("--min", type=float, default=cfg["min_duration"])
    ap.add_argument("--limit", type=int, default=0, help="0 = tout")
    args = ap.parse_args()

    raw = ROOT / "library" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    idx = load_index()
    base = args.account.rstrip("/")
    items = [i for i in list_account(args.account) if i["duration"] > args.min]
    print(f"{len(items)} vidéos de plus de {args.min:.0f}s trouvées")
    todo = [i for i in items if not (raw / f"{i['id']}.mp4").exists()]
    if args.limit:
        todo = todo[: args.limit]
    for n, it in enumerate(todo, 1):
        url = f"{base}/video/{it['id']}"
        print(f"[{n}/{len(todo)}] {it['id']} ({it['duration']:.0f}s)", flush=True)
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "-q", "--no-warnings",
                            "-f", "bv*+ba/b", "--merge-output-format", "mp4",
                            "-o", str(raw / "%(id)s.%(ext)s"), url])
        if r.returncode != 0:
            print("   échec, on passe")
            continue
        idx.setdefault(it["id"], {"duration": it["duration"], "title": it["title"], "used": False})
        save_index(idx)
    for it in items:  # complète l'index pour les vidéos déjà présentes
        if (raw / f"{it['id']}.mp4").exists():
            idx.setdefault(it["id"], {"duration": it["duration"], "title": it["title"], "used": False})
    save_index(idx)
    print(f"Terminé. {sum(1 for _ in raw.glob('*.mp4'))} vidéos dans library/raw")


if __name__ == "__main__":
    main()
