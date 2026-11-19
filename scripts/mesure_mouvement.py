"""Mesure le mouvement À L'INTÉRIEUR des plans d'une vidéo (coupes retirées) : part de l'image qui bouge et images figées.
    python3 scripts/mesure_mouvement.py output/a_publier_finance/NN_slug.mp4
Cible (chantier visuel du 19 nov.) : part qui bouge ≥ 6 %, images figées ≤ 15 % (La Ficelle : 5 à 8 % / 4 à 27 %)."""
import subprocess, sys
import numpy as np
def mouvement(path, fps=10, w=90, h=160):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))          # différence moyenne entre 2 images (0-255)
    dans = d[d < 25]                                          # on retire les coupes (gros sauts)
    bouge = (np.abs(np.diff(f, axis=0)) > 12).mean(axis=(1, 2))[d < 25]   # part de l'image qui bouge
    return float(np.median(dans)), float(np.mean(bouge) * 100), float(np.mean(dans < 0.5) * 100)
for p in sys.argv[1:]:
    m, b, fixe = mouvement(p)
    print(f"{p.split('/')[-1][:34]:34s} mouvement {m:5.2f} · part de l'image qui bouge {b:4.1f} % · images quasi figées {fixe:4.0f} %")
