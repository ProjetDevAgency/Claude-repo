"""Vérifie un script « survie à toi de choisir » contre les règles mesurables du moteur S1 (v2, construit
sur les critères du moteur H1).

    python tueur/verifier.py tueur/scripts/mon_loup_p1.txt

Format attendu (BLOC 11 du moteur) :
    PARTIE 1 — TITRE
    NARRATEUR > Deux heures quatorze. On frappe à ta porte.
    [TROIS COUPS]
    VOIX DERRIÈRE LA PORTE > Ouvre, mon loup.
    [PAUSE]

Ce qu'il peut pas vérifier (le sens, le twist, le test de la banane…) reste dans l'auto-check du moteur.
"""
import re
import sys
from pathlib import Path

PEUR = ["effrayant", "terrifiant", "terrifié", "terrifiée", "horrible", "angoissant", "glaçant", "mystérieux",
        "étrange", "sinistre", "cauchemar", "frisson", "surnaturel", "entité", "présence", "paranormal",
        "funeste", "lugubre", "macabre", "ténèbres", "effroi", "épouvante", "sépulcral", "pétrifié", "panique"]
ECRIT = ["néanmoins", "toutefois", "par conséquent", "en outre", "de plus", "ainsi", "cependant", "dès lors",
         "en effet", "soudain", "tout à coup"]
ANGLICISMES = ["basiquement", "définitivement", "impacter", "challenge", "ça fait sens", "en charge de",
               "attends de voir", "je peux pas croire", "laisse-moi te dire", "devient intéressant"]
ANNONCES = ["je t'explique", "je vous explique", "écoute bien", "jusqu'à la fin", "histoire vraie",
            "âmes sensibles", "storytime", "je vais te raconter", "tu vas pas croire"]
CTA = ["abonne", "commentaire", "commente", "like", "partage", "follow", "lien en bio", "écris a ou b"]
PRISES = ["pancake", "trente-trois", "3 h 33", "3h33", "fenêtre d'en face", "immeuble d'en face"]
MENT_OK = {"doucement", "lentement", "exactement", "carrément", "tranquillement", "brusquement"}
MENT_NOMS = {"moment", "comment", "appartement", "bâtiment", "logement", "vêtement", "médicament", "événement",
             "évènement", "monument", "instrument", "argument", "élément", "ment", "dément", "aliment", "ciment",
             "serment", "sentiment", "traitement", "jugement", "régiment", "segment", "gouvernement", "tourment"}
RELANCES = ["sauf que", "et pourtant", "mais alors", "sur le papier", "ce que peu de gens savent"]
PLU_FAUX = re.compile(r"\bplus (là|rien|personne|jamais|un bruit|une|un)\b", re.I)
PONCT = re.compile(r"[:;—–()«»\"…\[\]/*#]|(?<!\w)-(?!\w)|[\U0001F300-\U0001FAFF]")
DEUXIEME = re.compile(r"\b(tu|te|ta|ton|tes|toi)\b|\bt'", re.I)
NEG_NE = re.compile(r"\b(ne|n')\b|\bn'", re.I)
HEURE = re.compile(r"\b(heures?|minuit|midi)\b|\d{1,2}\s?h\s?\d{0,2}", re.I)


def parse(text):
    head, lines = None, []
    for raw in text.splitlines():
        l = raw.strip()
        if not l:
            continue
        if l.upper().startswith("PARTIE") and ">" not in l:
            head = l
        elif l.startswith("[") and l.endswith("]"):
            lines.append(("SFX", l[1:-1].strip()))
        elif ">" in l:
            who, txt = l.split(">", 1)
            lines.append((who.strip().upper(), txt.strip()))
        else:
            lines.append(("?", l))
    return head, lines


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", t) if s.strip()]


def check(path):
    head, lines = parse(Path(path).read_text(encoding="utf-8"))
    voice = [(w, t) for w, t in lines if w not in ("SFX", "?")]
    sfx = [t for w, t in lines if w == "SFX"]
    allsent = sentences(" ".join(t for _, t in voice))
    words = [len(s.split()) for s in allsent]
    chars = len(" ".join(t for _, t in voice))
    narr = " ".join(t for w, t in voice if w == "NARRATEUR")
    narr_sent = [s for w, t in voice if w == "NARRATEUR" for s in sentences(t)]
    others = {w for w, _ in voice if w != "NARRATEUR"}
    low = " ".join(t for _, t in voice).lower()
    suite = bool(head and re.search(r"PARTIE\s+([2-9]|\d{2})", head, re.I))
    res = []

    def ok(cond, label, detail="", warn=False):
        res.append(("✓" if cond else ("⚠" if warn else "✗"), label, detail))

    # forme
    ok(head is not None, "Ligne de titre PARTIE N", head or "manquante")
    ok(not [t for w, t in lines if w == "?"], "Chaque ligne a une voix ou est un bruitage",
       "; ".join(t for w, t in lines if w == "?")[:80])
    # budget (7.1)
    lo, hi = (1050, 1150) if suite else (1050, 1250)
    ok(chars >= 1050, "Au moins 1 050 caractères de voix (plancher)", f"{chars} caractères")
    ok(lo <= chars <= hi, f"Budget {lo} à {hi} caractères", f"{chars} caractères", warn=True)
    est = 11 + chars / 21
    ok(est >= 61, "Au moins 61 secondes estimées (voix resserrée)", f"≈ {est:.0f} s")
    # langue (BLOC 1)
    avg = sum(words) / max(1, len(words))
    ok(4.0 <= avg <= 7.0, "Moyenne 4 à 7 mots par phrase", f"{avg:.1f}", warn=True)
    long = [s for s in allsent if len(s.split()) > 16]
    ok(not long, "Aucune phrase de plus de 16 mots", " | ".join(long)[:120])
    frag = sum(1 for n in words if n <= 3)
    ok(frag >= 8, "Au moins 8 fragments (3 mots ou moins)", str(frag))
    n2 = len(DEUXIEME.findall(narr))
    ok(n2 >= 10, "Narrateur à la 2e personne", f"{n2} tu/te/ta/ton/tes/toi")
    je = re.findall(r"\b(je|j'|vous)\b", narr, re.I)
    ok(not je, "Narrateur sans je ni vous", ", ".join(je))
    neg = [t for w, t in voice if NEG_NE.search(t) and w == "NARRATEUR"]
    ok(not neg, "Négation sans ne (narrateur)", " | ".join(neg)[:120])
    plu = PLU_FAUX.findall(low)
    ok(not plu, "« plu » sans S quand ça veut dire ne plus", ", ".join("plus " + p for p in plu))
    bad = [t for _, t in voice if PONCT.search(t)]
    ok(not bad, "Ponctuation autorisée seulement (. , ? !)", " | ".join(bad)[:120])
    excl = sum(t.count("!") for _, t in voice)
    ok(excl <= 1, "Un point d'exclamation maximum", str(excl))
    ec = [m for m in ECRIT if re.search(r"\b" + m + r"\b", low)]
    ok(not ec, "Aucun connecteur d'écrit (1.5)", ", ".join(ec))
    an = [m for m in ANGLICISMES if m in low]
    ok(not an, "Aucun anglicisme ni tournure de traduction (1.1)", ", ".join(an))
    found = [m for m in PEUR if re.search(r"\b" + m + r"\b", low)]
    ok(not found, "Aucun mot zombie ni mot qui nomme la peur (1.7)", ", ".join(found))
    ment = sorted({w for w in re.findall(r"\b\w+ment\b", low) if w not in MENT_OK and w not in MENT_NOMS})
    ok(not ment, "Aucun adverbe en -ment hors des six tolérés", ", ".join(ment), warn=True)
    ann = [a for a in ANNONCES if a in low]
    ok(not ann, "Aucune annonce ni « je t'explique » (1.23)", ", ".join(ann))
    # hook (BLOC 3)
    ok(bool(lines) and lines[0][0] not in ("SFX", "?"), "Hook : la voix démarre à 0 s (rien avant la 1re réplique)",
       lines[0][1][:60] if lines else "")
    n1 = len(allsent[0].split()) if allsent else 0
    ok(n1 <= 14, "Hook couche 1 : 14 mots maximum", f"{n1} mots : {allsent[0] if allsent else ''}")
    first4 = " ".join(allsent[:4])
    if suite:
        ok(re.search(r"\bchoisi\b", first4, re.I) is not None, "Suite : le vote dans les 4 premières phrases", first4[:100])
        ok(not re.search(r"\bchoisi\b", allsent[0] if allsent else "", re.I),
           "Suite : le vote est pas la 1re phrase (rappel-choc d'abord)", allsent[0] if allsent else "", warn=True)
    else:
        ok(HEURE.search(first4) is not None, "Partie 1 : l'heure dans les 4 premières phrases", first4[:100])
    # voix et chaîne (1.4, 1.13)
    ok(len(voice) - sum(1 for w, _ in voice if w == "NARRATEUR") >= 3, "Au moins 3 répliques hors narrateur",
       str(len(voice) - sum(1 for w, _ in voice if w == "NARRATEUR")))
    ok(len(others) >= 2, "Au moins 2 voix hors narrateur", ", ".join(sorted(others)))
    q_avant = [s for s in narr_sent[:-1] if s.endswith("?") and (re.search(r"\bou\b", s, re.I) or re.search(r"tu crois|et toi", s, re.I))]
    ok(not q_avant, "Aucune question au viewer avant la dernière (1.13, règle 5)", " | ".join(q_avant)[:120])
    rel = [next((r for r in RELANCES if s.lower().startswith(r)), None) for s in narr_sent]
    rel = [r for r in rel if r]
    rep = [a for a, b in zip(rel, rel[1:]) if a == b]
    ok(not rep, "Jamais deux relances de suite avec le même mot", ", ".join(rep))
    ok(rel.count("mais alors") <= 2 and rel.count("ce que peu de gens savent") <= 1,
       "« Mais alors » deux fois max, le savoir caché une fois", f"{rel.count('mais alors')} / {rel.count('ce que peu de gens savent')}")
    # choix final (0.4, 6.4)
    last = voice[-1][1] if voice else ""
    ok(last.endswith("?") and re.search(r"\bou\b", last, re.I) is not None, "Dernière phrase = question A ou B", last)
    ok(4 <= len(last.split()) <= 14, "Question finale de 4 à 14 mots", str(len(last.split())))
    cta = [c for c in CTA if c in low]
    ok(not cta, "Aucun appel à l'action dans la voix (0.4)", ", ".join(cta))
    # rythme (7.2)
    pauses = sum(1 for t in sfx if t.upper() == "PAUSE")
    ok(2 <= pauses <= 4, "Trois pauses", str(pauses), warn=True)
    bruits = len(sfx) - pauses
    ok(4 <= bruits <= 8, "4 à 8 bruitages", str(bruits), warn=True)
    prises = [p for p in PRISES if p in low]
    ok(not prises, "Pas d'histoire déjà prise", ", ".join(prises))

    print(f"\n{path}\n")
    for s, label, d in res:
        print(f"  {s} {label}" + (f"  ({d})" if d else ""))
    errs = sum(1 for s, _, _ in res if s == "✗")
    print(f"\n  {'OK' if not errs else str(errs) + ' point(s) à corriger'}\n")
    return errs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(1 if sum(check(p) for p in sys.argv[1:]) else 0)
