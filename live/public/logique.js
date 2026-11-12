// Règles du village en live — partagées par le serveur (Node) et la page (mode démo sans serveur).
// Mêmes règles que les lives « village » : 1 abonné = 1 habitant, 1 like = 1 €,
// chaque cadeau construit un bâtiment selon son prix (barème ci-dessous), classement des bâtisseurs.

export const PALIERS = [
  { min: 1, nom: "UN ARBRE", sprite: "arbre" },
  { min: 5, nom: "UNE CABANE", sprite: "cabane" },
  { min: 30, nom: "UNE MAISON", sprite: "maison" },
  { min: 100, nom: "UNE GRANDE MAISON", sprite: "villa" },
  { min: 500, nom: "UN IMMEUBLE", sprite: "immeuble" },
  { min: 2000, nom: "UN MONUMENT", sprite: "chateau" },
];

const MAISONS = ["maison_jaune", "maison_bleue", "maison_rose", "maison_verte"];

export function hash(s) {
  let h = 2166136261;
  for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return h >>> 0;
}

export function palier(pieces) {
  let p = PALIERS[0];
  for (const t of PALIERS) if (pieces >= t.min) p = t;
  return p;
}

export function etatInitial(cfg) {
  const pseudos = {};
  const batiments = [];
  for (const b of cfg.batimentsDepart || []) {
    pseudos[b.id] = { nom: b.nom || b.id, abonne: true, pieces: 0 };
    batiments.push({ id: "depart:" + b.id, proprio: b.id, nom: b.nom || b.id, sprite: b.sprite });
  }
  return {
    habitants: cfg.habitantsDepart,
    budget: cfg.budgetDepart,
    pseudos,       // id → { nom, abonne, pieces }
    batiments,     // dans l'ordre de construction : { id, proprio, nom, sprite }
    arbres: [],    // { id, nom }
    n: 0,          // compteur pour des ids uniques
  };
}

export function nbMaisons(etat) {
  return etat.batiments.length;
}

function personne(etat, id, nom) {
  if (!etat.pseudos[id]) etat.pseudos[id] = { nom, abonne: false, pieces: 0 };
  else if (nom) etat.pseudos[id].nom = nom;
  return etat.pseudos[id];
}

// ev : { type: follow|gift|like|chat|share|join, id, nom, pieces?, cadeau?, n?, texte? }
export function appliquer(etat, ev) {
  const annonces = [];
  const p = ev.id ? personne(etat, ev.id, ev.nom) : null;
  switch (ev.type) {
    case "follow":
      if (!p.abonne) {
        p.abonne = true;
        etat.habitants += 1;
        annonces.push({ kind: "arrivee", id: ev.id, nom: p.nom, numero: etat.habitants });
      }
      break;
    case "gift": {
      const pieces = Math.max(1, Math.round(ev.pieces || 1));
      p.pieces += pieces;
      const pal = palier(pieces);
      const bid = "b" + ++etat.n;
      if (pal.sprite === "arbre") {
        etat.arbres.push({ id: bid, nom: p.nom });
      } else {
        const sprite = pal.sprite === "maison" ? MAISONS[hash(bid) % MAISONS.length] : pal.sprite;
        etat.batiments.push({ id: bid, proprio: ev.id, nom: p.nom, sprite });
      }
      annonces.push({ kind: "construction", id: ev.id, nom: p.nom, palier: pal.nom, bat: bid, arbre: pal.sprite === "arbre",
        pieces, monument: pal.sprite === "chateau" });
      break;
    }
    case "like":
      etat.budget += ev.n || 1;
      break;
    case "share":
      annonces.push({ kind: "partage", id: ev.id, nom: p.nom });
      break;
    case "chat":
      annonces.push({ kind: "bulle", id: ev.id, nom: p.nom, texte: String(ev.texte || "").trim().slice(0, 60) });
      break;
    case "join":
      annonces.push({ kind: "passant", id: ev.id, nom: p.nom });
      break;
  }
  return annonces;
}

export function topBatisseurs(etat, n = 5) {
  return Object.entries(etat.pseudos)
    .filter(([, p]) => p.pieces > 0)
    .sort((a, b) => b[1].pieces - a[1].pieces)
    .slice(0, n)
    .map(([id, p]) => ({ id, nom: p.nom, pieces: p.pieces }));
}

// ───── faux événements, pour la démo et les tests ─────
const NOMS = ["Kuromi", "SKR", "al_bsc", "Louane_", "Mskoww_91", "Waillox", "rph.49", "T_0", "Maël", "Michael",
  "PKMOI", "lea.mtz", "yanis93", "Nours", "Zoé_lpb", "kev.inn", "Sarah_b", "Inès", "Hugo_grt", "Lina.k"];
const PHRASES = ["c'est trop bien", "je veux une maison", "bonsoirrr", "ça va tout le monde", "trop styl", "weeee",
  "jsuis le 70e ?", "il est où l'oie", "go 10 000", "bien la famille", "moi", "ma maison elle est où"];
const CADEAUX = [["Rose", 1], ["Rose", 1], ["TikTok", 1], ["GG", 1], ["Rose x5", 5], ["Coeur", 5], ["Donut", 30],
  ["Casquette", 99], ["Licorne", 100], ["Chapeau", 199], ["Fusée", 500]];

export function fauxEvenement(r = Math.random) {
  const nom = NOMS[Math.floor(r() * NOMS.length)] + (r() < 0.4 ? String(Math.floor(r() * 99)) : "");
  const id = nom.toLowerCase();
  const x = r();
  if (x < 0.07) return { type: "follow", id, nom };
  if (x < 0.15) {
    const [cadeau, pieces] = CADEAUX[Math.floor(r() * CADEAUX.length)];
    return { type: "gift", id, nom, cadeau, pieces };
  }
  if (x < 0.5) return { type: "like", id, nom, n: 1 + Math.floor(r() * 15) };
  if (x < 0.53) return { type: "share", id, nom };
  if (x < 0.85) return { type: "chat", id, nom, texte: PHRASES[Math.floor(r() * PHRASES.length)] };
  return { type: "join", id, nom };
}
