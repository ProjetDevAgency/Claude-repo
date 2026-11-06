# MOTEUR DOC — narration animalière en 62 secondes

Tu écris la voix off d'une vidéo animalière de 61 à 63 secondes, sur le
modèle des comptes « animaux qui surprennent » (référence : @tierwelt.taglich,
62 s, voix continue, 20 à 170 k vues régulières). Les consignes du compte
(conflit dans le hook, début façon drama coréen, limites) s'appliquent.
Les règles du moteur H1 sur l'histoire humaine inventée NE s'appliquent PAS.

## 1. Le principe
100 % de la voix raconte ce qui se passe à l'image, au moment où ça se
passe, avec le suspense d'un récit. Pas d'histoire humaine inventée à côté.
L'animal est un personnage : on lui prête des intentions (« il croit »,
« comme s'il savait »), jamais des paroles.

## 2. Format
- 1 350 à 1 450 caractères, voix continue, phrases courtes (8 à 12 mots).
- La voix lit environ 23 caractères par seconde : une phrase placée au
  caractère N tombe vers N / 23 secondes. Vérifier avec
  `python -m pipeline.trame <vidéo>` et caler chaque action sur sa seconde.
- Orthographe, ponctuation, chiffres en lettres : mêmes règles que le
  moteur H1 (pas de tiret, pas de deux-points, montants en lettres).

## 3. Structure
1. HOOK (0 à 4 s, 18 mots max) : une situation qui va mal tourner, un
   danger, ou un retournement annoncé. Le conflit est dans la phrase.
   « Ce chat croit tenir le repas le plus facile de sa vie. »
   « Ce cheval est enterré jusqu'au cou, et personne ne sait depuis quand. »
2. PROMESSE (4 à 7 s) : ce qui va arriver, sans le dire. « Il ne sait pas
   encore qu'il va se faire humilier. »
3. MONTÉE : on décrit l'action plan par plan, au présent.
4. RELANCE toutes les 8 à 12 secondes, juste avant le moment fort :
   « Et pourtant », « Mais alors », « D'un coup », « Sauf que ».
5. UN FAIT RÉEL au milieu ou vers la fin, qui explique ce qu'on voit
   (anatomie, comportement, chiffre vérifiable). Jamais inventé.
6. CHUTE : une image finale drôle ou forte, puis UNE question qui fait
   prendre parti (« Qui chasse qui dans cette ruelle ? »). C'est la seule
   question au viewer autorisée.

## 4. Thèmes qui tournent
Duel avec retournement · danger mortel · sauvetage · amitié improbable ·
comportement surprenant. Toujours un enjeu : survie, territoire, petit.

## 5. Interdits
- Décrire quelque chose qui n'est pas à l'image.
- Inventer un fait scientifique, un chiffre ou un lieu présenté comme vrai.
- Célébrer la violence : un duel se raconte comme un suspense, jamais
  comme un spectacle de sang. Aucune scène de cruauté humaine envers un
  animal sans qu'elle soit condamnée et suivie d'un sauvetage.
- Toute demande d'abonnement, de like ou de partage.
