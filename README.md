# THE SIFT — Fabric Minecraft 26.3

**Independent fan-made mod, not an official Mojang/Minecraft Dungeons II release.**

This repository is the first compiled Fabric foundation. It registers 17 custom blocks and 4 new items, generates original placeholder textures and introduces two prototype Sift biomes in a separate dimension. This **initial CI branch** deliberately uses conservative vanilla terrain; the detailed terrain and fossils from the previous datapack prototype still need porting and in-game validation.

## Compilation
GitHub Actions: open **Actions → Build THE SIFT Fabric JAR → latest run → Artifacts**. Download `the-sift-0.4.1-jar` if the workflow completed successfully. Do not install a JAR if the workflow failed.

## Requirements
Minecraft Java 26.3, Java 25, Fabric Loader 0.19.5+, matching Fabric API. Source build requires Gradle 9.6 and Python 3 once to generate the placeholder assets.

## Testing
Use a *new creative world* and backup existing saves. Try `/give @s sift:teal_turf` or `/give @s sift:lumen_shard`. Experimental dimension: `/execute in sift:sift run tp @s 0 160 0` (creative/flying recommended).

All visual assets here are original placeholders rather than extracted Minecraft Dungeons II content.

## 0.4.1 corrections
- Three small plant items use flat inventory/held models rather than giant crossed world models.
- Added single-player `/function sift:enter` and `/function sift:leave` test commands; enter saves your overworld position and uses slow falling. These commands are experimental. Back up the world first.
- Automated checks verify JSON and generated item-model relationships before compiling.
- Terrain is **still the conservative prototype**. The earlier 0.3.7 biome terrain, giant fossils and fully custom Sift plants have not yet been ported into the compiled mod. Do not confuse compilation success with runtime validation.

## 0.5.0 — Fractured worldgen & prismatic tide (experimental)

Based on user-supplied *Minecraft Dungeons II* visual references, the Sift now has original dedicated roofless density generation. Broad 2D rift noise excavates connected ravines; plateau noise gives amplified cliffs; 3D noise cuts overhangs. Meadows and Carapace are distinct in the surface material rules, with sparse plants, trees and fossil spires.

A new **real flowing fluid** is registered as `sift:prismatic_tide` and generated at the base of the rifts. Its client uses original rainbow-colored textures. It releases SOUL / SOUL_FIRE_FLAME particles and causes periodic magic damage and normal burning on contact. **The player's standard orange burning overlay has not yet been recolored blue**; the visible blue fire is currently the emitted particles. Render/worldgen must be tested in Minecraft, not only CI.

### Test on a new Creative world only

- `/function sift:enter` — enters Sift from Overworld (singleplayer test).
- `/function sift:leave` — returns to saved location.
- `/give @s sift:prismatic_tide_bucket` — get the new real fluid.
- `/locate biome sift:carapace` — locate the second biome (in Sift).

DO NOT open existing Sift saves with this major worldgen overhaul. Existing chunks cannot be regenerated without a new world. This is not yet a 1:1 reconstruction of Dungeons II; the hero biome trees, moving tides, giant fossil structures and blue player-burning overlay are still being developed.
