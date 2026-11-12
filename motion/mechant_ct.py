"""Format v3 « le méchant » : l'adversaire est méprisant du début à la fin, avec sa propre voix (voix_duo.py).

Déroulé commun (61 s) : réplique-claque à 0:00 → « Faux » + gain en vert → mise en place → 3 répliques de plus en plus
dures → Sarah → « heureusement, Kévin est abonné » → la règle → la lettre/le mail → le méchant crache dessus →
la riposte → le calcul → « on en a tous un » → le gain arrive + question en commentaire → retour sur sa phrase.
Chaque vidéo donne son décor, son méchant et ses textes dans un dictionnaire (voir conges_ct.py, occasion_ct.py).
"""
from PIL import Image, ImageDraw

import rue
from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, shake, shock_lines, shot, tag)
from engine import H, W
from prime_ct import salon_bg
from vol_ct import SARAH, badge, carte_sombre

BASE = 1560
KX, MX = 300, 760
MHEAD = (MX, BASE - 700)
KHEAD = (KX, BASE - 700)


def parle(t):
    return "o" if int(t * 7) % 2 else "grin"


class Mechant:
    def __init__(self, c):
        self.c = c
        self.T = {}

    # ───── plans ─────
    def decor(self, t, kpose=None, mechant=None, z=1.0, center=None, **kx):
        big = self.c["fond"]().copy()
        d = ImageDraw.Draw(big)
        if mechant is not None:
            bob, blink = idle(t, 0.6)
            character(d, MX, BASE + bob, **{**self.c["look"], "blink": blink, "brows": "colere", **mechant})
        if kpose:
            kevin(d, KX, BASE, kpose, t, **kx)
        return rue.contour_aretes(shot(big, z, center=center), seuil=90, w=3)

    def salon(self, t, kpose="telephone", sarah=None, z=1.0, center=None):
        big = salon_bg().copy()
        d = ImageDraw.Draw(big)
        kx = 540
        if sarah is not None:
            bob, blink = idle(t, 1.7)
            character(d, 780, BASE + bob, **{**SARAH, "blink": blink, **sarah})
            kx = 300
        kevin(d, kx, BASE, kpose, t)
        return rue.contour_aretes(shot(big, z, center=center), seuil=90, w=3)

    def gros_plan(self, t, dur, z0=2.0, z1=2.2, **m):
        return self.decor(t, mechant={"mouth": parle(t), **m}, z=push(t, dur, z0, z1), center=(MHEAD[0] - 40, MHEAD[1] + 40))

    # ───── compteur du gain (sous la barre de TikTok) ─────
    def valeur(self, t):
        t0 = self.T.get("gain")
        if t0 is None or t < t0:
            return 0
        return int(self.c["montant"] * ease((t - t0) / 0.7))

    def compteur(self, img, v):
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([30, 215, 430, 335], radius=18, fill=(20, 20, 26), outline=WHITE, width=3)
        d.text((54, 243), self.c["compteur"], font=FA(28), fill=(210, 210, 220), anchor="lm")
        d.text((54, 298), f"{v:,} €".replace(",", " "), font=FA(62), fill=GREEN if v else (240, 80, 80), anchor="lm")

    def avec_compteur(self, fn):
        def g(lt, dur):
            img = fn(lt, dur)
            self.compteur(img, self.valeur(self.T.get(fn.__name__, 0) + lt))
            return img
        g.__name__ = fn.__name__
        return g

    # ───── scènes ─────
    def scenes(self):
        c, T = self.c, self.T

        def s_hook(lt, dur):
            img = self.gros_plan(lt, dur, 2.1, 2.25, arm=0.5)
            badge(img, 540, 1190, c["badge"])
            bubble(img, 540, 570, c["hook_bulle"], 64, 1.0, tail_x=640)
            tag(img, 540, 400, c["hook_tag"], 56, RED, WHITE, rot=-3, k=(lt + 0.3) / 0.3)   # au-dessus de la bulle : jamais sur le visage
            return shake(img, lt)

        def s_faux(lt, dur):
            img = self.decor(lt, "choc", z=2.1, center=(KHEAD[0] + 60, KHEAD[1] - 60))
            shock_lines(img, 540, 900, 300, lt)
            tag(img, 540, 420, "FAUX", 110, RED, WHITE, rot=-5, k=lt / 0.2)
            big_number(img, (540, 650), counter(0, c["montant"], lt - 0.4, 0.6, "{:,} €").replace(",", " "), 200, GREEN,
                       c["faux_sous"], k=1.0)
            return shake(flash(img, lt), lt)

        def s_setup(lt, dur):
            img = self.decor(lt, c["setup_pose"], mechant=dict(mouth="grin" if lt > dur * 0.6 else "flat"),
                             z=push(lt, dur, 1.0, 1.1), center=(540, 1000))
            for i, (txt, col, t0) in enumerate(c["setup_tags"]):
                tag(img, 540, 420 + i * 160, txt, 56, col, INK, rot=(-4, 3, -3)[i % 3], k=(lt - t0) / 0.3)
            return flash(img, lt)

        def s_m1(lt, dur):
            img = self.gros_plan(lt, dur, 1.9, 2.1, arm=0.4)
            bubble(img, 540, 545, c["m1"], 64, (lt - 0.1) / 0.25, tail_x=640)
            return flash(img, lt)

        def s_m2(lt, dur):
            img = self.decor(lt, "triste", mechant=dict(mouth=parle(lt), arm=0.6), z=push(lt, dur, 1.15, 1.25),
                             center=(540, 980))
            bubble(img, 600, 545, c["m2"], 58, lt / 0.25, tail_x=740)
            return flash(img, lt)

        def s_m3(lt, dur):
            img = self.gros_plan(lt, dur, 2.2, 2.4, arm=0.8)
            bubble(img, 540, 545, c["m3"], 64, lt / 0.25, tail_x=640)
            return shake(flash(img, lt), lt)

        def s_sarah(lt, dur):
            img = self.salon(lt, "triste", sarah=dict(mouth=parle(lt)), z=push(lt, dur, 1.1, 1.2), center=(540, 1000))
            bubble(img, 720, 570, c["sarah"], 64, lt / 0.3, tail_x=780)
            if lt > 1.6:
                tag(img, 540, 400, "LA PLUPART ABANDONNENT ICI", 50, RED, WHITE, rot=-3, k=(lt - 1.6) / 0.3)
            return flash(img, lt)

        def s_abonne(lt, dur):
            img = self.salon(lt, "telephone", z=1.0, center=(540, 1000))
            phone_big(img, 540, 900, lt, "19:42", [("Où va ton argent", "Où va ton argent", c["notif"], (40, 160, 90))])
            tag(img, 540, 410, "HEUREUSEMENT…", 64, YEL, INK, rot=-3, k=lt / 0.25)
            return img

        def s_regle(lt, dur):
            img = dim(self.salon(lt, "neutre"), 0.9)
            carte_sombre(img, c["regle"][0], c["regle"][1], lt, y0=480, sous=c["regle"][2])
            return img

        def s_lettre(lt, dur):
            img = dim(self.salon(lt, "telephone"), 0.85)
            card(img, 540, 780, c["lettre"][0], c["lettre"][1], c["lettre"][2], lt, rot=2)
            return img

        def s_m4(lt, dur):
            img = self.gros_plan(lt, dur, 2.0, 2.2, mouth="grin" if int(lt * 5) % 2 else "o", arms_up=False, arm=0.2)
            bubble(img, 540, 570, c["m4"], 62, lt / 0.25, tail_x=640)
            tag(img, 540, 400, "IL SE MOQUE ENCORE", 50, RED, WHITE, rot=-3, k=(lt - 1.0) / 0.3)
            return shake(flash(img, lt), lt)

        def s_riposte(lt, dur):
            img = dim(self.salon(lt, "neutre"), 0.85)
            card(img, 540, 760, c["lettre"][0], c["lettre"][1], c["lettre"][2], lt + 3, rot=2,
                 stamp=c["riposte"], stamp_t=3.5)
            return img

        def s_calcul(lt, dur):
            img = dim(self.salon(lt, "neutre"), 0.9)
            tag(img, 540, 410, "FAIS LE CALCUL AVEC KÉVIN", 56, YEL, INK, rot=-3, k=lt / 0.25)
            carte_sombre(img, c["calcul"][0], c["calcul"][1], lt, y0=520)
            return img

        def s_partage(lt, dur):
            img = dim(self.salon(lt, "telephone"), 0.85)
            d = ImageDraw.Draw(img)
            cols = [(214, 120, 40), (230, 120, 160), (60, 120, 220), (90, 180, 100)]
            noms = ["KÉVIN", "SARAH", "YANIS", "LÉA"]
            for k in range(4):
                x0, y0 = 90 + (k % 2) * 460, 500 + (k // 2) * 520
                d.rounded_rectangle([x0, y0, x0 + 440, y0 + 500], radius=24, fill=(40, 44, 60))
                lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
                character(ImageDraw.Draw(lay), x0 + 220, y0 + 640, sc=0.55, shirt=cols[k], pants=(40, 40, 60),
                          hair=(40, 30, 25), long_hair=k % 2 == 1, mouth="o" if k else "grin",
                          arms_up=k > 0 and lt > 0.5 + k * 0.3)
                lay = lay.resize((W, H), Image.LANCZOS).crop((x0, y0, x0 + 440, y0 + 500))
                img.paste(lay, (x0, y0), lay)
                d.text((x0 + 24, y0 + 470), noms[k], font=FA(34), fill=WHITE, anchor="lm")
            tag(img, 540, 430, "ON EN A TOUS UN", 70, YEL, INK, rot=-3, k=(lt - T["tous"] + T["s_partage"]) / 0.25)
            return img

        def s_fin(lt, dur):
            tg = T["gain"] - T["s_fin"]
            tq = T["question"] - T["s_fin"]
            img = self.salon(lt, "victoire" if lt > tg else "neutre", z=1.0, center=(540, 1000))
            if lt > tg:
                phone_big(img, 540, 960, lt - tg, "10:12", [c["notif_fin"]])
            if lt > tq:
                tag(img, 540, 420, c["question"], 54, YEL, INK, rot=-3, k=(lt - tq) / 0.25)
                tag(img, 540, 560, "DIS-LE EN COMMENTAIRE", 46, WHITE, INK, rot=2, k=(lt - tq - 0.4) / 0.25)
            return flash(img, lt)

        def s_chute(lt, dur):
            img = dim(self.gros_plan(lt, dur, 1.9, 2.0, mouth="sad", arm=0.0), 0.6)
            big_number(img, (540, 470), c["chute"], 110, RED, k=lt / 0.25, strike=ease((lt - 0.6) / 0.3))
            big_number(img, (540, 760), f"{c['montant']:,} €".replace(",", " "), 170, GREEN, c["chute_sous"],
                       k=(lt - 0.9) / 0.25, rot=-3)
            tag(img, 520, 1450, c["mention"], 24, (40, 40, 50), WHITE, rot=0, k=(lt - 0.5) / 0.3)
            return img

        return [s_hook, s_faux, s_setup, s_m1, s_m2, s_m3, s_sarah, s_abonne, s_regle, s_lettre, s_m4, s_riposte,
                s_calcul, s_partage, s_fin, s_chute]

    # ───── montage ─────
    def fabriquer(self):
        c = self.c
        v = CartoonVideo(c["nom"], c["script"], "", "", corner="")
        v.hook_head_start = 0.0
        v.sub_y = 0.69          # zone visible : au-dessus de la description TikTok
        v.voice(c["voix"])
        fonctions = self.scenes()
        for (cle, phrase), fn in zip(c["reperes"], fonctions):
            self.T[fn.__name__] = v.at(phrase)
        self.T["tous"] = v.at("On en a tous un")
        self.T["gain"] = v.at(c["gain_phrase"], after=self.T["s_fin"])
        self.T["question"] = v.at("Et toi", after=self.T["s_fin"])
        for fn in fonctions:
            v.scenes.append((self.T[fn.__name__], self.avec_compteur(fn)))
        T = self.T
        for t, nom, g in [(0.0, "impact", 1.0), (T["s_faux"], "impact", 0.9), (T["s_faux"] + 0.4, "ticks", 0.6),
                          (T["s_m1"], "whoosh", 0.6), (T["s_m2"], "impact", 0.6), (T["s_m3"], "impact", 0.9),
                          (T["s_sarah"] + 1.6, "rate", 0.7), (T["s_abonne"], "notif", 0.9), (T["s_regle"], "pop", 0.8),
                          (T["s_lettre"], "notif", 0.7), (T["s_m4"], "rate", 0.8), (T["s_riposte"] + 0.5, "tampon", 1.0),
                          (T["s_calcul"] + 1.4, "impact", 0.9), (T["s_partage"], "notif", 0.8),
                          (T["gain"], "succes", 1.0), (T["s_chute"], "impact", 0.8)]:
            v.sfx(t, nom, g)
        for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
            print(f"   {t0:5.1f}s {fn.__name__}")
        v.render()
