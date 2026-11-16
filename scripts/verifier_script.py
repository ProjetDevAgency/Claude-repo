"""Contrôle d'un script .dial AVANT de faire la vidéo (méthode v3 + règle 8/8).

    python3 scripts/verifier_script.py scripts/modele/22_valise_cassee.dial

Vérifie ce qui se mesure : longueur (60-65 s), ponctuation interdite, négations en « ne », phrases trop longues,
montant en toutes lettres dans la 1re phrase, objet nommé dans la 1re phrase, montant du hook repris dans la chute.
Le reste (les 8 critères de la machine à sujets, la règle de loi vérifiée) se coche à la main dans l'en-tête du .dial.
"""
import re
import sys

NOMBRES = r"\b(cent|cents|mille|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt|trente|quarante|cinquante|soixante)\b"


def verifier(chemin):
    lignes = [l.rstrip("\n") for l in open(chemin, encoding="utf-8")]
    rep = [(l[0], l[3:]) for l in lignes if l[:2] in ("M:", "N:")]
    texte = " ".join(t for _, t in rep)
    ok, ko = [], []

    n = len(texte)
    (ok if 1440 <= n <= 1600 else ko).append(f"longueur {n} caractères (cible 1 450 à 1 550, ≈ 62 s)")
    interdits = [c for c in ":;…«»()—" if c in texte]
    (ok if not interdits else ko).append(f"ponctuation interdite : {interdits or 'aucune'}")
    ne = re.findall(r"\bn['e]\s\w+", texte)
    (ok if not ne else ko).append(f"négations en « ne » : {ne or 'aucune'}")
    longues = [s for _, t in rep for s in re.split(r"(?<=[.?!])\s+", t) if len(s.split()) > 25]
    (ok if not longues else ko).append(f"phrases de plus de 25 mots : {len(longues)}")

    hook = rep[0][1] if rep else ""
    premiere = re.split(r"(?<=[.?!])\s+", hook)[0]
    a_montant = bool(re.search(NOMBRES, premiere.lower())) and "euro" in premiere.lower()
    (ok if a_montant else ko).append(f"montant en euros dans la 1re phrase : « {premiere} »")
    mots = [m for m in re.findall(r"[a-zàâçéèêëîïôûùüÿœ'-]+", premiere.lower())
            if not re.fullmatch(NOMBRES, m) and m not in ("euros", "euro", "de", "tu", "me", "t'as", "le", "la", "les",
                                                             "ton", "ta", "tes", "un", "une", "des", "et", "sur", "pour",
                                                             "sinon", "chacun", "je", "mets", "paies", "dépensé")]
    ko_obj = len(mots) < 1
    (ko if ko_obj else ok).append(f"objet nommé dans la 1re phrase : {mots[:4]}")

    chute = rep[-1][1] if rep else ""
    m = re.search(rf"((?:{NOMBRES[2:-2]})(?:[ -](?:{NOMBRES[2:-2]}))*) euros", hook.lower())
    reprise = bool(m and m.group(1) in chute.lower())
    (ok if reprise else ko).append(f"montant du hook repris dans la chute : {m.group(1) if m else '?'}")

    print(f"── {chemin}")
    for x in ok:
        print("  ✅", x)
    for x in ko:
        print("  ❌", x)
    print("  À vérifier à la main : les 8 critères (en-tête du .dial), la règle de loi sourcée, le hook clair en 2 s.")
    return not ko


if __name__ == "__main__":
    bons = [verifier(c) for c in sys.argv[1:]]
    sys.exit(0 if all(bons) else 1)
