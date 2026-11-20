"""Éléments graphiques posés par-dessus l'image : compteur, sous-titres, panneaux, cartes, notifications."""
import math

from dessin import (H, INK, LW, W, back, blit, circle, clamp, ease, ease_out, ecrit, flat, paint, poly, rrect,
                    stroke, texte)

YEL = (255, 210, 40)
RED = (232, 52, 60)
GREEN = (70, 205, 115)


# ───────────── compteur permanent (haut gauche) ─────────────

def compteur(ctx, t, titre, cles, apparition=0.0, prefixe="", suffixe=" €", toujours_vert=False):
    """cles : [(temps, valeur)] ; la valeur défile entre deux clés (0,6 s), en vert quand elle monte."""
    if t < apparition:
        return
    k = back((t - apparition) / 0.35)
    val, monte = cles[0][1], 0.0
    for i, (tk, v) in enumerate(cles):
        if t >= tk:
            prev = cles[i - 1][1] if i else v
            p = ease_out((t - tk) / 0.6)
            val = prev + (v - prev) * p
            if v > prev and p < 1:
                monte = 1 - p
    ctx.save()
    ctx.translate(48, 150)
    ctx.scale(k, k)
    rrect(ctx, 0, 0, 430, 140, 20)
    ctx.set_source_rgba(0.09, 0.08, 0.11, 0.9)
    ctx.fill_preserve()
    stroke(ctx, 5, GREEN if (monte > 0 or toujours_vert) else RED)
    ecrit(ctx, titre, 26, 34, 26, (230, 230, 235), ax=0)
    col = GREEN if (val > 0 or toujours_vert) else RED
    sc = 1 + 0.18 * monte
    ecrit(ctx, f"{prefixe}{int(round(val))}{suffixe}", 26, 92, 74, col, big=True, ax=0, scale=sc)
    ctx.restore()


# ───────────── sous-titres mot à mot ─────────────

def decouper(words, maxi=3):
    """Groupes de 1 à 3 mots, coupés sur la ponctuation et les changements de ligne."""
    groupes, cur = [], []
    for i, w in enumerate(words):
        if cur and (len(cur) >= maxi or w["line"] != cur[-1]["line"]):
            groupes.append(cur)
            cur = []
        cur.append(w)
        if w["w"][-1] in ",.!?…:;":
            groupes.append(cur)
            cur = []
    if cur:
        groupes.append(cur)
    return groupes


def sous_titres(ctx, t, groupes, y=1290, size=58, largeur_max=None):
    """Groupe de mots en cours ; s'il dépasse `largeur_max`, il passe sur 2 lignes (comme les vidéos de référence)."""
    g = None
    for i, gr in enumerate(groupes):
        fin = groupes[i + 1][0]["t0"] if i + 1 < len(groupes) else gr[-1]["t1"] + 0.6
        fin = min(fin, gr[-1]["t1"] + 0.7)
        if gr[0]["t0"] - 0.03 <= t < fin:
            g = gr
            break
    if not g:
        return
    sp = size * 0.32
    surfs = []
    for w in g:
        coul = (20, 20, 24) if w["mark"] == "y" else (255, 255, 255)
        surfs.append(texte(w["w"], size, coul))
    lignes, cur, larg = [], [], 0.0
    for w, sf in zip(g, surfs):
        lw_ = sf.get_width()
        colle = cur and w["w"][:1].isdigit() and cur[-1][0]["w"].rstrip(",.").isdigit()   # « 11 000 » reste entier
        if cur and largeur_max and larg + sp + lw_ > largeur_max and not colle:
            lignes.append(cur)
            cur, larg = [], 0.0
        cur.append((w, sf))
        larg += (sp if len(cur) > 1 else 0) + lw_
    lignes.append(cur)
    hgt = surfs[0].get_height()
    inter = hgt * 1.12
    tots = [sum(sf.get_width() for _, sf in li) + sp * (len(li) - 1) for li in lignes]
    k = back((t - g[0]["t0"]) / 0.18)
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    hb = hgt + inter * (len(lignes) - 1)
    rrect(ctx, -max(tots) / 2 - 24, -hgt / 2 - 14, max(tots) + 48, hb + 28, 18)
    ctx.set_source_rgba(0.08, 0.08, 0.1, 0.8)
    ctx.fill()
    for n, (li, tot) in enumerate(zip(lignes, tots)):
        x = -tot / 2
        yy = n * inter
        for w, sf in li:
            dit = t >= w["t0"] - 0.02
            if w["mark"] in ("y", "r"):
                rrect(ctx, x - 8, yy - hgt / 2 - 4, sf.get_width() + 16, hgt + 8, 10)
                flat(ctx, YEL if w["mark"] == "y" else RED, 1.0 if dit else 0.5)
            blit(ctx, sf, x, yy, ax=0, ay=0.5, alpha=1.0 if dit else 0.45)
            x += sf.get_width() + sp
    ctx.restore()


# ───────────── panneau incliné (mot-clé dans le décor) ─────────────

def panneau(ctx, x, y, txt, t, rot=-0.06, size=70, fond=(30, 28, 38), bord=RED, col=(250, 250, 250), s=1.0):
    if t < 0:
        return
    k = back(t / 0.3) * s
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot + math.sin(t * 2) * 0.01)
    ctx.scale(k, k)
    sf = texte(txt, size, col, True)
    w, h = sf.get_width() + 60, sf.get_height() + 34
    rrect(ctx, -w / 2 + 8, -h / 2 + 10, w, h, 14)
    flat(ctx, (0, 0, 0), 0.35)
    rrect(ctx, -w / 2, -h / 2, w, h, 14)
    ctx.set_source_rgb(*[v / 255 for v in fond])
    ctx.fill_preserve()
    stroke(ctx, 7, bord)
    blit(ctx, sf, 0, 2)
    ctx.restore()


def badge(ctx, x, y, txt, t):
    """Badge de rôle au-dessus d'une tête (LE VENDEUR…)."""
    panneau(ctx, x, y, txt, t, rot=0, size=34, fond=(250, 250, 250), bord=INK, col=INK)
    if t > 0:
        k = back(t / 0.3)
        poly(ctx, [(x - 14 * k, y + 32 * k), (x + 14 * k, y + 32 * k), (x, y + 50 * k)])
        flat(ctx, INK)


# ───────────── carte d'explication (liste cochée) ─────────────

def carte_regle(ctx, t, titre, items, y0=330):
    """items : [(temps d'apparition relatif, texte, mot à surligner ou None)]."""
    k = back(t / 0.35)
    ctx.save()
    ctx.translate(W / 2, y0)
    ctx.scale(k, k)
    rrect(ctx, -460, 0, 920, 140 + 170 * len(items), 30)
    ctx.set_source_rgba(0.97, 0.96, 0.93, 1)
    ctx.fill_preserve()
    stroke(ctx, LW * 1.2)
    rrect(ctx, -460, 0, 920, 120, 30)
    flat(ctx, RED)
    ctx.rectangle(-460, 80, 920, 40)
    flat(ctx, RED)
    ctx.move_to(-460, 120)
    ctx.line_to(460, 120)
    stroke(ctx, LW * 1.2)
    ecrit(ctx, titre, 0, 62, 70, (255, 255, 255), big=True)
    for i, (ti, txt, surl) in enumerate(items):
        lt = t - ti
        if lt < 0:
            continue
        yy = 210 + i * 170
        a = ease(lt / 0.25)
        dx = (1 - ease_out(lt / 0.3)) * 80
        # case cochée
        circle(ctx, -380 + dx, yy, 42)
        paint(ctx, GREEN, LW, shade=0.85)
        ck = ease(lt / 0.25)
        ctx.move_to(-400 + dx, yy)
        ctx.line_to(-386 + dx, yy + 16 * ck)
        ctx.line_to(-386 + 30 * ck + dx, yy + 16 - 34 * ck)
        stroke(ctx, 10, (255, 255, 255))
        lignes = txt.split("\n")
        for j, l in enumerate(lignes):
            ly = yy + (j - (len(lignes) - 1) / 2) * 62
            if surl and surl in l:
                sw = texte(l, 50, INK).get_width()
                p = ease((lt - 0.25) / 0.4)
                rrect(ctx, -310 + dx - 6, ly - 34, (sw + 12) * p, 66, 8)
                flat(ctx, YEL, 0.9)
            ecrit(ctx, l, -310 + dx, ly, 50, INK, ax=0, ay=0.5, alpha=a)
    ctx.restore()


# ───────────── notification qui tombe du haut ─────────────

def notif(ctx, t, x, y, app, titre, corps, s=1.0, couleur=(150, 70, 170)):
    if t < 0:
        return
    k = ease_out(t / 0.35)
    ctx.save()
    ctx.translate(x, y - (1 - k) * 260)
    ctx.scale(s, s)
    rrect(ctx, -420 + 10, 10, 840, 210, 34)
    flat(ctx, (0, 0, 0), 0.3)
    rrect(ctx, -420, 0, 840, 210, 34)
    paint(ctx, (250, 250, 252), LW, shade=0.95)
    rrect(ctx, -390, 34, 92, 92, 22)
    paint(ctx, couleur, LW * 0.8, shade=0.9)
    ecrit(ctx, app[:1], -344, 82, 60, (255, 255, 255), big=True)
    ecrit(ctx, app.upper(), -270, 50, 28, (120, 120, 130), ax=0)
    ecrit(ctx, "maintenant", 390, 50, 26, (150, 150, 160), ax=1)
    ecrit(ctx, titre, -270, 100, 40, INK, ax=0)
    ecrit(ctx, corps, -270, 160, 32, (90, 90, 100), ax=0)
    ctx.restore()


def bulle(ctx, x, y, txt, t, size=44, cote=1):
    """Bulle de message (style messagerie)."""
    if t < 0:
        return
    k = back(t / 0.3)
    sf = texte(txt, size, (255, 255, 255))
    w, h = sf.get_width() + 56, sf.get_height() + 40
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2.4)
    paint(ctx, (40, 140, 240), LW * 0.8, shade=1)
    blit(ctx, sf, 0, 0)
    ctx.restore()
