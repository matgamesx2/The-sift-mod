# THE SIFT — Fabric Minecraft 26.3

**Independent fan-made mod, not an official Mojang/Minecraft Dungeons II release.**

This repository is the first compiling Fabric foundation. It registers 17 custom blocks and 4 new items, generates original placeholder textures and introduces two prototype Sift biomes in a separate dimension. This **initial CI branch** deliberately uses conservative vanilla terrain; the detailed terrain and fossils from the previous datapack prototype still need porting and in-game validation.

## Compilation
GitHub Actions: open **Actions → Build THE SIFT Fabric JAR → latest run → Artifacts**. Download `the-sift-0.4.0-jar` if the workflow completed successfully. Do not install a JAR if the workflow failed.

## Requirements
Minecraft Java 26.3, Java 25, Fabric Loader 0.19.5+, matching Fabric API. Source build requires Gradle 9.6 and Python 3 once to generate the placeholder assets.

## Testing
Use a *new creative world* and backup existing saves. Try `/give @s sift:teal_turf` or `/give @s sift:lumen_shard`. Experimental dimension: `/execute in sift:sift run tp @s 0 160 0` (creative/flying recommended).

All visual assets here are original placeholders rather than extracted Minecraft Dungeons II content.
