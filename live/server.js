// Serveur du live « Fauché-les-Oies » : écoute ton live TikTok et pilote la page du village.
//
//   node server.js            → se connecte au live de config.json ("tiktok": "ton_pseudo")
//   node server.js --demo     → faux événements toutes les secondes (pour tester sans être en live)
//
// Page du village : http://localhost:3000        (à mettre dans LIVE Studio / à partager à l'écran)
// Page de pilotage : http://localhost:3000/admin (statut de la connexion, tests, remise à zéro)
//
// Le village repart de zéro à chaque lancement. Le serveur n'écoute que cet appareil (127.0.0.1) :
// personne d'autre sur le wifi ne peut envoyer de faux cadeaux.
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";
import { appliquer, etatInitial, fauxEvenement, vue } from "./public/logique.js";

const ICI = fileURLToPath(new URL(".", import.meta.url));
const PUBLIC = join(ICI, "public");
const CFG = JSON.parse(readFileSync(join(ICI, "config.json"), "utf8"));
const DEMO = process.argv.includes("--demo");
const PSEUDO = (process.argv.find((a) => a.startsWith("--tiktok=")) || "").split("=")[1] || CFG.tiktok;
// Pas besoin de clé Euler Stream : la connexion simple au live est gratuite. (--cle=… est accepté mais ignoré.)

// ───── état : on repart de zéro à chaque lancement ─────
let etat = etatInitial(CFG);
// bac à sable des tests : une copie jetable, effacée 30 s après le dernier test (ou au premier vrai événement)
let bac = null, finBac = 0;

// ───── serveur web ─────
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".png": "image/png",
  ".json": "application/json", ".css": "text/css" };
const http = createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p === "/") p = "/index.html";
  if (p === "/admin") p = "/admin.html";
  if (p === "/config.json") {
    res.writeHead(200, { "Content-Type": "application/json" }).end(JSON.stringify(CFG));
    return;
  }
  const f = normalize(join(PUBLIC, p));
  if (!f.startsWith(PUBLIC) || !existsSync(f)) {
    res.writeHead(404).end("introuvable");
    return;
  }
  res.writeHead(200, { "Content-Type": TYPES[extname(f)] || "application/octet-stream", "Cache-Control": "no-cache" });
  res.end(readFileSync(f));
});

const wss = new WebSocketServer({ server: http, path: "/ws" });
let statut = DEMO ? "démo" : "pas connecté";

function diffuser(msg) {
  const s = JSON.stringify(msg);
  for (const c of wss.clients) if (c.readyState === 1) c.send(s);
}

// Les annonces partent tout de suite. L'état (compteurs, rue) part avec elles s'il a changé ;
// pour les likes (très nombreux), on le regroupe : au plus 4 envois par seconde.
let vueEnRetard = false;
function evenement(ev, test = false) {
  if (!test && bac) finirBac();
  const cible = test ? bac : etat;
  const annonces = appliquer(cible, ev);
  const important = ev.type === "follow" || ev.type === "gift";
  if (important) diffuser({ t: "ev", annonces, vue: vue(cible) });
  else {
    if (annonces.length) diffuser({ t: "ev", annonces });
    if (ev.type === "like") vueEnRetard = true;
  }
}
setInterval(() => {
  if (!vueEnRetard) return;
  vueEnRetard = false;
  diffuser({ t: "vue", vue: vue(bac || etat) });
}, 250);

function finirBac() {
  bac = null;
  // la page efface tout ce qui vient du test (bonshommes compris)
  diffuser({ t: "etat", vue: vue(etat), cfg: CFG, statut, zero: true, test: false });
}
setInterval(() => { if (bac && Date.now() > finBac) finirBac(); }, 1000);

wss.on("connection", (ws) => {
  ws.send(JSON.stringify({ t: "etat", vue: vue(bac || etat), cfg: CFG, statut, test: !!bac }));
  ws.on("message", (raw) => {
    let m;
    try { m = JSON.parse(raw); } catch { return; }
    if (m.cmd === "test" && m.ev) {
      if (!bac) bac = structuredClone(etat);
      finBac = Date.now() + 30000;
      evenement(m.ev, true);
      diffuser({ t: "test", actif: true });
    } else if (m.cmd === "zero") {
      etat = etatInitial(CFG);
      bac = null;
      diffuser({ t: "etat", vue: vue(etat), cfg: CFG, statut, zero: true });
      console.log("Village remis à zéro.");
    }
  });
});

http.listen(CFG.port, "127.0.0.1", () => {
  console.log(`\n🏘️  Village : http://localhost:${CFG.port}`);
  console.log(`🎛️  Pilotage : http://localhost:${CFG.port}/admin\n`);
});

// ───── TikTok ─────
function nomDe(u) {
  return (u && (u.nickname || u.uniqueId)) || "quelqu'un";
}
function idDe(u) {
  return (u && (u.uniqueId || String(u.userId))) || "anonyme";
}

async function brancherTikTok() {
  const { TikTokLiveConnection, WebcastEvent } = await import("tiktok-live-connector");
  // surtout pas enableExtendedGiftInfo : cette option passe par un service payant et bloque la connexion.
  // Le prix de chaque cadeau arrive de toute façon avec le cadeau (giftDetails.diamondCount).
  const live = new TikTokLiveConnection(PSEUDO, {});
  const majStatut = (s) => {
    statut = s;
    console.log("TikTok :", s);
    diffuser({ t: "statut", statut });
  };
  const u = (d) => ({ id: idDe(d.user), nom: nomDe(d.user) });
  const connu = (d) => !!(d.user && (d.user.uniqueId || d.user.nickname));   // TikTok envoie parfois des messages sans pseudo

  live.on(WebcastEvent.FOLLOW, (d) => connu(d) && evenement({ type: "follow", ...u(d) }));
  live.on(WebcastEvent.SHARE, (d) => connu(d) && evenement({ type: "share", ...u(d) }));
  live.on(WebcastEvent.CHAT, (d) => connu(d) && d.comment && evenement({ type: "chat", ...u(d), texte: d.comment }));
  live.on(WebcastEvent.MEMBER, (d) => connu(d) && evenement({ type: "join", ...u(d) }));
  live.on(WebcastEvent.LIKE, (d) => evenement({ type: "like", ...u(d), n: d.likeCount || 1 }));
  live.on(WebcastEvent.GIFT, (d) => {
    const g = d.giftDetails || {};
    // cadeaux en série : on ne compte qu'à la fin de la série
    if (g.giftType === 1 && !d.repeatEnd) return;
    const pieces = (g.diamondCount || 1) * (d.repeatCount || 1);
    evenement({ type: "gift", ...u(d), pieces, cadeau: g.giftName || "cadeau" });
  });
  live.on(WebcastEvent.STREAM_END, () => majStatut("live terminé"));
  live.on(WebcastEvent.DISCONNECTED, () => majStatut("déconnecté"));

  const essayer = async () => {
    if (live.isConnected || live.isConnecting) return;
    try {
      await live.connect();
      majStatut(`connecté au live de @${PSEUDO}`);
    } catch (e) {
      const msg = String(e.message || e);
      const pasEnLive = /isn't online|offline|Room ID/i.test(msg);
      majStatut(pasEnLive ? `en attente du live de @${PSEUDO} (tu n'es pas en live)`
        : `connexion au live de @${PSEUDO} ratée, nouvel essai… (${msg.slice(0, 80)})`);
    }
  };
  await essayer();
  setInterval(essayer, 10000);   // se (re)connecte tout seul dès que tu lances le live
}

if (DEMO) {
  setInterval(() => evenement(fauxEvenement()), 900);
} else if (!PSEUDO) {
  console.log("⚠️  Mets ton pseudo TikTok dans config.json (\"tiktok\") ou lance : node server.js --tiktok=ton_pseudo");
} else {
  brancherTikTok().catch((e) => console.error("Connecteur TikTok :", e));
}
