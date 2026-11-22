"""Analyse image par image (toutes les images réelles, 30 / s) : éléments qui bougent, durée et vitesse des mouvements,
mouvement de caméra, nombre d'éléments dessinés."""
import json, subprocess, sys
import numpy as np, cv2
from scipy import ndimage

def frames(path, w=270, h=480):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)

def analyse(path, fps=30):
    F = frames(path)
    n = len(F)
    diff = np.abs(F[1:].astype(np.int16) - F[:-1]).mean(axis=(1, 2))
    cut = diff > 18
    nb_el, cam, vit, statique = [], [], [], 0
    gh, gw = 16, 9
    runs = []                       # durées des mouvements par case de grille
    cur = np.zeros((gh, gw), int)
    for i in range(n - 1):
        if cut[i]:
            runs += list(cur[cur > 0]); cur[:] = 0
            continue
        flow = cv2.calcOpticalFlowFarneback(F[i], F[i + 1], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.hypot(flow[..., 0], flow[..., 1]) * 4          # en pixels d'une image 1080 de large
        g = np.median(flow.reshape(-1, 2), axis=0)
        camm = np.hypot(*g) * 4
        cam.append(camm)
        rel = np.hypot(flow[..., 0] - g[0], flow[..., 1] - g[1]) * 4
        mov = rel > 2.0
        mov = ndimage.binary_opening(mov, iterations=1)
        lab, k = ndimage.label(ndimage.binary_dilation(mov, iterations=2))
        if k:
            sizes = ndimage.sum(np.ones_like(lab), lab, range(1, k + 1))
            k = int((sizes >= 60).sum())
        nb_el.append(k)
        if k == 0 and camm < 0.5:
            statique += 1
        if mov.any():
            vit.append(float(np.median(rel[mov])))
        cells = mov.reshape(gh, 480 // gh, gw, 270 // gw).mean(axis=(1, 3)) > 0.08
        runs += list(cur[(~cells) & (cur > 0)])
        cur = np.where(cells, cur + 1, 0)
    runs += list(cur[cur > 0])
    runs = np.array(runs) / fps
    # éléments dessinés : contours sur une image par seconde
    el = []
    for i in range(0, n, fps):
        e = cv2.Canny(F[i], 60, 160)
        cs, _ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        el.append(sum(1 for c in cs if cv2.arcLength(c, False) > 25))
    nb_el = np.array(nb_el); cam = np.array(cam)
    return {
        "images": n, "durée_s": round(n / fps, 1), "coupes": int(cut.sum()),
        "éléments_qui_bougent_médiane": float(np.median(nb_el)), "éléments_qui_bougent_moyenne": round(float(nb_el.mean()), 2),
        "images_avec_3+_éléments_qui_bougent_%": round(100 * float((nb_el >= 3).mean()), 1),
        "images_sans_aucun_mouvement_%": round(100 * statique / max(1, len(nb_el)), 1),
        "durée_mouvement_médiane_s": round(float(np.median(runs)), 2) if len(runs) else 0,
        "mouvements_de_plus_de_1s_%": round(100 * float((runs > 1).mean()), 1) if len(runs) else 0,
        "mouvements_de_plus_de_2s_%": round(100 * float((runs > 2).mean()), 1) if len(runs) else 0,
        "vitesse_mouvement_médiane_px_par_image": round(float(np.median(vit)), 1) if vit else 0,
        "caméra_qui_bouge_%": round(100 * float((cam > 0.5).mean()), 1),
        "vitesse_caméra_médiane_px_par_image": round(float(np.median(cam[cam > 0.5])), 2) if (cam > 0.5).any() else 0,
        "éléments_dessinés_par_image_médiane": float(np.median(el)),
    }

if __name__ == "__main__" and (len(sys.argv) < 2 or sys.argv[1] != "--regle"):
    out = {p.split("/")[-1]: analyse(p) for p in sys.argv[1:]}
    print(json.dumps(out, ensure_ascii=False, indent=1))


def trous(path, fps=30, seuil=0.03, maxi=2.0):
    """Règle « un changement toutes les 1 à 2 s » : renvoie les passages de plus de `maxi` secondes sans coupe ni
    animation visible (part de l'image qui bouge > seuil, bande des sous-titres exclue)."""
    F = frames(path)
    ev = []
    for i in range(len(F) - 1):
        a, b = F[i].astype(np.int16), F[i + 1].astype(np.int16)
        d = np.abs(b - a)
        d[300:360] = 0                                  # bande des sous-titres (y ≈ 1200-1440 sur 1920)
        if d.mean() > 18 or (d > 25).mean() > seuil:
            ev.append((i + 1) / fps)
    ev = [0.0] + ev + [len(F) / fps]
    gaps = [(a, b - a) for a, b in zip(ev, ev[1:]) if b - a > maxi]
    return ev, gaps


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "--regle":
    for p in sys.argv[2:]:
        ev, gaps = trous(p)
        print(p.split("/")[-1], f"{len(gaps)} passage(s) de plus de 2 s sans changement",
              [f"{a:.1f}s ({g:.1f}s)" for a, g in gaps])
