"""Outils partagés : config, ffmpeg, chemins."""
import json
import os
import ssl
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_config(path=None):
    path = Path(path or ROOT / "config.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(cmd, **kw):
    """Lance une commande et lève une erreur lisible si elle échoue."""
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        raise RuntimeError(f"Commande échouée : {' '.join(map(str, cmd))}\n{res.stderr[-3000:]}")
    return res.stdout


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def video_size(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height", "-of", "json", str(path)])
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"]


def ssl_context():
    """Contexte SSL qui respecte un bundle CA d'entreprise/proxy si présent."""
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not cafile and Path("/root/.ccr/ca-bundle.crt").exists():
        cafile = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
