// Page du village en direct (1080x1920). Reçoit l'état et les annonces du serveur par WebSocket,
// ou simule un live toute seule avec ?demo.
import { PALIERS, appliquer, etatInitial, fauxEvenement, hash, nbMaisons, topBatisseurs } from "./logique.js";

const W = 1080, H = 1920;
const cv = document.getElementById("c");
const ctx = cv.getContext("2d");
const DEMO = new URLSearchParams(location.search).has("demo") || window.VILLAGE_DEMO === true;

const INK = "#16161c", JAUNE = "#ffce00", VERT = "#3ccf6e", BLEU = "#3d8bff", ROUGE = "#e8323c", BLANC = "#fafafa";
const SOL = 1130;            // pied des bâtiments
const TROTTOIR = 1200;       // pied des habitants
const ECH_BAT = 0.52;        // échelle des façades
const ECH_ARBRE = 0.62;
const ECH_PERSO = 0.21;
const CYCLE = 480;           // un jour + une nuit = 8 minutes

let cfg = null, etat = null;
let meta = {};
const img = {};

// ───────── chargement ─────────
function charger(nom) {
  return new Promise((ok) => {
    const i = new Image();
    i.onload = () => ok((img[nom] = i));
    i.onerror = () => ok(null);
    i.src = `sprites/${nom}.png`;
  });
}

async function chargerTout() {
  meta = await (await fetch("sprites/sprites.json")).json();
  const noms = Object.keys(meta).flatMap((n) => (n.startsWith("perso_") ? [n, n + "_parle"] : [n]));
  await Promise.all(noms.map(charger));
  try { voix.liste = await (await fetch("voix/voix.json")).json(); } catch { voix.liste = {}; }
  await document.fonts.load("40px Anton");
  await document.fonts.load("800 40px Montserrat");
}

// ───────── utilitaires de dessin ─────────
const fmt = (n) => Math.round(n).toLocaleString("fr-FR").replace(/\s/g, " ");
const ease = (k) => Math.max(0, Math.min(1, k));
const back = (k) => { k = ease(k); const c = 1.9; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
const mix = (a, b, k) => a.map((v, i) => Math.round(v + (b[i] - v) * k));
const rgb = (c) => `rgb(${c.join(",")})`;

function rrect(x, y, w, h, r, fill, stroke, lw = 6) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function texte(t, x, y, { taille = 40, police = "Montserrat", couleur = BLANC, align = "center", base = "middle",
  contour = 0, max = 0 } = {}) {
  let s = taille;
  const f = () => `${police === "Montserrat" ? "800 " : ""}${s}px ${police}`;
  ctx.font = f();
  if (max) while (ctx.measureText(t).width > max && s > 10) { s -= 1; ctx.font = f(); }
  ctx.textAlign = align;
  ctx.textBaseline = base;
  if (contour) {
    ctx.lineJoin = "round";
    ctx.lineWidth = contour;
    ctx.strokeStyle = INK;
    ctx.strokeText(t, x, y);
  }
  ctx.fillStyle = couleur;
  ctx.fillText(t, x, y);
}

function sprite(nom, x, ySol, ech, { flip = false } = {}) {
  const i = img[nom], m = meta[nom.replace("_parle", "")];
  if (!i || !m) return;
  ctx.save();
  ctx.translate(x, ySol);
  if (flip) ctx.scale(-1, 1);
  ctx.drawImage(i, -m.ax * ech, -m.ay * ech, m.w * ech, m.h * ech);
  ctx.restore();
}

// ───────── sons et narrateur ─────────
let audio = null;
const boutonSon = document.getElementById("son");
function activerSon() {
  if (!audio) audio = new AudioContext();
  audio.resume();
  voix.debloquee = true;
  boutonSon.hidden = true;
}
boutonSon.onclick = activerSon;
cv.onclick = activerSon;

function bip(freq, dur, type = "square", vol = 0.08, glisse = 0, t0 = 0) {
  if (!audio || audio.state !== "running") return;
  const t = audio.currentTime + t0;
  const o = audio.createOscillator(), g = audio.createGain();
  o.type = type;
  o.frequency.setValueAtTime(freq, t);
  if (glisse) o.frequency.exponentialRampToValueAtTime(freq * glisse, t + dur);
  g.gain.setValueAtTime(vol, t);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g).connect(audio.destination);
  o.start(t);
  o.stop(t + dur);
}
const SONS = {
  pop: () => bip(500, 0.12, "sine", 0.2, 2.2),
  arrivee: () => [660, 880].forEach((f, i) => bip(f, 0.16, "triangle", 0.15, 0, i * 0.1)),
  piece: () => { bip(1320, 0.08, "square", 0.06); bip(1760, 0.18, "square", 0.06, 0, 0.07); },
  fanfare: () => [523, 659, 784, 1046].forEach((f, i) => bip(f, 0.22, "triangle", 0.16, 0, i * 0.11)),
  marteau: () => [0, 0.18, 0.36].forEach((t) => bip(180, 0.07, "square", 0.12, 0.5, t)),
};

// Le narrateur : des phrases enregistrées (voix/…), jamais deux en même temps, avec des temps de repos.
const voix = {
  liste: {}, debloquee: false, enCours: null, finLe: 0, dernier: {}, dernierTout: 0,
  REPOS: { arrivee: 12, construction: 10, monument: 5, discute: 120, appel: 0, soir: 0, matin: 0 },
  dire(cat, now) {
    const fichiers = this.liste[cat];
    if (!fichiers || !fichiers.length) return;
    if (now < this.finLe + 1.2) return;                                  // quelqu'un parle déjà
    if (now - (this.dernier[cat] ?? -1e9) < (this.REPOS[cat] ?? 10)) return;
    const a = new Audio(fichiers[Math.floor(Math.random() * fichiers.length)]);
    a.volume = 1;
    this.finLe = now + 6;
    a.onloadedmetadata = () => { this.finLe = performance.now() / 1000 + a.duration; };
    a.play().then(() => { boutonSon.hidden = true; }).catch(() => { this.finLe = 0; });
    this.dernier[cat] = this.dernierTout = now;
  },
};
const chats = [];             // instants des derniers commentaires (pour « ça discute bien »)
let prochainAppel = 40;

// ───────── jour / nuit ─────────
let phaseAvant = null;
const FORCE = new URLSearchParams(location.search).get("heure");   // ?heure=nuit ou ?heure=jour (tests)
function nuit(now) {
  if (FORCE) return FORCE === "nuit" ? 1 : 0;
  const ph = ((now + CYCLE * 0.44) % CYCLE) / CYCLE;  // on démarre en fin d'après-midi
  if (phaseAvant !== null) {
    if (phaseAvant < 0.42 && ph >= 0.42) voix.dire("soir", now);
    if (phaseAvant < 0.92 && ph >= 0.92) voix.dire("matin", now);
  }
  phaseAvant = ph;
  if (ph < 0.4) return 0;
  if (ph < 0.5) return (ph - 0.4) / 0.1;
  if (ph < 0.9) return 1;
  return 1 - (ph - 0.9) / 0.1;
}

const etoiles = Array.from({ length: 90 }, (_, i) => ({ x: (hash("x" + i) % 1080), y: 60 + (hash("y" + i) % 900), r: 1 + (i % 3) }));

// ───────── habitants qui marchent ─────────
const marcheurs = new Map();
const MAX_MARCHEURS = 26;

function marcheur(id, nom, abonne = false, surPlace = false) {
  let m = marcheurs.get(id);
  const now = performance.now() / 1000;
  if (!m) {
    if (marcheurs.size >= MAX_MARCHEURS) {
      const vieux = [...marcheurs.entries()].sort((a, b) => (a[1].abonne - b[1].abonne) || (a[1].vu - b[1].vu))[0];
      marcheurs.delete(vieux[0]);
    }
    const gauche = Math.random() < 0.5;
    m = { nom, look: `perso_${String(hash(id) % 16).padStart(2, "0")}`,
      x: surPlace ? 90 + Math.random() * (W - 180) : gauche ? -60 : W + 60,
      cible: 80 + Math.random() * (W - 160), vit: 70 + Math.random() * 50, dir: gauche ? 1 : -1,
      bulle: "", tBulle: -99, vu: now, abonne, ph: Math.random() * 6, ne: surPlace ? now : -99 };
    marcheurs.set(id, m);
  }
  m.nom = nom || m.nom;
  m.abonne = m.abonne || abonne;
  m.vu = now;
  return m;
}

function majMarcheurs(dt, now) {
  for (const m of marcheurs.values()) {
    if (now - m.tBulle < 5) continue;          // il parle : il s'arrête
    const d = m.cible - m.x;
    if (Math.abs(d) < 4) {
      if (Math.random() < dt * 0.5) m.cible = 60 + Math.random() * (W - 120);
    } else {
      m.dir = Math.sign(d);
      m.x += m.dir * Math.min(Math.abs(d), m.vit * dt);
    }
  }
}

function dessinerMarcheurs(now) {
  const liste = [...marcheurs.values()].sort((a, b) => a.ph - b.ph);
  for (const m of liste) {
    const parle = now - m.tBulle < 5;
    const marche = !parle && Math.abs(m.cible - m.x) > 4;
    const saut = marche ? Math.abs(Math.sin(now * 9 + m.ph)) * 8 : 0;
    const k = back((now - m.ne) / 0.35);
    const y = TROTTOIR + (m.ph % 1) * 14 - saut;
    ctx.save();
    ctx.translate(m.x, y);
    ctx.scale(k, k);
    sprite(parle && Math.floor(now * 7) % 2 ? m.look + "_parle" : m.look, 0, 0, ECH_PERSO, { flip: m.dir < 0 });
    ctx.restore();
    const haut = y - meta[m.look].ay * ECH_PERSO * k;
    ctx.font = "800 20px Montserrat";
    const tw = Math.min(ctx.measureText(m.nom).width, 170);
    rrect(m.x - tw / 2 - 10, haut - 36, tw + 20, 30, 15, m.abonne ? "rgba(22,22,28,.88)" : "rgba(22,22,28,.6)");
    texte(m.nom, m.x, haut - 21, { taille: 20, max: 170, couleur: m.abonne ? BLANC : "#cfd2dc" });
  }
  // bulles : le pseudo en rouge, le commentaire dessous
  for (const m of liste) {
    if (now - m.tBulle >= 5 || !m.bulle) continue;
    const k = back((now - m.tBulle) / 0.25);
    const y = TROTTOIR - meta[m.look].ay * ECH_PERSO - 70;
    ctx.save();
    ctx.translate(Math.max(170, Math.min(W - 170, m.x)), y);
    ctx.scale(k, k);
    ctx.font = "800 28px Montserrat";
    const tw = Math.max(120, Math.min(ctx.measureText(m.bulle).width, 300));
    rrect(-tw / 2 - 22, -86, tw + 44, 82, 22, BLANC, JAUNE, 5);
    ctx.beginPath(); ctx.moveTo(-14, -6); ctx.lineTo(14, -6); ctx.lineTo(0, 14); ctx.closePath();
    ctx.fillStyle = BLANC; ctx.fill();
    texte(m.nom, 0, -64, { taille: 20, couleur: ROUGE, max: 280 });
    texte(m.bulle, 0, -34, { taille: 28, couleur: INK, max: 300 });
    ctx.restore();
  }
}

// ───────── rue, arbres, lampadaires ─────────
const pops = new Map();
const poussieres = [];
let focus = null;
let camera = 0;

function rue() {
  let x = 70;
  const bats = etat.batiments.map((b) => {
    const m = meta[b.sprite];
    const w = (m ? m.w : 300) * ECH_BAT;
    const r = { ...b, x: x + (m ? m.ax : 150) * ECH_BAT, w };
    x += w + 34;
    return r;
  });
  const arbres = etat.arbres.map((a, i) => ({ ...a, x: 60 + i * 92 + (hash(a.id) % 40), w: 90 }));
  const long = Math.max(x + 40, arbres.length ? arbres[arbres.length - 1].x + 80 : 0, W);
  return { bats, arbres, long };
}

function dessinerVillage(now, dt, n) {
  const { bats, arbres, long } = rue();
  const marge = Math.max(0, long - W);
  let cam = marge * (0.5 - 0.5 * Math.cos(now / 28));
  if (focus && now < focus.jusqua) cam = Math.max(0, Math.min(marge, focus.x - W / 2));
  camera += (cam - camera) * Math.min(1, dt * 2.5);

  const d = img.decor, md = meta.decor;
  const off = -((camera * 0.35) % W);
  for (const x of [off, off + W]) ctx.drawImage(d, x, SOL - md.sol, W, md.h);

  ctx.save();
  ctx.translate(-camera, 0);
  const posee = (id, x, ech, nom, y = SOL) => {
    const t0 = pops.get(id);
    const k = t0 === undefined ? 1 : back((now - t0) / 0.6);
    if (k <= 0.01) return 0;
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k); sprite(nom, 0, 0, ech); ctx.restore();
    return k;
  };
  for (const a of arbres) posee(a.id, a.x, ECH_ARBRE, "arbre", SOL - 44);
  for (const b of bats) {
    const k = posee(b.id, b.x, ECH_BAT, b.sprite);
    const m = meta[b.sprite];
    if (k > 0.01) texte(b.nom, b.x, SOL - (m ? m.ay : 300) * ECH_BAT * k - 26, { taille: 26, contour: 7, max: Math.max(120, b.w) });
  }
  ctx.restore();

  // la nuit tombe sur le décor (pas sur l'interface ni les habitants)
  if (n > 0) {
    ctx.fillStyle = `rgba(8,12,38,${0.5 * n})`;
    ctx.fillRect(0, 0, W, TROTTOIR + 140);
  }
  // lampadaires (allumés le soir)
  ctx.save();
  ctx.translate(-((camera) % 300), 0);
  for (let x = 120; x < W + 300; x += 300) {
    ctx.fillStyle = "#2a2a33";
    ctx.fillRect(x - 5, SOL - 150, 10, 160);
    rrect(x - 18, SOL - 166, 36, 22, 8, n > 0.3 ? "#fff2b0" : "#d9d9df", INK, 3);
    if (n > 0.05) {
      const g = ctx.createRadialGradient(x, SOL - 155, 4, x, SOL - 155, 120);
      g.addColorStop(0, `rgba(255,220,120,${0.55 * n})`);
      g.addColorStop(1, "rgba(255,220,120,0)");
      ctx.fillStyle = g;
      ctx.fillRect(x - 120, SOL - 275, 240, 240);
    }
  }
  ctx.restore();

  for (let i = poussieres.length - 1; i >= 0; i--) {
    const q = poussieres[i];
    q.x += q.vx * dt; q.y += q.vy * dt; q.vy += 40 * dt; q.v -= dt;
    if (q.v <= 0) { poussieres.splice(i, 1); continue; }
    ctx.globalAlpha = Math.min(1, q.v);
    ctx.fillStyle = "#e9e2d0";
    ctx.beginPath(); ctx.arc(q.x - camera, q.y, q.r, 0, 7); ctx.fill();
    ctx.globalAlpha = 1;
  }
}

function construire(bid, now, arbre) {
  pops.set(bid, now);
  const r = rue();
  const b = (arbre ? r.arbres : r.bats).find((x) => x.id === bid);
  if (!b) return;
  if (!arbre) focus = { x: b.x, jusqua: now + 6 };
  for (let i = 0; i < (arbre ? 8 : 26); i++) {
    poussieres.push({ x: b.x + (Math.random() - 0.5) * b.w, y: SOL - Math.random() * 30, vx: (Math.random() - 0.5) * 260,
      vy: -60 - Math.random() * 120, r: 8 + Math.random() * 16, v: 0.8 + Math.random() * 0.8 });
  }
}

// ───────── interface ─────────
const aff = { habitants: 0, budget: 0, maisons: 0 };

function entete(now) {
  texte(cfg.ville, W / 2, 252, { taille: 74, police: "Anton", contour: 12 });
  const live = Math.floor(now * 1.5) % 2 === 0;
  rrect(W / 2 - 250, 298, 230, 40, 20, ROUGE);
  texte(`${live ? "●" : "○"} EN DIRECT`, W / 2 - 135, 319, { taille: 22 });
  rrect(W / 2 - 6, 298, 256, 40, 20, INK);
  texte("LE VILLAGE DES ABONNÉS", W / 2 + 122, 319, { taille: 18, couleur: JAUNE });
}

function compteurs(dt, now) {
  const cibles = { habitants: etat.habitants, budget: etat.budget, maisons: nbMaisons(etat) };
  for (const k in aff) aff[k] += (cibles[k] - aff[k]) * Math.min(1, dt * 6);
  [["HABITANTS", fmt(aff.habitants), VERT], ["BUDGET", fmt(aff.budget) + " €", JAUNE], ["MAISONS", fmt(aff.maisons), BLEU]]
    .forEach(([lab, val, col], i) => {
      const x = 40 + i * 340;
      rrect(x, 356, 320, 112, 22, "rgba(16,16,22,.88)", col, 6);
      texte(lab, x + 160, 384, { taille: 22, couleur: "#d7dae4" });
      texte(val, x + 160, 432, { taille: 50, police: "Anton", couleur: col, max: 290 });
    });
  const k = Math.min(1, etat.habitants / cfg.objectif);
  rrect(40, 486, W - 80, 46, 23, "rgba(16,16,22,.88)");
  rrect(44, 490, Math.max(46, (W - 88) * k), 38, 19, VERT);
  texte(`OBJECTIF : ${fmt(etat.habitants)} / ${fmt(cfg.objectif)} HABITANTS`, W / 2, 510, { taille: 22, contour: 6 });
  if (!toastDuMoment(now)) {
    texte(`♥ 1 LIKE = ${cfg.likeEuro} €   ·   ＋ ABONNÉ = 1 HABITANT`, W / 2, 560, { taille: 24, contour: 6, max: W - 60 });
  }
}

function panneaux() {
  const y0 = 590, h = 300;
  rrect(40, y0, 490, h, 22, "rgba(16,16,22,.9)", JAUNE, 5);
  texte("TON CADEAU = TA MAISON", 285, y0 + 32, { taille: 24, couleur: JAUNE, max: 450 });
  const cols = ["#7be08f", "#e3b179", "#ffd75e", "#7fc4ff", "#c79bff", "#ff8a8a"];
  PALIERS.forEach((p, i) => {
    const y = y0 + 78 + i * 38;
    texte(`${p.min}${i ? "+" : ""} pièce${p.min > 1 ? "s" : ""}`, 70, y, { taille: 22, align: "left" });
    texte(p.nom, 505, y, { taille: 22, align: "right", couleur: cols[i], max: 260 });
  });
  rrect(550, y0, 490, h, 22, "rgba(16,16,22,.9)", "#ff5ec8", 5);
  texte("TOP BÂTISSEURS", 795, y0 + 32, { taille: 24, couleur: "#ff7fd4" });
  const top = topBatisseurs(etat, 5);
  if (!top.length) texte("Sois le premier !", 795, y0 + 160, { taille: 26, couleur: "#cfd2dc" });
  top.forEach((t, i) => {
    const y = y0 + 80 + i * 44;
    texte(`${["🥇", "🥈", "🥉", "4.", "5."][i]} ${t.nom}`, 580, y, { taille: 24, align: "left", max: 330 });
    texte(fmt(t.pieces), 1010, y, { taille: 24, align: "right", couleur: JAUNE });
  });
}

// ───────── alertes + petits messages ─────────
const alertes = [];
let alerte = null;
const toasts = [];

function annoncer(a, now) {
  switch (a.kind) {
    case "arrivee":
      marcheur(a.id, a.nom, true);
      alertes.push({ ...a, couleur: VERT, l1: a.nom, l2: "s'abonne", l3: "EMMÉNAGE AU VILLAGE", l4: "+1 HABITANT", son: "arrivee",
        dire: "arrivee" });
      break;
    case "construction":
      if (a.arbre) {
        toasts.push({ t: `🌳 ${a.nom} plante un arbre` });
        construire(a.bat, now, true);
        SONS.pop();
      } else {
        alertes.push({ ...a, couleur: JAUNE, l1: a.nom, l2: `offre ${fmt(a.pieces)} pièces`, l3: a.palier,
          l4: "TON CADEAU = TA MAISON", son: "fanfare", dire: a.monument ? "monument" : "construction" });
      }
      break;
    case "partage":
      toasts.push({ t: `↗ ${a.nom} partage le live` });
      SONS.piece();
      break;
    case "bulle": {
      const m = marcheur(a.id, a.nom, !!etat.pseudos[a.id]?.abonne, true);
      m.bulle = a.texte;
      m.tBulle = now;
      chats.push(now);
      while (chats.length && now - chats[0] > 25) chats.shift();
      if (chats.length >= 6) voix.dire("discute", now);
      break;
    }
    case "passant":
      marcheur(a.id, a.nom, false);
      break;
  }
}

function dessinerAlerte(now) {
  if (!alerte && alertes.length) {
    alerte = { ...alertes.shift(), t0: now };
    SONS[alerte.son]?.();
    if (alerte.dire) voix.dire(alerte.dire, now);
    if (alerte.bat) { construire(alerte.bat, now + 0.4, false); SONS.marteau(); }
    confettis(alerte.couleur);
  }
  if (!alerte) return;
  const t = now - alerte.t0, dur = alertes.length > 2 ? 1.8 : 2.8;
  if (t > dur) { alerte = null; return; }
  const k = t < 0.3 ? back(t / 0.3) : t > dur - 0.25 ? ease((dur - t) / 0.25) : 1;
  ctx.save();
  ctx.translate(W / 2, 742);
  ctx.scale(k, k);
  rrect(-470, -150, 940, 300, 30, "rgba(12,12,18,.96)", alerte.couleur, 8);
  texte(alerte.l1, 0, -96, { taille: 54, police: "Anton", couleur: alerte.couleur, max: 860 });
  texte(alerte.l2, 0, -46, { taille: 28, couleur: "#d7dae4" });
  texte(alerte.l3, 0, 14, { taille: 62, police: "Anton", max: 860 });
  texte(alerte.l4, 0, 90, { taille: 28, couleur: alerte.couleur });
  ctx.restore();
}

// un petit message à la fois, à la place de la ligne des règles
function toastDuMoment(now) {
  while (toasts.length > 4) toasts.shift();
  const t = toasts[0];
  if (!t) return false;
  if (!t.debut) t.debut = now;
  const age = now - t.debut;
  if (age > 1.8) { toasts.shift(); return toastDuMoment(now); }
  const k = age < 0.2 ? back(age / 0.2) : 1;
  ctx.save();
  ctx.translate(W / 2, 560);
  ctx.scale(k, k);
  ctx.font = "800 26px Montserrat";
  const tw = Math.min(ctx.measureText(t.t).width, W - 140);
  rrect(-tw / 2 - 26, -24, tw + 52, 48, 24, JAUNE);
  texte(t.t, 0, 1, { taille: 26, couleur: INK, max: W - 140 });
  ctx.restore();
  return true;
}

const pluie = [];
function confettis(col) {
  for (let i = 0; i < 70; i++) {
    pluie.push({ x: W / 2 + (Math.random() - 0.5) * 300, y: 742, vx: (Math.random() - 0.5) * 900, vy: -300 - Math.random() * 600,
      r: Math.random() * 6.3, c: [col, BLANC, JAUNE, ROUGE, BLEU][i % 5], v: 2 + Math.random() });
  }
}
function dessinerConfettis(dt) {
  for (let i = pluie.length - 1; i >= 0; i--) {
    const q = pluie[i];
    q.x += q.vx * dt; q.y += q.vy * dt; q.vy += 900 * dt; q.vx *= 0.99; q.r += dt * 8; q.v -= dt;
    if (q.v <= 0 || q.y > H) { pluie.splice(i, 1); continue; }
    ctx.save(); ctx.translate(q.x, q.y); ctx.rotate(q.r);
    ctx.fillStyle = q.c; ctx.fillRect(-8, -4, 16, 8);
    ctx.restore();
  }
}

// ───────── boucle ─────────
function fond(n) {
  const ySol = SOL - meta.decor.sol;
  const g = ctx.createLinearGradient(0, 0, 0, ySol + 4);
  g.addColorStop(0, rgb(mix([90, 166, 230], [10, 14, 40], n)));
  g.addColorStop(1, rgb(mix([120, 190, 240], [30, 40, 85], n)));
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  if (n > 0.2) {
    ctx.fillStyle = `rgba(255,255,255,${(n - 0.2) * 0.9})`;
    for (const e of etoiles) ctx.fillRect(e.x, e.y, e.r, e.r);
  }
  const yb = ySol + meta.decor.h;
  ctx.fillStyle = rgb(mix([76, 76, 88], [40, 40, 52], n)); ctx.fillRect(0, yb, W, 150);
  ctx.fillStyle = "#f2f2f2";
  for (let x = -(camera % 120); x < W; x += 120) ctx.fillRect(x, yb + 70, 60, 10);
  ctx.fillStyle = rgb(mix([110, 190, 80], [45, 85, 45], n)); ctx.fillRect(0, yb + 150, W, H);
}

let avant = performance.now() / 1000;
function image() {
  const now = performance.now() / 1000;
  const dt = Math.min(0.1, now - avant);
  avant = now;
  if (etat && meta.decor) {
    const n = nuit(now);
    fond(n);
    dessinerVillage(now, dt, n);
    majMarcheurs(dt, now);
    dessinerMarcheurs(now);
    entete(now);
    compteurs(dt, now);
    panneaux();
    dessinerAlerte(now);
    dessinerConfettis(dt);
    if (now > prochainAppel && now - voix.dernierTout > 15) {
      voix.dire("appel", now);
      prochainAppel = now + 70 + Math.random() * 40;
    }
  }
  requestAnimationFrame(image);
}

function recevoirAnnonces(annonces) {
  const now = performance.now() / 1000;
  for (const a of annonces) annoncer(a, now);
}

function peupler() {
  Object.entries(etat.pseudos).filter(([, p]) => p.abonne).slice(-14)
    .forEach(([id, p]) => { const m = marcheur(id, p.nom, true); m.x = 60 + Math.random() * (W - 120); });
  aff.habitants = etat.habitants; aff.budget = etat.budget; aff.maisons = nbMaisons(etat);
}

async function demarrer() {
  await chargerTout();
  if (DEMO) {
    cfg = await (await fetch("config.json")).json();
    etat = etatInitial(cfg);
    peupler();
    setInterval(() => recevoirAnnonces(appliquer(etat, fauxEvenement())), 850);
  } else {
    brancher();
  }
  try { audio = new AudioContext(); } catch { audio = null; }
  // OBS / LIVE Studio laissent jouer le son tout seul ; sinon, un bouton (hors du live) pour l'activer
  setTimeout(() => { boutonSon.hidden = !!audio && audio.state === "running"; voix.debloquee = !boutonSon.hidden; }, 300);
  requestAnimationFrame(image);
}

function brancher() {
  const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.t === "etat") {
      const premier = !etat;
      etat = m.etat; cfg = m.cfg;
      if (premier) peupler();
    } else if (m.t === "ev") {
      etat = m.etat;
      recevoirAnnonces(m.annonces);
    }
  };
  ws.onclose = () => setTimeout(brancher, 2000);
}

demarrer();
