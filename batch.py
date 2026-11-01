"""Fabrique plusieurs vidéos à la suite à partir d'un fichier YAML.

    python batch.py batch.yaml
"""
import subprocess
import sys

import yaml

jobs = yaml.safe_load(open(sys.argv[1] if len(sys.argv) > 1 else "batch.yaml", encoding="utf-8"))
failed = []
for n, job in enumerate(jobs, 1):
    print(f"\n━━━━ {n}/{len(jobs)} : {job['script']} ━━━━", flush=True)
    cmd = [sys.executable, "make_video.py", "--script", job["script"], "--video", job["video"]]
    if job.get("title"):
        cmd += ["--title", job["title"]]
    if job.get("voice_file"):
        cmd += ["--voice-file", job["voice_file"]]
    if subprocess.run(cmd).returncode != 0:
        failed.append(job["script"])
print("\nTerminé." + (f" Échecs : {failed}" if failed else " Tout est bon."))
