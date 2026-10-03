execute if data storage sift:return {saved:1b} run function sift:leave_saved with storage sift:return
execute unless data storage sift:return {saved:1b} run tellraw @s {"text":"No saved return position. Enter with /function sift:enter from the Overworld first.","color":"red"}
