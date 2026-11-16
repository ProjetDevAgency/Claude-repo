// Branding du compte TikTok « Tu choisis » (@tuchoisis.fr).
//   node branding/tuchoisis/make_branding.js
// Produit les photos de profil, l'aperçu du profil et la couverture de « Mon loup, partie 1 ».
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const DIR = __dirname;
const FONTS = path.resolve(DIR, "../../assets/fonts");
const C = { nuit: "#05070d", nuit2: "#0d1324", rouge: "#ff2b2b", chaud: "#ffb36b", blanc: "#ffffff" };
const HANDLE = "@tuchoisis.fr", NOM = "Tu choisis";
const BIO = "Histoires d'horreur où c'est toi le héros. A ou B ? La suite suit ton vote 👇";

const base = (w, h, body, css = "") => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Anton; src: url("file://${FONTS}/Anton-Regular.ttf"); }
@font-face { font-family: Mont; src: url("file://${FONTS}/Montserrat-ExtraBold.ttf"); }
html, body { margin: 0; width: ${w}px; height: ${h}px; overflow: hidden; background: ${C.nuit}; font-family: Inter, sans-serif; color: #fff; }
.nuit { position: absolute; inset: 0; background: radial-gradient(circle at 50% 42%, #1b2442 0%, ${C.nuit2} 38%, ${C.nuit} 72%); }
${css}</style></head><body>${body}</body></html>`;

// 1. A | B : les deux étiquettes du vote, comme à la fin des vidéos
const avatarAB = base(1080, 1080, `<div class="nuit"></div>
<div class="row"><div class="k a">A</div><div class="k b">B</div></div>
<div class="glow"></div>`, `
.row { position: absolute; top: 300px; left: 0; right: 0; display: flex; justify-content: center; gap: 46px; }
.k { width: 300px; height: 380px; border-radius: 40px; display: flex; align-items: center; justify-content: center;
     font: 330px/1 Anton; box-shadow: 0 30px 80px rgba(0,0,0,.6); }
.a { background: ${C.rouge}; color: #fff; transform: rotate(-5deg); }
.b { background: #fff; color: ${C.nuit}; transform: rotate(5deg); }
.glow { position: absolute; left: 240px; right: 240px; top: 760px; height: 26px; border-radius: 50%; background: ${C.chaud}; filter: blur(22px); opacity: .55; }`);

// 2. Deux portes : une lumière chaude dessous, l'autre rouge
const door = (x, col) => `<div class="door" style="left:${x}px"><i class="h"></i><i class="p"></i></div>
<div class="light" style="left:${x - 20}px;background:${col}"></div>`;
const avatarPortes = base(1080, 1080, `<div class="nuit"></div>${door(250, C.chaud)}${door(600, C.rouge)}
<div class="q">?</div>`, `
.door { position: absolute; top: 250px; width: 230px; height: 480px; background: #3a2a22; border: 14px solid #1c2236; border-bottom: none; box-sizing: border-box; }
.door .h { position: absolute; right: 22px; top: 230px; width: 26px; height: 26px; border-radius: 50%; background: #d9b45a; }
.door .p { position: absolute; left: 50%; top: 120px; width: 14px; height: 14px; margin-left: -7px; border-radius: 50%; background: #ffd28a; }
.light { position: absolute; top: 722px; width: 270px; height: 34px; border-radius: 50%; filter: blur(14px); opacity: .95; }
.q { position: absolute; top: 760px; width: 100%; text-align: center; font: 150px/1 Anton; color: #fff; opacity: .9; }`);

// 3. Le nom, avec les deux flèches du choix
const avatarTexte = base(1080, 1080, `<div class="nuit"></div>
<div class="t1">TU</div><div class="t2">CHOISIS</div>
<div class="ar"><span class="l">←</span><span class="r">→</span></div>`, `
.t1 { position: absolute; top: 250px; width: 100%; text-align: center; font: 200px/1 Anton; letter-spacing: 6px; }
.t2 { position: absolute; top: 450px; width: 100%; text-align: center; font: 210px/1 Anton; color: ${C.rouge}; letter-spacing: 2px; }
.ar { position: absolute; top: 690px; width: 100%; display: flex; justify-content: center; gap: 120px; font: 130px/1 Anton; }
.ar .l { color: #fff; } .ar .r { color: ${C.rouge}; }`);

// Couverture « Mon loup, partie 1 » : le décor + 2 à 3 mots, dans la zone visible de la grille (3:4 au centre)
const cover = (titre, rouge, partie, decor) => base(1080, 1920, `
<img src="file://${decor}" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,7,13,.75) 0%,rgba(5,7,13,.1) 40%,rgba(5,7,13,.1) 60%,rgba(5,7,13,.8) 100%)"></div>
<div class="pill">● ${partie}</div>
<div class="t">${titre}<br><span>${rouge}</span></div>
<div class="h">${HANDLE}</div>`, `
.pill { position: absolute; top: 330px; left: 50%; transform: translateX(-50%); background: ${C.rouge}; font: 800 52px Mont; letter-spacing: 4px; padding: 14px 32px; border-radius: 14px; }
.t { position: absolute; top: 470px; width: 100%; text-align: center; font: 230px/0.95 Anton; text-transform: uppercase;
     -webkit-text-stroke: 8px #000; paint-order: stroke fill; text-shadow: 0 12px 40px rgba(0,0,0,.8); }
.t span { color: ${C.rouge}; }
.h { position: absolute; top: 1540px; width: 100%; text-align: center; font: 700 42px Inter; opacity: .85; }`);

// Aperçu : le profil TikTok sur un téléphone, et les trois photos à la taille du fil
const apercu = (avatars, coverPng) => base(1080, 1500, `
<div class="hd">Aperçu du profil</div>
<img class="av" src="file://${avatars[0]}">
<div class="nom">${NOM}</div><div class="hdl">${HANDLE}</div>
<div class="stats"><div><b>0</b>Abonnements</div><div><b>0</b>Followers</div><div><b>0</b>J'aime</div></div>
<div class="bio">${BIO}</div>
<div class="grid"><img src="file://${coverPng}"><div class="ph">PARTIE 2<br>BIENTÔT</div><div class="ph">PARTIE 3<br>BIENTÔT</div></div>
<div class="feed">${avatars.map((a, i) => `<div><img src="file://${a}"><img src="file://${a}" class="s"><span>${i + 1}</span></div>`).join("")}</div>`, `
body { background: #000; }
.hd { position: absolute; top: 30px; width: 100%; text-align: center; font: 600 34px Inter; color: #aaa; }
.av { position: absolute; top: 100px; left: 50%; margin-left: -110px; width: 220px; height: 220px; border-radius: 50%; }
.nom { position: absolute; top: 345px; width: 100%; text-align: center; font: 800 46px Inter; }
.hdl { position: absolute; top: 405px; width: 100%; text-align: center; font: 500 32px Inter; color: #bbb; }
.stats { position: absolute; top: 465px; width: 100%; display: flex; justify-content: center; gap: 70px; font: 500 28px Inter; color: #aaa; text-align: center; }
.stats b { display: block; font: 800 38px Inter; color: #fff; }
.bio { position: absolute; top: 580px; left: 120px; right: 120px; text-align: center; font: 500 32px/1.35 Inter; }
.grid { position: absolute; top: 700px; left: 6px; right: 6px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.grid img, .grid .ph { width: 100%; aspect-ratio: 3 / 4; object-fit: cover; }
.grid .ph { background: #11141d; display: flex; align-items: center; justify-content: center; text-align: center; font: 52px/1.1 Anton; color: #555; }
.feed { position: absolute; top: 1240px; width: 100%; display: flex; justify-content: center; gap: 80px; }
.feed div { display: flex; align-items: center; gap: 22px; font: 800 40px Inter; color: #888; }
.feed img { width: 150px; height: 150px; border-radius: 50%; } .feed img.s { width: 72px; height: 72px; }`);

(async () => {
  const b = await chromium.launch();
  const shot = async (html, out, w, h) => {
    const tmp = path.join(DIR, `.tmp_${path.basename(out, ".png")}.html`);
    fs.writeFileSync(tmp, html);
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto("file://" + tmp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    await p.screenshot({ path: out }); await p.close(); fs.unlinkSync(tmp);
    console.log(path.relative(process.cwd(), out));
  };
  const out = n => path.join(DIR, n);
  await shot(avatarAB, out("avatar_1_ab.png"), 1080, 1080);
  await shot(avatarPortes, out("avatar_2_portes.png"), 1080, 1080);
  await shot(avatarTexte, out("avatar_3_texte.png"), 1080, 1080);
  await shot(cover("MON", "LOUP", "PARTIE 1", out("decor_mon_loup_p1.png")), out("couverture_mon_loup_p1.png"), 1080, 1920);
  await shot(apercu([out("avatar_1_ab.png"), out("avatar_2_portes.png"), out("avatar_3_texte.png")], out("couverture_mon_loup_p1.png")),
             out("apercu_profil.png"), 1080, 1500);
  await b.close();
})();
