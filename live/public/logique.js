// Règles du village en live — partagées par le serveur (Node) et la page (mode démo sans serveur).
// Mêmes règles que les lives « village » : 1 abonné = 1 habitant, 1 like = 1 €,
// chaque cadeau construit un bâtiment selon son prix (barème ci-dessous), classement des bâtisseurs.

export const PALIERS = [
  // icone : le cadeau TikTok typique à ce prix (rose 1, cœur 5, donut 30, confettis 100, billets 500, baleine 2000)
  { min: 1, nom: "UN ARBRE", sprite: "arbre", icone: "cadeau_rose" },
  { min: 5, nom: "UNE CABANE", sprite: "cabane", icone: "cadeau_coeur" },
  { min: 30, nom: "UNE MAISON", sprite: "maison", icone: "cadeau_donut" },
  { min: 100, nom: "UNE GRANDE MAISON", sprite: "villa", icone: "cadeau_confettis" },
  { min: 500, nom: "UN IMMEUBLE", sprite: "immeuble", icone: "cadeau_billets" },
  { min: 2000, nom: "UN MONUMENT", sprite: "chateau", icone: "cadeau_baleine" },
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

// Chaque lancement repart de zéro (le village n'est pas relié au vrai nombre d'abonnés du compte).
// Les bâtiments des épisodes restent dans la rue comme décor, sans compter dans MAISONS.
export function etatInitial(cfg) {
  return {
    habitants: 0,
    budget: 0,
    decor: (cfg.batimentsDepart || []).map((b) => ({ id: "decor:" + b.id, nom: b.nom || b.id, sprite: b.sprite })),
    pseudos: {},   // seulement les abonnés et les donateurs du live : id → { nom, abonne, pieces }
    batiments: [], // construits pendant le live : { id, proprio, nom, sprite }
    arbres: [],    // { id, nom }
    nbArbres: 0,
    recents: [],   // derniers abonnés (pour peupler la rue si la page se recharge)
    n: 0,
  };
}

const MAX_ARBRES = 80;     // au-delà, les plus anciens arbres laissent la place (le compteur continue)

// Ce que la page a besoin de savoir : léger, même avec des milliers de spectateurs.
export function vue(etat) {
  return {
    habitants: etat.habitants,
    budget: etat.budget,
    decor: etat.decor,
    batiments: etat.batiments,
    arbres: etat.arbres,
    top: topBatisseurs(etat, 5),
    recents: etat.recents,
  };
}

function personne(etat, id, nom) {
  if (!etat.pseudos[id]) etat.pseudos[id] = { nom, abonne: false, pieces: 0 };
  else if (nom) etat.pseudos[id].nom = nom;
  return etat.pseudos[id];
}

// ev : { type: follow|gift|like|chat|share|join, id, nom, pieces?, cadeau?, n?, texte? }
// Renvoie les annonces ; « change » dit si les compteurs ou la rue ont bougé.
export function appliquer(etat, ev) {
  const annonces = [];
  const abonne = !!etat.pseudos[ev.id]?.abonne;
  switch (ev.type) {
    case "follow": {
      const p = personne(etat, ev.id, ev.nom);
      if (!p.abonne) {
        p.abonne = true;
        etat.habitants += 1;
        etat.recents.push({ id: ev.id, nom: p.nom });
        if (etat.recents.length > 14) etat.recents.shift();
        annonces.push({ kind: "arrivee", id: ev.id, nom: p.nom, numero: etat.habitants });
      }
      break;
    }
    case "gift": {
      const p = personne(etat, ev.id, ev.nom);
      const pieces = Math.max(1, Math.round(ev.pieces || 1));
      p.pieces += pieces;
      const pal = palier(pieces);
      const bid = "b" + ++etat.n;
      if (pal.sprite === "arbre") {
        etat.arbres.push({ id: bid, nom: p.nom });
        etat.nbArbres += 1;
        if (etat.arbres.length > MAX_ARBRES) etat.arbres.shift();
      } else {
        const sprite = pal.sprite === "maison" ? MAISONS[hash(bid) % MAISONS.length] : pal.sprite;
        etat.batiments.push({ id: bid, proprio: ev.id, nom: p.nom, sprite });
      }
      annonces.push({ kind: "construction", id: ev.id, nom: p.nom, palier: pal.nom, bat: bid, arbre: pal.sprite === "arbre",
        pieces, type: pal.sprite, icone: pal.icone, image: ev.image || null, cadeau: ev.cadeau || null });
      break;
    }
    case "like":
      etat.budget += ev.n || 1;
      annonces.push({ kind: "like", n: ev.n || 1 });
      break;
    // partages, commentaires, entrées : on ne garde rien en mémoire (sinon ça gonfle avec le monde)
    case "share":
      annonces.push({ kind: "partage", id: ev.id, nom: ev.nom });
      break;
    case "chat":
      annonces.push({ kind: "bulle", id: ev.id, nom: ev.nom, abonne, texte: String(ev.texte || "").trim().slice(0, 60) });
      break;
    case "join":
      annonces.push({ kind: "passant", id: ev.id, nom: ev.nom, abonne });
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
  "jsuis le 70e ?", "il est où l'oie", "go 10 000", "bien la famille", "moi", "ma maison elle est où",
  "1", "2", "1", "2", "2", "1"];
const CADEAUX = [["Rose", 1], ["Rose", 1], ["TikTok", 1], ["GG", 1], ["Rose x5", 5], ["Coeur", 5], ["Donut", 30],
  ["Casquette", 99], ["Licorne", 100], ["Chapeau", 199], ["Fusée", 500]];

export function fauxEvenement(r = Math.random) {
  const nom = NOMS[Math.floor(r() * NOMS.length)] + (r() < 0.4 ? String(Math.floor(r() * 99)) : "");
  const id = nom.toLowerCase();
  const abonne = hash(id) % 3 === 0;
  const x = r();
  if (x < 0.07) return { type: "follow", id, nom, abonne: true };
  if (x < 0.15) {
    const [cadeau, pieces] = CADEAUX[Math.floor(r() * CADEAUX.length)];
    return { type: "gift", id, nom, cadeau, pieces, abonne };
  }
  if (x < 0.5) return { type: "like", id, nom, n: 1 + Math.floor(r() * 15) };
  if (x < 0.53) return { type: "share", id, nom };
  if (x < 0.85) return { type: "chat", id, nom, abonne, texte: PHRASES[Math.floor(r() * PHRASES.length)] };
  return { type: "join", id, nom, abonne };
}
