// Étape 2 : rend la scène 3D image par image et assemble la vidéo avec l'audio.
//   node tueur/render.js [sortie.mp4] [--ep mon_loup_p2] [--preview t1,t2,...] [--sans-ui] [--fps 30]
// Par défaut la vidéo va dans output/<sortie de l'épisode>.mp4
const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const BUILD = path.join(__dirname, "build");
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const FPS = Number(opt("--fps", 30));
const preview = opt("--preview", null);
const EP = opt("--ep", null);  // l'épisode : le dossier build/<sortie> (par défaut, le plus récent)
const sansUI = args.includes("--sans-ui");  // images du décor seul, pour les couvertures

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".ttf": "font/ttf", ".json": "application/json" };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split("?")[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, r));
  const port = server.address().port;
  const eps = fs.readdirSync(BUILD).filter(d => fs.existsSync(path.join(BUILD, d, "timeline.json")))
    .sort((a, b) => fs.statSync(path.join(BUILD, b, "timeline.json")).mtimeMs - fs.statSync(path.join(BUILD, a, "timeline.json")).mtimeMs);
  const EPDIR = path.join(BUILD, EP || eps[0]);
  const tl = JSON.parse(fs.readFileSync(path.join(EPDIR, "timeline.json"), "utf8"));
  const out = args[0] && !args[0].startsWith("--") ? args[0] : path.join(ROOT, "output", (tl.sortie || "episode") + ".mp4");
  const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", e => console.error("PAGE:", e.message));
  page.on("console", m => m.type() === "error" && console.error("CONSOLE:", m.text()));
  await page.goto(`http://localhost:${port}/tueur/scene.html`);
  await page.waitForFunction(() => window.ready === true);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(tl => window.setup(tl), tl);

  if (preview) {
    fs.mkdirSync(path.join(EPDIR, "preview"), { recursive: true });
    for (const t of preview.split(",").map(Number)) {
      await page.evaluate(t => window.renderAt(t), t);
      if (sansUI) await page.evaluate(() => { document.getElementById("ui").style.display = "none"; });
      const f = path.join(EPDIR, "preview", `${sansUI ? "decor_" : ""}t${t.toFixed(1)}.${sansUI ? "png" : "jpg"}`);
      await page.screenshot(sansUI ? { path: f, type: "png" } : { path: f, type: "jpeg", quality: 85 });
      console.log(f);
    }
  } else {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const n = Math.ceil(tl.duration * FPS);
    const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
      "-i", path.join(EPDIR, "audio.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
      "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => window.renderAt(t), i / FPS);
      const buf = await page.screenshot({ type: "jpeg", quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      if (i % 60 === 0) console.log(`image ${i}/${n}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on("close", r));
    console.log("vidéo ->", out);
  }
  await browser.close(); server.close();
})();
