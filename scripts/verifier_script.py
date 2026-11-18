"""Contrôle d'un script .dial AVANT de faire la vidéo : moteur H1 complet (prompts/methode/moteur_script_H1.pdf)
+ règles maison (zone grise, doute). Le prix dans l'accroche est FACULTATIF : s'il y en a un, il est dans la
1re phrase, jamais en 1er mot, avant l'objet, et revient à l'identique dans la chute (2 fois en tout).

    python3 scripts/verifier_script.py scripts/modele/27_carte_piratee.dial

Vérifie tout ce qui se compte. Le reste (casting TIER S/A, twist W1-W6, test de la banane, dette du hook) se décide
avant d'écrire et se note dans l'en-tête du .dial ; le script affiche ces lignes à relire à la fin.
"""
import re
import sys

NB = r"(?:cent|cents|mille|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|" \
     r"vingt|trente|quarante|cinquante|soixante)"
MONTANT = rf"({NB}(?:[ -]{NB})*) euros"
INTERDITS = ["avocat", "illégal", "porter plainte", "poursuites", "diffamation", "injuste", "irrespectueux", "humiliant",
             "minutieux", "méticuleux", "sublime", "exquis", "remarquable", "prestation", "premium", "haut de gamme",
             "optimiser", "valoriser", "algorithme", "abonnés", "abonne", "commentaire", "partage", "la vidéo",
             "bouleversant", "émouvant", "magique", "inoubliable", "précieux", "néanmoins", "toutefois",
             "par conséquent", "en outre", "de plus,", "ainsi,", "cependant", "dès lors", "en effet", "je vous explique",
             "attendez", "écoutez bien", "laissez-moi", "basiquement", "impacter", "challenge", "ça fait sens"]
MENT_OK = {"honnêtement", "franchement", "exactement", "doucement", "carrément", "tranquillement"}
MENT_NOMS = {"moment", "comment", "paiement", "appartement", "remboursement", "prélèvement", "logement", "gouvernement",
             "changement", "enterrement", "département", "comportement", "traitement", "équipement", "argument",
             "document", "élément", "segment", "ment", "jument", "serment", "aliment", "vêtement", "bâtiment",
             "signalement", "embarquement", "règlement", "versement", "jugement", "établissement", "testament"}


def phrases(t):
    return [s for s in re.split(r"(?<=[.?!])\s+", t.strip()) if s]


def mots(s):
    return re.findall(r"[\wÀ-ÿ'-]+", s)


def verifier(chemin):
    lignes = [l.rstrip("\n") for l in open(chemin, encoding="utf-8")]
    rep = [(l[0], l[3:].strip()) for l in lignes if l[:2] in ("M:", "N:")]
    texte = " ".join(t for _, t in rep)
    bas = texte.lower()
    narr = " ".join(t for k, t in rep if k == "N").lower()
    ok, ko = [], []

    def test(cond, msg):
        (ok if cond else ko).append(msg)

    # ── longueur (7.1) et forme (1.3, 1.8)
    n = len(texte)
    test(1450 <= n <= 1500, f"longueur {n} caractères (moteur : 1 450 à 1 500, plancher 1 350)")
    interdits = [c for c in ":;…«»()—/*#&€[]" if c in texte] + (["tiret"] if re.search(r"\s-\s", texte) else [])
    test(not interdits, f"ponctuation interdite : {interdits or 'aucune'}")
    test(texte.count("!") <= 1, f"points d'exclamation : {texte.count('!')} (1 maximum)")
    ne = re.findall(r"\bn['e]\s\w+", texte)
    test(not ne, f"négations en « ne » : {ne or 'aucune'}")
    ph = [s for _, t in rep for s in phrases(t)]
    longues = [s for s in ph if len(mots(s)) > 25]
    test(len(longues) <= 1, f"phrases de plus de 25 mots : {len(longues)} (une seule tolérée)")
    fins = phrases(" ".join(t for _, t in rep[-2:]))[-2:]
    test(all(3 <= len(mots(s)) <= 8 for s in fins), f"les 2 dernières phrases font 3 à 8 mots : {[len(mots(s)) for s in fins]}")
    frag = [s for s in ph if len(mots(s)) <= 4]
    test(len(frag) >= 4, f"phrases courtes / fragments : {len(frag)} (au moins 4)")

    # ── le hook (3.2, 3.5) : prix dans la 1re phrase, jamais en 1er mot, avant l'objet ; 10 à 18 mots
    premiere = phrases(rep[0][1])[0]
    m = re.search(MONTANT, premiere.lower())
    if not m:
        ok.append(f"pas de prix dans l'accroche (facultatif) : « {premiere} »")
    if m:
        avant = mots(premiere[:m.start()])
        test(len(avant) >= 1, "le prix est DANS la phrase, pas en 1er mot")
        test(len(avant) <= 6, f"le prix arrive tôt, avant l'objet (mots avant : {' '.join(avant)})")
    test(10 <= len(mots(premiere)) <= 18, f"couche 1 : {len(mots(premiere))} mots (10 à 18)")

    # ── le montant deux fois, à l'identique (1.10) : hook + punchline
    if m:
        montant = m.group(1)
        nb = len(re.findall(rf"(?<![\w-]){re.escape(montant)} euros", bas))
        test(nb == 2, f"montant « {montant} » dit {nb} fois (exactement 2 : hook + punchline)")
        test(montant in " ".join(t for _, t in rep[-2:]).lower(), "le montant revient dans la chute")

    # ── dialogue (1.4) : au moins 3 répliques, au moins 2 bouches
    m_lignes = [t for k, t in rep if k == "M"]
    cites_n = re.findall(r"\b(?:je lui (?:dis|réponds|ai dit)|elle me fait|il me fait|elle me dit|il me dit)\s*,\s*\w", narr)
    test(len(m_lignes) + len(cites_n) >= 3, f"répliques citées : {len(m_lignes)} du méchant + {len(cites_n)} dans la narration")
    test(bool(re.search(r"\bje lui (?:dis|réponds|ai dit)\s*,", narr)), "Kévin a sa propre réplique (2 bouches)")

    # ── écho (1.11) : 2 à 5 mots, seul, repris du COUP 1
    coup1 = next((t for i, (k, t) in enumerate(rep) if k == "M" and i > 0), "")
    echos = [t for k, t in rep if k == "N" and 2 <= len(mots(t)) <= 5 and len(phrases(t)) == 1
             and all(w.lower() in coup1.lower() for w in mots(t))]
    test(len(echos) == 1, f"écho sur le coup 1 : {echos or 'absent'}")

    # ── lexique (1.5, 1.7, 1.23)
    trouves = [w for w in INTERDITS if w in narr]
    test(not trouves, f"mots interdits : {trouves or 'aucun'}")
    ment = sorted({w for w in re.findall(r"\b\w+ment\b", bas) if w not in MENT_OK | MENT_NOMS})
    test(not ment, f"adverbes en -ment hors des 6 tolérés : {ment or 'aucun'}")
    test("tout le monde" not in narr.replace("pour tous", ""), "pas de « tout le monde » dans la narration (témoins chiffrés)")

    # ── chaîne de problématiques (1.13)
    entrees = {"et pourtant": narr.count("et pourtant"), "mais alors": narr.count("mais alors"),
               "sauf qu": narr.count("sauf qu"), "sur le papier": narr.count("sur le papier"),
               "ce que peu de gens savent": narr.count("ce que peu de gens savent")}
    test(sum(1 for v in entrees.values() if v) >= 3, f"chaîne de problématiques : {entrees} (au moins 3 entrées différentes)")
    test(entrees["mais alors"] <= 2 and entrees["ce que peu de gens savent"] <= 1, "« Mais alors » ≤ 2, savoir caché ≤ 1")
    test("?" in narr, "au moins une problématique dite par une question")

    # ── doute, zone grise, zéro CTA
    doute = re.search(r"honnêtement|je me demande|des fois je", narr)
    test(bool(doute), "le doute / la demi-raison est là")
    entete = " ".join(l for l in lignes if l.startswith("#")).lower()
    test("zone grise" in entete, "zone grise décrite dans l'en-tête")
    for cle in ("transgression", "verrou", "twist", "mot-enjeu", "tier"):
        test(cle in entete, f"en-tête : {cle} noté")
    cta = re.findall(r"\b(abonne|like|commente|partage|lien en bio|et vous|et toi, t'aurais)\b", narr)
    test(not cta, f"zéro appel au spectateur : {cta or 'aucun'}")

    print(f"── {chemin}")
    for x in ok:
        print("  ✅", x)
    for x in ko:
        print("  ❌", x)
    print("  À relire à la main : casting TIER S/A, dette du hook, twist qui referme une prémisse, test de la banane.")
    return not ko


if __name__ == "__main__":
    bons = [verifier(c) for c in sys.argv[1:]]
    sys.exit(0 if all(bons) else 1)
