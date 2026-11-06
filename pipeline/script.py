"""Écriture des scripts avec tes deux prompts + contrôle automatique des règles.

    # 20 sujets pour ta niche (prompt « Machine à sujets »)
    python -m pipeline.script sujets

    # Script complet (moteur H1) à partir d'un hook + sujet, en regardant la vidéo
    python -m pipeline.script ecrire --hook "..." --sujet "..." --video library/raw/123.mp4 --out scripts/mon_script.txt

    # Vérifier un script écrit à la main
    python -m pipeline.script verifier scripts/mon_script.txt

La génération utilise l'API Claude (variable ANTHROPIC_API_KEY). Sans clé,
tu peux coller les PDF dans claude.ai, récupérer le script et le mettre
dans scripts/. Le contrôle des règles marche sans clé.
"""
import argparse
import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .common import ROOT, duration, load_config

PROMPTS = ROOT / "prompts"

APP_MODE = """
════════════════════════════════════════════════════════════════════════
MODE APPLICATION
════════════════════════════════════════════════════════════════════════
Tu es appelé par l'application, pas par une personne. Le BLOC 0 et le
BLOC 10 du moteur s'appliquent, le bloc C1 « en conversation » ne
s'applique pas : tu ne poses aucune question. Tu rends uniquement le
script, du premier mot du hook au dernier mot de la chute, sans bloc de
code, sans titre, sans annotation.
"""


# ───────────────────────────── contrôle des règles ─────────────────────────────

FORBIDDEN_PUNCT = {"-": "tiret", "—": "tiret cadratin", "–": "tiret", ":": "deux-points",
                   ";": "point-virgule", "(": "parenthèse", ")": "parenthèse",
                   "[": "crochet", "]": "crochet", "…": "points de suspension",
                   "\"": "guillemets", "«": "guillemets", "»": "guillemets", "/": "slash",
                   "*": "astérisque", "#": "dièse", "&": "esperluette", "€": "symbole €"}

# connecteurs d'écrit : interdits en début de phrase ou de proposition
WRITTEN_CONNECTORS = ["néanmoins", "toutefois", "par conséquent", "en outre", "de plus",
                      "cependant", "dès lors", "en effet", "ainsi"]

FORBIDDEN_WORDS = [
    "abonne", "abonnez", "follow", "like", "commente", "partage", "lien en bio",
    "partie 2", "je vous explique", "laissez-moi", "attendez", "écoutez bien",
    "basiquement", "définitivement", "réaliser", "impacter", "challenge", "ça fait sens",
    "bouleversant", "émouvant", "magique", "inoubliable",
    "algorithme", "viral", "mes abonnés", "ma communauté", "déclara", "s'exclama",
    "rétorqua", "minutieux", "méticuleux", "sublime", "exquis", "savoir-faire ancestral",
]


def check(script: str, duration_target=60, real_voice=False):
    """Retourne (ok, liste de messages). Contrôle mécanique, pas un jugement d'écriture."""
    issues, info = [], []
    text = re.sub(r"\s+", " ", script.strip())
    n = len(text)
    if duration_target >= 55:
        lo, hi = (1600, 1800) if real_voice else (1350, 1500)
        best = "1 450 à 1 500" if not real_voice else "1 600 à 1 800"
    else:
        lo, hi, best = 950, 1150, "950 à 1 050"
    info.append(f"{n} caractères (cible {best})")
    if n < lo or n > hi + 60:
        issues.append(f"longueur hors budget : {n} caractères")
    for ch, name in FORBIDDEN_PUNCT.items():
        # le tiret court est toléré dans les mots composés (peut-être, c'est-à-dire)
        if ch == "-":
            bad = re.findall(r"(?:^|\s)-|-(?:\s|$)", text)
            if bad:
                issues.append("tiret utilisé comme ponctuation")
            continue
        if ch in text:
            issues.append(f"ponctuation interdite : {name}")
    if text.count("!") > 1:
        issues.append(f"{text.count('!')} points d'exclamation (1 maximum)")
    if re.search(r"\b1\b", text):
        issues.append("chiffre 1 utilisé (écrire « un » / « une »)")
    if re.search(r"\d+\s*(euros?|€)", text):
        issues.append("montant en chiffres : l'écrire en toutes lettres")
    low = text.lower()
    for w in FORBIDDEN_WORDS:
        if re.search(r"(?<![a-zà-ÿ])" + re.escape(w) + r"(?![a-zà-ÿ])", low):
            issues.append(f"mot ou tournure interdite : « {w} »")
    for w in WRITTEN_CONNECTORS:
        if re.search(r"(?:^|[.?!,]\s+)" + re.escape(w) + r"\b", low):
            issues.append(f"connecteur d'écrit : « {w} »")
    negs = re.findall(r"\b(?:ne|n')\s?\w+\s+(?:pas|plus|rien|jamais|personne)\b", low)
    if negs:
        issues.append(f"négation avec « ne » : {negs[:3]} (une seule tolérée pour caractériser)")
    sentences = [s for s in re.split(r"(?<=[.?!])\s+", text) if s]
    if sentences and len(sentences[0].split()) > 18:
        issues.append(f"hook trop long : {len(sentences[0].split())} mots (18 maximum)")
    long_ones = [s for s in sentences if len(s.split()) > 25]
    if len(long_ones) > 1:
        issues.append(f"{len(long_ones)} phrases de plus de 25 mots (1 maximum)")
    words_per = [len(s.split()) for s in sentences]
    if words_per:
        info.append(f"{len(sentences)} phrases, {sum(words_per) / len(words_per):.1f} mots en moyenne")
    return (not issues), issues, info


# ───────────────────────────── génération via l'API ─────────────────────────────

def _frames_b64(video, n=6):
    """Quelques images de la vidéo pour que Claude écrive sans contredire l'image."""
    d = duration(video)
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for k in range(n):
            t = d * (k + 0.5) / n
            p = Path(tmp) / f"f{k}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                            "-frames:v", "1", "-vf", "scale=432:-2", "-q:v", "4", str(p)], check=True)
            out.append(base64.b64encode(p.read_bytes()).decode())
    return out


def _client():
    import anthropic
    return anthropic.Anthropic()


def _ask(system_text, user_content, model, max_tokens=16000):
    client = _client()
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        # le long prompt système est mis en cache : les appels suivants coûtent ~10x moins cher
        system=[{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason == "refusal":
        raise RuntimeError("Claude a refusé cette demande : reformule le sujet.")
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def write_script(hook, sujet, video=None, description=None, cfg=None, moteur=None):
    cfg = cfg or load_config()["script"]
    moteur = moteur or cfg.get("moteur", "h1")
    base = "moteur_doc.md" if moteur == "doc" else "moteur_script.txt"
    system = ((PROMPTS / base).read_text(encoding="utf-8") + APP_MODE
              + "\n\n" + (PROMPTS / "consignes_compte.md").read_text(encoding="utf-8"))
    lines = [f"[HOOK] {hook}" if hook else "[HOOK] aucun, choisis le meilleur gabarit de l'annexe A",
             f"[SUJET] {sujet}",
             f"[NICHE] {cfg['niche']}",
             f"[AUDIENCE] {cfg['audience']}",
             f"[VOIX] {cfg['voice_type']}",
             "[DURÉE] 60 secondes"]
    if description:
        lines.append(f"[DESCRIPTION VIDÉO] {description}")
    content = []
    if video:
        for b64 in _frames_b64(video):
            content.append({"type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}})
        lines.append("[DESCRIPTION VIDÉO] Les images jointes sont extraites de la vidéo, dans "
                     "l'ordre. Ne contredis jamais ce qu'elles montrent et ne décris pas les gestes "
                     "visibles.")
    content.append({"type": "text", "text": "\n".join(lines)})
    script = _ask(system, content, cfg["model"])
    script = script.strip("`").strip()
    # une passe de correction si le contrôle mécanique échoue
    ok, issues, _ = check(script)
    if not ok:
        fix = (f"Voici ton script :\n\n{script}\n\nLe contrôle automatique relève : "
               f"{'; '.join(issues)}. Corrige uniquement ces points, garde l'histoire, et rends "
               "le script seul.")
        script = _ask(system, [{"type": "text", "text": fix}], cfg["model"]).strip("`").strip()
    return script


def subjects(niche_description, cfg=None):
    cfg = cfg or load_config()["script"]
    system = ((PROMPTS / "machine_a_sujets.txt").read_text(encoding="utf-8") + "\n\n"
              + (PROMPTS / "consignes_compte.md").read_text(encoding="utf-8"))
    return _ask(system, [{"type": "text", "text": niche_description}], cfg["model"])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sujets")
    s.add_argument("--niche", default=None)
    w = sub.add_parser("ecrire")
    w.add_argument("--hook", default="")
    w.add_argument("--sujet", required=True)
    w.add_argument("--video")
    w.add_argument("--description")
    w.add_argument("--out", required=True)
    v = sub.add_parser("verifier")
    v.add_argument("fichier")
    args = ap.parse_args()

    if args.cmd == "verifier":
        ok, issues, info = check(Path(args.fichier).read_text(encoding="utf-8"))
        print("\n".join(info))
        print("OK ✅" if ok else "À corriger :\n - " + "\n - ".join(issues))
        sys.exit(0 if ok else 1)
    if args.cmd == "sujets":
        cfg = load_config()["script"]
        print(subjects(args.niche or f"Le métier : {cfg['niche']}"))
    if args.cmd == "ecrire":
        txt = write_script(args.hook, args.sujet, args.video, args.description)
        Path(args.out).write_text(txt + "\n", encoding="utf-8")
        ok, issues, info = check(txt)
        print(txt, "\n\n" + "\n".join(info))
        if not ok:
            print("Encore à corriger :\n - " + "\n - ".join(issues))


if __name__ == "__main__":
    main()
