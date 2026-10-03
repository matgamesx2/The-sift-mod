#!/usr/bin/env python3
"""THE SIFT 0.5.4 dedicated 26.3 world generator.
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
# Two 2D fracture networks make long connected tectonic rifts instead of rolling mountains.
def fissure(name,width,scale,strength,edge=1.0,warp=0.0):
    centerline=ab(noise(name,scale,0.0))
    if warp:
        # Warp the fault EDGE in three dimensions, rather than lifting mesa
        # summits. The wall moves inward/outward across Y to form rock breaks.
        centerline=add(centerline,mul(warp,noise("wall_breakup",.62,.50)))
    mask=clamp(mul(edge,add(width,mul(-1.0,centerline))),0.0,width)
    return mul(-strength,mask)
main_distance=ab(noise("rift_network",.56,0.0))
# Tributaries get shallower away from the main fault instead of making a
# second equally-wide canyon system. Higher-frequency branches meet the trunk.
branch_reach=clamp(mul(8.0,add(.28,mul(-1.0,main_distance))),0.0,1.0)
rifts=add(fissure("rift_network",.100,.56,90.0,edge=4.0,warp=.050),
          mul(branch_reach,fissure("rift_branches",.055,.70,62.0)))
# Keep high plateaus, but give the fractures priority.
# Quantized tectonic elevations make true flat mesas, not rounded hilltops.
# The 2D field chooses each plateau's altitude; 3D noise is restricted to walls.
def terrace(field,low,mid,high):
    return {"type":"minecraft:range_choice","input":field,
        "min_inclusive":-1000.0,"max_exclusive":-.16,
        "when_in_range":low,"when_out_of_range":{
            "type":"minecraft:range_choice","input":field,
            "min_inclusive":-.16,"max_exclusive":.18,
            "when_in_range":mid,"when_out_of_range":high}}
meadow=terrace(noise("meadow_swell",.60,0.0),-.12,.18,.58)
carapace=terrace(add(noise("carapace_ridge",.62,0.0),
                    mul(.22,ab(noise("sharp_cliffs",.74,0.0)))),.02,.34,.76)
biome_relief={"type":"minecraft:range_choice","input":"minecraft:overworld/temperature",
    "min_inclusive":-1000.0,"max_exclusive":-0.08,
    "when_in_range":meadow,"when_out_of_range":carapace}
summit_fade={"type":"minecraft:gradient","axis":"y","tiling":"clamp_to_edge",
    "from_coordinate":72,"to_coordinate":104,"from_value":1.0,"to_value":0.0}
overhang=mul(summit_fade,add(mul(.90,noise("overhang",.65,.48)),
             mul(.58,noise("wall_breakup",.78,.95))))
surface_gradient={"type":"minecraft:gradient","axis":"y","tiling":"clamp_to_edge",
    "from_coordinate":-64,"to_coordinate":285,"from_value":4.10,"to_value":-4.05}
# A steeper upper gradient limits rounded summits; fault-side ledges cut the
# long walls into broken horizontal shelves without filling the canyon trunk.
upper_cap={"type":"minecraft:gradient","axis":"y","tiling":"clamp_to_edge",
    "from_coordinate":96,"to_coordinate":160,"from_value":1.25,"to_value":-2.85}
surface_gradient={"type":"minecraft:min","left":surface_gradient,"right":upper_cap}
fractured=add(add(surface_gradient,biome_relief),add(rifts,overhang))
# Local rock bridges: thin crossing bands with open space underneath, bounded
# vertically so they cannot turn into a Nether roof. 3D noise roughens the arch.
def minimum(a,b):return {"type":"minecraft:min","left":a,"right":b}
def ygradient(a,b,lo,hi):return {"type":"minecraft:gradient","axis":"y",
    "tiling":"clamp_to_edge","from_coordinate":a,"to_coordinate":b,
    "from_value":lo,"to_value":hi}
ledge_zone=clamp(mul(25.0,add(main_distance,-.055)),0.0,1.0)
ledge_patch=clamp(add(.35,noise("wall_breakup",.46,0.0)),0.0,.7)
for bottom,top in ((6,19),(35,47),(64,75),(88,97)):
    band=minimum(ygradient(bottom-7,bottom,-1.0,1.0),
                 ygradient(top,top+7,1.0,-1.0))
    band=clamp(band,0.0,1.0)
    fractured=add(fractured,mul(ledge_zone,mul(ledge_patch,mul(2.4,band))))
bridge_band=minimum(ygradient(46,70,-1.0,1.0),ygradient(82,110,1.0,-1.0))
bridge_shape=add(bridge_band,mul(.52,noise("overhang",.65,.48)))
bridge_crossing=mul(32.0,add(.034,mul(-1.0,ab(noise("bridge_paths",.65,0.0)))))
bridge_zone=mul(12.0,add(.115,mul(-1.0,main_distance)))
bridges=minimum(bridge_zone,minimum(bridge_crossing,bridge_shape))
fractured={"type":"minecraft:max","left":fractured,"right":bridges}
# Irregular impermeable substrate above the vanilla generator's deep lava
# layer. Even the lowest floor must remain above Y=-54; tide fills the basin.
floor={"type":"minecraft:gradient","axis":"y","tiling":"clamp_to_edge",
       "from_coordinate":-56,"to_coordinate":-30,
       "from_value":10.0,"to_value":-10.0}
floor=add(floor,mul(2.0,noise("basin_floor",.70,0.0)))
density={"type":"minecraft:interpolated",
         "input":{"type":"minecraft:max","left":fractured,"right":floor},
         "cell_size_xz":4,"cell_size_y":8}
for name,octave,amps in [
    ("rift_network",-8,[1.0,.65,.32,.17]),
    ("rift_branches",-7,[1.0,.58,.31,.16]),
    ("meadow_swell",-7,[1.0,.58,.28]),
    ("carapace_ridge",-6,[1.0,.75,.45]),
    ("sharp_cliffs",-5,[1.0,.55,.30]),
    ("overhang",-5,[1.0,.75,.35]),
    ("wall_breakup",-4,[1.0,.55,.25]),
    ("bridge_paths",-6,[1.0,.45,.20]),
    ("basin_floor",-5,[1.0,.65,.30])]:
    put(Path("worldgen/noise")/(name+".json"),{
        "base_octave":octave,"octave_count":len(amps),"amplitude_modifiers":amps})
put("worldgen/noise_settings/fractured.json",{
    "sea_level":-23,"disable_mob_generation":True,"legacy_random_source":False,
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
        "chunk_surface_level":122.0
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
    top,sub,condition(biome("meadows"),block("sift:carapace_shale")),
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
def placed(name,positions,rarity=None,count=None,rock=False):
    mods=[]
    if rarity is not None:mods.append({"type":"minecraft:rarity_filter","chance":rarity})
    if count is not None:mods.append({"type":"minecraft:count","count":count})
    mods += [{"type":"minecraft:in_square"},
             {"type":"minecraft:heightmap","heightmap":"WORLD_SURFACE_WG"},
             {"type":"minecraft:block_predicate_filter",
              "predicate":{"type":"minecraft:all_of","predicates":[
                  {"type":"minecraft:matching_blocks","blocks":"minecraft:air"},
                  {"type":"minecraft:matching_blocks","offset":[0,-1,0],
                   "blocks":(["sift:carapace_stone","sift:carapace_shale","sift:sift_ochre"]
                             if rock else ["sift:teal_turf","sift:meadow_soil",
                                           "sift:red_growth","sift:spore_mat"])}]}},
             {"type":"minecraft:biome"}]
    put("worldgen/placed_feature/"+positions+".json",{"feature":"sift:"+name,"placement":mods})
simple_feature("meadow_reeds","sift:meadow_reed")
simple_feature("scarlet_sprouts","sift:scarlet_sprout")
simple_feature("soul_blooms","sift:soul_bloom")
simple_feature("carapace_glints","sift:lumen_cluster")
placed("meadow_reeds","meadow_reeds",count=5)
placed("scarlet_sprouts","scarlet_sprouts",count=4)
placed("soul_blooms","soul_blooms",count=3)
placed("carapace_glints","carapace_glints",count=2,rock=True)
# Dry-ground predicates run BEFORE the tree feature can replace its substrate.
# All three silhouettes use our own red bark/canopy rather than vanilla stems.
for name,height,radius,rarity in (("scarlet_tree",4,2,12),
                                  ("scarlet_tree_wide",5,4,22),
                                  ("scarlet_tree_tall",8,3,32)):
    put("worldgen/feature/"+name+".json",{
        "type":"minecraft:tree",
        "below_trunk_provider":{"type":"minecraft:simple","state":{"id":"sift:teal_turf"}},
        "decorators":[],
        "foliage_placer":{"type":"minecraft:blob_foliage_placer","height":3,
                          "offset":0,"radius":radius},
        "foliage_provider":{"type":"minecraft:simple","state":{"id":"sift:red_canopy"}},
        "ignore_vines":True,"minimum_size":{"type":"minecraft:two_layers_feature_size","upper_size":2},
        "trunk_placer":{"type":"minecraft:straight_trunk_placer",
                        "base_height":height,"height_rand_a":2,"height_rand_b":1},
        "trunk_provider":{"type":"minecraft:simple","state":{"id":"sift:scarlet_trunk"}}
    })
    placed(name,name+"s",rarity=rarity)
put("worldgen/feature/fossil_spires.json",{
    "type":"minecraft:block_column",
    "allowed_placement":{"type":"minecraft:matching_blocks","blocks":"minecraft:air"},
    "direction":"up",
    "layers":[{"height":{"type":"minecraft:uniform","min_inclusive":8,"max_inclusive":25},
               "provider":{"type":"minecraft:simple","state":{"id":"sift:fossil_rib"}}}],
    "prioritize_tip":False
})
placed("fossil_spires","fossil_spires",rarity=25,rock=True)
for name,sky,fog,water,features in [
    ("meadows","#b7a4c8","#847a99","#183a59",
     ["sift:scarlet_trees","sift:scarlet_tree_wides","sift:scarlet_tree_talls","sift:meadow_reeds","sift:scarlet_sprouts","sift:soul_blooms"]),
    ("carapace","#969cbc","#64718c","#183a59",
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
print("Generated 0.5.4: flat tectonic mesas, sharp branching faults, broken walls, arches and lava-proof basin floor")
