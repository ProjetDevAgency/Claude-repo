// Mode « Le Quiz du Million » : les spectateurs répondent en écrivant A, B, C ou D dans les commentaires.
//   20 s par question · 10 paliers de 6 questions, chacun sur un thème tiré au sort · les gains montent à chaque palier
//   tout juste = 1 000 000 € (argent fictif) · abonné = +20 % · cadeau = joker, x2 sur le palier, 50/50 pour tout le monde
// Toute la partie tourne dans la page ; le serveur ne fait que transmettre les commentaires, cadeaux et abonnements.

export const LETTRES = ["A", "B", "C", "D"];
export const PALIERS = [1000, 2000, 3000, 5000, 7500, 10000, 15000, 25000, 40000, 60000];  // € par bonne réponse
export const PAR_PALIER = 6;
export const BONUS = [
  { min: 1, texte: "JOKER : 1 ERREUR PARDONNÉE", icone: "cadeau_rose" },
  { min: 30, texte: "x2 SUR TOUT LE PALIER", icone: "cadeau_donut" },
  { min: 100, texte: "50/50 POUR TOUT LE MONDE", icone: "cadeau_confettis" },
];
const COUL = ["#ff9f43", "#b48cff", "#2fd47d", "#ff5c8a"];
const OR = "#ffd76a", INK = "#16161c", BLANC = "#fafafa";
const DUREE = { intro: 10, palier: 7, question: 20, reponse: 6, bilan: 6, classement: 8, fin: 15 };
const ABONNE = 1.2;

// « a », « B », « réponse c », « D ! » → index 0..3 ; sinon null
export function lireReponse(texte) {
  const m = /^\s*(?:r[ée]p(?:onse)?\s*:?\s*)?([abcd])\s*[.!?]*\s*$/i.exec(String(texte || ""));
  return m ? "abcd".indexOf(m[1].toLowerCase()) : null;
}

export function creerQuiz(o) {
  const { ctx, W, img, texte, rrect, fmt, back, ease, SONS, voix, hash, demo } = o;
  let banque = null;
  fetch("questions.json").then((r) => r.json()).then((b) => { banque = b; }).catch(() => {});

  const joueurs = new Map();       // id → { nom, avatar, gains, abonne, joker, x2Palier, x2Utilise, rep, bonnes, erreur, histo }
  const posees = new Set();        // questions déjà posées (on ne repose qu'une fois la banque épuisée)
  const derniersThemes = [];
  let phase = null, t0 = 0, palier = 0, num = 0, theme = null, liste = [], q = null;
  let reponses = new Map();        // id → { i, t }
  let cachees = new Set();         // réponses enlevées par un 50/50
  let moitieEnAttente = null;      // 50/50 offert entre deux questions
  let resultat = null;
  let viteDit = false, dernierTic = -1, themeDit = false;
  const alertes = [];
  let alerte = null;
  let fauxJoueurs = [];

  // ───── joueurs ─────
  function joueur(ev) {
    let j = joueurs.get(ev.id);
    if (!j) {
      j = { nom: ev.nom || "?", avatar: ev.avatar || null, gains: 0, abonne: false, joker: 0, x2Palier: -1, x2Utilise: false,
        rep: 0, bonnes: 0, erreur: false, histo: [] };
      joueurs.set(ev.id, j);
    }
    if (ev.nom) j.nom = ev.nom;
    if (ev.avatar) j.avatar = ev.avatar;
    if (ev.abonne) j.abonne = true;
    return j;
  }

  // ───── déroulé de la partie ─────
  function aller(p, now) { phase = p; t0 = now; }

  function nouvellePartie(now) {
    palier = 0;
    for (const j of joueurs.values()) Object.assign(j, { gains: 0, x2Palier: -1, x2Utilise: false, rep: 0, bonnes: 0, erreur: false, histo: [] });
    aller("intro", now);
    voix.dire("quiz_partie", now);
  }

  function choisirPalier() {
    const cible = palier < 3 ? 1 : palier < 7 ? 2 : 3;
    const libres = (t) => banque.questions.filter((x) => x.t === t && !posees.has(x.id));
    let themes = Object.keys(banque.themes).filter((t) => libres(t).length >= PAR_PALIER);
    if (themes.length < 3) { posees.clear(); themes = Object.keys(banque.themes); }
    const frais = themes.filter((t) => !derniersThemes.includes(t));
    const pool = frais.length ? frais : themes;
    theme = pool[Math.floor(Math.random() * pool.length)];
    derniersThemes.push(theme);
    if (derniersThemes.length > 4) derniersThemes.shift();
    liste = libres(theme)
      .map((x) => ({ x, k: Math.abs(x.d - cible) + Math.random() * 0.9 }))
      .sort((a, b) => a.k - b.k).slice(0, PAR_PALIER).map((e) => e.x)
      .sort((a, b) => a.d - b.d);
    for (const x of liste) posees.add(x.id);
  }

  function nouveauPalier(now) {
    choisirPalier();
    num = 0; themeDit = false;
    for (const j of joueurs.values()) { j.rep = 0; j.bonnes = 0; j.erreur = false; j.histo = []; }
    aller("palier", now);
    voix.dire(palier === PALIERS.length - 1 ? "quiz_million" : "quiz_nouveau", now);
    SONS.fanfare();
  }

  function nouvelleQuestion(now) {
    const brute = liste[num];
    const ordre = [0, 1, 2, 3].sort(() => Math.random() - 0.5);
    q = { id: brute.id, texte: brute.q, choix: ordre.map((i) => brute.r[i]), bonne: ordre.indexOf(0) };
    reponses = new Map();
    cachees = new Set();
    resultat = null;
    viteDit = false; dernierTic = -1;
    aller("question", now);
    voix.dire(`q_${q.id}`, now, { prio: true, attente: 3 });
    if (moitieEnAttente) { moitie(moitieEnAttente, now, true); moitieEnAttente = null; }
    if (demo) fauxRepondants(now, brute.d);
  }

  function reveler(now) {
    const valeur = PALIERS[palier];
    let bons = 0;
    for (const [id, r] of reponses) {
      const j = joueurs.get(id);
      if (!j) continue;
      j.rep += 1;
      if (r.i === q.bonne) {
        bons += 1; j.bonnes += 1; j.histo.push(1);
        const gain = valeur * (j.x2Palier === palier ? 2 : 1) * (j.abonne ? ABONNE : 1);
        j.gains += Math.round(gain);
        r.gain = Math.round(gain);
      } else if (j.joker > 0) {
        j.joker -= 1; j.bonnes += 1; j.histo.push(2);       // le joker efface l'erreur (sans gain)
        r.joker = true;
      } else {
        j.erreur = true; j.histo.push(0);
      }
    }
    resultat = { bons, total: reponses.size };
    aller("reponse", now);
    if (!reponses.size) voix.dire(`quiz_bonne_${"abcd"[q.bonne]}`, now, { prio: true, attente: 3 });
    else if (!bons) voix.dire("quiz_personne", now, { prio: true, attente: 3 });
    else if (bons === reponses.size && bons >= 5) voix.dire("quiz_tous", now, { prio: true, attente: 3 });
    else voix.dire(`quiz_bonne_${"abcd"[q.bonne]}`, now, { prio: true, attente: 3 });
    if (bons) SONS.bonne(); else SONS.buzz();
  }

  function simuler(now) {
    if (!banque) return;
    if (!phase) nouvellePartie(now);
    const t = now - t0;
    if (phase === "intro" && t > DUREE.intro) nouveauPalier(now);
    else if (phase === "palier") {
      if (t > 3.2 && !themeDit) { themeDit = true; voix.dire(`theme_${theme}`, now, { prio: true, attente: 2 }); SONS.revele(); }
      if (t > DUREE.palier) nouvelleQuestion(now);
    } else if (phase === "question") {
      const reste = DUREE.question - t;
      if (reste <= 5 && reste > 0 && Math.ceil(reste) !== dernierTic) { dernierTic = Math.ceil(reste); SONS.tic(); }
      if (reste <= 5.5 && !viteDit) { viteDit = true; if (Math.random() < 0.35) voix.dire("quiz_vite", now); }
      if (t > DUREE.question) reveler(now);
    } else if (phase === "reponse" && t > DUREE.reponse) {
      num += 1;
      if (num < liste.length) nouvelleQuestion(now);
      else { aller("bilan", now); voix.dire("quiz_palier", now); SONS.victoire(); }
    } else if (phase === "bilan" && t > DUREE.bilan) aller("classement", now);
    else if (phase === "classement" && t > DUREE.classement) {
      palier += 1;
      if (palier < PALIERS.length) nouveauPalier(now);
      else { aller("fin", now); voix.dire("quiz_fin", now); SONS.victoire(); }
    } else if (phase === "fin" && t > DUREE.fin) nouvellePartie(now);
    if (demo) for (const f of fauxJoueurs) if (f.quand <= now && !f.fait) { f.fait = true; evenement(f.ev, now); }
  }

  // ───── bonus des cadeaux ─────
  function moitie(nom, now, silencieux) {
    if (phase !== "question" || cachees.size) { moitieEnAttente = nom; return; }
    const faux = [0, 1, 2, 3].filter((i) => i !== q.bonne).sort(() => Math.random() - 0.5).slice(0, 2);
    for (const i of faux) cachees.add(i);
    cachees.par = nom;
    if (!silencieux) SONS.speciale?.();
  }

  // ───── événements du live ─────
  function evenement(ev, now) {
    switch (ev.type) {
      case "chat": {
        const i = lireReponse(ev.texte);
        if (i === null) { if (ev.abonne && joueurs.has(ev.id)) joueurs.get(ev.id).abonne = true; return; }
        if (phase !== "question" || reponses.has(ev.id) || cachees.has(i)) return;
        joueur(ev);
        reponses.set(ev.id, { i, t: now - t0 });
        SONS.pop();
        return;
      }
      case "follow": {
        const j = joueur({ ...ev, abonne: true });
        alertes.push({ couleur: OR, l1: `⭐ ${j.nom}`, l2: "S'ABONNE : +20 % SUR SES GAINS", voix: "quiz_abonne", abonne: true });
        return;
      }
      case "gift": {
        const j = joueur(ev);
        const p = ev.pieces || 1;
        let l2, dire;
        if (p >= 100) {
          moitie(j.nom, now);
          j.joker += 1;
          l2 = "50/50 POUR TOUT LE MONDE + 1 JOKER"; dire = "quiz_moitie";
        } else if (p >= 30 && !j.x2Utilise) {
          j.x2Utilise = true; j.x2Palier = palier;
          l2 = "x2 SUR TOUT LE PALIER !"; dire = "quiz_x2";
        } else {
          j.joker += p >= 30 ? 2 : 1;
          l2 = p >= 30 ? "2 JOKERS : 2 ERREURS PARDONNÉES" : "JOKER : 1 ERREUR PARDONNÉE"; dire = "quiz_joker";
        }
        alertes.push({ couleur: "#7fd3ff", l1: j.nom, l2, voix: dire, image: ev.image,
          icone: BONUS.findLast((b) => p >= b.min)?.icone, cadeau: ev.cadeau, pieces: p });
        return;
      }
    }
  }

  // ───── démo (aperçu sans live) ─────
  const PRENOMS = ["Laura", "Mehdi", "Sonia83", "Kev", "Inès", "Lucas_", "Yanis", "Nadia", "Tom", "Jade", "Rayan", "Chloé", "Bilal",
    "Léa", "Samir", "Emma", "Nour", "Hugo", "Lina", "Adam", "Zoé", "Karim", "Manon", "Ilyes", "Sarah", "Théo", "Maëlys", "Nassim"];
  function fauxRepondants(now, d) {
    fauxJoueurs = [];
    const n = 14 + Math.floor(Math.random() * 14);
    for (let k = 0; k < n; k++) {
      const nom = PRENOMS[(k * 5 + palier * 3) % PRENOMS.length];
      const juste = Math.random() < 0.85 - d * 0.15;
      const i = juste ? q.bonne : [0, 1, 2, 3].filter((x) => x !== q.bonne)[Math.floor(Math.random() * 3)];
      fauxJoueurs.push({ quand: now + 2 + Math.random() * 16, ev: { type: "chat", id: nom.toLowerCase(), nom, texte: "abcd"[i],
        abonne: hash(nom) % 4 === 0 } });
    }
  }

  // ───── dessin ─────
  const avatars = new Map();
  function avatarImg(url) {
    if (!url) return null;
    let i = avatars.get(url);
    if (!i) {
      i = new Image();
      i.referrerPolicy = "no-referrer";
      i.src = url;
      avatars.set(url, i);
      if (avatars.size > 500) avatars.delete(avatars.keys().next().value);
    }
    return i.complete && i.naturalWidth ? i : null;
  }
  function rond(j, x, y, r, bord = BLANC) {
    const im = avatarImg(j.avatar);
    ctx.save();
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
    if (im) { ctx.clip(); ctx.drawImage(im, x - r, y - r, 2 * r, 2 * r); }
    else {
      ctx.fillStyle = `hsl(${hash(j.nom) % 360} 55% 42%)`; ctx.fill();
      texte((Array.from(j.nom.trim())[0] || "?").toUpperCase(), x, y + 2, { taille: Math.round(r * 1.05), police: "Anton" });
    }
    ctx.restore();
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.lineWidth = 3; ctx.strokeStyle = bord; ctx.stroke();
  }

  function lignes(t, max, taille) {
    ctx.font = `800 ${taille}px Montserrat`;
    const mots = t.split(" "), out = [];
    let l = "";
    for (const m of mots) {
      const essai = l ? `${l} ${m}` : m;
      if (ctx.measureText(essai).width > max && l) { out.push(l); l = m; } else l = essai;
    }
    if (l) out.push(l);
    return out;
  }

  function classement() {
    return [...joueurs.values()].filter((j) => j.gains > 0).sort((a, b) => b.gains - a.gains);
  }

  function bandeau(now) {
    const valeur = PALIERS[palier];
    rrect(40, 224, W - 80, 66, 33, "rgba(14,16,30,.92)", "rgba(127,211,255,.45)", 3);
    texte(`PALIER ${palier + 1}/${PALIERS.length}`, 72, 258, { taille: 26, align: "left", couleur: "#7fd3ff" });
    texte(banque && theme ? banque.themes[theme] : "", W / 2 - 30, 258, { taille: 22, couleur: "#d7dae4", max: 330 });
    texte(`${fmt(valeur)} €`, W - 72, 258, { taille: 30, align: "right", couleur: OR, police: "Anton" });
    // les 6 questions du palier
    const n = liste.length || PAR_PALIER, l = (W - 80 - (n - 1) * 10) / n;
    for (let k = 0; k < n; k++) {
      const fait = k < num || (k === num && phase === "reponse");
      const c = fait ? "#7fd3ff" : k === num && phase === "question" ? OR : "rgba(255,255,255,.14)";
      rrect(40 + k * (l + 10), 300, l, 10, 5, c);
    }
  }

  function cartes(now) {
    const y0 = 326, h = 150, ecart = 14;
    const t = now - t0;
    for (let i = 0; i < 4; i++) {
      const y = y0 + i * (h + ecart);
      const revele = phase === "reponse";
      const juste = revele && i === q.bonne;
      const eteint = (revele && !juste) || cachees.has(i);
      const entree = phase === "question" ? back((t - i * 0.08) / 0.35) : 1;
      if (entree <= 0.01) continue;
      ctx.save();
      ctx.globalAlpha = cachees.has(i) ? 0.18 : eteint ? 0.38 : 1;
      ctx.translate(W / 2, y + h / 2); ctx.scale(entree, entree); ctx.translate(-W / 2, -(y + h / 2));
      if (juste) {
        const p = 0.6 + 0.4 * Math.sin(now * 8);
        ctx.shadowColor = "#2fd47d"; ctx.shadowBlur = 30 * p;
      }
      rrect(40, y, W - 80, h, 26, juste ? "rgba(20,70,45,.96)" : "rgba(18,18,32,.94)", juste ? "#2fd47d" : COUL[i], juste ? 8 : 4);
      ctx.shadowBlur = 0;
      rrect(W - 136, y + 22, 76, 76, 18, "rgba(0,0,0,.35)", COUL[i], 4);
      texte(LETTRES[i], W - 98, y + 62, { taille: 54, police: "Anton", couleur: COUL[i] });
      texte(q.choix[i], W - 160, y + 58, { taille: 50, police: "Anton", align: "right", couleur: juste ? BLANC : COUL[i], max: 640 });
      if (cachees.has(i)) { ctx.fillStyle = BLANC; ctx.fillRect(60, y + h / 2 - 3, W - 220, 6); }
      // qui a répondu quoi : les photos des joueurs dans la case
      const ici = [...reponses.entries()].filter(([, r]) => r.i === i);
      const place = 11;
      ici.slice(0, place).forEach(([id], k) => { const j = joueurs.get(id); if (j) rond(j, 82 + k * 50, y + h - 40, 26, COUL[i]); });
      if (ici.length > place) {
        rrect(82 + place * 50 - 20, y + h - 60, 74, 40, 20, COUL[i]);
        texte(`+${ici.length - place}`, 82 + place * 50 + 17, y + h - 40, { taille: 22, couleur: INK });
      }
      if (ici.length) texte(`${ici.length} joueur${ici.length > 1 ? "s" : ""}`, W - 98, y + 122, { taille: 18, couleur: "#cfd2dc", max: 120 });
      if (juste) texte("✓ BONNE RÉPONSE", 64, y + 34, { taille: 24, align: "left", couleur: "#7dffb0" });
      ctx.restore();
    }
  }

  function boiteQuestion(now) {
    const y = 990, h = 224;
    rrect(40, y, W - 80, h, 30, "rgba(14,16,30,.96)", "rgba(127,211,255,.6)", 4);
    const ls = lignes(q.texte, 730, 44).slice(0, 3);
    const taille = ls.length > 2 ? 40 : 46;
    ls.forEach((l, k) => texte(l, 440, y + h / 2 + (k - (ls.length - 1) / 2) * (taille + 10), { taille, couleur: OR, max: 760 }));
    // chrono
    const cx = W - 130, cy = y + h / 2, r = 66;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fillStyle = "rgba(0,0,0,.45)"; ctx.fill();
    ctx.lineWidth = 10; ctx.strokeStyle = "rgba(255,255,255,.12)"; ctx.stroke();
    if (phase === "question") {
      const reste = Math.max(0, DUREE.question - (now - t0));
      ctx.beginPath(); ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * (reste / DUREE.question));
      ctx.strokeStyle = reste <= 5 ? "#ff5c5c" : "#7fd3ff"; ctx.lineWidth = 10; ctx.lineCap = "round"; ctx.stroke(); ctx.lineCap = "butt";
      const k = reste <= 5 ? 1 + 0.12 * Math.max(0, Math.sin((reste % 1) * Math.PI)) : 1;
      ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k);
      texte(String(Math.ceil(reste)), 0, 2, { taille: 60, police: "Anton", couleur: reste <= 5 ? "#ff7070" : BLANC });
      ctx.restore();
    } else if (resultat) {
      texte(`${resultat.bons}`, cx, cy - 14, { taille: 50, police: "Anton", couleur: "#7dffb0" });
      texte(`/${resultat.total}`, cx, cy + 32, { taille: 24, couleur: "#cfd2dc" });
    }
  }

  function basDePage(now) {
    const y = 1232;
    // la règle, toujours visible
    const p = 1 + Math.sin(now * 3) * 0.02;
    ctx.save(); ctx.translate(W / 2, y + 30); ctx.scale(p, p);
    rrect(-500, -30, 1000, 60, 30, OR);
    texte("ÉCRIS  A, B, C OU D  EN COMMENTAIRE · TA 1ʳᵉ RÉPONSE COMPTE", 0, 1, { taille: 25, couleur: INK, max: 960 });
    ctx.restore();
    // cadeaux (gauche) et top 5 (droite)
    const y2 = y + 76;
    rrect(40, y2, 470, 250, 24, "rgba(14,16,30,.9)", "#7fd3ff", 3);
    texte("TON CADEAU =", 275, y2 + 30, { taille: 22, couleur: "#7fd3ff" });
    BONUS.forEach((b, k) => {
      const yy = y2 + 76 + k * 52;
      if (img[b.icone]) ctx.drawImage(img[b.icone], 58, yy - 20, 40, 40);
      texte(`${b.min}+`, 106, yy, { taille: 20, align: "left", couleur: "#cfd2dc" });
      texte(b.texte, 492, yy, { taille: 19, align: "right", max: 330 });
    });
    texte("⭐ ABONNÉ = +20 % SUR TES GAINS", 275, y2 + 228, { taille: 20, couleur: OR, max: 430 });
    rrect(530, y2, 510, 250, 24, "rgba(14,16,30,.9)", OR, 3);
    texte("TOP 5 · GAINS", 785, y2 + 30, { taille: 22, couleur: OR });
    const top = classement().slice(0, 5);
    if (!top.length) texte("Réponds pour entrer !", 785, y2 + 130, { taille: 24, couleur: "#cfd2dc" });
    top.forEach((j, k) => {
      const yy = y2 + 72 + k * 38;
      texte(`${k + 1}`, 556, yy, { taille: 22, align: "left", couleur: OR, police: "Anton" });
      rond(j, 600, yy, 16, k ? "#cfd2dc" : OR);
      texte(`${j.abonne ? "⭐ " : ""}${j.nom}`, 626, yy, { taille: 21, align: "left", max: 230 });
      texte(`${fmt(j.gains)} €`, 1018, yy, { taille: 22, align: "right", couleur: "#7dffb0" });
    });
  }

  function panneau(h = 860) {
    const y = 330;
    rrect(40, y, W - 80, h, 36, "rgba(12,14,28,.96)", "rgba(127,211,255,.55)", 4);
    return y;
  }

  function ecranIntro(now) {
    const y = panneau(), t = now - t0;
    texte("LE QUIZ", W / 2, y + 90, { taille: 96, police: "Anton", couleur: BLANC, contour: 10 });
    texte("DU MILLION", W / 2, y + 190, { taille: 110, police: "Anton", couleur: OR, contour: 10 });
    const regles = [
      ["✍️", "Écris A, B, C ou D en commentaire"],
      ["⏱️", "20 secondes · ta 1ʳᵉ réponse compte"],
      ["🪜", "10 paliers de 6 questions : les gains montent"],
      ["💰", "Tout juste = 1 000 000 €"],
      ["⭐", "Abonné : +20 % sur tes gains"],
      ["🎁", "Cadeau : joker, x2 ou 50/50"],
    ];
    regles.forEach(([ic, l], k) => {
      const a = ease((t - 0.4 - k * 0.25) / 0.3);
      ctx.globalAlpha = a;
      texte(`${ic}  ${l}`, 110, y + 310 + k * 72, { taille: 34, align: "left", max: 860 });
      ctx.globalAlpha = 1;
    });
    texte("argent fictif, pour le jeu", W / 2, y + 770, { taille: 20, couleur: "#9aa0b4" });
    const r = Math.ceil(DUREE.intro - t);
    texte(`Première question dans ${Math.max(0, r)} s`, W / 2, y + 822, { taille: 30, couleur: "#7fd3ff" });
  }

  function ecranPalier(now) {
    const y = panneau(), t = now - t0;
    texte(palier === PALIERS.length - 1 ? "LE PALIER DU MILLION" : "NOUVEAU PALIER", W / 2, y + 70, { taille: 32, couleur: "#7fd3ff" });
    const k = back(t / 0.5);
    ctx.save(); ctx.translate(W / 2, y + 160); ctx.scale(k, k);
    texte(`PALIER ${palier + 1}`, 0, 0, { taille: 120, police: "Anton", couleur: OR, contour: 10 });
    ctx.restore();
    texte(`${fmt(PALIERS[palier])} € PAR BONNE RÉPONSE`, W / 2, y + 262, { taille: 36, couleur: BLANC });
    // tirage au sort du thème
    rrect(110, y + 310, W - 220, 150, 28, "rgba(255,255,255,.06)", "rgba(127,211,255,.5)", 3);
    texte("THÈME DU PALIER", W / 2, y + 345, { taille: 22, couleur: "#7fd3ff" });
    const noms = Object.values(banque.themes);
    let nom = banque.themes[theme];
    if (t < 3.2) {
      const vitesse = 18 * (1 - t / 3.4) + 2;
      nom = noms[Math.floor(t * vitesse * 3) % noms.length];
      if (Math.floor(t * vitesse * 3) !== ecranPalier.dernier) { ecranPalier.dernier = Math.floor(t * vitesse * 3); SONS.tic?.(true); }
    }
    texte(nom, W / 2, y + 412, { taille: 52, police: "Anton", couleur: t < 3.2 ? "#cfd2dc" : OR, max: W - 280 });
    // l'échelle des gains
    PALIERS.forEach((v, i) => {
      const yy = y + 820 - i * 34;
      const ici = i === palier;
      if (ici) rrect(300, yy - 16, W - 600, 32, 16, OR);
      texte(`${i + 1}`, 330, yy, { taille: 22, align: "left", couleur: ici ? INK : i < palier ? "#7dffb0" : "#9aa0b4" });
      texte(`${fmt(v)} €`, W - 330, yy, { taille: 22, align: "right", couleur: ici ? INK : i < palier ? "#7dffb0" : "#cfd2dc" });
    });
  }

  function ecranBilan(now) {
    const y = panneau(), t = now - t0;
    const k = back(t / 0.4);
    ctx.save(); ctx.translate(W / 2, y + 110); ctx.scale(k, k);
    texte("BRAVO !", 0, 0, { taille: 110, police: "Anton", couleur: BLANC, contour: 10 });
    ctx.restore();
    texte(`PALIER ${palier + 1} VALIDÉ`, W / 2, y + 205, { taille: 40, couleur: "#7dffb0" });
    const sf = [...joueurs.values()].filter((j) => j.rep >= liste.length && !j.erreur && j.bonnes >= liste.length);
    texte(sf.length ? `LES SANS-FAUTE (${sf.length})` : "Aucun sans-faute sur ce palier…", W / 2, y + 280, { taille: 30, couleur: OR });
    sf.slice(0, 24).forEach((j, i) => {
      const c = i % 3, l = Math.floor(i / 3);
      const x = 75 + c * 315, yy = y + 330 + l * 62;
      ctx.globalAlpha = ease((t - 0.5 - i * 0.05) / 0.25);
      rrect(x, yy, 300, 50, 25, "rgba(47,212,125,.22)", "#2fd47d", 3);
      rond(j, x + 26, yy + 25, 19, "#2fd47d");
      texte(j.nom, x + 170, yy + 25, { taille: 22, max: 230 });
      ctx.globalAlpha = 1;
    });
    if (sf.length > 24) texte(`et ${sf.length - 24} autres !`, W / 2, y + 840, { taille: 26, couleur: "#cfd2dc" });
  }

  function ecranClassement(now) {
    const y = panneau(), t = now - t0;
    texte("CLASSEMENT GÉNÉRAL", W / 2, y + 70, { taille: 56, police: "Anton", couleur: BLANC });
    texte(`après le palier ${palier + 1}/${PALIERS.length}`, W / 2, y + 120, { taille: 24, couleur: "#7fd3ff" });
    const top = classement().slice(0, 10);
    if (!top.length) texte("Personne n'a encore marqué… À toi de jouer !", W / 2, y + 400, { taille: 30, couleur: "#cfd2dc", max: 900 });
    top.forEach((j, i) => {
      const yy = y + 170 + i * 66;
      ctx.globalAlpha = ease((t - 0.2 - i * 0.08) / 0.25);
      rrect(70, yy, W - 140, 56, 28, i < 3 ? "rgba(255,215,106,.16)" : "rgba(255,255,255,.06)", i < 3 ? OR : "rgba(255,255,255,.15)", 2);
      texte(`#${i + 1}`, 100, yy + 28, { taille: 26, align: "left", police: "Anton", couleur: i < 3 ? OR : "#cfd2dc" });
      rond(j, 190, yy + 28, 22, i < 3 ? OR : "#cfd2dc");
      texte(`${j.abonne ? "⭐ " : ""}${j.nom}`, 226, yy + 28, { taille: 26, align: "left", max: 340 });
      j.histo.slice(-PAR_PALIER).forEach((h, k) => {
        const cx = 610 + k * 34;
        ctx.beginPath(); ctx.arc(cx, yy + 28, 13, 0, Math.PI * 2);
        ctx.fillStyle = h === 1 ? "#2fd47d" : h === 2 ? "#7fd3ff" : "#ff5c5c"; ctx.fill();
      });
      texte(`${fmt(j.gains)} €`, W - 100, yy + 28, { taille: 28, align: "right", police: "Anton", couleur: "#7dffb0" });
      ctx.globalAlpha = 1;
    });
  }

  function ecranFin(now) {
    const y = panneau(), t = now - t0;
    texte("FIN DE LA PARTIE", W / 2, y + 80, { taille: 70, police: "Anton", couleur: BLANC, contour: 8 });
    const top = classement().slice(0, 3);
    const places = [[W / 2, 330, 1], [W / 2 - 300, 400, 2], [W / 2 + 300, 430, 3]];
    top.forEach((j, i) => {
      const [x, h, rang] = places[i];
      const k = back((t - 0.6 - (2 - i) * 0.5) / 0.5);
      if (k <= 0.01) return;
      ctx.save(); ctx.translate(x, y + h); ctx.scale(k, k);
      rond(j, 0, 0, i ? 62 : 84, i ? "#cfd2dc" : OR);
      texte(["🥇", "🥈", "🥉"][i], 0, -(i ? 92 : 116), { taille: 54 });
      texte(j.nom, 0, (i ? 92 : 118), { taille: 30, max: 280 });
      texte(`${fmt(j.gains)} €`, 0, (i ? 136 : 164), { taille: 34, police: "Anton", couleur: "#7dffb0" });
      if (j.gains >= 1000000) texte("MILLIONNAIRE !", 0, (i ? 178 : 210), { taille: 28, couleur: OR });
      ctx.restore();
      void rang;
    });
    if (!top.length) texte("Personne n'a marqué… La prochaine sera la bonne !", W / 2, y + 420, { taille: 30, couleur: "#cfd2dc", max: 900 });
    const r = Math.ceil(DUREE.fin - t);
    texte(`Nouvelle partie dans ${Math.max(0, r)} s`, W / 2, y + 810, { taille: 30, couleur: "#7fd3ff" });
  }

  function dessinerAlerte(now) {
    if (!alerte && alertes.length) {
      alerte = { ...alertes.shift(), t0: now };
      if (alerte.voix) voix.dire(alerte.voix, now);
      if (alerte.abonne) SONS.victoire(); else SONS.fanfare();
      if (alerte.image) { alerte.img = new Image(); alerte.img.src = alerte.image; }
    }
    while (alertes.filter((x) => !x.abonne).length > 5) alertes.splice(alertes.findIndex((x) => !x.abonne), 1);
    if (!alerte) return;
    const t = now - alerte.t0, dur = alertes.length > 2 ? 1.6 : 2.8;
    if (t > dur) { alerte = null; return; }
    const k = t < 0.3 ? back(t / 0.3) : t > dur - 0.25 ? ease((dur - t) / 0.25) : 1;
    ctx.save();
    ctx.translate(W / 2, 1434);
    ctx.scale(k, k);
    rrect(-500, -128, 1000, 256, 30, "rgba(10,10,18,.97)", alerte.couleur, 8);
    const ic = alerte.img?.complete && alerte.img.naturalWidth ? alerte.img : img[alerte.icone];
    const large = ic ? 640 : 900;
    texte(alerte.l1, 0, -52, { taille: 54, police: "Anton", couleur: alerte.couleur, max: large });
    if (alerte.pieces) texte(`${alerte.cadeau && alerte.cadeau !== "cadeau" ? alerte.cadeau + " · " : ""}${fmt(alerte.pieces)} pièce${alerte.pieces > 1 ? "s" : ""}`, 0, 0, { taille: 24, couleur: "#cfd2dc", max: large });
    texte(alerte.l2, 0, 56, { taille: 36, police: "Anton", max: large });
    if (ic) for (const sx of [-1, 1]) ctx.drawImage(ic, sx * 400 - 55, -55, 110, 110);
    ctx.restore();
  }

  return {
    evenement,
    calme: () => phase === "reponse" || phase === "classement" || phase === "bilan",
    dessiner(now) {
      simuler(now);
      if (!banque || !phase) return;
      if (phase === "intro") ecranIntro(now);
      else if (phase === "palier") { bandeau(now); ecranPalier(now); }
      else if (phase === "bilan") { bandeau(now); ecranBilan(now); }
      else if (phase === "classement") { bandeau(now); ecranClassement(now); }
      else if (phase === "fin") ecranFin(now);
      else { bandeau(now); cartes(now); boiteQuestion(now); }
      basDePage(now);
      dessinerAlerte(now);
    },
  };
}
