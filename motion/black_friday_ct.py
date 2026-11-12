"""Tes droits : Black Friday, prix barré faux + 14 jours de rétractation. Format v2 en 61 s, ouverture corrigée."""
from PIL import Image, ImageDraw

from box_ct import CHEAD, CONSEILLER, plateau
from cartoon import (FA, GREEN, INK, RED, SS, WHITE, YEL, CartoonVideo, big_number, bubble, card, character, counter,
                     dim, ease, flash, idle, kevin, phone_big, push, shake, shock_lines, shot, tag)
from engine import H, W
from prime_ct import salon_bg
from vol_ct import SARAH, badge, carte_sombre
import rue

BASE = 1560
T = {}


def salon(t, kpose="telephone", sarah=None, z=1.0, center=None, kx=540):
    big = salon_bg().copy()
    d = ImageDraw.Draw(big)
    if sarah is not None:
        bob, blink = idle(t, 1.7)
        character(d, 780, BASE + bob, **{**SARAH, "blink": blink, **sarah})
        kx = 300
    kevin(d, kx, BASE, kpose, t)
    return rue.contour_aretes(shot(big, z, center=center), seuil=90, w=3)


def pl(t, sans_panneau=False, **kw):
    """sans_panneau : gros plan sans le panneau SERVICE CLIENT (sinon coupé par le bord / le compteur)."""
    if not sans_panneau:
        return rue.contour_aretes(plateau(t, **kw), seuil=90, w=3)
    import box_ct
    avec = box_ct.plateau_bg()
    box_ct._bg["p"] = box_ct.room("vide")
    try:
        return rue.contour_aretes(plateau(t, **kw), seuil=90, w=3)
    finally:
        box_ct._bg["p"] = avec


def talk(t):
    return "o" if int(t * 7) % 2 else "grin"


def rembourse(t):
    return 0 if "remb" not in T or t < T["remb"] else int(299 * ease((t - T["remb"]) / 0.6))


def compteur(img, v):
    d = ImageDraw.Draw(img)
    # sous la barre de TikTok (recherche + onglets), qui cache les 200 premiers pixels
    d.rounded_rectangle([30, 215, 400, 335], radius=18, fill=(20, 20, 26), outline=WHITE, width=3)
    d.text((54, 243), "REMBOURSÉ À KÉVIN", font=FA(28), fill=(210, 210, 220), anchor="lm")
    d.text((54, 298), f"{v} €", font=FA(62), fill=GREEN if v else (240, 80, 80), anchor="lm")


def avec_compteur(fn):
    def g(lt, dur):
        img = fn(lt, dur)
        compteur(img, rembourse(T.get(fn.__name__, 0) + lt))
        return img
    g.__name__ = fn.__name__
    return g


def produit(img, cx, cy, lt, ancien="499 €", nouveau="299 €", remise="−40 %", k=None, titre="BLACK FRIDAY"):
    """Fiche produit du site (console) avec prix barré."""
    k = ease(lt / 0.3) if k is None else k
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    w, h = 760, 520
    x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=30, fill=WHITE, outline=INK, width=6)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + 90], radius=30, fill=(20, 20, 26))
    d.text((cx, y0 + 45), titre, font=FA(54), fill=YEL, anchor="mm")
    d.rounded_rectangle([x0 + 50, y0 + 140, x0 + 300, y0 + 440], radius=20, fill=(235, 235, 242))
    d.rounded_rectangle([x0 + 110, y0 + 170, x0 + 170, y0 + 410], radius=26, fill=WHITE, outline=INK, width=4)
    d.rounded_rectangle([x0 + 175, y0 + 170, x0 + 235, y0 + 410], radius=26, fill=WHITE, outline=INK, width=4)
    d.text((x0 + 520, y0 + 170), "CONSOLE", font=FA(50), fill=INK, anchor="mm")
    d.text((x0 + 520, y0 + 260), ancien, font=FA(60), fill=(150, 150, 160), anchor="mm")
    lw = FA(60).getlength(ancien)
    if ancien:
        d.line([x0 + 520 - lw / 2 - 8, y0 + 275, x0 + 520 + lw / 2 + 8, y0 + 245], fill=RED, width=8)
    d.text((x0 + 520, y0 + 360), nouveau, font=FA(96), fill=RED, anchor="mm")
    tag(img, x0 + w - 40, y0 + 110, remise, 50, RED, WHITE, rot=8, k=1.0)


# ───────────── scènes ─────────────

def s_hook(lt, dur):
    """0:00 — visage du conseiller bien visible, phrase courte sur une ligne."""
    img = pl(lt, conseiller=dict(mouth=talk(lt), arm=0.3), z=push(lt, dur, 2.0, 2.15), center=(CHEAD[0], CHEAD[1] - 40))
    badge(img, 540, 1180, "LE SERVICE CLIENT")
    tag(img, 540, 480, "« UNE PROMO, ÇA SE REMBOURSE PAS »", 58, WHITE, INK, rot=-3, k=1.0)
    big_number(img, (540, 720), "−40 %", 170, RED, k=(lt + 0.3) / 0.3)
    return shake(img, lt)


def s_faux(lt, dur):
    """0:02 — le gain promis en grand, Kévin choqué, image claire."""
    img = salon(lt, "choc", z=2.1, center=(540, BASE - 760))
    shock_lines(img, 540, 900, 300, lt)
    tag(img, 540, 400, "FAUX", 110, RED, WHITE, rot=-5, k=lt / 0.2)
    big_number(img, (540, 620), counter(0, 299, lt - 0.4, 0.6, "{} €"), 210, GREEN, "QU'IL VA RÉCUPÉRER", k=1.0)
    return shake(flash(img, lt), lt)


def s_truc(lt, dur):
    img = salon(lt, "telephone", z=push(lt, dur, 1.5, 1.65), center=(540, BASE - 640))
    tag(img, 540, 450, "UN SEUL PETIT TRUC", 70, YEL, INK, rot=-4, k=lt / 0.25)
    tag(img, 540, 610, "FAIT DÉBUT NOVEMBRE", 52, WHITE, INK, rot=3, k=(lt - 0.6) / 0.25)
    return flash(img, lt)


def s_achat(lt, dur):
    img = salon(lt, "telephone", z=1.0, center=(540, 1000))
    tag(img, 540, 400, "L'AN DERNIER, AU BLACK FRIDAY", 56, WHITE, INK, rot=-3, k=lt / 0.25)
    produit(img, 540, 760, lt - 0.4)
    return flash(img, lt)


def s_appel(lt, dur):
    img = salon(lt, "telephone", z=push(lt, dur, 1.5, 1.7), center=(540, BASE - 620))
    tag(img, 540, 450, "3 JOURS PLUS TARD", 66, WHITE, INK, rot=-3, k=lt / 0.25)
    return flash(img, lt)


def s_c1(lt, dur):
    img = pl(lt, sans_panneau=True, conseiller=dict(mouth=talk(lt), arm=0.3), z=push(lt, dur, 1.9, 2.1), center=(CHEAD[0] - 60, CHEAD[1] + 60))
    bubble(img, 560, 540, ["C'EST UNE PROMO,", "NI REPRIS", "NI ÉCHANGÉ"], 62, (lt - 0.4) / 0.3, tail_x=680)
    return flash(img, lt)


def s_c2(lt, dur):
    img = pl(lt, sans_panneau=True, conseiller=dict(mouth=talk(lt)), z=push(lt, dur, 1.5, 1.6), center=(840, CHEAD[1] - 20))
    bubble(img, 540, 540, ["FALLAIT RÉFLÉCHIR", "AVANT"], 70, lt / 0.3, tail_x=470)
    return flash(img, lt)


def s_sarah(lt, dur):
    img = salon(lt, "triste", sarah=dict(mouth=talk(lt)), z=push(lt, dur, 1.1, 1.2), center=(540, 1000))
    bubble(img, 720, 520, ["GARDE LA", "CONSOLE"], 70, lt / 0.3, tail_x=780)
    return flash(img, lt)


def s_echo(lt, dur):
    img = dim(pl(lt, sans_panneau=True, conseiller=dict(mouth="grin"), z=1.5, center=(840, CHEAD[1] - 20)), 0.7)
    tag(img, 540, 760, "« NI REPRIS NI ÉCHANGÉ »", 76, RED, WHITE, rot=-4, k=lt / 0.25)
    return img


def s_abonne(lt, dur):
    img = salon(lt, "telephone", z=1.0, center=(540, 1000))
    phone_big(img, 540, 900, lt, "19:42", [("Où va ton argent", "Où va ton argent", "Black Friday : tes droits", (40, 160, 90))])
    tag(img, 540, 410, "HEUREUSEMENT…", 64, YEL, INK, rot=-3, k=lt / 0.25)
    tr = T["deux"] - T["s_abonne"]
    if lt > tr:
        tag(img, 540, 1210, "RETIENS BIEN LES 2 RÈGLES", 56, RED, WHITE, rot=-2, k=(lt - tr) / 0.25)
    return img


def s_r1(lt, dur):
    img = dim(salon(lt, "neutre"), 0.9)
    carte_sombre(img, "RÈGLE 1 · LE PRIX BARRÉ", [("= le plus bas des", 0.5, False), ("30 derniers jours", 1.0, True)],
                 lt, y0=560, sous="CODE DE LA CONSOMMATION · L112-1-1")
    return img


def s_capture(lt, dur):
    img = salon(lt, "telephone", z=1.0, center=(540, 1000))
    tag(img, 540, 400, "LE PETIT TRUC DE KÉVIN", 60, YEL, INK, rot=-3, k=lt / 0.25)
    tag(img, 540, 550, "UNE CAPTURE D'ÉCRAN", 56, WHITE, INK, rot=3, k=(lt - 0.5) / 0.25)
    produit(img, 540, 900, lt - 1.0, ancien="", nouveau="319 €", remise="3 NOV.", titre="CAPTURE · 3 NOVEMBRE")
    return flash(img, lt)


def s_calcul(lt, dur):
    img = dim(salon(lt, "neutre"), 0.9)
    tag(img, 540, 410, "FAIS LE CALCUL AVEC KÉVIN", 56, YEL, INK, rot=-3, k=lt / 0.25)
    carte_sombre(img, "LA VRAIE RÉDUCTION", [("319 € → 299 €", 0.6, False), ("= −6 %", 1.4, True),
                                             ("PAS −40 %", 2.0, False)], lt, y0=520)
    return img


def s_r2(lt, dur):
    img = dim(salon(lt, "neutre"), 0.9)
    carte_sombre(img, "RÈGLE 2 · ACHAT EN LIGNE", [("14 jours pour te rétracter", 0.6, True), ("même en promo", 1.6, False),
                                                   ("sans te justifier", 2.4, False)], lt, y0=520,
                 sous="CODE DE LA CONSOMMATION · L221-18")
    return img


def s_partage(lt, dur):
    img = dim(salon(lt, "telephone"), 0.85)
    d = ImageDraw.Draw(img)
    cols = [(214, 120, 40), (230, 120, 160), (60, 120, 220), (90, 180, 100)]
    noms = ["KÉVIN", "SARAH", "YANIS", "LÉA"]
    for k in range(4):
        x0, y0 = 90 + (k % 2) * 460, 500 + (k // 2) * 520
        d.rounded_rectangle([x0, y0, x0 + 440, y0 + 500], radius=24, fill=(40, 44, 60))
        lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        character(ImageDraw.Draw(lay), x0 + 220, y0 + 640, sc=0.55, shirt=cols[k], pants=(40, 40, 60), hair=(40, 30, 25),
                  long_hair=k % 2 == 1, mouth="o" if k else "grin", arms_up=k > 0 and lt > 0.5 + k * 0.3)
        lay = lay.resize((W, H), Image.LANCZOS).crop((x0, y0, x0 + 440, y0 + 500))
        img.paste(lay, (x0, y0), lay)
        d.text((x0 + 24, y0 + 470), noms[k], font=FA(34), fill=WHITE, anchor="lm")
    tag(img, 540, 480, "ON EN A TOUS UN", 70, YEL, INK, rot=-3, k=(lt - T["tous"] + T["s_partage"]) / 0.25)
    return img


def s_renvoi(lt, dur):
    img = salon(lt, "victoire" if lt > T["remb"] - T["s_renvoi"] else "neutre", z=1.0, center=(540, 1000))
    ts = T["signal"] - T["s_renvoi"]
    tr = T["remb"] - T["s_renvoi"]
    if lt > tr:
        phone_big(img, 540, 960, lt - tr, "10:12", [("Banque", "Remboursement", "SITE · +299,00 €", (60, 110, 230))])
    if lt > ts:
        tag(img, 540, 410, "SIGNALÉ SUR SIGNALCONSO", 56, WHITE, INK, rot=-3, k=(lt - ts) / 0.25)
    return flash(img, lt)


def s_chute(lt, dur):
    img = salon(lt, "victoire", z=push(lt, dur, 1.1, 1.2), center=(540, 1000))
    big_number(img, (540, 450), "PRIX BARRÉ", 130, RED, "FAUX", k=lt / 0.25, strike=ease((lt - 0.5) / 0.3))
    big_number(img, (540, 800), "299 €", 170, GREEN, "REMBOURSÉS, BIEN RÉELS", k=(lt - 0.9) / 0.25, rot=-3)
    tag(img, 520, 1450, "CAS TYPE · L112-1-1 ET L221-18 · CECI N'EST PAS UN CONSEIL", 24, (40, 40, 50),
        WHITE, rot=0, k=(lt - 0.5) / 0.3)
    return img


def main():
    v = CartoonVideo("droits_black_friday", "scripts/modele/10_black_friday.txt", "", "", corner="")
    v.hook_head_start = 0.0
    v.sub_y = 0.69   # zone visible : au-dessus de la description TikTok
    v.voice("output/_work_droits_bf/voice_raw.mp3")
    sc = [("Moins quarante pour cent", s_hook), ("Faux. Kévin", s_faux), ("Grâce à un seul", s_truc),
          ("L'an dernier, au Black", s_achat), ("Trois jours plus tard", s_appel), ("Le conseiller rigole", s_c1),
          ("Et en raccrochant", s_c2), ("Même Sarah", s_sarah)]
    for phrase, fn in sc:
        T[fn.__name__] = v.at(phrase)
    T["s_echo"] = v.at("Ni repris ni échangé", after=T["s_sarah"])
    sc += [("Ni repris ni échangé", s_echo)]
    sc2 = [("Sauf que heureusement", s_abonne), ("La première", s_r1), ("Et le petit truc", s_capture),
           ("Fais le calcul", s_calcul), ("La deuxième", s_r2), ("Et c'est là que Kévin", s_partage),
           ("Kévin renvoie", s_renvoi), ("Le prix barré était faux", s_chute)]
    for phrase, fn in sc2:
        T[fn.__name__] = v.at(phrase)
    T["deux"], T["tous"] = v.at("Retiens bien les deux"), v.at("On en a tous un")
    T["signal"], T["remb"] = v.at("et il signale"), v.at("Le site rembourse")
    for phrase, fn in sc + sc2:
        v.scene(phrase, avec_compteur(fn), after=T["s_sarah"] if fn is s_echo else 0.0)
    v.sfx(0.0, "impact", 1.0)
    v.sfx(T["s_faux"], "impact", 0.9)
    v.sfx(T["s_faux"] + 0.4, "ticks", 0.6)
    v.sfx(T["s_achat"] + 0.4, "notif", 0.8)
    v.sfx(T["s_appel"], "attente", 0.6)
    v.sfx(T["s_c1"], "whoosh", 0.5)
    v.sfx(T["s_echo"], "rate", 0.8)
    v.sfx(T["s_abonne"], "notif", 0.9)
    v.sfx(T["s_r1"], "pop", 0.8)
    v.sfx(T["s_capture"] + 1.0, "pop", 0.8)
    v.sfx(T["s_calcul"] + 1.4, "impact", 0.9)
    v.sfx(T["s_r2"], "pop", 0.8)
    v.sfx(T["s_partage"], "notif", 0.8)
    v.sfx(T["signal"], "tampon", 0.9)
    v.sfx(T["remb"], "succes", 1.0)
    for t0, fn in sorted(v.scenes, key=lambda x: x[0]):
        print(f"   {t0:5.1f}s {fn.__name__}")
    v.render()


if __name__ == "__main__":
    main()
