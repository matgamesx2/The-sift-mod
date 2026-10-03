#!/usr/bin/env python3
"""THE SIFT 0.5.0 dedicated 26.3 world generator.
The look is an original interpretation of the user-provided Dungeons II references:
roofless amplified cliffs, elongated deep rifts, unstable ridges and prismatic tide below.
All files are plain data; no proprietary game assets are copied.
"""
from pathlib import Path
import json
root=Path("src/main/resources/data/sift")
def put(relative, value):
    p=root/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def noise(name,xz,y):
    return {"type":"minecraft:noise","noise":"sift:"+name,"xz_scale":xz,"y_scale":y}
def add(left,right):return {"type":"minecraft:add","left":left,"right":right}
def mul(left,right):return {"type":"minecraft:mul","left":left,"right":right}
def ab(value):return {"type":"minecraft:abs","input":value}
def clamp(value,low,high):return {"type":"minecraft:clamp","input":value,"min":low,"max":high}
def gradient():return {"type":"minecraft:gradient","axis":"y","tiling":"clamp_to_edge",
    "from_coordinate":-64,"to_coordinate":280,"from_value":4.2,"to_value":-5.0}
# Long branching trenches appear where a broad 2D noise field crosses zero;
# subtracting them from the full vertical density cuts down toward the tide.
rifts=mul(-14.0,clamp(add(.24,mul(-1.0,ab(noise("rift_network",.54,0.0)))),0.0,.24))
# Large plateaus, serrated ridges and three-dimensional cliff undercuts.
meadow=mul(1.45,noise("meadow_swell",.64,0.0))
carapace=add(mul(1.55,noise("carapace_ridge",.60,0.0)),
             mul(.72,ab(noise("sharp_cliffs",.83,.10))))
biome_relief={"type":"minecraft:range_choice","input":"minecraft:overworld/temperature",
    "min_inclusive":-1000.0,"max_exclusive":-0.08,
    "when_in_range":meadow,"when_out_of_range":carapace}
overhang=mul(.88,noise("overhang",.67,.29))
# Use exposed 26.3 interpolation inside final_density, with strictly negative
# density at the highest altitude so NO NETHER-LIKE BEDROCK CEILING can form.
density={"type":"minecraft:interpolated",
         "input":add(add(gradient(),biome_relief),add(rifts,overhang)),
         "cell_size_xz":4,"cell_size_y":8}
for name,octave,amps in [
    ("rift_network",-8,[1.0,.65,.32,.17]),
    ("meadow_swell",-7,[1.0,.58,.28]),
    ("carapace_ridge",-6,[1.0,.75,.45]),
    ("sharp_cliffs",-5,[1.0,.55,.30]),
    ("overhang",-5,[1.0,.75,.35])]:
    put(Path("worldgen/noise")/(name+".json"),{
        "base_octave":octave,"octave_count":len(amps),"amplitude_modifiers":amps})
put("worldgen/noise_settings/fractured.json",{
    "sea_level":26,"disable_mob_generation":True,"legacy_random_source":False,
    "default_block":{"id":"sift:carapace_shale"},
    "default_fluid":{"id":"sift:prismatic_tide_block"},
    "noise":{"height":384,"min_y":-64},
    "noise_router":{
        "continents":"minecraft:overworld/continents",
        "depth":"minecraft:overworld/depth",
        "erosion":"minecraft:overworld/erosion",
        "ridges":"minecraft:overworld/ridges",
        "temperature":"minecraft:overworld/temperature",
        "vegetation":"minecraft:overworld/vegetation",
        "final_density":density,
        "chunk_surface_level":88.0
    },
    "material_rule":"sift:fractured",
    "spawn_target":[
        {"minecraft:overworld/temperature":[-.8,-.2]},
        {"minecraft:overworld/temperature":[.2,.8]}
    ]
})
def block(name):return {"type":"minecraft:block","result_state":{"id":name}}
def condition(test,then):return {"type":"minecraft:condition","if_true":test,"then_run":then}
def biome(name):return {"type":"minecraft:biome","biome_is":"sift:"+name}
def layer(offset,adddepth):
    return {"type":"minecraft:stone_depth","add_surface_depth":adddepth,
        "offset":offset,"secondary_depth_range":0,"surface_type":"floor"}
bedrock={"type":"minecraft:vertical_gradient","random_name":"sift:bedrock_floor",
    "true_at_and_below":{"above_bottom":0},"false_at_and_above":{"above_bottom":5}}
top=condition(layer(0,False),{"type":"minecraft:sequence","sequence":[
    condition(biome("meadows"),{"type":"minecraft:sequence","sequence":[
        condition({"type":"minecraft:noise_threshold","noise":"minecraft:surface",
                   "min_threshold":.34,"max_threshold":10.0},block("sift:meadow_soil")),
        block("sift:teal_turf")]}),
    condition(biome("carapace"),{"type":"minecraft:sequence","sequence":[
        condition({"type":"minecraft:noise_threshold","noise":"minecraft:surface",
                   "min_threshold":.2,"max_threshold":10.0},block("sift:sift_ochre")),
        block("sift:carapace_stone")]}),
]})
sub=condition(layer(3,True),{"type":"minecraft:sequence","sequence":[
    condition(biome("meadows"),block("sift:meadow_soil")),
    condition(biome("carapace"),block("sift:carapace_shale"))
]})
put("worldgen/material_rule/fractured.json",{"type":"minecraft:sequence","sequence":[
    condition(bedrock,block("minecraft:bedrock")),
    top,sub,condition(biome("meadows"),block("sift:meadow_soil")),
    condition(biome("carapace"),block("sift:carapace_shale"))
]})
def climate(lo,hi):
    return {"temperature":[lo,hi],"humidity":[-1.0,1.0],"continentalness":[-1.0,1.0],
            "erosion":[-1.0,1.0],"weirdness":[-1.0,1.0],"depth":[-1.0,1.0],"offset":0.0}
put("dimension/sift.json",{"type":"minecraft:overworld","generator":{
    "type":"minecraft:noise","settings":"sift:fractured",
    "biome_source":{"type":"minecraft:multi_noise","biomes":[
        {"biome":"sift:meadows","parameters":climate(-1.0,-.08)},
        {"biome":"sift:carapace","parameters":climate(-.08,1.0)}]}}})
# 26.3 feature layout already validated in our 0.3.7 pack: worldgen/feature is
# unified configured-feature + configuration; placement lives separately.
def simple_feature(name,blockname):
    put("worldgen/feature/"+name+".json",{
        "type":"minecraft:simple_block","to_place":{
            "type":"minecraft:simple","state":{"id":blockname}}})
def placed(name,positions,rarity=None,count=None):
    mods=[]
    if rarity is not None:mods.append({"type":"minecraft:rarity_filter","chance":rarity})
    if count is not None:mods.append({"type":"minecraft:count","count":count})
    mods += [{"type":"minecraft:in_square"},
             {"type":"minecraft:heightmap","heightmap":"WORLD_SURFACE_WG"},
             {"type":"minecraft:block_predicate_filter",
              "predicate":{"type":"minecraft:matching_blocks","blocks":"minecraft:air"}},
             {"type":"minecraft:biome"}]
    put("worldgen/placed_feature/"+positions+".json",{"feature":"sift:"+name,"placement":mods})
simple_feature("meadow_reeds","sift:meadow_reed")
simple_feature("scarlet_sprouts","sift:scarlet_sprout")
simple_feature("soul_blooms","sift:soul_bloom")
simple_feature("carapace_glints","sift:lumen_cluster")
placed("meadow_reeds","meadow_reeds",count=6)
placed("scarlet_sprouts","scarlet_sprouts",count=7)
placed("soul_blooms","soul_blooms",count=3)
placed("carapace_glints","carapace_glints",count=2)
# Familiar trees are intentionally scarce while cliff shapes are tested; no endless Nether forest.
put("worldgen/feature/scarlet_tree.json",{
    "type":"minecraft:tree",
    "below_trunk_provider":{"type":"minecraft:simple","state":{"id":"sift:teal_turf"}},
    "decorators":[],
    "foliage_placer":{"type":"minecraft:blob_foliage_placer","height":2,"offset":0,"radius":3},
    "foliage_provider":{"type":"minecraft:simple","state":{"id":"minecraft:red_poplar_leaves"}},
    "ignore_vines":True,"minimum_size":{"type":"minecraft:two_layers_feature_size","upper_size":2},
    "trunk_placer":{"type":"minecraft:straight_trunk_placer",
                    "base_height":8,"height_rand_a":3,"height_rand_b":2},
    "trunk_provider":{"type":"minecraft:simple","state":{"id":"minecraft:crimson_stem"}}
})
placed("scarlet_tree","scarlet_trees",rarity=7)
put("worldgen/feature/fossil_spires.json",{
    "type":"minecraft:block_column",
    "allowed_placement":{"type":"minecraft:matching_blocks","blocks":"minecraft:air"},
    "direction":"up",
    "layers":[{"height":{"type":"minecraft:uniform","min_inclusive":8,"max_inclusive":25},
               "provider":{"type":"minecraft:simple","state":{"id":"sift:fossil_rib"}}}],
    "prioritize_tip":False
})
placed("fossil_spires","fossil_spires",rarity=25)
for name,sky,fog,water,features in [
    ("meadows","#dfa9ee","#b98ac5","#87daca",
     ["sift:scarlet_trees","sift:meadow_reeds","sift:scarlet_sprouts","sift:soul_blooms"]),
    ("carapace","#a5a1d9","#7f8aa8","#caa7dd",
     ["sift:fossil_spires","sift:carapace_glints"])]:
    put("worldgen/biome/"+name+".json",{
        "attributes":{"minecraft:visual/sky_color":sky,"minecraft:visual/fog_color":fog},
        "carvers":[],"downfall":0.0,
        "effects":{"water_color":water,"grass_color":"#4dc9ac","foliage_color":"#5ab7c8"},
        "features":[[] for _ in range(10)]+[features],
        "has_precipitation":False,"temperature":.65})
# Distinct fluid tag. We deliberately avoid minecraft:water: water extinguishes
# fire and would conflict with the Sift's blue-burning hazard.
put("tags/fluid/prismatic_tide.json",{
    "values":["sift:prismatic_tide","sift:flowing_prismatic_tide"]})
put("function/tide_test.mcfunction",None) if False else None
print("Generated roofless fractured Sift terrain, biome-specific surfaces and 6 decor features")
