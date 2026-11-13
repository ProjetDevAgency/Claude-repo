// Physique de la machine à pièces (pousseur de pièces), vue du dessus, sans dessin : testable dans Node.
// Les pièces ne glissent pas toutes seules (frottement) : elles bougent seulement quand on les pousse.
// Le pousseur va et vient au fond ; ce qui passe le bord avant TOMBE (gagné), ce qui passe sur les côtés
// tombe dans la caisse du maire.

export const TW = 880;          // largeur du plateau
export const TL = 640;          // profondeur du plateau (le bord avant est à y = TL)
export const P0 = 40;           // pousseur rentré
export const COURSE = 120;      // course normale du pousseur
export const PERIODE = 3.2;     // un aller-retour
export const COTE_OUVERT = TL * 0.62;   // les murs des côtés s'arrêtent ici

export const SORTES = {
  piece: { r: 30, m: 1, val: 10 },
  or: { r: 30, m: 1, val: 50 },
  geante: { r: 60, m: 4, val: 200 },
  sac: { r: 42, m: 2, val: 100 },
  lingot: { r: 44, m: 3, val: 500 },
  oie: { r: 58, m: 6, val: 0 },           // vaut le jackpot
};
const RMAX = 62;

export function creerMachine({ alea = Math.random } = {}) {
  let pieces = [];
  let t = 0, amp = COURSE, ampCible = COURSE, seisme = 0, n = 0;
  let pAvant = P0;

  const pousseur = () => pAvant;
  const position = (tt) => P0 + amp * (1 - Math.cos((2 * Math.PI * tt) / PERIODE)) / 2;

  function ajouter(sorte, x, y, extra = {}) {
    const s = SORTES[sorte];
    const p = { id: ++n, sorte, x, y: Math.max(y, pAvant + s.r), r: s.r, m: s.m, val: s.val, ...extra };
    pieces.push(p);
    return p;
  }

  // une pièce tombe dans la fente : elle se pose juste devant le pousseur
  function lacher(sorte, x, extra) {
    const s = SORTES[sorte];
    x = Math.max(s.r + 6, Math.min(TW - s.r - 6, x));
    return ajouter(sorte, x, pAvant + s.r + 4 + alea() * 50, extra);
  }

  function relacher(iter = 6) {
    const P = pAvant;
    for (let k = 0; k < iter; k++) {
      pieces.sort((a, b) => a.x - b.x);
      for (let i = 0; i < pieces.length; i++) {
        const a = pieces[i];
        for (let j = i + 1; j < pieces.length; j++) {
          const b = pieces[j];
          if (b.x - a.x >= a.r + RMAX) break;
          const dx = b.x - a.x, dy = b.y - a.y, rr = a.r + b.r;
          const d2 = dx * dx + dy * dy;
          if (d2 >= rr * rr) continue;
          let d = Math.sqrt(d2), nx, ny;
          if (d < 1e-4) { nx = alea() - 0.5; ny = alea() - 0.5; d = Math.hypot(nx, ny) || 1; nx /= d; ny /= d; d = 0; }
          else { nx = dx / d; ny = dy / d; }
          const o = rr - d;
          // une pièce collée au pousseur ne recule pas : masse infinie
          let wa = a.y - a.r <= P + 0.5 ? 0 : 1 / a.m;
          let wb = b.y - b.r <= P + 0.5 ? 0 : 1 / b.m;
          if (wa + wb === 0) { wa = wb = 1; ny = 0; nx = Math.sign(dx) || 1; }
          const ka = (o * wa) / (wa + wb), kb = (o * wb) / (wa + wb);
          a.x -= nx * ka; a.y -= ny * ka;
          b.x += nx * kb; b.y += ny * kb;
        }
      }
      for (const p of pieces) {
        if (p.y < P + p.r) p.y = P + p.r;                       // le pousseur et le mur du fond
        if (p.y < COTE_OUVERT) p.x = Math.max(p.r, Math.min(TW - p.r, p.x));   // murs des côtés
      }
    }
  }

  // avance de dt secondes ; renvoie les pièces tombées [{ p, cote }]
  function pas(dt) {
    t += dt;
    amp += (ampCible - amp) * Math.min(1, dt * 1.5);
    const P = position(t);
    const pousse = P > pAvant;
    pAvant = P;
    if (pousse) for (const p of pieces) if (p.y < P + p.r) p.y = P + p.r;
    if (seisme > 0) {
      seisme -= dt;
      for (const p of pieces) {
        const k = 1 / Math.sqrt(p.m);
        p.y += (alea() * 90 + 20) * dt * k;
        p.x += (alea() - 0.5) * 120 * dt * k;
      }
    }
    relacher(6);
    const tombees = [];
    pieces = pieces.filter((p) => {
      const avant = p.y - p.r * 0.15 > TL;
      const cote = p.y >= COTE_OUVERT && (p.x < -p.r * 0.15 || p.x > TW + p.r * 0.15);
      if (avant || cote) { tombees.push({ p, cote: !avant }); return false; }
      return true;
    });
    return tombees;
  }

  // plateau de départ : déjà bien rempli, avec l'oie d'or au fond
  function remplir(nb = 125) {
    pieces = [];
    for (let i = 0; i < nb; i++) ajouter("piece", 40 + alea() * (TW - 80), P0 + 40 + alea() * (TL - 70));
    ajouter("sac", TW * 0.25, TL * 0.55);
    ajouter("lingot", TW * 0.72, TL * 0.62);
    ajouter("oie", TW / 2, P0 + COURSE + 80);
    for (let i = 0; i < 300; i++) relacher(1);
    pieces = pieces.filter((p) => p.y - p.r * 0.15 <= TL && p.x > 0 && p.x < TW);
  }

  return {
    get pieces() { return pieces; },
    get pousseur() { return pousseur(); },
    get seisme() { return seisme; },
    get bulldozer() { return ampCible > COURSE; },
    ajouter, lacher, pas, remplir,
    secouer(duree) { seisme = Math.max(seisme, duree); },
    pousserFort(on) { ampCible = on ? COURSE * 2.1 : COURSE; },
  };
}
