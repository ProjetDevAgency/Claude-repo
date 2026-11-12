// Mode « Villageois vs Zombies » : deux équipes de spectateurs s'affrontent en direct.
//   commentaire 1 = villageois, 2 = zombies · cadeau = renforts dans ton équipe · like = répare ton camp
//   abonnement = un combattant offert · manches de 4 minutes · combattants automatiques si peu de monde.
// Toute la bataille tourne dans la page ; le serveur ne fait que transmettre les événements du live.

export const RENFORTS = [
  { min: 1, texte: "1 COMBATTANT", icone: "cadeau_rose" },
  { min: 5, texte: "3 COMBATTANTS", icone: "cadeau_coeur" },
  { min: 30, texte: "1 CHAMPION", icone: "cadeau_donut" },
  { min: 100, texte: "5 + 1 CHAMPION", icone: "cadeau_confettis" },
  { min: 500, texte: "1 GÉANT", icone: "cadeau_billets" },
  { min: 2000, texte: "ATTAQUE SPÉCIALE", icone: "cadeau_baleine" },
];

const TYPES = {
  bot: { pv: 22, deg: 5, vit: 48, ech: 0.24 },
  soldat: { pv: 34, deg: 7, vit: 56, ech: 0.28 },
  champion: { pv: 140, deg: 16, vit: 50, ech: 0.4 },
  geant: { pv: 520, deg: 36, vit: 34, ech: 0.62 },
};
const CAMP_PV = 1500;
const DUREE_MANCHE = 240;
const SOL = 1200;              // pied des combattants
const X_V = 110, X_Z = 970;    // camps : villageois à gauche, zombies à droite
const COUL = { v: "#3ccf6e", z: "#b56cff" };
const NOM = { v: "VILLAGEOIS", z: "ZOMBIES" };

export function creerBataille(o) {
  const { ctx, W, img, meta, sprite, texte, rrect, fmt, back, ease, SONS, voix, hash } = o;
  const joueurs = new Map();   // id → { equipe, nom, pieces, degats, unite, finRespawn }
  let unites = [];
  const effets = [];           // particules, éclairs, chiffres
  const alertes = [];
  let alerte = null;
  const fileBulles = [];
  let bulle = null;
  const score = { v: 0, z: 0 };
  let camp, manche = 0, phase = "debut", tPhase = 0, debutManche = 0, finManche = 0, gagnant = null, mvp = null;
  let prochainBot = { v: 0, z: 0 };
  let n = 0;

  function nouvelleManche(now) {
    manche += 1;
    camp = { v: CAMP_PV, z: CAMP_PV };
    unites = [];
    for (const j of joueurs.values()) { j.unite = null; j.degats = 0; j.piecesManche = 0; }
    phase = "debut"; tPhase = now; debutManche = now + 3; finManche = debutManche + DUREE_MANCHE;
    gagnant = null; mvp = null;
    voix.dire("bataille_debut", now);
  }

  function equipeAuto() {
    let nv = 0, nz = 0;
    for (const j of joueurs.values()) j.equipe === "v" ? nv++ : nz++;
    return nv <= nz ? "v" : "z";
  }

  function joueur(id, nom, equipe) {
    let j = joueurs.get(id);
    if (!j) { j = { equipe: equipe || equipeAuto(), nom, pieces: 0, piecesManche: 0, degats: 0, unite: null, finRespawn: 0 }; joueurs.set(id, j); }
    if (nom) j.nom = nom;
    if (equipe) j.equipe = equipe;
    return j;
  }

  function lancer(equipe, type, nom = "", id = null, now = 0) {
    const t = TYPES[type];
    const look = equipe === "v" ? `perso_${String(hash(id || String(n)) % 16).padStart(2, "0")}`
      : `zombie_${String(hash(id || String(n)) % 8).padStart(2, "0")}`;
    const u = { id: ++n, equipe, type, nom, joueur: id, look, x: equipe === "v" ? X_V + 60 : X_Z - 60,
      dy: (n * 37) % 40 - 20, pv: t.pv, pvMax: t.pv, deg: t.deg, vit: t.vit * (0.9 + (n % 5) * 0.05), ech: t.ech,
      ne: now, ph: (n * 1.7) % 6, coup: 0 };
    unites.push(u);
    return u;
  }

  // ───── événements du live ─────
  function evenement(ev, now) {
    if (phase === "fin" && ev.type !== "chat" && ev.type !== "like") { /* on garde quand même les cadeaux pour la manche suivante */ }
    switch (ev.type) {
      case "chat": {
        const t = String(ev.texte || "").trim().toLowerCase();
        const choix = /^(1|villageois?)$/.test(t) ? "v" : /^(2|zombies?)$/.test(t) ? "z" : null;
        if (choix) {
          const deja = joueurs.get(ev.id);
          const j = joueur(ev.id, ev.nom, choix);
          if (!deja || deja.equipe !== choix || !j.unite || j.unite.pv <= 0) {
            if (j.unite && j.unite.pv > 0) j.unite.pv = 0;
            if (phase === "combat") j.unite = lancer(choix, "soldat", j.nom, ev.id, now);
            if (!deja) annoncePetite(`${j.nom} rejoint les ${NOM[choix].toLowerCase()}`, COUL[choix]);
            SONS.pop();
          }
        } else {
          const j = joueurs.get(ev.id);
          if (j && (!j.unite || j.unite.pv <= 0) && now > j.finRespawn && phase === "combat") {
            j.unite = lancer(j.equipe, "soldat", j.nom, ev.id, now);   // un commentaire fait revenir ton combattant
            j.finRespawn = now + 8;
          }
          fileBulles.push({ id: ev.id, nom: ev.nom, texte: String(ev.texte || "").slice(0, 50) });
          if (fileBulles.length > 6) fileBulles.shift();
        }
        break;
      }
      case "gift": {
        const j = joueur(ev.id, ev.nom);
        j.pieces += ev.pieces; j.piecesManche += ev.pieces;
        const p = ev.pieces;
        const e = j.equipe;
        const quoi = p >= 2000 ? "speciale" : p >= 500 ? "geant" : p >= 100 ? "gros" : p >= 30 ? "champion" : p >= 5 ? "trois" : "un";
        const faire = () => {
          if (quoi === "un") lancer(e, "soldat", j.nom, ev.id, now);
          if (quoi === "trois") for (let i = 0; i < 3; i++) lancer(e, "soldat", j.nom, ev.id, now);
          if (quoi === "champion") lancer(e, "champion", j.nom, ev.id, now);
          if (quoi === "gros") { for (let i = 0; i < 5; i++) lancer(e, "soldat", j.nom, ev.id, now); lancer(e, "champion", j.nom, ev.id, now); }
          if (quoi === "geant") lancer(e, "geant", j.nom, ev.id, now);
          if (quoi === "speciale") { attaqueSpeciale(e, now); lancer(e, "geant", j.nom, ev.id, now); }
        };
        if (phase === "combat") faire();
        if (p >= 30) {
          alertes.push({ couleur: COUL[e], l1: j.nom, l2: `${ev.cadeau && ev.cadeau !== "cadeau" ? ev.cadeau + " · " : ""}${fmt(p)} pièces`,
            l3: { speciale: "ATTAQUE SPÉCIALE !", geant: "UN GÉANT !", gros: "UNE ARMÉE !", champion: "UN CHAMPION !" }[quoi],
            l4: `RENFORTS POUR LES ${NOM[e]}`, icone: RENFORTS.findLast((r) => p >= r.min)?.icone,
            image: ev.image, voix: quoi === "speciale" ? "bataille_speciale" : quoi === "geant" ? "bataille_geant" : "bataille_renforts" });
        } else {
          annoncePetite(`${ev.cadeau && ev.cadeau !== "cadeau" ? "🎁 " : ""}${j.nom} : +${quoi === "trois" ? 3 : 1} ${e === "v" ? "villageois" : "zombie"}${quoi === "trois" ? "s" : ""}`, COUL[e]);
          voix.dire("bataille_renforts", now);
        }
        break;
      }
      case "like": {
        const j = joueurs.get(ev.id);
        if (j && camp && phase === "combat") camp[j.equipe] = Math.min(CAMP_PV, camp[j.equipe] + (ev.n || 1));
        break;
      }
      case "follow": {
        const j = joueur(ev.id, ev.nom);
        if (phase === "combat") lancer(j.equipe, "soldat", j.nom, ev.id, now);
        alertes.push({ couleur: "#3ccf6e", l1: ev.nom, l2: "s'abonne", l3: "+1 COMBATTANT", l4: `CHEZ LES ${NOM[j.equipe]}`, voix: "arrivee" });
        break;
      }
      case "share":
        annoncePetite(`↗ ${ev.nom} partage le live`, "#ffce00");
        break;
    }
  }

  function attaqueSpeciale(e, now) {
    const ennemi = e === "v" ? "z" : "v";
    for (const u of unites) if (u.equipe === ennemi) { u.pv -= 220; touche(u.x, SOL - 60, "#ffd75e"); }
    camp[ennemi] = Math.max(0, camp[ennemi] - 180);
    effets.push({ kind: "eclair", t0: now, couleur: COUL[e] });
    SONS.fanfare();
  }

  const petites = [];
  function annoncePetite(t, c) { petites.push({ t, c }); if (petites.length > 4) petites.shift(); }

  function touche(x, y, c = "#ffffff") {
    for (let i = 0; i < 6; i++) effets.push({ kind: "p", x, y, vx: (Math.random() - 0.5) * 200, vy: -80 - Math.random() * 120, v: 0.6, c });
  }

  // ───── simulation ─────
  function simuler(now, dt) {
    if (phase === "debut" && now >= debutManche) phase = "combat";
    if (phase === "fin") { if (now - tPhase > 12) nouvelleManche(now); return; }
    if (phase !== "combat") return;

    // combattants automatiques : jamais moins de 3 par équipe
    for (const e of ["v", "z"]) {
      const vivants = unites.filter((u) => u.equipe === e && u.pv > 0).length;
      if (vivants < 4 && now > prochainBot[e]) { lancer(e, "bot", "", null, now); prochainBot[e] = now + 2.5; }
    }
    for (const u of unites) {
      if (u.pv <= 0) continue;
      const sens = u.equipe === "v" ? 1 : -1;
      const portee = 30 + u.ech * 80;
      // l'ennemi le plus proche devant
      let cible = null, dmin = 1e9;
      for (const w of unites) {
        if (w.equipe === u.equipe || w.pv <= 0) continue;
        const d = (w.x - u.x) * sens;
        if (d > -10 && d < dmin) { dmin = d; cible = w; }
      }
      const xCamp = u.equipe === "v" ? X_Z - 70 : X_V + 70;
      const dCamp = (xCamp - u.x) * sens;
      if (cible && dmin < portee) {
        cible.pv -= u.deg * dt;
        u.coup += dt;
        if (u.coup > 0.5) { u.coup = 0; touche(cible.x, SOL - 70 * cible.ech / 0.2, u.equipe === "v" ? "#ffe08a" : "#9dff8a"); }
        const j = u.joueur && joueurs.get(u.joueur); if (j) j.degats += u.deg * dt;
      } else if (dCamp <= 0) {
        const ennemi = u.equipe === "v" ? "z" : "v";
        camp[ennemi] = Math.max(0, camp[ennemi] - u.deg * dt);
        u.coup += dt;
        if (u.coup > 0.5) { u.coup = 0; touche(xCamp + sens * 40, SOL - 120, "#cccccc"); }
        const j = u.joueur && joueurs.get(u.joueur); if (j) j.degats += u.deg * dt;
      } else {
        u.x += sens * u.vit * dt;
      }
    }
    for (const u of unites) if (u.pv <= 0 && !u.mort) { u.mort = now; touche(u.x, SOL - 50, "#888"); }
    unites = unites.filter((u) => !u.mort || now - u.mort < 0.6);
    if (unites.length > 90) unites = unites.slice(-90);

    // alerte « camp en danger »
    for (const e of ["v", "z"]) if (camp[e] < CAMP_PV * 0.25) voix.dire("bataille_danger", now);

    if (camp.v <= 0 || camp.z <= 0 || now >= finManche) finir(now);
  }

  function finir(now) {
    gagnant = camp.v === camp.z ? (Math.random() < 0.5 ? "v" : "z") : camp.v > camp.z ? "v" : "z";
    score[gagnant] += 1;
    let best = null;
    for (const [id, j] of joueurs) {
      const s = j.piecesManche * 10 + j.degats;
      if (s > 0 && (!best || s > best.s)) best = { id, nom: j.nom, s, equipe: j.equipe };
    }
    mvp = best;
    phase = "fin"; tPhase = now;
    voix.dire(gagnant === "v" ? "bataille_victoire_v" : "bataille_victoire_z", now);
    SONS.fanfare();
  }

  // ───── dessin ─────
  function dessinerTerrain(now, n) {
    const d = img.decor, md = meta.decor;
    if (d) ctx.drawImage(d, 0, SOL - 20 - md.sol, W, md.h);
    ctx.fillStyle = `rgba(20,10,40,${0.35 + 0.25 * n})`;
    ctx.fillRect(0, 0, W, SOL + 120);
    // camps
    sprite("chateau", X_V - 10, SOL - 20, 0.5);
    sprite("crypte", X_Z + 10, SOL - 20, 0.5);
    barreCamp(X_V - 10, SOL - 330, camp.v, COUL.v);
    barreCamp(X_Z + 10, SOL - 330, camp.z, COUL.z);
  }

  function barreCamp(x, y, pv, c) {
    rrect(x - 80, y, 160, 20, 10, "rgba(10,10,16,.85)");
    rrect(x - 78, y + 2, Math.max(12, 156 * pv / CAMP_PV), 16, 8, c);
  }

  function dessinerUnites(now) {
    const liste = [...unites].sort((a, b) => a.dy - b.dy);
    for (const u of liste) {
      const k = Math.min(back((now - u.ne) / 0.35), u.mort ? ease(1 - (now - u.mort) / 0.6) : 1);
      if (k <= 0.01) continue;
      const marche = !u.mort && Math.abs(Math.sin(now * 8 + u.ph)) * 6;
      const y = SOL + u.dy - marche;
      ctx.save();
      ctx.translate(u.x, y);
      ctx.scale(k, k);
      if (u.type === "champion" || u.type === "geant") {
        const g = ctx.createRadialGradient(0, -60 * u.ech / 0.2, 5, 0, -60 * u.ech / 0.2, 90 * u.ech / 0.2);
        g.addColorStop(0, u.equipe === "v" ? "rgba(255,220,90,.55)" : "rgba(170,90,255,.55)");
        g.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = g; ctx.fillRect(-120 * u.ech / 0.2, -160 * u.ech / 0.2, 240 * u.ech / 0.2, 200 * u.ech / 0.2);
      }
      sprite(u.look, 0, 0, u.ech, { flip: u.equipe === "z" });
      ctx.restore();
      const m = meta[u.look];
      const haut = y - (m ? m.ay : 700) * u.ech * k;
      // barre de vie
      if (!u.mort && u.pv < u.pvMax) {
        rrect(u.x - 26, haut - 12, 52, 7, 3, "rgba(0,0,0,.6)");
        rrect(u.x - 26, haut - 12, Math.max(4, 52 * u.pv / u.pvMax), 7, 3, COUL[u.equipe]);
      }
      if (u.nom) {
        ctx.font = "800 22px Montserrat";
        const tw = Math.min(ctx.measureText(u.nom).width, 170);
        rrect(u.x - tw / 2 - 10, haut - 46, tw + 20, 30, 15, u.equipe === "v" ? "rgba(20,70,40,.92)" : "rgba(60,25,90,.92)");
        texte(u.nom, u.x, haut - 31, { taille: 22, max: 170 });
      }
    }
  }

  function dessinerBulle(now) {
    if (phase === "debut") return;
    if ((!bulle || now > bulle.fin) && fileBulles.length) {
      const b = fileBulles.shift();
      bulle = { ...b, debut: now, fin: now + (fileBulles.length > 2 ? 1.8 : 3) };
    }
    if (!bulle || now > bulle.fin) return;
    const j = joueurs.get(bulle.id);
    const u = j?.unite && j.unite.pv > 0 ? j.unite : null;
    const x = Math.max(200, Math.min(W - 200, u ? u.x : W / 2));
    const y = u ? SOL - (meta[u.look]?.ay || 700) * u.ech - 70 : 860;
    const k = back((now - bulle.debut) / 0.25);
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(k, k);
    ctx.font = "800 34px Montserrat";
    const tw = Math.max(160, Math.min(ctx.measureText(bulle.texte).width, 380));
    rrect(-tw / 2 - 26, -100, tw + 52, 96, 24, "#fafafa", j ? COUL[j.equipe] : "#ffce00", 6);
    texte(bulle.nom, 0, -76, { taille: 24, couleur: "#e8323c", max: 360 });
    texte(bulle.texte, 0, -40, { taille: 34, couleur: "#16161c", max: 380 });
    ctx.restore();
  }

  function dessinerHUD(now) {
    texte("VILLAGEOIS", W / 2 - 150, 250, { taille: 60, police: "Anton", couleur: COUL.v, contour: 10 });
    texte("VS", W / 2, 250, { taille: 50, police: "Anton", contour: 10 });
    texte("ZOMBIES", W / 2 + 160, 250, { taille: 60, police: "Anton", couleur: COUL.z, contour: 10 });
    // équipes
    let nv = 0, nz = 0;
    for (const j of joueurs.values()) j.equipe === "v" ? nv++ : nz++;
    for (const [e, x, nb] of [["v", 40, nv], ["z", 560, nz]]) {
      rrect(x, 300, 480, 120, 22, "rgba(16,16,22,.9)", COUL[e], 6);
      texte(`${NOM[e]} · ${score[e]} manche${score[e] > 1 ? "s" : ""}`, x + 240, 328, { taille: 22, couleur: COUL[e] });
      rrect(x + 20, 350, 440, 26, 13, "rgba(255,255,255,.1)");
      rrect(x + 22, 352, Math.max(16, 436 * (camp?.[e] ?? CAMP_PV) / CAMP_PV), 22, 11, COUL[e]);
      texte(`CAMP ${Math.round(100 * (camp?.[e] ?? CAMP_PV) / CAMP_PV)} %`, x + 240, 363, { taille: 18, contour: 5 });
      texte(`${fmt(nb)} joueur${nb > 1 ? "s" : ""}`, x + 240, 398, { taille: 20, couleur: "#d7dae4" });
    }
    // chrono
    const reste = phase === "combat" ? Math.max(0, finManche - now) : phase === "debut" ? DUREE_MANCHE : 0;
    const mm = Math.floor(reste / 60), ss = String(Math.floor(reste % 60)).padStart(2, "0");
    rrect(W / 2 - 150, 432, 300, 44, 22, "rgba(16,16,22,.9)");
    texte(`MANCHE ${manche} · ${mm}:${ss}`, W / 2, 455, { taille: 24, couleur: reste < 30 && phase === "combat" ? "#ff7070" : "#fafafa" });
    // comment jouer, ou le dernier petit message
    const p = petites[0];
    if (p && !p.debut) p.debut = now;
    if (p && now - p.debut > 1.8) petites.shift();
    if (p && now - p.debut <= 1.8) {
      ctx.font = "800 26px Montserrat";
      const tw = Math.min(ctx.measureText(p.t).width, W - 140);
      rrect(W / 2 - tw / 2 - 26, 488, tw + 52, 48, 24, p.c);
      texte(p.t, W / 2, 513, { taille: 26, couleur: "#16161c", max: W - 140 });
    } else {
      texte("TAPE  1 = VILLAGEOIS   ·   2 = ZOMBIES   ·   ♥ LIKE = RÉPARE TON CAMP", W / 2, 512, { taille: 22, contour: 6, max: W - 60 });
    }
    // barème des renforts
    rrect(40, 548, W - 80, 190, 22, "rgba(16,16,22,.9)", "#ffce00", 5);
    texte("TON CADEAU = DES RENFORTS POUR TON ÉQUIPE", W / 2, 576, { taille: 22, couleur: "#ffce00" });
    RENFORTS.forEach((r, i) => {
      const col = i % 2, lig = Math.floor(i / 2);
      const x = 70 + col * 490, y = 618 + lig * 40;
      if (img[r.icone]) ctx.drawImage(img[r.icone], x, y - 17, 34, 34);
      texte(`${fmt(r.min)}${i ? "+" : ""}`, x + 44, y, { taille: 21, align: "left" });
      texte(r.texte, x + 440, y, { taille: 21, align: "right", couleur: ["#7be08f", "#e3b179", "#ffd75e", "#7fc4ff", "#c79bff", "#ff8a8a"][i] });
    });
  }

  function dessinerAlerte(now) {
    if (!alerte && alertes.length) {
      alerte = { ...alertes.shift(), t0: now };
      if (alerte.voix) voix.dire(alerte.voix, now);
      SONS.fanfare();
      if (alerte.image) { alerte.img = new Image(); alerte.img.src = alerte.image; }
    }
    if (alertes.length > 5) alertes.splice(0, alertes.length - 5);
    if (!alerte) return;
    const t = now - alerte.t0, dur = 2.6;
    if (t > dur) { alerte = null; return; }
    const k = t < 0.3 ? back(t / 0.3) : t > dur - 0.25 ? ease((dur - t) / 0.25) : 1;
    ctx.save();
    ctx.translate(W / 2, 880);
    ctx.scale(k, k);
    rrect(-470, -130, 940, 260, 30, "rgba(12,12,18,.95)", alerte.couleur, 8);
    texte(alerte.l1, 0, -82, { taille: 48, police: "Anton", couleur: alerte.couleur, max: 600 });
    texte(alerte.l2, 0, -38, { taille: 26, couleur: "#d7dae4", max: 600 });
    texte(alerte.l3, 0, 14, { taille: 58, police: "Anton", max: 600 });
    texte(alerte.l4, 0, 78, { taille: 26, couleur: alerte.couleur, max: 600 });
    const ic = alerte.img?.complete && alerte.img.naturalWidth ? alerte.img : img[alerte.icone];
    if (ic) for (const sx of [-1, 1]) ctx.drawImage(ic, sx * 370 - 55, -65, 110, 110);
    ctx.restore();
  }

  function dessinerFin(now) {
    if (phase === "debut") {
      const r = Math.ceil(debutManche - now);
      if (r > 0) texte(String(r), W / 2, 900, { taille: 200, police: "Anton", contour: 16, couleur: "#ffce00" });
      texte(`MANCHE ${manche}`, W / 2, 1020, { taille: 60, police: "Anton", contour: 10 });
      return;
    }
    if (phase !== "fin") return;
    const k = back((now - tPhase) / 0.4);
    ctx.save();
    ctx.translate(W / 2, 880);
    ctx.scale(k, k);
    rrect(-480, -170, 960, 340, 30, "rgba(12,12,18,.96)", COUL[gagnant], 10);
    texte(`LES ${NOM[gagnant]}`, 0, -100, { taille: 70, police: "Anton", couleur: COUL[gagnant], max: 880 });
    texte("GAGNENT LA MANCHE !", 0, -20, { taille: 56, police: "Anton", max: 880 });
    texte(`${NOM.v} ${score.v} – ${score.z} ${NOM.z}`, 0, 50, { taille: 30, couleur: "#d7dae4" });
    if (mvp) texte(`⭐ MEILLEUR JOUEUR : ${mvp.nom}`, 0, 115, { taille: 32, couleur: "#ffce00", max: 880 });
    ctx.restore();
    const r = Math.ceil(12 - (now - tPhase));
    texte(`Nouvelle manche dans ${Math.max(0, r)} s`, W / 2, 1100, { taille: 26, contour: 6 });
  }

  function dessinerEffets(now, dt) {
    for (let i = effets.length - 1; i >= 0; i--) {
      const e = effets[i];
      if (e.kind === "eclair") {
        const a = 1 - (now - e.t0) / 0.8;
        if (a <= 0) { effets.splice(i, 1); continue; }
        ctx.fillStyle = e.couleur; ctx.globalAlpha = a * 0.5; ctx.fillRect(0, 760, W, 520); ctx.globalAlpha = 1;
        continue;
      }
      e.x += e.vx * dt; e.y += e.vy * dt; e.vy += 400 * dt; e.v -= dt;
      if (e.v <= 0) { effets.splice(i, 1); continue; }
      ctx.globalAlpha = Math.min(1, e.v * 2); ctx.fillStyle = e.c;
      ctx.beginPath(); ctx.arc(e.x, e.y, 5, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
    }
  }

  return {
    demarrer(now) { if (!camp) nouvelleManche(now); },
    evenement,
    dessiner(now, dt, nuit) {
      if (!camp) nouvelleManche(now);
      simuler(now, dt);
      dessinerTerrain(now, nuit);
      dessinerUnites(now);
      dessinerEffets(now, dt);
      dessinerHUD(now);
      dessinerBulle(now);
      dessinerAlerte(now);
      dessinerFin(now);
    },
  };
}
