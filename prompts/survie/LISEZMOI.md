# Survie « à toi de choisir » : sujets, hooks, scripts, vérification

Tiré de 18 vidéos à plus d'un million de vues (@talkin_guy, @creepydillemas, @velqenx6).
Le détail des chiffres est dans `analyse_1M.md`.

| Fichier | À quoi ça sert |
|---|---|
| `machine_a_sujets_survie.md` | Colle-le dans Claude. Une question, puis 12 sujets de série à chaque « encore », chacun avec son angle de hook. |
| `machine_a_hooks_survie.md` | Colle-le dans Claude, envoie un sujet : huit hooks (un par gabarit), chacun avec son image zéro. C'est l'annexe A du moteur, toute seule. |
| `moteur_script_survie.md` | Version 2.0, construite sur le squelette de H1. Colle-le dans Claude. Il te propose trois hooks, puis écrit la partie 1, la suite d'après le vote, ou refait à ta sauce une vidéo qui a marché ailleurs. |
| `comparaison_H1_S1.md` | Toutes les différences entre H1 et S1, bloc par bloc, et ce qu'on en a fait (repris, adapté, ou gardé parce que les données du format le disent). |
| `analyse_1M.md` | Ce que les 18 vidéos ont en commun, hook compris, avec les chiffres. |
| `../methode/*_survie.pdf`, `../methode/analyse_1M.pdf` | Les mêmes documents en PDF. |

## Le circuit

```
machine à sujets ──► une carte sujet ──► (machine à hooks) ──► moteur S1 ──► script (NARRATEUR > …)
                                                                               │
                                                     python tueur/verifier.py mon_script.txt
                                                                               │
                                              vidéo 3D (dossier tueur/) ──► post ──► vote en commentaire
                                                                                           │
                                                  moteur S1, porte 2 (la suite) ◄──────────┘
```

La machine à hooks est facultative : le moteur propose déjà trois hooks. Elle sert quand tu veux plus de
choix, ou tester plusieurs hooks sur le même sujet.

## Le hook en bref

- La voix démarre à 0 seconde, la menace est à l'image dès la première frame.
- Trois couches : le choc (0 à 3 s, 14 mots max), le verrou (3 à 7 s), la couture (7 à 12 s).
- Neuf gabarits. Pour une suite, le rappel-choc (la menace en action d'abord, le vote ensuite).

## Vérifier un script

Colle le script du moteur dans un fichier texte, puis :

```bash
python tueur/verifier.py tueur/scripts/mon_script.txt
```

Il contrôle : le budget en caractères (plancher 1 050, donc les 61 secondes à voix naturelle), la longueur des phrases, les fragments, le « tu »,
les négations sans « ne », « plu », la ponctuation, un seul point d'exclamation, les connecteurs d'écrit, les anglicismes, les adverbes en -ment, les mots qui nomment la peur, « je t'explique », aucune question au viewer avant la fin, pas deux relances de suite avec le même mot, le hook (voix à 0 s, 14 mots max
en première phrase, pas d'annonce, l'heure en partie 1, le vote après le rappel-choc en suite), les
répliques, la question finale A ou B, l'absence d'appel à l'action dans la voix, les pauses et les
bruitages, et les histoires déjà prises par d'autres comptes.

Deux scripts modèles qui passent : `tueur/scripts/mon_loup_p1.txt` et `mon_loup_p2.txt`.
