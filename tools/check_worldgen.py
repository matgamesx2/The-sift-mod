#!/usr/bin/env python3
"""Fail CI on missing Sift 0.5 resources and mismatched worldgen references."""
import json,struct
from pathlib import Path
data=Path("src/main/resources/data/sift")
assets=Path("src/main/resources/assets/sift")
for f in (data.parent.parent).rglob("*.json"):
    json.loads(f.read_text(encoding="utf-8"))
cfg=json.loads((data/"worldgen/noise_settings/fractured.json").read_text(encoding="utf-8"))
assert cfg["default_fluid"]["id"]=="sift:prismatic_tide_block"
assert cfg["material_rule"]=="sift:fractured"
density=cfg["noise_router"]["final_density"]
assert density["type"]=="minecraft:interpolated"
assert density["input"]["type"]=="minecraft:max"
assert density["input"]["right"]["left"]["from_coordinate"]==-56
assert density["input"]["right"]["left"]["from_value"]>=9.0
assert cfg["sea_level"] < 0
assert "rift_branches" in json.dumps(density)
assert "rift_network" in json.dumps(density)
assert "overhang" in json.dumps(density)
assert "bridge_paths" in json.dumps(density)
assert "basin_floor" in json.dumps(density)
assert "range_choice" in json.dumps(density)
assert (data/"worldgen/material_rule/fractured.json").exists()
dimension=json.loads((data/"dimension/sift.json").read_text(encoding="utf-8"))
assert dimension["generator"]["settings"]=="sift:fractured"
for biome in ("meadows","carapace"):
    obj=json.loads((data/"worldgen/biome"/(biome+".json")).read_text(encoding="utf-8"))
    assert len(obj["features"])==11
    for group in obj["features"]:
        for feature in group:
            name=feature.split(":")[-1]
            p=data/"worldgen/placed_feature"/(name+".json")
            assert p.exists(),(biome,p)
            entry=json.loads(p.read_text(encoding="utf-8"))
            name2=entry["feature"].split(":")[-1]
            assert (data/"worldgen/feature"/(name2+".json")).exists(),name2
# Reject the exact regression: air above a fluid is not valid plant ground.
for path in (data/"worldgen/placed_feature").glob("*.json"):
    value=json.loads(path.read_text())
    filters=[m["predicate"] for m in value["placement"]
             if m["type"]=="minecraft:block_predicate_filter"]
    assert filters and filters[0]["type"]=="minecraft:all_of",path
    ground=filters[0]["predicates"][1]
    assert ground["offset"]==[0,-1,0],path
    assert "sift:prismatic_tide_block" not in ground["blocks"],path
for tag in (data/"tags/fluid/prismatic_tide.json",):
    assert tag.exists()
for name,height in (("still",4096),("flow",4096),("overlay",128)):
    f=assets/"textures/block"/("prismatic_tide_"+name+".png")
    header=f.read_bytes()[:24]
    assert header[:8]==bytes.fromhex("89504e470d0a1a0a")
    assert struct.unpack(">II",header[16:24])==(128,height)
    if name != "overlay":
        metadata=json.loads(f.with_suffix(".png.mcmeta").read_text())
        assert metadata["animation"]["interpolate"]
        assert metadata["animation"]["height"]==128
assert (assets/"textures/item/prismatic_tide_bucket.png").exists()
fluidstate=json.loads((assets/"blockstates/prismatic_tide_block.json").read_text())
assert fluidstate["variants"][""]["model"]=="sift:block/prismatic_tide_empty"
assert json.loads((assets/"models/block/prismatic_tide_empty.json").read_text())["elements"]==[]
print("PASS SIFT 0.5.4: animated tide, 2 biomes, branching faults, bounded arches and basin floor")
