# Singleplayer test only: shared data storage cannot safely store several players' return points.
execute store result storage sift:return x double 0.001 run data get entity @s Pos[0] 1000
execute store result storage sift:return y double 0.001 run data get entity @s Pos[1] 1000
execute store result storage sift:return z double 0.001 run data get entity @s Pos[2] 1000
data modify storage sift:return saved set value 1b
