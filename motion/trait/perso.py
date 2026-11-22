"""Personnage articulé du style « trait » : grosse tête ronde, corps en bloc, bras et jambes en tubes.

    p = Perso(cheveux="boucles", haut="sweat", couleur_haut=(46, 170, 120))
    p.pose(0.0, "repos"); p.pose(2.1, "pointe")          # poses calées dans le temps (fondu 0,25 s)
    p.emotion(0.0, "neutre"); p.emotion(2.1, "choc")
    p.draw(ctx, x, y_pieds, echelle, t, bouche=0..1)

Vie permanente : respiration, léger balancement, clignement des yeux, bouche sur la voix.
"""
import math

from dessin import INK, LW, circle, dark, ease, ellipse, flat, mix, ombre_sol, paint, poly, rrect, stroke, tube

# angles en degrés : (épaule, coude) ; épaule 0 = bras le long du corps, + = vers l'extérieur / le haut
import os as _os
# Mouvement de repos (respiration, balancement, tête) : 0,25 = calme comme La Ficelle (mesure du 22 nov. : chez eux un
# personnage ne bouge que la bouche entre deux gestes) ; 1 = ancien réglage.
CALME = float(_os.environ.get("TRAIT_CALME", "0.25"))

POSES = {
    "repos": ((8, 6), (8, 6)),
    "mains_hanches": ((38, -95), (38, -95)),
    "pointe": ((8, 6), (82, 4)),                # bras droit (côté écran droit) tendu
    "pointe_g": ((82, 4), (8, 6)),
    "leve": ((160, 15), (160, 15)),            # deux bras en l'air
    "leve_d": ((8, 6), (165, 10)),
    "objet": ((22, -105), (22, -105)),         # tient un objet devant lui (tablette, contrat)
    "telephone": ((8, 6), (24, -128)),         # téléphone dans la main droite, près du torse
    "oreille": ((8, 6), (30, -155)),           # téléphone à l'oreille
    "facepalm": ((8, 6), (40, -150)),
    "haussement": ((40, 40), (40, 40)),
    "pointe_cam": ((8, 6), (40, -60)),         # pointe vers le spectateur
}

EMOTIONS = ("neutre", "choc", "content", "colere", "malin", "triste")


def _lerp_pose(a, b, k):
    return tuple(tuple(x + (y - x) * k for x, y in zip(sa, sb)) for sa, sb in zip(a, b))


class Perso:
    def __init__(self, peau=(240, 192, 152), cheveux="court", couleur_cheveux=(70, 46, 34),
                 haut="sweat", couleur_haut=(46, 170, 120), bas=(58, 84, 150), chaussures=(245, 245, 245),
                 barbe=False, moustache=False, lunettes=False, badge=None, seed=0):
        self.peau, self.cheveux, self.cc = peau, cheveux, couleur_cheveux
        self.haut, self.ch, self.bas, self.chaus = haut, couleur_haut, bas, chaussures
        self.barbe, self.moustache, self.lunettes, self.badge = barbe, moustache, lunettes, badge
        self.seed = seed
        self._poses = [(0.0, "repos")]
        self._emos = [(0.0, "neutre")]
        self.objet = None                       # fonction (ctx, x_main, y_main, échelle) pour ce qu'il tient

    # ── calage dans le temps ──
    def pose(self, t, nom):
        self._poses.append((t, nom))
        self._poses.sort(key=lambda x: x[0])
        return self

    def emotion(self, t, nom):
        self._emos.append((t, nom))
        self._emos.sort(key=lambda x: x[0])
        return self

    def _pose_at(self, t, fondu=0.22):
        prev, cur, tc = "repos", "repos", 0.0
        for tt, n in self._poses:
            if tt <= t:
                prev, cur, tc = cur, n, tt
        k = ease((t - tc) / fondu)
        return _lerp_pose(POSES[prev], POSES[cur], k), k, cur

    def _emo_at(self, t):
        cur, tc = "neutre", 0.0
        for tt, n in self._emos:
            if tt <= t:
                cur, tc = n, tt
        return cur, t - tc

    # ── dessin ──
    def draw(self, ctx, x, y, s, t, bouche=0.0, regard=0.0, dos=False):
        """x, y = milieu des pieds ; s = échelle (1 = 1000 px de haut)."""
        (pg, pd), _, pose_nom = self._pose_at(t)
        emo, de = self._emo_at(t)
        ph = self.seed * 1.7
        souffle = math.sin(t * 2.2 + ph) * 5 * CALME
        bal = math.sin(t * 1.1 + ph) * 1.6 * CALME
        sursaut = 0.0
        if emo == "choc":
            sursaut = -28 * math.exp(-de * 7) * math.cos(de * 22)      # petit saut de surprise
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(s, s)
        lw = LW / max(s, 0.35) * min(1.0, s * 1.15)                    # contour ~constant à l'écran
        ombre_sol(ctx, 0, 0, 150)
        ctx.translate(0, sursaut)

        # jambes + chaussures
        for sx in (-1, 1):
            tube(ctx, [(sx * 40, -430), (sx * 42, -40)], 66, self.bas, lw)
            ellipse(ctx, sx * 52, -22, 52, 26)
            paint(ctx, self.chaus, lw, shade=0.85)

        ctx.rotate(math.radians(bal))
        ctx.translate(0, souffle * 0.4)
        # torse
        top, bot = -770, -410
        poly(ctx, [(-118, top + 30), (118, top + 30), (110, bot), (-110, bot)])
        ctx.new_path()
        rrect(ctx, -122, top, 244, bot - top + 12, 46)
        paint(ctx, self.ch, lw, shade=0.78)
        self._details_haut(ctx, top, bot, lw)

        # bras
        epaules = {-1: (-112, top + 52), 1: (112, top + 52)}
        mains = {}
        for sx, (a_ep, a_co) in ((-1, pg), (1, pd)):
            ex, ey = epaules[sx]
            a1 = math.radians(a_ep)
            cx_, cy_ = ex + sx * math.sin(a1) * 175, ey + math.cos(a1) * 175
            a2 = a1 + math.radians(a_co)
            hx, hy = cx_ + sx * math.sin(a2) * 165, cy_ + math.cos(a2) * 165
            mains[sx] = (hx, hy)
            tube(ctx, [(ex, ey), (cx_, cy_), (hx, hy)], 60, self.ch, lw)
            circle(ctx, hx, hy, 30)
            paint(ctx, self.peau, lw, shade=0.85)

        # tête
        hx, hy = 0, -880 + souffle * 0.6
        if pose_nom in ("leve", "leve_d"):
            hy -= 4
        ctx.save()
        ctx.translate(hx, hy)
        ctx.rotate(math.radians(math.sin(t * 0.9 + ph) * 2.5 * CALME + regard * 4))
        rrect(ctx, -26, 70, 52, 50, 10)
        paint(ctx, dark(self.peau, 0.9), lw, shade=1)
        for sx in (-1, 1):
            circle(ctx, sx * 110, 8, 24)
            paint(ctx, self.peau, lw, shade=1)
        circle(ctx, 0, 0, 112)
        paint(ctx, self.peau, lw, shade=0.86)
        self._visage(ctx, t, emo, de, bouche, regard, lw)
        self._cheveux(ctx, lw)
        ctx.restore()

        # objet tenu + main droite par-dessus
        if self.objet and pose_nom in ("objet", "telephone", "oreille"):
            if pose_nom == "objet":
                ox, oy = (mains[-1][0] + mains[1][0]) / 2, (mains[-1][1] + mains[1][1]) / 2
            else:
                ox, oy = mains[1]
            self.objet(ctx, ox, oy, 1.0)
            for sx in ((-1, 1) if pose_nom == "objet" else (1,)):
                circle(ctx, *mains[sx], 30)
                paint(ctx, self.peau, lw, shade=0.85)
        if pose_nom == "facepalm":
            circle(ctx, 30, -870, 34)
            paint(ctx, self.peau, lw, shade=0.85)
        ctx.restore()
        # point d'ancrage pour les badges, bulles, traits de choc (coordonnées monde)
        return {"tete": (x, y + (hy - 0 + sursaut) * s), "haut_tete": (x, y + (hy - 150 + sursaut) * s),
                "main_d": (x + mains[1][0] * s, y + mains[1][1] * s)}

    def _details_haut(self, ctx, top, bot, lw):
        if self.haut == "sweat":
            # poche kangourou + cordons de capuche
            rrect(ctx, -70, bot - 120, 140, 82, 22)
            paint(ctx, dark(self.ch, 0.9), lw * 0.7, shade=1)
            for sx in (-1, 1):
                ctx.move_to(sx * 26, top + 40)
                ctx.line_to(sx * 30, top + 130)
                stroke(ctx, lw * 1.3, (245, 245, 245))
            ctx.move_to(-70, top + 18)
            ctx.curve_to(-40, top + 60, 40, top + 60, 70, top + 18)
            stroke(ctx, lw * 0.8)
        elif self.haut == "polo":
            poly(ctx, [(-44, top + 6), (0, top + 70), (44, top + 6)], close=False)
            stroke(ctx, lw * 0.8)
            rrect(ctx, 46, top + 90, 46, 34, 8)       # logo du magasin
            paint(ctx, (255, 214, 60), lw * 0.6, shade=1)
            # cordon de badge
            ctx.move_to(-40, top + 10)
            ctx.line_to(-62, top + 170)
            stroke(ctx, lw * 0.9, (230, 60, 70))
            rrect(ctx, -92, top + 168, 60, 76, 8)
            paint(ctx, (250, 250, 250), lw * 0.6, shade=1)
            rrect(ctx, -84, top + 180, 44, 12, 3)
            flat(ctx, (60, 60, 70))
        elif self.haut == "chemise":
            poly(ctx, [(-40, top), (0, top + 60), (40, top)], close=False)
            stroke(ctx, lw * 0.8)
            poly(ctx, [(0, top + 55), (-16, top + 80), (0, bot - 40), (16, top + 80)])
            paint(ctx, (200, 40, 60), lw * 0.6, shade=1)
        elif self.haut == "gilet":
            for sx in (-1, 1):
                rrect(ctx, sx * 112 - (sx > 0) * 76, top + 10, 76, bot - top - 30, 18)
                paint(ctx, (210, 235, 40), lw * 0.7, shade=0.9)
            rrect(ctx, -118, top + 200, 236, 22, 4)
            flat(ctx, (230, 230, 230), 0.9)

    def _visage(self, ctx, t, emo, de, bouche, regard, lw):
        # joues
        for sx in (-1, 1):
            circle(ctx, sx * 66, 42, 20)
            flat(ctx, (240, 120, 120), 0.33)
        # clignement : 0,12 s toutes les ~3,5 s
        cl = ((t + self.seed * 1.3) % 3.6) < 0.12
        ex = regard * 10
        for sx in (-1, 1):
            x0 = sx * 40 + ex
            if emo == "choc" and not cl:
                circle(ctx, x0, -6, 22)
                paint(ctx, (255, 255, 255), lw * 0.7, shade=1)
                circle(ctx, x0, -4, 9)
                flat(ctx, INK)
            elif cl:
                ctx.move_to(x0 - 14, 0)
                ctx.curve_to(x0 - 6, -12, x0 + 6, -12, x0 + 14, 0)
                stroke(ctx, lw * 0.9)
            elif emo in ("malin", "colere"):
                ellipse(ctx, x0, 0, 12, 12)
                flat(ctx, INK)
                ctx.rectangle(x0 - 18, -22, 36, 20)
                flat(ctx, self.peau)
                ctx.move_to(x0 - 16, -1 + (sx * 4 if emo == "colere" else 0))
                ctx.line_to(x0 + 16, -1 - (sx * 4 if emo == "colere" else 0))
                stroke(ctx, lw * 1.1)
            elif emo == "content":
                ctx.move_to(x0 - 13, 2)
                ctx.curve_to(x0 - 6, -14, x0 + 6, -14, x0 + 13, 2)
                stroke(ctx, lw * 0.9)
            else:
                ellipse(ctx, x0, -2, 11, 14)
                flat(ctx, INK)
                circle(ctx, x0 + 4, -7, 4)
                flat(ctx, (255, 255, 255))
        # sourcils
        for sx in (-1, 1):
            x0 = sx * 40 + ex
            a = {"colere": 0.42, "malin": 0.18, "triste": -0.35, "choc": -0.15}.get(emo, 0.0)
            yb = -38 if emo != "choc" else -50
            dx, dy = 20 * math.cos(a), 20 * math.sin(a) * sx
            ctx.move_to(x0 - dx, yb - dy)
            ctx.line_to(x0 + dx, yb + dy)
            stroke(ctx, lw * 1.4, dark(self.cc, 0.8) if self.cheveux != "chauve" else (90, 70, 60))
        if self.lunettes:
            for sx in (-1, 1):
                circle(ctx, sx * 40 + ex, -2, 28)
                stroke(ctx, lw * 0.8)
            ctx.move_to(-12, -4)
            ctx.line_to(12, -4)
            stroke(ctx, lw * 0.8)
        # barbe / moustache
        if self.barbe:
            ctx.move_to(-96, 20)
            ctx.curve_to(-80, 110, 80, 110, 96, 20)
            ctx.curve_to(60, 70, -60, 70, -96, 20)
            flat(ctx, self.cc, 0.85)
        if self.moustache:
            ctx.move_to(-38, 46)
            ctx.curve_to(-20, 30, 20, 30, 38, 46)
            ctx.curve_to(18, 40, -18, 40, -38, 46)
            paint(ctx, self.cc, lw * 0.5, shade=1)
        # bouche
        my = 58
        o = max(0.0, min(1.0, bouche))
        if emo == "choc" and o < 0.3:
            o = 0.55
        if o > 0.08:
            hgt = 8 + 30 * o
            wid = 22 + 8 * o if emo != "content" else 30
            ellipse(ctx, 0, my + hgt * 0.35, wid, hgt)
            paint(ctx, (120, 30, 40), lw * 0.8, shade=1)
            ellipse(ctx, 0, my + hgt * 0.35 + hgt * 0.45, wid * 0.6, hgt * 0.35)
            flat(ctx, (230, 100, 110))
            ctx.rectangle(-wid * 0.6, my + hgt * 0.35 - hgt + 2, wid * 1.2, 7)
            flat(ctx, (255, 255, 255), 0.9)
        elif emo in ("content", "malin"):
            ctx.move_to(-30, my - 4)
            ctx.curve_to(-16, my + 22, 16 if emo == "content" else 22, my + 22, 32, my - 10 if emo == "malin" else my - 4)
            stroke(ctx, lw * 1.0)
        elif emo in ("colere", "triste"):
            ctx.move_to(-24, my + 10)
            ctx.curve_to(-10, my - 4, 10, my - 4, 24, my + 10)
            stroke(ctx, lw * 1.0)
        else:
            ctx.move_to(-16, my + 4)
            ctx.curve_to(-6, my + 10, 6, my + 10, 16, my + 4)
            stroke(ctx, lw * 1.0)

    def _cheveux(self, ctx, lw):
        c = self.cc
        st = self.cheveux
        if st == "boucles":
            pts = [(-108, -44), (-112, -82), (-92, -116), (-60, -136), (-20, -144), (22, -144), (62, -136),
                   (94, -114), (112, -80), (108, -44)]
            for (px, py) in pts:
                circle(ctx, px, py, 34)
                paint(ctx, c, lw, shade=1)
            ctx.move_to(-112, -48)
            ctx.curve_to(-90, -160, 90, -160, 112, -48)
            ctx.curve_to(70, -76, -70, -76, -112, -48)
            flat(ctx, c)
            for (px, py) in [(-52, -92), (0, -104), (52, -92)]:
                circle(ctx, px, py, 30)
                paint(ctx, c, lw * 0.7, shade=1)
            # reflet
            ctx.arc(-20, -96, 60, math.radians(200), math.radians(250))
            stroke(ctx, lw * 1.4, (255, 255, 255), alpha=0.35)
        elif st == "court":
            ctx.move_to(-114, 0)
            ctx.curve_to(-120, -160, 120, -160, 114, 0)
            ctx.curve_to(100, -50, 30, -70, -10, -62)
            ctx.curve_to(-60, -56, -100, -40, -114, 0)
            paint(ctx, c, lw, shade=0.85)
            ctx.arc(-10, -60, 70, math.radians(215), math.radians(265))
            stroke(ctx, lw * 1.4, (255, 255, 255), alpha=0.35)
        elif st == "plaque":            # cheveux gominés en arrière
            ctx.move_to(-114, 10)
            ctx.curve_to(-130, -180, 130, -180, 114, 10)
            ctx.curve_to(104, -40, 60, -62, 0, -62)
            ctx.curve_to(-60, -62, -104, -40, -114, 10)
            paint(ctx, c, lw, shade=0.82)
            for k in (-40, 0, 40):
                ctx.move_to(k - 30, -100)
                ctx.curve_to(k - 10, -126, k + 20, -126, k + 40, -112)
                stroke(ctx, lw * 0.6, dark(c, 0.6))
        elif st == "chauve":
            for sx in (-1, 1):
                ctx.move_to(sx * 112, 10)
                ctx.curve_to(sx * 118, -40, sx * 100, -70, sx * 80, -86)
                ctx.line_to(sx * 96, -40)
                ctx.close_path()
                paint(ctx, c, lw * 0.8, shade=1)
            ctx.arc(-20, -40, 80, math.radians(215), math.radians(255))
            stroke(ctx, lw * 1.6, (255, 255, 255), alpha=0.4)
        elif st == "chignon":
            circle(ctx, 0, -128, 46)
            paint(ctx, c, lw, shade=0.85)
            ctx.move_to(-116, 40)
            ctx.curve_to(-130, -170, 130, -170, 116, 40)
            ctx.curve_to(100, -40, 20, -70, -20, -60)
            ctx.curve_to(-80, -50, -110, -20, -116, 40)
            paint(ctx, c, lw, shade=0.85)


def traits_choc(ctx, x, y, r, t, n=7, color=INK):
    """Traits de choc autour d'une tête (apparaissent et vibrent)."""
    k = min(1.0, t * 6)
    for i in range(n):
        a = -math.pi * (0.15 + 0.7 * i / (n - 1)) + math.sin(t * 30 + i) * 0.03
        r0, r1 = r * (1.0 + 0.04 * math.sin(t * 25 + i)), r * (1.0 + 0.28 * k)
        ctx.move_to(x + math.cos(a) * r0, y + math.sin(a) * r0)
        ctx.line_to(x + math.cos(a) * r1, y + math.sin(a) * r1)
        stroke(ctx, 9, color)
