#!/usr/bin/env python3
"""Generate 21 original low-resolution placeholder textures and Minecraft 26.3 model/data files.
All generated resources use original palettes. No Mojang or Dungeons assets are redistributed.
"""
from pathlib import Path
import json, random, hashlib, struct, zlib
root=Path("src/main/resources")
asset=root/"assets/sift"
data=root/"data/sift"
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
palette={
"meadow_soil":("#368e91","#28757c"),"red_growth":("#bb4051","#8a2d48"),
"carapace_stone":("#5359a2","#333d79"),"luminous_relic":("#b5eff1","#4486b0"),
"teal_turf":("#45b8b9","#237b87"),"sift_ochre":("#c58069","#956080"),
"carapace_shale":("#4f65b0","#323e7d"),"fossil_rib":("#e6dcc1","#b8a788"),
"lumen_cluster":("#72d5d6","#395caa"),"red_canopy":("#ca314b","#862037"),
"spore_mat":("#576ac7","#38478d"),"ichor_crust":("#df8ca9","#aa5989"),
"meadow_reed":("#63d9d2","#1b748a"),"scarlet_sprout":("#da4861","#8d2943"),
"carapace_spire":("#677cd0","#303f79"),"soul_bloom":("#eff4ee","#80c6ca"),
"scarlet_trunk":("#902a41","#672438")}
items={"lumen_shard":("#78e2d9","#2a83b5"),"fossil_fragment":("#e8deba","#a18a6d"),
"scarlet_seed":("#e9546a","#862545"),"sift_compass_core":("#ac81f4","#3e398c")}
flora={"meadow_reed","scarlet_sprout","soul_bloom"}
def rgb(hex): return bytes.fromhex(hex.lstrip("#"))
def chunk(label,data):
    return struct.pack(">I",len(data))+label+data+struct.pack(">I",zlib.crc32(label+data)&0xffffffff)
def png(path,pixel):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=b"".join(b"\x00"+b"".join(pixel(x,y) for x in range(16)) for y in range(16))
    hdr=struct.pack(">IIBBBBB",16,16,8,6,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",hdr)+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b""))
for name,(c1,c2) in {**palette,**items}.items():
    rng=random.Random(int(hashlib.sha256(name.encode()).hexdigest()[:12],16))
    pixels=[(rgb(c1) if rng.randrange(5) else rgb(c2))+b"\xff" for _ in range(256)]
    if name in flora or name in items:
        for y in range(16):
            for x in range(16):
                if name in flora:
                    visible=(abs(x-8)<2 and y>4) or ((x+y)%4==0 and abs(x-8)<5 and 4<y<12)
                else:
                    visible=(abs(x-8)+abs(y-8)<10)
                if not visible: pixels[y*16+x]=b"\x00\x00\x00\x00"
    png(asset/("textures/item" if name in items else "textures/block")/(name+".png"),lambda x,y:pixels[y*16+x])
for name in palette:
    if name in flora:
        model={"parent":"minecraft:block/cross","textures":{"cross":"sift:block/"+name}}
    else:
        model={"parent":"minecraft:block/cube_all","textures":{"all":"sift:block/"+name}}
    write(asset/"models/block"/(name+".json"),model)
    write(asset/"blockstates"/(name+".json"),{"variants":{"":{"model":"sift:block/"+name}}})
    write(asset/"models/item"/(name+".json"),{"parent":"sift:block/"+name})
    write(asset/"items"/(name+".json"),{"model":{"type":"minecraft:model","model":"sift:block/"+name}})
for name in items:
    write(asset/"models/item"/(name+".json"),{"parent":"minecraft:item/generated","textures":{"layer0":"sift:item/"+name}})
    write(asset/"items"/(name+".json"),{"model":{"type":"minecraft:model","model":"sift:item/"+name}})
for locale in ("fr_fr","en_us"):
    translations={}
    for name in palette: translations["block.sift."+name]=name.replace("_"," ").title()
    for name in items: translations["item.sift."+name]=name.replace("_"," ").title()
    write(asset/"lang"/(locale+".json"),translations)
# First compile uses a conservative vanilla-noise base; custom terrain from the 0.3.7 prototype is being ported separately.
def climate(temp1,temp2):
    return {"temperature":[temp1,temp2],"humidity":[-1,1],"continentalness":[-1,1],
            "erosion":[-1,1],"weirdness":[-1,1],"depth":[-1,1],"offset":0}
write(data/"dimension/sift.json",{"type":"minecraft:overworld","generator":{
    "type":"minecraft:noise","settings":"minecraft:overworld",
    "biome_source":{"type":"minecraft:multi_noise","biomes":[
        {"biome":"sift:meadows","parameters":climate(-1,-0.08)},
        {"biome":"sift:carapace","parameters":climate(-0.08,1)}]}}})
for name,sky,fog,water in [
    ("meadows","#dfa9ee","#b98ac5","#54cad0"),("carapace","#a5a1d9","#7f8aa8","#566999")]:
    write(data/"worldgen/biome"/(name+".json"),{
        "attributes":{"minecraft:visual/sky_color":sky,"minecraft:visual/fog_color":fog},
        "carvers":[],"downfall":0,"effects":{"water_color":water,
            "grass_color":"#4dc9ac","foliage_color":"#5ab7c8"},
        "features":[[] for _ in range(11)],"has_precipitation":False,"temperature":0.65})
write(data/"recipe/luminous_relic.json",{"type":"minecraft:crafting_shaped","pattern":["SS","SS"],
    "key":{"S":"sift:lumen_shard"},"result":{"id":"sift:luminous_relic","count":1}})
print("Generated",len(palette),"blocks and",len(items),"items with independent art/models")
