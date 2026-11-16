"""Vérifie un script « survie à toi de choisir » contre les règles mesurables du moteur S1.

    python tueur/verifier.py tueur/scripts/mon_loup_p1.txt

Format attendu (BLOC 11 du moteur) :
    PARTIE 1 — TITRE
    NARRATEUR > Deux heures quatorze. On frappe à ta porte.
    [TROIS COUPS]
    VOIX DERRIÈRE LA PORTE > Ouvre, mon loup.
    [PAUSE]
"""
import re
import sys
from pathlib import Path

INTERDITS = ["effrayant", "terrifiant", "terrifié", "horrible", "angoissant", "glaçant", "mystérieux",
             "étrange", "sinistre", "cauchemar", "frisson", "surnaturel", "entité", "présence"]
CTA = ["abonne", "commentaire", "commente", "like", "partage", "follow", "lien en bio"]
PRISES = ["pancake", "trente-trois", "3 h 33", "3h33", "fenêtre d'en face", "immeuble d'en face"]
PONCT = re.compile(r"[:;—–()«»\"…]|(?<!\w)-(?!\w)|[\U0001F300-\U0001FAFF]")
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
    sents = [s for _, t in voice for s in sentences(t)]
    words = [len(s.split()) for s in sents]
    total = sum(words)
    narr = " ".join(t for w, t in voice if w == "NARRATEUR")
    menace = {w for w, _ in voice if w != "NARRATEUR"}
    suite = bool(head and re.search(r"PARTIE\s+([2-9]|\d{2})", head, re.I))
    res = []

    def ok(cond, label, detail="", warn=False):
        res.append(("✓" if cond else ("⚠" if warn else "✗"), label, detail))

    ok(head is not None, "Ligne de titre PARTIE N", head or "manquante")
    ok(not [t for w, t in lines if w == "?"], "Chaque ligne a une voix ou est un bruitage",
       "; ".join(t for w, t in lines if w == "?")[:80])
    lo, hi = (145, 165) if suite else (155, 180)
    ok(lo <= total <= hi, f"Longueur {lo}-{hi} mots", f"{total} mots ≈ {total / 2.3:.0f} s à 2,3 mots/s")
    ok(total / 2.3 >= 61, "Au moins 61 secondes estimées", f"{total / 2.3:.0f} s")
    avg = total / max(1, len(words))
    ok(4.0 <= avg <= 7.5, "Moyenne 4-7 mots par phrase", f"{avg:.1f}", warn=True)
    long = [s for s in sents if len(s.split()) > 16]
    ok(not long, "Aucune phrase de plus de 16 mots", " | ".join(long)[:120])
    frag = sum(1 for n in words if n <= 3)
    ok(frag >= 8, "Au moins 8 fragments (3 mots ou moins)", str(frag))
    n2 = len(DEUXIEME.findall(narr))
    ok(n2 >= 10, "Narrateur à la 2e personne", f"{n2} tu/te/ta/ton/tes/toi")
    je = re.findall(r"\b(je|j'|vous)\b", narr, re.I)
    ok(not je, "Narrateur sans je ni vous", ", ".join(je))
    neg = [t for w, t in voice if NEG_NE.search(t) and w == "NARRATEUR"]
    ok(not neg, "Négation sans ne (narrateur)", " | ".join(neg)[:120])
    bad = [t for _, t in voice if PONCT.search(t)]
    ok(not bad, "Ponctuation autorisée seulement (. , ? !)", " | ".join(bad)[:120])
    excl = sum(t.count("!") for _, t in voice)
    ok(excl <= 2, "Deux points d'exclamation maximum", str(excl))
    low = " ".join(t for _, t in voice).lower()
    found = [m for m in INTERDITS if re.search(r"\b" + m + r"\b", low)]
    ok(not found, "Aucun mot qui nomme la peur", ", ".join(found))
    first2 = " ".join(sentences(" ".join(t for _, t in voice))[:2])
    if suite:
        ok(re.search(r"\bchoisi\b", first2, re.I) is not None, "Suite : rappel + vote dans les 2 premières phrases", first2[:100])
    else:
        ok(HEURE.search(first2) is not None, "Partie 1 : l'heure dans les 2 premières phrases", first2[:100])
    ok(len(voice) - sum(1 for w, _ in voice if w == "NARRATEUR") >= 3, "Au moins 3 répliques hors narrateur",
       str(len(voice) - sum(1 for w, _ in voice if w == "NARRATEUR")))
    ok(len(menace) >= 2, "Au moins 2 voix hors narrateur", ", ".join(sorted(menace)))
    last = voice[-1][1] if voice else ""
    ok(last.endswith("?") and re.search(r"\bou\b", last, re.I) is not None, "Dernière phrase = question A ou B", last)
    ok(4 <= len(last.split()) <= 14, "Question finale de 4 à 14 mots", str(len(last.split())))
    cta = [c for c in CTA if c in low]
    ok(not cta, "Aucun appel à l'action dans la voix", ", ".join(cta))
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
