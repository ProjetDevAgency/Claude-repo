"""Format v3 « récit » (méthode prompts/methode_ecriture.md) : Kévin raconte à la 1re personne, le méchant a sa
propre voix (voix_duo.py). Chaque vidéo donne ses scènes, chacune calée sur une phrase du script ; ce module
s'occupe des plans communs, du compteur (sous la barre TikTok), des bruitages et du rendu.

Règles d'image : jamais de texte sur un visage (bandeaux à y ≈ 420/560, bulles au-dessus des têtes),
compteur en y 215–335, sous-titres à 69 % de la hauteur.
"""
import os

from PIL import Image, ImageDraw

import rue
from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, character, dim, ease, idle,
                     kevin, push, shot, tag)
from engine import H, W

BASE = 1560
KX, MX = 300, 780
MHEAD = (MX, BASE - 700)
KHEAD = (KX, BASE - 700)


def parle(t):
    return "o" if int(t * 7) % 2 else "grin"


def plan(fond, t, kpose=None, kx=KX, mechant=None, look=None, mx=MX, autres=(), devant=None, z=1.0, center=None,
         **kextra):
    """Un plan : décor + personnages secondaires + méchant + Kévin + premier plan, contours noirs."""
    big = fond().copy()
    d = ImageDraw.Draw(big)
    for x, lk, pose, seed, *base in autres:
        bob, blink = idle(t, seed)
        character(d, x, (base[0] if base else BASE) + bob, **{**lk, "blink": blink, **pose})
    if mechant is not None:
        bob, blink = idle(t, 0.6)
        character(d, mx, BASE + bob, **{**look, "blink": blink, "brows": "colere", **mechant})
    if kpose:
        kevin(d, kx, BASE, kpose, t, **kextra)
    if devant:
        devant(d, t)
    return rue.contour_aretes(shot(big, z, center=center), seuil=90, w=3)


def gros_plan_mechant(fond, look, lt, dur, z0=2.05, z1=2.2, devant=None, **pose):
    return plan(fond, lt, mechant={"mouth": parle(lt), **pose}, look=look, devant=devant, z=push(lt, dur, z0, z1),
                center=(MHEAD[0] - 40, MHEAD[1] + 40))


def gros_plan_kevin(fond, lt, dur, pose="triste", devant=None):
    return plan(fond, lt, pose, devant=devant, z=push(lt, dur, 2.0, 2.12), center=(KHEAD[0] + 40, KHEAD[1] + 40))


def echo(img, txt):
    """L'écho : les mots du méchant, seuls, en grand."""
    big_number(img, (540, 470), f"« {txt} »", 92, WHITE, k=1.0)


def barres(img, titre, items, lt, y0=470, sous=None):
    """Petit graphique en barres sur carte sombre. items : [(étiquette, valeur, texte, couleur, t0)]."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([70, y0, 1010, y0 + 760], radius=34, fill=(28, 28, 36))
    d.text((540, y0 + 70), titre, font=FA(56), fill=YEL, anchor="mm")
    if sous:
        d.text((540, y0 + 125), sous, font=FA(30), fill=(170, 170, 185), anchor="mm")
    vmax = max(v for _, v, _, _, _ in items)
    n = len(items)
    larg = 700 / n
    for k, (lab, v, txt, col, t0) in enumerate(items):
        if lt < t0:
            continue
        g = ease((lt - t0) / 0.6)
        x0 = 190 + k * larg
        h = 440 * v / vmax * g
        yb = y0 + 680
        d.rounded_rectangle([x0, yb - max(h, 8), x0 + larg - 80, yb], radius=12, fill=col)
        d.text((x0 + (larg - 80) / 2, yb - h - 40), txt, font=FA(44), fill=WHITE, anchor="mm")
        d.text((x0 + (larg - 80) / 2, yb + 40), lab, font=FA(32), fill=(200, 200, 210), anchor="mm")


class Recit:
    """compteur = dict(label, depart, montant, phrase) : le compteur passe de depart à montant à la phrase donnée."""

    def __init__(self, nom, script, voix, compteur=None):
        self.nom, self.script, self.voix, self.cpt = nom, script, voix, compteur
        self.T = {}

    def valeur(self, t):
        c = self.cpt
        t0 = self.T.get("gain")
        if t0 is None or t < t0:
            return c["depart"]
        return int(c["depart"] + (c["montant"] - c["depart"]) * ease((t - t0) / 0.7))

    def compteur(self, img, t):
        if not self.cpt:
            return
        v = self.valeur(t)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([30, 215, 450, 335], radius=18, fill=(20, 20, 26), outline=WHITE, width=3)
        d.text((54, 243), self.cpt["label"], font=FA(28), fill=(210, 210, 220), anchor="lm")
        d.text((54, 298), f"{v:,} €".replace(",", " "), font=FA(62), fill=GREEN if v else (240, 80, 80), anchor="lm")

    def fabriquer(self, beats):
        """beats : [(phrase de départ, fonction(lt, dur), bruitage ou None)]. La 1re scène démarre à 0."""
        v = CartoonVideo(self.nom, self.script, "", "", corner="")
        v.hook_head_start = 0.0
        v.sub_y = 0.69
        v.voice(self.voix)
        T = self.T
        apres = 0.0
        for k, (phrase, fn, son) in enumerate(beats):
            t0 = 0.0 if k == 0 else v.at(phrase, after=apres)
            apres = t0 + 0.01
            T[fn.__name__] = t0

            def g(lt, dur, fn=fn, t0=t0):
                img = fn(lt, dur)
                self.compteur(img, t0 + lt)
                return img
            g.__name__ = fn.__name__
            v.scenes.append((t0, g))
            if son:
                v.sfx(t0 + son[2] if len(son) > 2 else t0, son[0], son[1])
        if self.cpt and self.cpt.get("phrase"):
            T["gain"] = v.at(self.cpt["phrase"])
            v.sfx(T["gain"], "succes", 1.0)
        for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
            print(f"   {t0:5.1f}s {fn.__name__}")
        if os.environ.get("APERCU"):
            return self.apercu(v, os.environ["APERCU"])
        return v.render()

    def apercu(self, v, chemin):
        """Planche de contrôle : une image au milieu de chaque scène (sans rendu vidéo)."""
        sc = sorted(v.scenes, key=lambda x: x[0])
        vues = []
        for k, (t0, fn) in enumerate(sc):
            fin = sc[k + 1][0] if k + 1 < len(sc) else v.dur
            t = t0 + min(2.6, (fin - t0) * 0.7)
            vues.append((t, v._image(int(t * 30)).convert("RGB").resize((270, 480))))
        cols = 8
        planche = Image.new("RGB", (270 * cols, 480 * ((len(vues) + cols - 1) // cols)), (0, 0, 0))
        d = ImageDraw.Draw(planche)
        for k, (t, im) in enumerate(vues):
            planche.paste(im, ((k % cols) * 270, (k // cols) * 480))
            d.text(((k % cols) * 270 + 8, (k // cols) * 480 + 8), f"{t:.1f}s", font=FA(22), fill=YEL)
        planche.save(chemin)
        print("planche :", chemin)


def calque_kevin_tete(img, x, y, sc=1.0):
    """La tête de Kévin (casquette) dans une fenêtre de voiture."""
    d = ImageDraw.Draw(img)
    r = 48 * sc
    d.ellipse([x - r, y - r, x + r, y + r], fill=(242, 196, 160), outline=INK, width=4)
    d.chord([x - r - 4, y - r - 10, x + r + 4, y + r * 0.3], 180, 360, fill=(28, 28, 34), outline=INK, width=4)
    d.rectangle([x - r - 4, y - 8 * sc, x + r + 40 * sc, y + 4 * sc], fill=(28, 28, 34))
    d.ellipse([x - 18 * sc, y + 6 * sc, x - 6 * sc, y + 18 * sc], fill=INK)
    d.ellipse([x + 10 * sc, y + 6 * sc, x + 22 * sc, y + 18 * sc], fill=INK)
    d.arc([x - 20 * sc, y + 14 * sc, x + 24 * sc, y + 40 * sc], 10, 170, fill=INK, width=5)


def mention(img, txt, lt):
    tag(img, 540, 1460, txt, 24, (40, 40, 50), WHITE, rot=0, k=(lt - 0.5) / 0.3)


__all__ = ["BASE", "KX", "MX", "MHEAD", "KHEAD", "parle", "plan", "gros_plan_mechant", "gros_plan_kevin", "echo",
           "barres", "Recit", "calque_kevin_tete", "mention", "Image", "ImageDraw", "SS", "W", "H", "RED", "GREEN",
           "YEL", "WHITE", "INK", "dim", "tag", "big_number", "push", "ease"]
