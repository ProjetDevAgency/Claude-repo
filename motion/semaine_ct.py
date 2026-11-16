"""Où va ton argent ? — les 8 vidéos 8/8 de la semaine du 18 au 22 nov. (méthode v3).

    python3 motion/semaine_ct.py carte      → 27_carte_piratee.dial
    python3 motion/semaine_ct.py colis      → 28_colis_perdu.dial
    python3 motion/semaine_ct.py salaire    → 29_salaire_retard.dial
    python3 motion/semaine_ct.py voiture    → 30_voiture_occasion.dial
    python3 motion/semaine_ct.py dentiste   → 31_dentiste.dial
    python3 motion/semaine_ct.py retard     → 32_retard_retenue.dial
    python3 motion/semaine_ct.py smic       → 33_smic_decembre.dial
    python3 motion/semaine_ct.py garantie   → 34_garantie_legale.dial

Les scènes sont fabriquées par de petites usines (hook, plan, gros plan, écho, carte, téléphone, fin) : chaque vidéo
n'est qu'une liste de (début de phrase, scène, bruitage). Mêmes règles d'image que recit.py : aucun texte sur un
visage (bandeaux à y 420/560, bulles au-dessus des têtes), compteur en haut à gauche.
"""
import sys

import facades
from cartoon import FA, bubble, card, flash, phone_big, room, shake
from demission_ct import entrepot_bg
from heures_sup_ct import boutique_bg
from occasion_ct import garage_bg
from prime_ct import salon_bg
from recit import (BASE, GREEN, INK, KX, MX, RED, SS, WHITE, YEL, W, H, Image, ImageDraw, Recit, barres, big_number,
                   dim, gros_plan_kevin, gros_plan_mechant, mention, plan, push, tag)
from trop_percu_ct import headset
from vol_ct import badge, carte_sombre

BLEU, GRIS, VIOLET = (60, 110, 230), (120, 120, 135), (130, 80, 200)
_bg = {}


# ───────────── décors ─────────────

def _cache(cle, fabrique):
    if cle not in _bg:
        _bg[cle] = fabrique()
    return _bg[cle]


def _enseigne(d, txt, col=(30, 30, 36), fg=YEL, x0=240, x1=840):
    s = SS
    d.rounded_rectangle([x0 * s, 90 * s, x1 * s, 190 * s], radius=20 * s, fill=col)
    d.text(((x0 + x1) // 2 * s, 140 * s), txt, font=FA(int(50 * s)), fill=fg, anchor="mm")


def banque_bg():
    def f():
        im = room("vide").copy()
        _enseigne(ImageDraw.Draw(im), "BANQUE · AGENCE", (30, 60, 130), WHITE)
        return im
    return _cache("banque", f)


def guichet_fg(d, t):
    s = SS
    d.rectangle([0, 1260 * s, W * s, 1530 * s], fill=(70, 100, 160))
    d.rectangle([0, 1260 * s, W * s, 1290 * s], fill=(110, 140, 200))


def callcenter_bg():
    def f():
        im = room("bureau").copy()
        _enseigne(ImageDraw.Draw(im), "SERVICE CLIENT", (40, 40, 50), WHITE)
        return im
    return _cache("call", f)


def casque(d, t):
    headset(d, MX, BASE)


def chantier_bg(voiture=False):
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (150, 200, 240))
        d = ImageDraw.Draw(im)
        d.rectangle([120 * s, 300 * s, 960 * s, 1400 * s], fill=(175, 175, 180))          # l'immeuble en béton
        for y in range(380, 1400, 200):
            for x in range(170, 940, 190):
                d.rectangle([x * s, y * s, (x + 120) * s, (y + 120) * s], fill=(90, 95, 110))
        for x in range(100, 1000, 170):                                                      # l'échafaudage
            d.rectangle([x * s, 260 * s, (x + 12) * s, 1400 * s], fill=(230, 130, 30))
        for y in range(300, 1400, 200):
            d.rectangle([90 * s, y * s, 990 * s, (y + 10) * s], fill=(230, 130, 30))
        d.rectangle([0, 1400 * s, W * s, H * s], fill=(150, 120, 90))
        d.rectangle([0, 1400 * s, W * s, 1416 * s], fill=(120, 95, 70))
        _enseigne(d, "CHANTIER · ACCÈS INTERDIT", (240, 200, 0), INK, 200, 880)
        if voiture:
            facades.voiture(d, 760)
        return im
    return _cache(f"chantier{voiture}", f)


def cabinet_bg():
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (225, 238, 242))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 1450 * s, W * s, H * s], fill=(190, 200, 205))
        d.rectangle([0, 1440 * s, W * s, 1455 * s], fill=(160, 170, 175))
        # le fauteuil dentaire, au fond au centre
        d.rounded_rectangle([430 * s, 1180 * s, 700 * s, 1300 * s], radius=40 * s, fill=(40, 160, 170))
        d.rounded_rectangle([380 * s, 1000 * s, 470 * s, 1290 * s], radius=40 * s, fill=(40, 160, 170))
        d.rectangle([540 * s, 1300 * s, 580 * s, 1450 * s], fill=(150, 150, 160))
        d.line([(600 * s, 1450 * s), (600 * s, 900 * s), (470 * s, 860 * s)], fill=(150, 150, 160), width=16 * s)
        d.ellipse([420 * s, 820 * s, 520 * s, 900 * s], fill=(250, 250, 220))
        _enseigne(d, "CABINET DENTAIRE", (40, 160, 170), WHITE)
        return im
    return _cache("cabinet", f)


def route_bg(arret=False):
    """La rocade / la rue du bus : ciel, immeubles au loin, glissière, route."""
    def f():
        s = SS
        im = Image.new("RGB", (W * s, H * s), (150, 200, 240))
        d = ImageDraw.Draw(im)
        for x, h in [(0, 520), (170, 380), (330, 600), (520, 450), (700, 560), (880, 400)]:
            d.rectangle([x * s, (1250 - h) * s, (x + 160) * s, 1250 * s], fill=(120, 130, 160))
            for wy in range(1250 - h + 40, 1230, 80):
                d.rectangle([(x + 30) * s, wy * s, (x + 60) * s, (wy + 30) * s], fill=(200, 210, 230))
        d.rectangle([0, 1250 * s, W * s, 1420 * s], fill=(110, 170, 90))
        d.rectangle([0, 1420 * s, W * s, H * s], fill=(70, 72, 80))
        for x in range(0, W, 180):
            d.rectangle([x * s, 1640 * s, (x + 90) * s, 1660 * s], fill=(250, 250, 250))
        if arret:
            d.rectangle([880 * s, 900 * s, 900 * s, 1420 * s], fill=(80, 80, 90))
            d.rounded_rectangle([820 * s, 880 * s, 960 * s, 1000 * s], radius=16 * s, fill=(30, 90, 200))
            d.text((890 * s, 940 * s), "BUS", font=FA(int(50 * s)), fill=WHITE, anchor="mm")
            d.rectangle([820 * s, 1020 * s, 960 * s, 1080 * s], fill=(220, 40, 40))
            d.text((890 * s, 1050 * s), "GRÈVE", font=FA(int(36 * s)), fill=WHITE, anchor="mm")
        else:
            d.rectangle([0, 1380 * s, W * s, 1400 * s], fill=(190, 190, 200))
            for x in range(40, W, 200):
                d.rectangle([x * s, 1380 * s, (x + 14) * s, 1430 * s], fill=(150, 150, 160))
        return im
    return _cache(f"route{arret}", f)


def atelier_bg():
    def f():
        s = SS
        im = entrepot_bg().copy()
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([470 * s, 1130 * s, 610 * s, 1470 * s], radius=14 * s, fill=(40, 40, 46))   # machine à café
        d.rectangle([495 * s, 1160 * s, 585 * s, 1230 * s], fill=(90, 160, 220))
        d.rectangle([505 * s, 1330 * s, 575 * s, 1400 * s], fill=(20, 20, 24))
        d.rectangle([525 * s, 1360 * s, 555 * s, 1400 * s], fill=(250, 250, 250))
        return im
    return _cache("atelier", f)


def machine(d, x, y, sc=1.0, fumee=False, t=0.0):
    """Machine à laver (coordonnées finales)."""
    s = SS * sc

    def P(a, b):
        return x * SS + a * s, y * SS + b * s
    d.rounded_rectangle([*P(-110, -260), *P(110, 0)], radius=int(18 * s), fill=(245, 245, 248), outline=INK, width=int(4 * s))
    d.rectangle([*P(-110, -260), *P(110, -210)], fill=(215, 215, 222))
    d.ellipse([*P(-70, -180), *P(70, -40)], fill=(150, 170, 200), outline=(120, 120, 130), width=int(10 * s))
    if fumee:
        for k in range(3):
            r = 26 + 10 * ((t * 1.5 + k * 0.33) % 1) * 3
            yy = -300 - 90 * ((t * 1.5 + k * 0.33) % 1) * 3
            d.ellipse([*P(-r + 20 * k - 20, yy - r), *P(r + 20 * k - 20, yy + r)], fill=(120, 120, 125))


def magasin_bg():
    def f():
        s = SS
        im = room("vide").copy()
        d = ImageDraw.Draw(im)
        for x in range(130, 1000, 250):
            machine(d, x, 1500, 0.8)
        _enseigne(d, "ÉLECTROMÉNAGER", (200, 40, 40), WHITE)
        return im
    return _cache("magasin", f)


def salon_machine(d, t):
    machine(d, 800, 1560)


def salon_fumee(d, t):
    machine(d, 800, 1560, fumee=True, t=t)


def radiateur(d, t):
    s = SS
    d.rounded_rectangle([600 * s, 1150 * s, 1000 * s, 1400 * s], radius=14 * s, fill=(235, 235, 240), outline=INK, width=4 * s)
    for k, col in enumerate([(250, 210, 220), (200, 230, 250), (250, 240, 190), (210, 240, 210)]):
        x = 630 + k * 95
        d.rounded_rectangle([x * s, 1120 * s, (x + 80) * s, 1240 * s], radius=20 * s, fill=col)


def gateau(d, t):
    s = SS
    d.rectangle([0, 1300 * s, W * s, 1560 * s], fill=(150, 104, 74))
    d.rounded_rectangle([420 * s, 1180 * s, 660 * s, 1300 * s], radius=16 * s, fill=(250, 230, 240), outline=INK, width=3 * s)
    d.rectangle([420 * s, 1230 * s, 660 * s, 1245 * s], fill=(230, 80, 120))
    for x in (480, 540, 600):
        d.rectangle([(x - 5) * s, 1140 * s, (x + 5) * s, 1180 * s], fill=(80, 160, 230))
        d.ellipse([(x - 9) * s, (1120 + 6 * ((t * 9 + x) % 2)) * s, (x + 9) * s, 1145 * s], fill=(255, 200, 40))


def pancarte(d, t):
    s = SS
    d.rectangle([520 * s, 1300 * s, 560 * s, 1500 * s], fill=(120, 80, 50))
    d.rectangle([300 * s, 1120 * s, 780 * s, 1320 * s], fill=(250, 250, 245), outline=INK, width=5 * s)
    d.text((540 * s, 1180 * s), "VENDUE ICI,", font=FA(int(64 * s)), fill=RED, anchor="mm")
    d.text((540 * s, 1260 * s), "EN L'ÉTAT", font=FA(int(64 * s)), fill=RED, anchor="mm")


# ───────────── usines à scènes ─────────────

def _n(f, nom):
    f.__name__ = nom
    return f


def _tags(img, lt, tags):
    for k, (txt, col, t0) in enumerate(tags):
        fg = INK if col in (YEL, WHITE, GREEN) else WHITE
        tag(img, 540, 420 + 140 * k, txt, 54 if len(txt) < 22 else 46, col, fg, rot=(-3, 2, -2)[k % 3],
            k=(lt - t0) / 0.3)


def echo_fit(img, txt):
    d = ImageDraw.Draw(img)
    t = f"« {txt} »"
    size = 92
    while FA(size).getlength(t) > 960 and size > 50:
        size -= 4
    big_number(img, (540, 470), t, size, WHITE, k=1.0)


class Video:
    """Les décors, les personnages et les usines à scènes d'une vidéo."""

    def __init__(self, fond, look, kextra=None):
        self.fond, self.look, self.kx = fond, look, kextra or {}

    def hook(self, nom, badge_txt, lignes, devant=None, **pose):
        def f(lt, dur):
            img = gros_plan_mechant(self.fond, self.look, lt, dur, arm=0.5, devant=devant, **pose)
            badge(img, 540, 1190, badge_txt)
            bubble(img, 540, 570, lignes, 58, (lt + 0.3) / 0.3, tail_x=660)
            return shake(img, lt)
        return _n(f, nom)

    def gp(self, nom, lignes, z=(1.95, 2.15), secoue=False, devant=None, fond=None, **pose):
        def f(lt, dur):
            img = gros_plan_mechant(fond or self.fond, self.look, lt, dur, z[0], z[1], devant=devant,
                                    **{"arm": 0.4, **pose})
            bubble(img, 540, 560, lignes, 56, lt / 0.25, tail_x=660)
            img = flash(img, lt)
            return shake(img, lt) if secoue else img
        return _n(f, nom)

    def scene(self, nom, kpose="neutre", tags=(), fond=None, mechant=None, autres=(), devant=None, z=(1.0, 1.06),
              kx=KX, mx=MX, sans_mechant=False, fx=True, **extra):
        def f(lt, dur):
            m = None if sans_mechant else (mechant or dict(mouth="flat"))
            img = plan(fond or self.fond, lt, kpose, kx=kx, mechant=m, look=self.look, mx=mx, autres=autres,
                       devant=devant, z=push(lt, dur, *z), center=(540, 1000), **{**self.kx, **extra})
            _tags(img, lt, tags)
            return flash(img, lt) if fx else img
        return _n(f, nom)

    def geste(self, nom, txt="IL EN RAJOUTE", fond=None, devant=None, kpose="triste", **pose):
        return self.scene(nom, kpose, [(txt, RED, 0.4)], fond=fond, devant=devant, z=(1.1, 1.2),
                          mechant={"mouth": "grin", "arm": 0.8, **pose}, mx=820)

    def silence(self, nom, kpose="triste", fond=None, devant=None, autres=(), mechant=None):
        return self.scene(nom, kpose, fond=fond, devant=devant, autres=autres, z=(1.0, 1.04), fx=False,
                          mechant=mechant or dict(mouth="grin"))

    def echo(self, nom, txt, fond=None, devant=None):
        def f(lt, dur):
            img = dim(gros_plan_kevin(fond or self.fond, lt, dur, devant=devant, **self.kx), 0.75)
            echo_fit(img, txt)
            return img
        return _n(f, nom)

    def carte(self, nom, titre, rows, sous=None, fond=None, kpose="telephone"):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.9)
            carte_sombre(img, titre, rows, lt, y0=470, sous=sous)
            return img
        return _n(f, nom)

    def gros_mots(self, nom, mots, fond=None, kpose="telephone"):
        """Des mots qui tombent un par un sur un plan assombri : mots = [(texte, couleur, t0)]."""
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.85)
            for i, (txt, col, t0) in enumerate(mots):
                fg = INK if col in (YEL, WHITE, GREEN) else WHITE
                tag(img, 540, 520 + i * 160, txt, 62 if len(txt) < 20 else 50, col, fg, rot=(-3, 2, -2)[i % 3],
                    k=(lt - t0) / 0.25)
            return img
        return _n(f, nom)

    def tel(self, nom, heure, lignes, kpose="telephone", fond=None, tags=(), devant=None):
        def f(lt, dur):
            img = plan(fond or self.fond, lt, kpose, kx=270, devant=devant, **self.kx)
            phone_big(img, 700, 960, lt, heure, lignes)
            _tags(img, lt, tags)
            return flash(img, lt)
        return _n(f, nom)

    def fiche(self, nom, titre, sous, rows, kpose="telephone", fond=None, stamp=None, stamp_t=99.0):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, kpose, kx=540, **self.kx), 0.85)
            card(img, 540, 760, titre, sous, rows, lt, rot=2, stamp=stamp, stamp_t=stamp_t)
            return img
        return _n(f, nom)

    def calcul(self, nom, titre, items, sous=None, fond=None):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, "neutre", kx=540, **self.kx), 0.9)
            barres(img, titre, items, lt, sous=sous)
            return img
        return _n(f, nom)

    def doute(self, nom, txt, fond=None, devant=None):
        def f(lt, dur):
            img = plan(fond or self.fond, lt, "triste", kx=540, devant=devant, z=push(lt, dur, 1.1, 1.18),
                       center=(540, 1000), **self.kx)
            tag(img, 540, 420, txt, 50, WHITE, INK, rot=-3, k=(lt - 0.4) / 0.3)
            return img
        return _n(f, nom)

    def fin(self, nom, montant, sous, ref, fond=None):
        def f(lt, dur):
            img = dim(plan(fond or self.fond, lt, z=1.0), 0.6)
            big_number(img, (540, 470), montant, 150, GREEN, sous, k=lt / 0.25, rot=-3)
            mention(img, ref, lt)
            return img
        return _n(f, nom)


def recit(nom, dial, label, montant, phrase):
    return Recit(nom, f"scripts/modele/{dial}.txt", f"output/_work_{nom}/voice_duo.wav",
                 compteur=dict(label=label, depart=0, montant=montant, phrase=phrase))


# ═════════════ 27. La carte piratée de mamie ═════════════

CONSEILLER = dict(shirt=(40, 70, 130), pants=(36, 36, 44), hair=(50, 40, 30), tie=True, glasses=True)
MAMIE = dict(shirt=(170, 120, 170), pants=(60, 60, 80), hair=(215, 215, 222), long_hair=True, glasses=True)
V = Video(banque_bg, CONSEILLER)
CARTE = (recit("s_carte", "27_carte_piratee", "REMBOURSÉ À MAMIE", 3200, "Deux jours plus tard"), [
    ("Trois mille deux cents euros volés", V.hook("h", "LE CONSEILLER DE SA BANQUE", ["TA GRAND-MÈRE S'EST FAIT", "VOLER 3 200 € ?", "C'EST POUR ELLE"], devant=guichet_fg), ("impact", 1.0)),
    ("C'est ce que le conseiller", V.scene("couture", "carte", [("LA CARTE DE MAMIE", YEL, 0.3), ("MAISON DE RETRAITE : J-5", RED, 3.2)], mechant=dict(mouth="grin", arm=0.3), devant=guichet_fg), ("whoosh", 0.6)),
    ("Mamie, elle a", V.scene("montee", "neutre", [("MAMIE · 84 ANS", GREEN, 0.2), ("ELLE GÈRE TOUT SEULE", YEL, 1.6)], fond=salon_bg, sans_mechant=True, autres=[(780, MAMIE, dict(mouth="smile"), 0.4)]), ("pop", 0.8)),
    ("Un faux SMS", V.tel("sms", "14:07", [("SMS", "Livraison", "Colis bloqué, payez", GRIS), ("Banque", "Paiement carte", "− 3 200,00 €", RED)], "choc", fond=salon_bg), ("notif", 0.7)),
    ("Elle a donné ses codes", V.gp("coup1", ["ELLE A DONNÉ SES", "CODES. NÉGLIGENCE", "GRAVE"], devant=guichet_fg), ("impact", 0.8)),
    ("Et en tapant", V.geste("geste", devant=guichet_fg), ("whoosh", 0.5)),
    ("À son âge", V.gp("coup2", ["À SON ÂGE, ON LUI", "RETIRE SA CARTE"], (2.2, 2.4), True, devant=guichet_fg, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence", "carte", devant=guichet_fg), None),
    ("On lui retire sa carte", V.echo("echo", "ON LUI RETIRE SA CARTE", devant=guichet_fg), ("rate", 0.6)),
    ("Sauf que la loi", V.carte("regle", "PAIEMENT PAS AUTORISÉ", [("La banque rembourse tout de suite", 0.4, True), ("au plus tard le jour ouvrable", 2.4, False), ("suivant", 3.2, False)], "CODE MONÉTAIRE ET FINANCIER · L133-18", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, et la négligence", V.carte("preuve", "LA NÉGLIGENCE GRAVE", [("C'est à la banque de la prouver", 0.5, True), ("Un faux SMS, ça suffit pas", 2.8, False), ("Cour de cassation", 4.2, False)], "CODE MONÉTAIRE ET FINANCIER · L133-19", fond=salon_bg), ("impact", 0.6)),
    ("Le lendemain, je reviens", V.scene("rec", "carte", [("LA LETTRE DE CONTESTATION", YEL, 0.3), ("REC · TÉLÉPHONE EN POCHE", RED, 2.2)], mechant=dict(mouth="grin", arm=0.4), devant=guichet_fg), ("ticks", 0.6)),
    ("J'envoie l'audio", V.tel("audio", "18:40", [("Mail", "Directeur d'agence", "audio.m4a + lettre", BLEU)], fond=salon_bg), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "ENREGISTRÉ SANS LUI DIRE", fond=salon_bg), None),
    ("Deux jours plus tard", V.tel("twist", "09:12", [("Banque", "Remboursement", "+ 3 200,00 €", GREEN), ("Appel", "Banque de mamie", "Une nouvelle carte ?", BLEU)], "victoire", fond=salon_bg), ("succes", 0.8)),
    ("Trois mille deux cents euros, et", V.fin("fin", "3 200 €", "ET ELLE GARDE SA CARTE", "CAS TYPE · CODE MONÉTAIRE ET FINANCIER L133-18 ET L133-19", fond=salon_bg), ("impact", 0.9)),
])


# ═════════════ 28. Le colis jamais reçu ═════════════

SERVICE = dict(shirt=(60, 140, 200), pants=(36, 36, 44), hair=(30, 25, 20))
V = Video(callcenter_bg, SERVICE)
APPART = lambda: room("appart")  # noqa: E731
COLIS = (recit("s_colis", "28_colis_perdu", "REMBOURSÉ PAR LE SITE", 1200, "Le vendredi, le site"), [
    ("Mille deux cents euros d'ordinateur", V.hook("h", "LE SERVICE CLIENT", ["VOTRE ORDI À 1 200 €", "JAMAIS ARRIVÉ ? VOYEZ", "AVEC LE TRANSPORTEUR"], devant=casque), ("impact", 1.0)),
    ("C'est ce que le service client", V.scene("couture", "telephone", [("MISSION DE GRAPHISTE : LUNDI", YEL, 0.3), ("PLUS D'ORDI", RED, 3.0)], fond=APPART, sans_mechant=True), ("whoosh", 0.6)),
    ("Et pourtant j'étais fier", V.scene("montee", "victoire", [("3 MOIS DE PETITS BOULOTS", GREEN, 0.2), ("LE CONTRAT EST SIGNÉ", YEL, 2.0)], fond=APPART, sans_mechant=True), ("pop", 0.8)),
    ("Le suivi dit livré", V.tel("suivi", "14:02", [("Suivi", "Colis 4471", "LIVRÉ · 14:02", GREEN)], "choc", fond=APPART, tags=[("PERSONNE A SONNÉ", RED, 2.5)]), ("notif", 0.7)),
    ("Une fois chez le transporteur", V.gp("coup1", ["UNE FOIS CHEZ LE", "TRANSPORTEUR, C'EST", "PLUS NOTRE AFFAIRE"], devant=casque), ("impact", 0.8)),
    ("Et en me mettant en attente", V.scene("geste", None, [("MISE EN ATTENTE", RED, 0.4)], mechant=dict(mouth="grin", arm=0.8), mx=540, z=(1.1, 1.2), devant=lambda d, t: headset(d, 540, BASE)), ("whoosh", 0.5)),
    ("Vous les jeunes", V.gp("coup2", ["VOUS LES JEUNES,", "VOUS COMMANDEZ TOUT,", "APRÈS VOUS PLEUREZ"], (2.2, 2.4), True, devant=casque, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.scene("silence", "triste", fond=APPART, sans_mechant=True, z=(1.0, 1.04), fx=False), None),
    ("Après vous pleurez", V.echo("echo", "APRÈS VOUS PLEUREZ", fond=APPART), ("rate", 0.6)),
    ("Sauf que quand t'achètes", V.carte("regle", "ACHAT À DISTANCE", [("Tant que t'as pas le colis en main", 0.4, False), ("le risque est sur le VENDEUR", 2.2, True), ("pas sur toi, pas sur le livreur", 4.0, False)], "CODE DE LA CONSOMMATION · L216-4", fond=APPART), ("pop", 0.8)),
    ("Mais alors s'il est marqué", V.gros_mots("preuve", [("UNE SIGNATURE ?", WHITE, 1.4), ("UNE PHOTO ?", WHITE, 2.4), ("SINON, IL REMBOURSE", GREEN, 3.4)], fond=APPART), ("impact", 0.6)),
    ("Le soir même, je publie", V.tel("avis", "21:30", [("Avis", "1 sur 5 · le site", "Julien, du SAV", (240, 160, 0))], fond=APPART), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "SON PRÉNOM, EN PUBLIC", fond=APPART), None),
    ("Le vendredi, le site", V.tel("twist", "10:05", [("Banque", "Remboursement", "+ 1 200,00 €", GREEN), ("Mail", "Vendeur au livreur", "Merci de payer", BLEU)], "victoire", fond=APPART), ("succes", 0.8)),
    ("Mille deux cents euros, et", V.fin("fin", "1 200 €", "C'EST LE VENDEUR QUI VOIT AVEC LE LIVREUR", "CAS TYPE · CODE DE LA CONSOMMATION L216-4 ET L221-15", fond=APPART), ("impact", 0.9)),
])


# ═════════════ 29. Le salaire en retard ═════════════

PATRON = dict(shirt=(245, 245, 248), pants=(50, 50, 60), hair=(80, 70, 60), glasses=True)
GILET = dict(shirt=(230, 120, 40))
V = Video(chantier_bg, PATRON, GILET)
SALAIRE = (recit("s_salaire", "29_salaire_retard", "RENDU PAR LE PATRON", 90, "Le mois suivant"), [
    ("Quatre-vingt-dix euros de frais", V.hook("h", "MON PATRON", ["QUE JE TE PAIE", "TES 90 € DE FRAIS ?", "LE SALAIRE TOMBE", "QUAND IL TOMBE"]), ("impact", 1.0)),
    ("C'est ce que mon patron", V.scene("couture", "choc", [("PAIE ATTENDUE LE 1er · ON EST LE 12", YEL, 0.3), ("LOYER REJETÉ", RED, 3.4)], mechant=dict(mouth="grin")), ("whoosh", 0.6)),
    ("Et pourtant j'aimais", V.scene("montee", "victoire", [("2 ANS DE CHANTIERS", GREEN, 0.2), ("MÊME SOUS LA NEIGE", YEL, 2.4)]), ("pop", 0.8)),
    ("Je lui montre juste", V.fiche("rejet", "AVIS DE REJET", "TA BANQUE", [("Prélèvement du loyer", "rejeté", 0.3, False), ("Frais de rejet", "90 €", 1.0, True)]), None),
    ("T'as qu'à avoir", V.gp("coup1", ["T'AS QU'À AVOIR", "DE L'ÉPARGNE, COMME", "TOUT LE MONDE"]), ("impact", 0.8)),
    ("Et en montant dans sa voiture", V.geste("geste", "SA VOITURE NEUVE", fond=lambda: chantier_bg(True)), ("whoosh", 0.5)),
    ("À vingt-cinq ans", V.gp("coup2", ["À 25 ANS, T'AS MÊME", "PAS UN MOIS D'AVANCE"], (2.2, 2.4), True, fond=lambda: chantier_bg(True), arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence", "carte"), None),
    ("Pas un mois d'avance", V.echo("echo", "PAS UN MOIS D'AVANCE"), ("rate", 0.6)),
    ("Sauf qu'un salaire en retard", V.carte("regle", "SALAIRE EN RETARD", [("Des intérêts au taux légal", 0.4, True), ("dès la mise en demeure écrite", 2.0, False), ("automatiques", 3.6, False)], "CODE CIVIL · ARTICLE 1231-6", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, et les frais", V.carte("frais", "ET LES FRAIS DE BANQUE ?", [("1. Un préjudice à part", 1.6, False), ("2. La mauvaise foi du patron", 2.8, True)], "IL FAUT PROUVER LES DEUX", fond=salon_bg), ("impact", 0.6)),
    ("Et sa mauvaise foi, je l'avais", V.tel("vocal", "19:48", [("WhatsApp", "Groupe Ouvriers", "Vocal du patron · 0:07", GREEN), ("Texte", "Je les paie le 12,", "ça me fait de la tréso", GRIS)], "choc", fond=salon_bg), ("notif", 0.7)),
    ("Il l'a effacé", V.tel("efface", "19:58", [("WhatsApp", "Groupe Ouvriers", "Message supprimé", GRIS), ("Fichiers", "Enregistré", "vocal_patron.opus", BLEU)], fond=salon_bg), ("ticks", 0.6)),
    ("Honnêtement", V.doute("doute", "UN MESSAGE PAS POUR MOI", fond=salon_bg), None),
    ("Le mois suivant", V.tel("twist", "08:01", [("Banque", "Salaire · le 1er", "+ 1 712,40 €", GREEN), ("Banque", "Frais + intérêts", "+ 96,80 €", GREEN)], "victoire", fond=salon_bg), ("succes", 0.8)),
    ("Quatre-vingt-dix euros, et", V.fin("fin", "90 €", "ET CETTE FOIS, ÇA TOMBE À L'HEURE", "CAS TYPE · CODE CIVIL 1231-6 · CASS. SOC. 6 MAI 2025"), ("impact", 0.9)),
])


# ═════════════ 30. La voiture d'occasion ═════════════

GARAGISTE = dict(shirt=(60, 90, 140), pants=(60, 90, 140), hair=(40, 30, 25))
V = Video(garage_bg, GARAGISTE)
VOITURE = (recit("s_voiture", "30_voiture_occasion", "PAYÉ PAR LE GARAGE", 1800, "Deux heures plus tard"), [
    ("Mille huit cents euros l'embrayage", V.hook("h", "LE GARAGISTE", ["QUE JE PAIE TON", "EMBRAYAGE À 1 800 € ?", "VENDUE EN L'ÉTAT,", "T'AS SIGNÉ"]), ("impact", 1.0)),
    ("C'est ce que le garagiste", V.scene("couture", "choc", [("OCCASION · 6 500 €", YEL, 0.3), ("3 SEMAINES APRÈS", RED, 1.6), ("CDI LUNDI · À 40 KM", WHITE, 5.0)], mechant=dict(mouth="grin")), ("whoosh", 0.6)),
    ("Et pourtant j'avais tout fait", V.scene("montee", "victoire", [("LE CRÉDIT, L'ASSURANCE", GREEN, 0.3), ("DES TAPIS NEUFS", YEL, 2.0)], mechant=dict(mouth="smile")), ("pop", 0.8)),
    ("Sur la rocade", V.scene("panne", "choc", [("L'EMBRAYAGE LÂCHE", RED, 0.2), ("REMORQUAGE · DEVIS", YEL, 1.6)], fond=route_bg, sans_mechant=True), ("impact", 0.6)),
    ("Une occasion, c'est un risque", V.gp("coup1", ["UNE OCCASION,", "C'EST UN RISQUE.", "FALLAIT UNE NEUVE"]), ("impact", 0.8)),
    ("Et en rangeant ses clés", V.geste("geste"), ("whoosh", 0.5)),
    ("À ton âge", V.gp("coup2", ["À TON ÂGE, ON ACHÈTE", "UNE TROTTINETTE"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence"), None),
    ("Une trottinette", V.echo("echo", "UNE TROTTINETTE"), ("rate", 0.6)),
    ("Sauf qu'un garage", V.carte("regle", "UN GARAGE = UN PRO", [("Il te doit la garantie légale", 0.4, True), ("de conformité", 1.6, False), ("même sur une occasion", 3.0, False)], "CODE DE LA CONSOMMATION · L217-3", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, vendue en l'état", V.carte("etat", "« VENDUE EN L'ÉTAT » ?", [("Face à un particulier : rien", 0.6, True), ("1re année : la panne est", 2.8, False), ("présumée là dès la vente", 3.6, False)], "CODE DE LA CONSOMMATION · L217-7", fond=salon_bg), ("impact", 0.6)),
    ("Le lendemain, je fais déposer", V.scene("pancarte", None, [("DEVANT SA VITRINE", YEL, 0.3)], sans_mechant=True, devant=pancarte, z=(1.0, 1.08)), ("pop", 0.6)),
    ("Honnêtement", V.doute("doute", "PAS LAISSÉ LE TEMPS DE RÉPONDRE", fond=salon_bg), None),
    ("Deux heures plus tard", V.tel("twist", "11:20", [("Appel", "Le garagiste", "Embrayage : 0 €", GREEN), ("SMS", "Le garagiste", "Et la pancarte ?", BLEU)], "victoire", fond=salon_bg), ("succes", 0.8)),
    ("Mille huit cents euros, et", V.fin("fin", "1 800 €", "ET CETTE FOIS, C'EST LUI QUI SIGNE", "CAS TYPE · CODE DE LA CONSOMMATION L217-3 ET L217-7"), ("impact", 0.9)),
])


# ═════════════ 31. La dentiste et le 100 % Santé ═════════════

DENTISTE = dict(shirt=(245, 245, 250), pants=(245, 245, 250), hair=(60, 40, 30), long_hair=True, glasses=True)
MAMAN = dict(shirt=(150, 92, 165), pants=(50, 50, 70), hair=(110, 70, 40), long_hair=True)
V = Video(cabinet_bg, DENTISTE)
MAMAN_C = [(560, MAMAN, dict(mouth="flat", sc=0.92), 0.8)]
DENTISTE_V = (recit("s_dentiste", "31_dentiste", "ÉCONOMISÉ", 2400, "Trois semaines plus tard"), [
    ("Deux mille quatre cents euros les deux", V.hook("h", "LA DENTISTE", ["C'EST CHER, 2 400 €", "LES COURONNES ? LE PAS", "CHER, C'EST DU CARTON"]), ("impact", 1.0)),
    ("C'est ce que la dentiste", V.scene("couture", "carte", [("LE DEVIS", YEL, 0.3), ("RETRAITE DE MAMAN : J-21", RED, 2.6)], mechant=dict(mouth="grin"), autres=MAMAN_C, mx=840), ("whoosh", 0.6)),
    ("Quarante-deux ans", V.scene("montee", "neutre", [("42 ANS À LA CANTINE", GREEN, 0.2), ("SOURIRE SUR LES PHOTOS", YEL, 3.4)], fond=salon_bg, sans_mechant=True, autres=[(760, MAMAN, dict(mouth="smile"), 0.8)]), ("pop", 0.8)),
    ("Sur le devis", V.fiche("devis", "DEVIS · 2 COURONNES", "CABINET DENTAIRE", [("Céramique", "2 400 €", 0.3, True), ("Option 100 % Santé", "AUCUNE", 1.6, False)], kpose="carte"), None),
    ("Moi, je fais du travail", V.gp("coup1", ["MOI, JE FAIS DU", "TRAVAIL PROPRE.", "LE BAS DE GAMME,", "ALLEZ À L'HÔPITAL"]), ("impact", 0.8)),
    ("Et en raccompagnant", V.geste("geste", "ELLE EN RAJOUTE"), ("whoosh", 0.5)),
    ("Fallait se brosser", V.gp("coup2", ["FALLAIT SE BROSSER", "LES DENTS AVANT,", "MADAME"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence", autres=MAMAN_C), None),
    ("Se brosser les dents", V.echo("echo", "SE BROSSER LES DENTS"), ("rate", 0.6)),
    ("Ce que la dentiste a pas dit", V.carte("regle", "COURONNE DENTAIRE", [("Le devis doit proposer", 0.5, False), ("une option 100 % Santé", 1.6, True), ("0 € avec une mutuelle responsable", 4.0, False)], "OBLIGATOIRE DEPUIS 2020 · DGCCRF", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors si elle veut pas", V.gros_mots("ailleurs", [("ELLE DOIT L'ÉCRIRE", WHITE, 1.4), ("TU PEUX ALLER AILLEURS", GREEN, 2.8)], fond=salon_bg), ("impact", 0.6)),
    ("Le soir, j'envoie", V.tel("signal", "20:15", [("Mail", "Assurance maladie", "Signalement + devis", BLEU), ("Agenda", "Dentiste d'en face", "Mardi · 100 % Santé", GREEN)], fond=salon_bg), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "POUR UNE CASE OUBLIÉE ?", fond=salon_bg), None),
    ("Trois semaines plus tard", V.scene("twist", "victoire", [("BONNE RETRAITE MAMAN", YEL, 0.3), ("0 € À PAYER", GREEN, 2.0)], fond=salon_bg, sans_mechant=True, devant=gateau, autres=[(760, MAMAN, dict(mouth="grin", arms_up=True), 0.8)]), ("succes", 0.8)),
    ("Deux mille quatre cents euros de devis", V.fin("fin", "2 400 €", "DE DEVIS, ET ZÉRO À PAYER", "CAS TYPE · 100 % SANTÉ · CODE DE LA SANTÉ PUBLIQUE · DGCCRF", fond=salon_bg), ("impact", 0.9)),
])


# ═════════════ 32. 10 minutes de retard, 1 heure retirée ═════════════

GERANTE = dict(shirt=(140, 40, 70), pants=(30, 30, 40), hair=(90, 50, 30), long_hair=True, glasses=True)
GILET_B = dict(shirt=(30, 90, 160))
V = Video(boutique_bg, GERANTE, GILET_B)
RETARD = (recit("s_retard", "32_retard_retenue", "RENDU PAR LA GÉRANTE", 108, "Le mois suivant"), [
    ("Cent huit euros retirés", V.hook("h", "MA GÉRANTE", ["JE T'AI RETIRÉ 108 €,", "OUI. UNE HEURE PAR", "RETARD, C'EST LA RÈGLE"]), ("impact", 1.0)),
    ("C'est ce que ma gérante", V.scene("couture", "choc", [("GRÈVE DES BUS : 9 RETARDS", YEL, 1.6), ("VOYAGE SCOLAIRE : VENDREDI", RED, 4.6)], mechant=dict(mouth="grin")), ("whoosh", 0.6)),
    ("Et pourtant je partais", V.scene("montee", "marche", [("PARTI 1 H AVANT", GREEN, 0.2), ("2 ARRÊTS À PIED", YEL, 1.6)], fond=lambda: route_bg(True), sans_mechant=True), ("pop", 0.8)),
    ("Neuf fois dix minutes", V.calcul("calcul", "9 RETARDS DE 10 MIN", [("RETARD RÉEL", 90, "1 H 30", GREEN, 0.4), ("RETIRÉ", 540, "9 H", RED, 2.2)], "EN MINUTES"), ("ticks", 0.6)),
    ("Le calcul, c'est moi", V.gp("coup1", ["LE CALCUL, C'EST MOI.", "T'ES PAS CONTENT,", "LA PORTE EST LÀ"]), ("impact", 0.8)),
    ("Et en rangeant les fiches", V.geste("geste", "ELLE EN RAJOUTE"), ("whoosh", 0.5)),
    ("Ceux qui ont de l'ambition", V.gp("coup2", ["CEUX QUI ONT DE", "L'AMBITION, ILS", "HABITENT À CÔTÉ"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence"), None),
    ("Habiter à côté", V.echo("echo", "HABITER À CÔTÉ"), ("rate", 0.6)),
    ("Sauf que le Code du travail", V.carte("regle", "UN RETARD", [("Les amendes sont interdites", 0.4, True), ("On retire le temps exact", 2.4, False), ("10 minutes = 10 minutes", 4.4, False)], "CODE DU TRAVAIL · L1331-2", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, une heure", V.gros_mots("sanction", [("1 HEURE POUR 10 MIN", WHITE, 0.6), ("SANCTION INTERDITE", RED, 2.0), ("AMENDE : 3 750 €", YEL, 4.0)], fond=salon_bg), ("impact", 0.6)),
    ("Le soir, je prends en photo", V.tel("photo", "21:05", [("Photo", "Tableau des retenues", "Toute l'équipe", GRIS), ("Mail", "Inspection du travail", "Envoyé", BLEU)], fond=salon_bg), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "SANS DEMANDER AUX COLLÈGUES", fond=salon_bg), None),
    ("Le mois suivant", V.fiche("note", "NOTE DE SERVICE", "AFFICHÉE AU VESTIAIRE", [("Retenue à la minute près", "", 0.3, True), ("Retenues rendues à l'équipe", "", 1.6, False)], kpose="victoire"), ("succes", 0.8)),
    ("Cent huit euros, et", V.fin("fin", "108 €", "ET LA RÈGLE ICI, C'EST LA LOI", "CAS TYPE · CODE DU TRAVAIL L1331-2 · CASS. SOC. 24 NOV. 1992"), ("impact", 0.9)),
])


# ═════════════ 33. ACTU : le SMIC au 1er décembre ═════════════

PATRON_A = dict(shirt=(60, 60, 70), pants=(40, 40, 50), hair=(50, 40, 30), glasses=True, tie=True)
BLEU_TRAVAIL = dict(shirt=(50, 80, 150))
V = Video(atelier_bg, PATRON_A, BLEU_TRAVAIL)
SMIC = (recit("s_smic", "33_smic_decembre", "EN PLUS PAR MOIS", 24, "Fin décembre"), [
    ("Vingt-quatre euros de plus", V.hook("h", "MON PATRON", ["TU CROIS TOUCHER 24 €", "DE PLUS ? LE SMIC, C'EST", "EN JANVIER. PAS CHEZ MOI"]), ("impact", 1.0)),
    ("C'est ce que mon patron", V.scene("couture", "choc", [("SMIC : 1er DÉCEMBRE", YEL, 0.3), ("NOËL DE MES 2 NIÈCES", RED, 3.0)], mechant=dict(mouth="grin")), ("whoosh", 0.6)),
    ("Et pourtant j'avais suivi", V.tel("actu", "07:45", [("Actu", "9 novembre", "SMIC + 1,6 %", BLEU), ("Actu", "Dès le 1er décembre", "Un mois plus tôt", GREEN)], fond=salon_bg), ("notif", 0.7)),
    ("Je lui demande juste", V.scene("demande", "parle", [("SUR LA PAIE ?", WHITE, 0.3)], mechant=dict(mouth="flat")), None),
    ("Tu crois tout", V.gp("coup1", ["TU CROIS TOUT", "CE QUE TU LIS SUR", "TON TÉLÉPHONE ?"]), ("impact", 0.8)),
    ("Et en retournant", V.geste("geste"), ("whoosh", 0.5)),
    ("Ici, c'est moi", V.gp("coup2", ["ICI, C'EST MOI QUI", "DÉCIDE QUI MÉRITE", "UNE AUGMENTATION"], (2.2, 2.4), True, arm=0.8), ("impact", 1.0)),
    ("Je dis rien", V.silence("silence", "telephone"), None),
    ("Qui mérite", V.echo("echo", "QUI MÉRITE"), ("rate", 0.6)),
    ("Sauf que le SMIC", V.carte("regle", "LE SMIC", [("Un plancher fixé par l'État", 0.8, True), ("Il monte pour tout le monde", 3.0, False), ("sans l'accord du patron", 4.4, False)], "CODE DU TRAVAIL · L3231-2", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, ça fait combien", V.carte("montant", "AU 1er DÉCEMBRE 2026", [("≈ 1 478 € → ≈ 1 502 € net", 0.6, True), ("pour un temps plein", 2.2, False), ("décret à paraître", 4.0, False)], "ANNONCE DU GOUVERNEMENT · 9 NOV.", fond=salon_bg), ("ticks", 0.6)),
    ("Le soir, je crée un groupe", V.tel("groupe", "08:00", [("WhatsApp", "SMIC atelier", "8 participants", GREEN), ("Mail", "Envoyé à 8:00", "8 mails pareils", BLEU)], fond=salon_bg), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "TOUT L'ATELIER CONTRE LUI", fond=salon_bg), None),
    ("Fin décembre", V.scene("twist", "victoire", [("PAIE DE DÉCEMBRE · LA LIGNE EST LÀ", GREEN, 0.3), ("CHEZ MOI, ON RESPECTE LA LOI", WHITE, 2.4)], mechant=dict(mouth="grin", arm=0.5)), ("succes", 0.8)),
    ("Vingt-quatre euros, et", V.fin("fin", "24 €", "ET CHEZ LUI AUSSI", "SMIC + 1,6 % AU 1er DÉC. 2026 · ANNONCE DU 9 NOV. · DÉCRET À PARAÎTRE"), ("impact", 0.9)),
])


# ═════════════ 34. La garantie légale de 2 ans ═════════════

VENDEUR = dict(shirt=(200, 40, 40), pants=(36, 36, 44), hair=(160, 110, 60))
TECH = dict(shirt=(50, 80, 150), pants=(50, 80, 150), hair=(40, 30, 25), cap=(50, 80, 150))
V = Video(magasin_bg, VENDEUR)
GARANTIE = (recit("s_garantie", "34_garantie_legale", "PAYÉ PAR LE MAGASIN", 650, "Trois jours plus tard"), [
    ("Six cent cinquante euros la machine", V.hook("h", "LE VENDEUR DU MAGASIN", ["VOTRE MACHINE À 650 €", "EN PANNE ? VOYEZ", "AVEC LA MARQUE"], phone=True), ("impact", 1.0)),
    ("C'est ce que le vendeur", V.scene("couture", "telephone", [("MA FILLE A 8 MOIS", YEL, 1.4), ("1 SEMAINE DE LINGE SALE", RED, 3.0)], fond=salon_bg, sans_mechant=True, devant=salon_machine), ("whoosh", 0.6)),
    ("Et pourtant on l'avait", V.scene("montee", "victoire", [("LA PLUS SOLIDE DU RAYON", GREEN, 0.3), ("650 €", YEL, 1.8)], mechant=dict(mouth="smile", arm=0.5)), ("pop", 0.8)),
    ("Quatorze mois après", V.scene("panne", "choc", [("14 MOIS APRÈS", WHITE, 0.2), ("PLUS D'ESSORAGE", RED, 1.4)], fond=salon_bg, sans_mechant=True, devant=salon_fumee), ("impact", 0.6)),
    ("La garantie, c'est un an", V.gp("coup1", ["LA GARANTIE, C'EST", "UN AN. APRÈS, C'EST", "PLUS CHEZ NOUS"], phone=True), ("impact", 0.8)),
    ("Et avant de raccrocher", V.geste("geste", phone=True), ("whoosh", 0.5)),
    ("Avec un bébé", V.gp("coup2", ["AVEC UN BÉBÉ, ON PREND", "L'EXTENSION. ÇA S'APPELLE", "ÊTRE UN PÈRE RESPONSABLE"], (2.2, 2.4), True, phone=True), ("impact", 1.0)),
    ("Je dis rien", V.scene("silence", "triste", fond=salon_bg, sans_mechant=True, devant=radiateur, z=(1.0, 1.04), fx=False), None),
    ("Un père responsable", V.echo("echo", "UN PÈRE RESPONSABLE", fond=salon_bg), ("rate", 0.6)),
    ("Sauf qu'il mélange", V.carte("regle", "DEUX GARANTIES", [("La marque : 1 an, commerciale", 0.6, False), ("La loi : 2 ans", 3.0, True), ("et c'est le MAGASIN qui la doit", 4.6, False)], "CODE DE LA CONSOMMATION · L217-3", fond=salon_bg), ("pop", 0.8)),
    ("Mais alors, il peut", V.gros_mots("marque", [("RENVOYER VERS LA MARQUE ?", WHITE, 0.4), ("NON", RED, 2.0), ("RÉPARER OU REMPLACER", GREEN, 3.0)], fond=salon_bg), ("impact", 0.6)),
    ("Ma cousine travaille", V.fiche("lettre", "CABINET D'AVOCATS", "MISE EN DEMEURE · PAPIER À EN-TÊTE", [("Garantie légale de conformité", "", 0.3, False), ("Réparation ou remplacement", "", 1.0, True), ("sans frais", "", 1.8, False)], fond=salon_bg), ("notif", 0.7)),
    ("Honnêtement", V.doute("doute", "MA COUSINE EN DANGER ?", fond=salon_bg), None),
    ("Trois jours plus tard", V.scene("twist", "victoire", [("PIÈCE CHANGÉE", GREEN, 0.3), ("RIEN À PAYER", YEL, 1.6)], fond=salon_bg, sans_mechant=True, devant=lambda d, t: machine(d, 960, 1560), autres=[(740, TECH, dict(mouth="smile", arm=0.4), 1.1)]), ("succes", 0.8)),
    ("Six cent cinquante euros, et", V.fin("fin", "650 €", "ET C'EST LUI QUI A VU AVEC LA MARQUE", "CAS TYPE · CODE DE LA CONSOMMATION L217-3 ET SUIVANTS", fond=salon_bg), ("impact", 0.9)),
])


VIDEOS = {"carte": CARTE, "colis": COLIS, "salaire": SALAIRE, "voiture": VOITURE, "dentiste": DENTISTE_V,
          "retard": RETARD, "smic": SMIC, "garantie": GARANTIE}

if __name__ == "__main__":
    rec, beats = VIDEOS[sys.argv[1]]
    rec.fabriquer(beats)
