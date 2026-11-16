# Survie « à toi de choisir » : sujets, scripts, vérification

Tiré de 18 vidéos à plus d'un million de vues (@talkin_guy, @creepydillemas, @velqenx6).
Le détail des chiffres est dans `analyse_1M.md`.

| Fichier | À quoi ça sert |
|---|---|
| `machine_a_sujets_survie.md` | Colle-le dans Claude. Une question, puis 12 sujets de série à chaque « encore ». |
| `moteur_script_survie.md` | Colle-le dans Claude. Il écrit la partie 1, la suite d'après le vote, ou refait à ta sauce une vidéo qui a marché ailleurs. |
| `analyse_1M.md` | Ce que les 18 vidéos ont en commun, avec les chiffres. |
| `../methode/*_survie.pdf`, `../methode/analyse_1M.pdf` | Les mêmes documents en PDF. |

## Le circuit

```
machine à sujets ──► une carte sujet ──► moteur S1 ──► script (format NARRATEUR > …)
                                                         │
                                  python tueur/verifier.py mon_script.txt
                                                         │
                                       vidéo 3D (dossier tueur/) ──► post ──► vote en commentaire
                                                                                     │
                                         moteur S1, porte 2 (la suite) ◄─────────────┘
```

## Vérifier un script

Colle le script du moteur dans un fichier texte, puis :

```bash
python tueur/verifier.py tueur/scripts/mon_script.txt
```

Il contrôle : la longueur (et donc les 61 secondes), la longueur des phrases, les fragments, le « tu »,
les négations sans « ne », la ponctuation, les mots qui nomment la peur, l'heure dans le hook (partie 1)
ou le rappel du vote (suite), les répliques, la question finale A ou B, l'absence d'appel à l'action dans
la voix, les pauses et les bruitages, et les histoires déjà prises par d'autres comptes.

Deux scripts modèles qui passent : `tueur/scripts/mon_loup_p1.txt` et `mon_loup_p2.txt`.
