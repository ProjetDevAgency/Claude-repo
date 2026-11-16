# Charte du compte « Tu choisis » (@tuchoisis.fr)

Histoires d'horreur et de survie à la 2e personne : le viewer est le héros, chaque épisode finit sur un
choix A ou B, la suite suit le vote. Un compte pour toutes les séries (tueur, imposteur, légendes…).

## Le profil

| Champ | Contenu |
|---|---|
| Nom affiché | **Tu choisis** |
| @ | **@tuchoisis.fr** (libre au 16/11/2026 d'après tiktok.com ; à confirmer dans l'appli) |
| Photo | `avatar_1_ab.png` conseillée : les étiquettes A et B du vote, lisibles même en tout petit dans le fil. Alternatives : `avatar_3_texte.png` (le nom), `avatar_2_portes.png` (trop sombre en petit) |
| Bio (76 caractères, max 80) | `Histoires d'horreur où c'est toi le héros. A ou B ? La suite suit ton vote 👇` |

Autres bios possibles :
- `Une nuit, un choix. Tu votes A ou B, la suite suit ton vote 👇` (61)
- `C'est toi le héros. Tu choisis, tu survis ou pas. Vote en commentaire 👇` (71)

## Les couleurs

| Rôle | Couleur |
|---|---|
| Fond, nuit | `#05070d`, dégradé vers `#0d1324` |
| Rouge (le mot qui fait peur, l'option A, PARTIE N) | `#ff2b2b` |
| Lumière chaude (sous les portes, les lampes) | `#ffb36b` |
| Texte | blanc `#ffffff`, contour noir sur les vidéos |

## Les polices (dans `assets/fonts`)

- **Anton** : sous-titres, titres de couverture, horloge, étiquettes du choix.
- **Montserrat ExtraBold** : la pastille PARTIE N, les cartons de règle.
- **Inter** : textos, @ du compte, petits textes.

## Ce qu'on retrouve dans chaque vidéo

- En haut à gauche : `@tuchoisis.fr` en petit, la pastille rouge **PARTIE N**, l'heure qui défile, le lieu.
- Sous-titres de 2 à 3 mots, en majuscules Anton, un mot en rouge.
- Les cartons **RÈGLE N°1** et les textos en bulle de téléphone.
- L'écran final : les deux options écrites sur le décor avec une flèche, puis **COMMENTE ↓**.
- La voix : Hugo, grave et posé, sans respiration ni chuchotement (règle tirée des 17 vidéos à 1 M).

## Les séries

- **Un titre court** par série, deux mots maximum : « Mon loup ».
- **Couverture** de chaque épisode : le décor de l'épisode, la pastille PARTIE N, le titre en Anton avec un
  mot en rouge, le @ en bas. Le texte reste dans le centre de l'image, la partie visible dans la grille du
  profil. Modèle : `couverture_mon_loup_p1.png` (fabriquée par `make_branding.js`).
- **Description** : commence par `Titre, partie N.`, puis l'accroche, 👀, la question du choix, 👇, et 3 à 5
  hashtags (`#horreur #pov #histoire #creepypasta #pourtoi`).
- **Commentaire épinglé** sur chaque épisode : `A = … / B = … La partie N+1 suit le choix qui gagne.`
- **Épingler** la partie 1 de la série en cours (3 épingles maximum sur TikTok), pour que les nouveaux
  visiteurs commencent au début.
- **Une playlist par série** dès que TikTok la propose sur le compte.

## Refaire les images

```bash
node branding/tuchoisis/make_branding.js
```

Pour une nouvelle couverture : une image du décor sans texte avec
`node tueur/render.js --preview <seconde> --sans-ui`, puis un nouvel appel à `cover()` dans le script.
