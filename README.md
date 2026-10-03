# THE SIFT — Fabric 0.5.4

Mod pour Minecraft Java **26.3**, Java **25**, Fabric Loader **0.19.5+** et Fabric API **0.161.0+26.3**.

La dimension `sift:sift` contient deux biomes, Meadows et Carapace, des failles principales et secondaires, des plateaux, des arches et des surplombs. Les 17 blocs, 4 objets, recettes et fonctions de téléportation sont conservés, ainsi que le véritable fluide personnalisé et son seau.

## Changements 0.5.4

- Nouveaux matériaux originaux en 32 px, avec une palette commune : sols turquoise, schiste bleu-violet, végétation écarlate et fossiles ivoire. Faces supérieures et latérales distinctes, rotations des modèles pour varier les motifs.
- Placement de chaque arbre, plante et décor conditionné à un sol solide autorisé. L'air au-dessus du liquide n'autorise plus la génération de végétation.
- Trois silhouettes d'arbres utilisant les blocs et textures Sift, avec une densité réduite.
- Sommets moins bombés, parois plus accidentées et corniches à différentes hauteurs. Le sous-sol des falaises est rocheux plutôt qu'un immense volume de sol turquoise.
- Marée sombre et translucide : 32 images animées, reflets irisés déformés, coloration selon la profondeur et teinte sous-marine. Particules d'âme, lumière bleue, dégâts et flammes discrètes aux coins de l'écran conservés.
- Fond rocheux imperméable au-dessus de la couche de lave vanilla.

Les textures sont originales et s'inspirent des références Dungeons ; ce mod n'est pas une reproduction exacte des assets du jeu.

## Installation et exploration

Télécharger l'artefact `the-sift-0.5.4-jar` dans le dernier workflow **Build THE SIFT Fabric JAR** réussi. Placer le JAR dans `mods/`, avec Fabric API, en remplaçant l'ancienne version du mod.

- `/function sift:enter` : entrer dans Sift et mémoriser la position de retour.
- `/function sift:leave` : revenir à la position mémorisée.
- `/give @s sift:prismatic_tide_bucket` : obtenir le seau du fluide.
- `/locate biome sift:carapace` : trouver Carapace depuis Sift.

**Tester le terrain dans un nouveau monde ou de nouveaux chunks.** Les chunks déjà générés gardent leurs formes et les anciennes plantes. Les nouvelles textures s'appliquent aussi aux blocs existants.

## Compilation et vérifications

Avec Python 3, Java 25 et Gradle 9.6 :

```sh
python3 tools/generate_assets.py
python3 tools/generate_worldgen.py
python3 tools/generate_tide.py
python3 tools/check_assets.py
python3 tools/check_worldgen.py
gradle --no-daemon clean build
```

Les sources des textures sont dans `tools/art/` ; les scripts les installent et génèrent les modèles, animations et données du monde.

Le workflow serveur démarre Minecraft et vérifie de vrais chunks avec la graine 42819 : équilibre crevasses/plateaux, ciel ouvert, arches, substrat solide, absence de lave et de végétation à la surface des bassins, écoulement et dégâts du fluide sans feu orange. Le workflow client démarre une fenêtre Minecraft sous OpenGL logiciel, rejoint un serveur local et conserve les captures et journaux comme artefacts. Consulter son résultat avant de considérer la vérification visuelle comme réussie.
