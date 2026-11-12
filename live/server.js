// Serveur du live « Fauché-les-Oies » : écoute ton live TikTok et pilote la page du village.
//
//   node server.js            → se connecte au live de config.json ("tiktok": "ton_pseudo")
//   node server.js --demo     → faux événements toutes les secondes (pour tester sans être en live)
//
// Page du village : http://localhost:3000        (à mettre dans LIVE Studio / à partager à l'écran)
// Page de pilotage : http://localhost:3000/admin (statut de la connexion, tests)
import { createServer } from "node:http";
import { readFileSync, writeFileSync, existsSync, renameSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";
import { WebSocketServer } from "ws";
import { appliquer, etatInitial, fauxEvenement } from "./public/logique.js";

const ICI = fileURLToPath(new URL(".", import.meta.url));
const PUBLIC = join(ICI, "public");
const CFG = JSON.parse(readFileSync(join(ICI, "config.json"), "utf8"));
const FICHIER_ETAT = join(ICI, "etat.json");
const DEMO = process.argv.includes("--demo");
const PSEUDO = (process.argv.find((a) => a.startsWith("--tiktok=")) || "").split("=")[1] || CFG.tiktok;

// ───── état (sauvegardé : le village continue d'un live à l'autre) ─────
let etat = existsSync(FICHIER_ETAT) && !DEMO ? JSON.parse(readFileSync(FICHIER_ETAT, "utf8")) : etatInitial(CFG);
let sale = false;
setInterval(() => {
  if (!sale || DEMO) return;
  writeFileSync(FICHIER_ETAT + ".tmp", JSON.stringify(etat));
  renameSync(FICHIER_ETAT + ".tmp", FICHIER_ETAT);
  sale = false;
}, 3000);

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

function evenement(ev) {
  const annonces = appliquer(etat, ev);
  sale = true;
  diffuser({ t: "ev", ev, annonces, etat });
}

wss.on("connection", (ws) => {
  ws.send(JSON.stringify({ t: "etat", etat, cfg: CFG, statut }));
  ws.on("message", (raw) => {
    let m;
    try { m = JSON.parse(raw); } catch { return; }
    if (m.cmd === "test" && m.ev) {
      evenement(m.ev);
      return;
    }
  });
});

http.listen(CFG.port, () => {
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
  const live = new TikTokLiveConnection(PSEUDO, { enableExtendedGiftInfo: true });
  const majStatut = (s) => {
    statut = s;
    console.log("TikTok :", s);
    diffuser({ t: "statut", statut });
  };
  const u = (d) => ({ id: idDe(d.user), nom: nomDe(d.user) });

  live.on(WebcastEvent.FOLLOW, (d) => evenement({ type: "follow", ...u(d) }));
  live.on(WebcastEvent.SHARE, (d) => evenement({ type: "share", ...u(d) }));
  live.on(WebcastEvent.CHAT, (d) => evenement({ type: "chat", ...u(d), texte: d.comment }));
  live.on(WebcastEvent.MEMBER, (d) => evenement({ type: "join", ...u(d) }));
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
      majStatut(`en attente du live de @${PSEUDO} (${String(e.message || e).slice(0, 80)})`);
    }
  };
  await essayer();
  setInterval(essayer, 20000);   // se (re)connecte tout seul dès que tu lances le live
}

if (DEMO) {
  setInterval(() => evenement(fauxEvenement()), 900);
} else if (!PSEUDO) {
  console.log("⚠️  Mets ton pseudo TikTok dans config.json (\"tiktok\") ou lance : node server.js --tiktok=ton_pseudo");
} else {
  brancherTikTok().catch((e) => console.error("Connecteur TikTok :", e));
}
