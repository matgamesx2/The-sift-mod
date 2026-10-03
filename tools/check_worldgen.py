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
assert density["input"]["right"]["from_value"]>=9.0
assert cfg["sea_level"] < 0
assert "rift_branches" in json.dumps(density)
assert "rift_network" in json.dumps(density)
assert "overhang" in json.dumps(density)
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
for tag in (data/"tags/fluid/prismatic_tide.json",):
    assert tag.exists()
for name,size in (("still",64),("flow",64),("overlay",64)):
    f=assets/"textures/block"/("prismatic_tide_"+name+".png")
    header=f.read_bytes()[:24]
    assert header[:8]==bytes.fromhex("89504e470d0a1a0a")
    assert struct.unpack(">II",header[16:24])==(size,size)
assert (assets/"textures/item/prismatic_tide_bucket.png").exists()
print("PASS SIFT 0.5.1: registered tide textures, 2 biomes, rift density, and all decor refs")
