"""Vidéo promo (≈14 s) du live « Villageois vs Zombies », montée à partir d'un enregistrement de la vraie page.

Usage : python3 motion/promo_live.py BRUT.webm DOSSIER_VOIX SORTIE.mp4 [début_s]
  BRUT.webm     : enregistrement de la page (Playwright, 1080x1920)
  DOSSIER_VOIX  : contient v_accroche.mp3 et v_appel.mp3
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motion"))
import sfx  # noqa: E402

BRUT, VOIX, SORTIE = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
DEBUT = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
DUREE = 14.6
W, H = 1080, 1920
ANTON = str(ROOT / "assets/fonts/Anton-Regular.ttf")
MONT = str(ROOT / "assets/fonts/Montserrat-ExtraBold.ttf")
INK, JAUNE, BLANC, ROUGE, VERT, VIOLET = (22, 22, 28), (255, 206, 0), (250, 250, 250), (232, 50, 60), (60, 207, 110), (181, 108, 255)

# temps dans la vidéo finale (s) : quand chaque alerte apparaît à l'écran
T_CHAMPION, T_GEANT, T_ABONNE, T_SPECIALE, T_APPEL = 3.6, 6.2, 8.8, 11.4, 12.2


def carton(lignes, y, fichier, pastille=None):
    """Texte en gros, contour noir, dans la zone libre du bas (au-dessus de l'interface TikTok)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if pastille:
        txt, coul = pastille
        f = ImageFont.truetype(MONT, 40)
        tw = d.textlength(txt, font=f) + 40          # + la place du point « en direct »
        d.rounded_rectangle([W / 2 - tw / 2 - 30, y - 92, W / 2 + tw / 2 + 30, y - 32], radius=30, fill=coul)
        x0 = W / 2 - tw / 2
        d.ellipse([x0, y - 74, x0 + 24, y - 50], fill=BLANC)
        d.text((x0 + 40, y - 62), txt, font=f, fill=BLANC, anchor="lm")
    for txt, taille, coul in lignes:
        f = ImageFont.truetype(ANTON, taille)
        d.text((W / 2, y), txt, font=f, fill=coul, anchor="mt", stroke_width=max(8, taille // 10), stroke_fill=INK)
        y += int(taille * 1.12)
    im.save(fichier)


def main():
    tmp = Path(tempfile.mkdtemp())
    cartons = [
        (0.0, T_CHAMPION, [("TAPE 1 OU 2", 150, JAUNE), ("ET TU ENTRES DANS LA BATAILLE", 64, BLANC)], None),
        (T_CHAMPION, T_ABONNE, [("TON CADEAU", 120, BLANC), ("= DES RENFORTS", 120, JAUNE)], None),
        (T_ABONNE, T_SPECIALE, [("ABONNÉ", 130, JAUNE), ("= CHAMPION", 130, BLANC)], None),
        (T_SPECIALE, DUREE, [("VILLAGEOIS VS ZOMBIES", 84, BLANC), ("CHOISIS TON CAMP", 120, JAUNE)], ("EN LIVE MAINTENANT", ROUGE)),
    ]
    entrees, filtres = [], []
    for i, (t0, t1, lignes, past) in enumerate(cartons):
        f = tmp / f"carton{i}.png"
        carton(lignes, 1330, f, past)
        entrees += ["-loop", "1", "-t", str(DUREE), "-i", str(f)]
    # image : léger zoom continu vers le champ de bataille, puis les cartons (petit « pop » à l'entrée)
    z = f"1+0.08*t/{DUREE}"
    filtres.append(f"[0:v]fps=30,scale=w='iw*({z})':h='ih*({z})':eval=frame,"
                   f"crop={W}:{H}:x='(iw-{W})/2':y='(ih-{H})*1000/{H}',setsar=1[v0]")
    prec = "v0"
    for i, (t0, t1, _, _) in enumerate(cartons):
        filtres.append(f"[{i + 1}:v]format=rgba[c{i}]")
        filtres.append(f"[{prec}][c{i}]overlay=0:0:enable='between(t,{t0},{t1})'[v{i + 1}]")
        prec = f"v{i + 1}"

    # son : musique de bataille + voix + bruitages
    SR = sfx.SR
    n = int(DUREE * SR)

    def lire(chemin, gain=1.0):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(chemin), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        return np.frombuffer(raw, dtype=np.float32) * gain

    def poser(piste, son, t):
        i = int(t * SR)
        j = min(len(piste), i + len(son))
        if i < len(piste):
            piste[i:j] += son[:j - i]

    voix = np.zeros(n, np.float32)
    poser(voix, lire(VOIX / "v_accroche.mp3"), 0.1)
    poser(voix, lire(ROOT / "live/public/voix/bataille_geant_1.mp3"), T_GEANT + 0.1)
    poser(voix, lire(ROOT / "live/public/voix/bataille_abonne_1.mp3"), T_ABONNE + 0.1)
    poser(voix, lire(VOIX / "v_appel.mp3"), T_APPEL)
    musique = lire(ROOT / "live/public/musique/bataille.mp3")[int(20 * SR):int(20 * SR) + n]
    musique = np.pad(musique, (0, n - len(musique)))
    # la musique baisse quand la voix parle
    env = np.convolve(np.abs(voix), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    musique = musique * np.where(env > 0.01, 0.28, 0.6)
    bruits = sfx.mix(np.zeros(n, np.float32), [
        (0.15, "pop", 0.6), (0.9, "pop", 0.5), (1.7, "pop", 0.5), (2.5, "pop", 0.5),
        (T_CHAMPION, "whoosh", 0.8), (T_CHAMPION + 0.2, "impact", 0.8),
        (T_GEANT, "impact", 1.0), (T_GEANT + 0.35, "impact", 0.9), (T_GEANT + 0.7, "impact", 0.9),
        (T_ABONNE, "succes", 0.9),
        (T_SPECIALE - 0.3, "whoosh", 1.0), (T_SPECIALE, "impact", 1.0), (T_SPECIALE + 0.1, "marteau", 0.6),
        (T_APPEL - 0.1, "notif", 0.7),
    ], sfx_gain=0.7)
    son = voix * 1.0 + musique + bruits
    son *= 0.95 / max(1e-6, np.max(np.abs(son)))
    wav = tmp / "son.f32"
    son.astype(np.float32).tofile(wav)

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(DEBUT), "-t", str(DUREE), "-i", str(BRUT), *entrees,
           "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(wav),
           "-filter_complex", ";".join(filtres + [f"[{len(cartons) + 1}:a]loudnorm=I=-14:TP=-1.5[a]"]),
           "-map", f"[{prec}]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-t", str(DUREE), "-movflags", "+faststart", str(SORTIE)]
    subprocess.run(cmd, check=True)
    print("✅", SORTIE)


if __name__ == "__main__":
    main()
