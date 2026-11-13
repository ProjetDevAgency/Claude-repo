"""Génère les phrases du narrateur du live (ElevenLabs) → live/public/voix/*.mp3 + voix.json.

Usage : ELEVENLABS_API_KEY=… ELEVENLABS_VOICE_ID=… python3 live/make_voix.py
Les fichiers déjà présents ne sont pas régénérés (supprime-les pour refaire une phrase).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.tts import synthesize_elevenlabs  # noqa: E402

OUT = Path(__file__).resolve().parent / "public" / "voix"
OUT.mkdir(parents=True, exist_ok=True)

PHRASES = {
    # abonnement
    "arrivee": [
        "Une nouvelle famille arrive au village !",
        "Un nouvel habitant ! Bienvenue à Fauché-les-Oies !",
        "Bienvenue ! Ta maison t'attend.",
        "Encore un nouveau voisin. Le village grandit !",
        "Les cartons arrivent… Quelqu'un emménage !",
    ],
    # cadeaux, selon le bâtiment construit
    "arbre": [
        "Un arbre de plus dans le village. Merci !",
        "On plante un arbre ! Un peu de verdure, ça fait du bien.",
        "Et hop, un nouvel arbre pousse !",
        "Merci pour l'arbre ! Les oies vont adorer.",
    ],
    "cabane": [
        "Une petite cabane sort de terre !",
        "Une cabane ! C'est un début. Merci !",
        "Quelqu'un s'installe dans une cabane. Merci pour le cadeau !",
        "Des planches, des clous… et voilà une cabane !",
    ],
    "maison": [
        "Et une nouvelle maison ! Merci pour le cadeau !",
        "Ça construit à Fauché-les-Oies ! Une maison de plus !",
        "Une maison toute neuve ! Merci beaucoup !",
        "Le village s'agrandit : nouvelle maison dans la rue !",
    ],
    "grande_maison": [
        "Oh, une grande maison ! Il y a du beau monde au village !",
        "Une grande maison, avec tout le confort ! Merci !",
        "Ça, c'est une belle maison ! Merci pour le cadeau !",
        "Une grande maison sort de terre. Le quartier devient chic !",
    ],
    "immeuble": [
        "Un immeuble entier ! Merci, c'est énorme !",
        "Attention, un immeuble arrive dans le village !",
        "Un immeuble ! Fauché-les-Oies devient une vraie ville !",
        "Des dizaines d'appartements d'un coup ! Merci !",
    ],
    "monument": [
        "Oh ! Un monument ! Merci, c'est énorme !",
        "Un monument ! Tout le village est en fête !",
        "Incroyable… Un monument pour Fauché-les-Oies !",
        "Ce cadeau restera dans l'histoire du village. Merci !",
    ],
    # likes, partages, commentaires, visiteurs
    "like": [
        "Les likes pleuvent ! Le budget grimpe !",
        "Continuez de liker : chaque like remplit la caisse !",
        "Ça tapote fort, merci !",
        "Le budget du village monte… Continuez !",
    ],
    "partage": [
        "Merci pour le partage ! Plus on est, plus le village grandit.",
        "Quelqu'un partage le live ! Bienvenue aux nouveaux !",
        "Un partage ! Ramène tes potes au village !",
        "Merci ! Les nouveaux voisins arrivent grâce à toi.",
    ],
    "discute": [
        "Ça discute bien dans le village ce soir !",
        "Il y a du monde dans les rues aujourd'hui !",
        "Ça papote sur la place du village !",
        "Les habitants ont des choses à se dire !",
        "Quelle ambiance dans le village !",
    ],
    "visiteur": [
        "Tiens, un visiteur se promène dans le village.",
        "Un curieux passe par Fauché-les-Oies…",
        "Bienvenue au visiteur ! Abonne-toi pour avoir ta maison.",
        "Quelqu'un découvre le village. Fais comme chez toi !",
    ],
    # mode « Villageois vs Zombies »
    "bataille_debut": [
        "Nouvelle manche ! Tape un pour les villageois, deux pour les zombies !",
        "Les zombies sortent de la crypte… Choisis ton camp !",
        "C'est reparti ! Villageois ou zombies, à toi de choisir !",
    ],
    "bataille_renforts": [
        "Des renforts arrivent !",
        "Merci pour les renforts !",
        "Encore des combattants sur le terrain !",
        "Ça se bat fort, merci pour le cadeau !",
    ],
    "bataille_geant": [
        "Attention… Un géant entre sur le terrain !",
        "Un géant ! Ça va faire mal !",
    ],
    "bataille_speciale": [
        "Attaque spéciale ! Tout le terrain est balayé !",
        "Énorme ! Une attaque spéciale qui change tout !",
    ],
    "bataille_danger": [
        "Le camp est presque détruit ! Envoyez des renforts !",
        "Attention, le camp ne tiendra plus longtemps !",
        "Likez pour réparer votre camp, vite !",
    ],
    "bataille_victoire_v": [
        "Les villageois gagnent la manche ! Bravo !",
        "Victoire des villageois ! Les zombies retournent dans leur crypte !",
        "Le village est sauvé ! Victoire des villageois !",
    ],
    "bataille_victoire_z": [
        "Les zombies gagnent la manche !",
        "Victoire des zombies ! Le village est envahi !",
        "Les zombies ont tout cassé ! Victoire des zombies !",
    ],
    "bataille_appel": [
        "Tape un ou deux pour rejoindre une équipe !",
        "Ton cadeau envoie des renforts dans ton équipe !",
        "Chaque like répare le camp de ton équipe !",
        "Abonne-toi, et ton combattant devient un champion !",
        "Les abonnés se battent avec des champions. Abonne-toi !",
    ],
    "bataille_regle": [
        "Tape un pour être villageois, tape deux pour être un zombie !",
        "Pour jouer, c'est simple. Un, t'es villageois. Deux, t'es zombie !",
        "T'arrives ? Tape un ou deux dans les commentaires, et ton bonhomme entre dans la bataille !",
    ],
    "bataille_abonne": [
        "Un nouvel abonné ! Son combattant devient un champion !",
        "Abonné ! Et hop, un champion de plus sur le terrain !",
        "Merci pour l'abonnement ! Ton combattant passe champion !",
    ],
    # mode « Quiz »
    "quiz_partie": [
        "Nouvelle partie ! Tout le monde repart de zéro. Réponds juste à tout, et tu deviens millionnaire !",
        "C'est parti pour une nouvelle partie ! Dix paliers, et un million à la clé !",
    ],
    "quiz_regle": [
        "Pour jouer, écris A, B, C ou D dans les commentaires ! Attention, seule ta première réponse compte.",
        "Tu viens d'arriver ? Écris juste la lettre de ta réponse dans les commentaires : A, B, C ou D !",
        "Vingt secondes par question. Écris A, B, C ou D, et grimpe dans le classement !",
    ],
    "quiz_vite": ["Plus que cinq secondes !", "Vite, il reste cinq secondes !", "Dépêche-toi, c'est presque fini !"],
    "quiz_bonne_a": [
        "La bonne réponse, c'était la A ! Bravo à ceux qui ont trouvé !",
        "C'était la A ! Félicitations aux gagnants !",
        "Réponse A ! Bien joué à tous ceux qui l'ont trouvée !",
    ],
    "quiz_bonne_b": [
        "La bonne réponse, c'était la B ! Bravo à ceux qui ont trouvé !",
        "C'était la B ! Félicitations aux gagnants !",
        "Réponse B ! Bien joué à tous ceux qui l'ont trouvée !",
    ],
    "quiz_bonne_c": [
        "La bonne réponse, c'était la C ! Bravo à ceux qui ont trouvé !",
        "C'était la C ! Félicitations aux gagnants !",
        "Réponse C ! Bien joué à tous ceux qui l'ont trouvée !",
    ],
    "quiz_bonne_d": [
        "La bonne réponse, c'était la D ! Bravo à ceux qui ont trouvé !",
        "C'était la D ! Félicitations aux gagnants !",
        "Réponse D ! Bien joué à tous ceux qui l'ont trouvée !",
    ],
    "quiz_premiere": ["Première question !", "Voici la première question !", "Attention, première question !"],
    "quiz_suivante": ["Question suivante !", "On passe à la question suivante !", "Allez, question suivante !"],
    "quiz_personne": ["Personne n'a trouvé ! Elle était dure, celle-là.", "Aïe… Personne ! On se rattrape à la prochaine."],
    "quiz_tous": ["Tout le monde a trouvé ! Trop facile pour vous !", "Cent pour cent de bonnes réponses ! Bravo !"],
    "quiz_palier": ["Bravo ! Palier validé !", "Et voilà, palier terminé ! Regardez le classement.", "Palier validé ! Bravo aux sans-faute !"],
    "quiz_nouveau": ["Nouveau palier ! Les gains augmentent… Tirage au sort du thème !", "On monte d'un palier ! Quel sera le thème ?"],
    "quiz_million": [
        "Le palier du million ! Les six dernières questions… Concentrez-vous !",
        "Dernier palier ! C'est maintenant que tout se joue !",
    ],
    "quiz_fin": ["Fin de la partie ! Voici notre grand gagnant !", "La partie est terminée ! Applaudissez notre champion !"],
    "quiz_abonne": [
        "Un nouvel abonné ! Ses bonnes réponses rapportent vingt pour cent de plus !",
        "Merci pour l'abonnement ! Bonus de vingt pour cent sur tes gains !",
        "Abonné ! Et hop, tes gains grimpent de vingt pour cent !",
    ],
    "quiz_joker": ["Merci pour le cadeau ! Ton joker est activé : ta prochaine erreur ne compte pas.", "Joker activé ! Tu as le droit à une erreur."],
    "quiz_x2": ["Double gain ! Toutes tes bonnes réponses du palier comptent double !", "Fois deux ! Merci, tes gains doublent sur ce palier !"],
    "quiz_moitie": ["Cinquante-cinquante ! Deux mauvaises réponses disparaissent, pour tout le monde !", "Merci ! On enlève deux mauvaises réponses !"],
    "quiz_appel": [
        "Abonne-toi : tes bonnes réponses rapportent vingt pour cent de plus !",
        "Un cadeau, et tu as un joker : ta prochaine erreur ne compte pas !",
        "Partage le live à tes potes, et défie-les au quiz !",
    ],
    # ambiance
    "soir": ["Le soir tombe sur Fauché-les-Oies… C'est magnifique."],
    "matin": ["Le soleil se lève sur Fauché-les-Oies. Bonne journée, les habitants !"],
    "appel": [
        "Abonne-toi, et tu deviens un habitant du village !",
        "Partage le live à tes potes : plus on est, plus le village grandit !",
        "Chaque like, c'est un euro pour le village. Allez, on tapote !",
        "Envoie un cadeau, et ta maison apparaît dans la rue !",
    ],
}

# quiz : chaque question est lue à voix haute, et chaque thème est annoncé
QUIZ = json.loads((OUT.parent / "questions.json").read_text())
for cle, nom in QUIZ["themes"].items():
    PHRASES[f"theme_{cle}"] = [f"Thème : {nom.lower()} !"]
for q in QUIZ["questions"]:
    PHRASES[f"q_{q['id']}"] = [q["q"].replace("«", "").replace("»", "").replace("…", "...")]

# textes déjà enregistrés : on régénère un fichier seulement si sa phrase a changé
ANCIEN = OUT / "textes.json"
deja = json.loads(ANCIEN.read_text()) if ANCIEN.exists() else {}
textes = {}

index = {}
for cat, lignes in PHRASES.items():
    index[cat] = []
    for i, txt in enumerate(lignes):
        f = OUT / f"{cat}_{i}.mp3"
        textes[f.name] = txt
        if f.exists() and deja.get(f.name, txt) != txt:
            f.unlink()
        if not f.exists():
            synthesize_elevenlabs(txt, f, model="eleven_v4", stability=0.5, style=0.35)
            print("✓", f.name, "·", txt)
        index[cat].append(f"voix/{f.name}")
ANCIEN.write_text(json.dumps(textes, ensure_ascii=False, indent=1))
for f in OUT.glob("*.mp3"):
    if f.name not in textes:
        f.unlink()                      # phrase retirée
(OUT / "voix.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
print(sum(len(v) for v in index.values()), "phrases")
