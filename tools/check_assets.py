"""Minimal offline checks for generated resources. Not an in-game smoke test."""
import json
from pathlib import Path
root=Path("src/main/resources")
assets=root/"assets/sift"
blocks=[
"meadow_soil","red_growth","carapace_stone","luminous_relic","teal_turf",
"sift_ochre","carapace_shale","fossil_rib","lumen_cluster","red_canopy",
"spore_mat","ichor_crust","meadow_reed","scarlet_sprout","carapace_spire",
"soul_bloom","scarlet_trunk"]
items=["lumen_shard","fossil_fragment","scarlet_seed","sift_compass_core"]
flora=["meadow_reed","scarlet_sprout","soul_bloom"]
for file in root.rglob("*.json"):
    json.loads(file.read_text(encoding="utf-8"))
for name in blocks:
    png=assets/"textures/block"/(name+".png")
    assert png.read_bytes()[:8]==b"\\x89PNG\\r\\n\\x1a\\n", png
    assert (assets/"blockstates"/(name+".json")).exists()
    itemdef=json.loads((assets/"items"/(name+".json")).read_text(encoding="utf-8"))
    model=json.loads((assets/"models/item"/(name+".json")).read_text(encoding="utf-8"))
    if name in flora:
        assert itemdef["model"]["model"]=="sift:item/"+name, name
        assert model["parent"]=="minecraft:item/generated", name
for name in items:
    assert (assets/"textures/item"/(name+".png")).exists()
for name in ("enter","leave","save_return","leave_saved"):
    assert (root/"data/sift/function"/(name+".mcfunction")).exists()
print("OK: 17 blocks, 4 items, 3 flat held-plant models, 4 teleport functions; JSON parsed")
