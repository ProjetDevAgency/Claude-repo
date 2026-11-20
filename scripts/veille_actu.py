"""Veille d'actu sur les comptes TikTok que regardent nos spectateurs (onglet « Spectateurs » de TikTok Studio, 20 nov.).
Liste leurs dernières vidéos (titre, vues, date), garde celles des 3 derniers jours, repère celles qui parlent d'argent,
et écrit prompts/veille_actu.md (réécrit à chaque lancement).

    python3 scripts/veille_actu.py            (≈ 3 à 6 min)

On reprend le SUJET (un fait d'actu, vérifié dans 2 sources), jamais leurs images, leur texte ou leur logo.
"""
import json
import re
import subprocess
import time
from pathlib import Path

COMPTES = ["hugodecrypte", "tf1info", "bfmtv", "franceinfo", "leparisien", "loopsider", "brut", "m6info", "ulyces"]
PAR_COMPTE = 40
JOURS = 3
ARGENT = re.compile(r"(€|euros?\b|prix|salaire|smic|imp[ôo]t|taxe|tva|loyer|logement|retraite|bourse|action|crypto|bitcoin|"
                    r"banque|livret|[ée]pargne|cr[ée]dit|caf\b|apl|aide|prime|allocation|ch[ôo]mage|facture|[ée]lectricit|"
                    r"gaz|carburant|essence|gazole|budget|inflation|pouvoir d.achat|soldes|black friday|arnaque|escroquer|"
                    r"amende|p[ée]age|abonnement|forfait|assurance|mutuelle|travail|gr[èe]ve|licenci|entreprise|ipo|"
                    r"milliard|million|co[ûu]t|cher|gratuit|rembours|frais|tarif|hausse|baisse)", re.I)


def videos(compte):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--playlist-end", str(PAR_COMPTE), "-J",
                        f"https://www.tiktok.com/@{compte}"], capture_output=True, text=True, timeout=240)
    try:
        return json.loads(r.stdout).get("entries", []) or []
    except Exception:
        return []


def main():
    limite = time.time() - JOURS * 86400
    lignes, toutes = [], []
    for c in COMPTES:
        es = videos(c)
        if not es:
            lignes.append(f"- @{c} : illisible aujourd'hui")
            continue
        for e in es:
            ts = e.get("timestamp") or 0
            if ts < limite:
                continue
            titre = " ".join((e.get("title") or e.get("description") or "").split())
            toutes.append(dict(compte=c, vues=e.get("view_count") or 0, ts=ts, titre=titre, url=e.get("url") or "",
                               argent=bool(ARGENT.search(titre))))
    toutes.sort(key=lambda x: -x["vues"])
    date = time.strftime("%d/%m/%Y %H:%M")
    out = [f"# Veille actu — {date} (vidéos des {JOURS} derniers jours, triées par vues)", "",
           "Comptes que regardent nos spectateurs. On reprend le SUJET, vérifié dans 2 sources, jamais leurs images.", ""]
    out += ["## Sujets argent", "", "| vues | compte | date | titre |", "|---|---|---|---|"]
    for v in [x for x in toutes if x["argent"]][:30]:
        out.append(f"| {v['vues']:,} | @{v['compte']} | {time.strftime('%d/%m %Hh', time.localtime(v['ts']))} | {v['titre'][:140]} |".replace(",", " "))
    out += ["", "## Les plus vues, tous sujets (pour repérer ce dont tout le monde parle)", "", "| vues | compte | titre |",
            "|---|---|---|"]
    for v in toutes[:15]:
        out.append(f"| {v['vues']:,} | @{v['compte']} | {v['titre'][:140]} |".replace(",", " "))
    if lignes:
        out += ["", "## Comptes non lus", ""] + lignes
    Path("prompts/veille_actu.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(toutes)} vidéos lues, {sum(x['argent'] for x in toutes)} sur l'argent → prompts/veille_actu.md")


if __name__ == "__main__":
    main()
