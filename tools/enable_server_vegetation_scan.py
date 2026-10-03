#!/usr/bin/env python3
"""CI-only exhaustive, non-destructive scan of vegetation directly on natural tide.
Dry shoreline plants at the same altitude are valid and must not fail the test.
"""
from pathlib import Path
import json
root=Path('src/main/resources/data/sift')
tag=root/'tags/block/ci_basin_vegetation.json';tag.parent.mkdir(parents=True,exist_ok=True)
tag.write_text(json.dumps({'values':['sift:scarlet_trunk','sift:meadow_reed',
    'sift:scarlet_sprout','sift:soul_bloom']})+'\n')
path=root/'function/ci_vegetation_scan.mcfunction'
path.write_text(''.join(f'execute if block {x} -23 {z} #sift:ci_basin_vegetation '
    f'if block {x} -24 {z} sift:prismatic_tide_block run scoreboard players add found sift_veg 1\n'
    for x in range(192) for z in range(192))+
    "scoreboard players set scan_done sift_veg 1\n")
print('Installed CI-only scan of 36,864 generated waterline positions')
