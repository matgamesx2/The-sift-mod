# Experimental single-player command. Always enter from the Overworld.
execute unless dimension minecraft:overworld run tellraw @s {"text":"Enter the Sift from the Overworld so your return position can be saved.","color":"red"}
execute if dimension minecraft:overworld run function sift:save_return
execute if dimension minecraft:overworld in sift:sift run tp @s 96 180 0
execute if dimension sift:sift run spreadplayers 96 0 24 90 false @s
execute if dimension sift:sift run effect give @s minecraft:slow_falling 25 0 true
execute if dimension sift:sift run tellraw @s {"text":"THE SIFT: experimental biome terrain. /function sift:leave to return.","color":"aqua"}
