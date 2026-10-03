#!/usr/bin/env python3
"""CI-only exhaustive, non-destructive scan, split below command-chain limits.
Dry shoreline plants at the same altitude are valid and must not fail the test.
"""
from pathlib import Path
import json
root=Path('src/main/resources/data/sift')
tag=root/'tags/block/ci_basin_vegetation.json';tag.parent.mkdir(parents=True,exist_ok=True)
tag.write_text(json.dumps({'values':['sift:scarlet_trunk','sift:meadow_reed',
    'sift:scarlet_sprout','sift:soul_bloom']})+'\n')
for bx in range(0,192,32):
    for bz in range(0,192,32):
        path=root/f'function/ci_vegetation_scan_{bx}_{bz}.mcfunction'
        path.write_text(''.join(f'execute if block {x} -23 {z} #sift:ci_basin_vegetation '
            f'if block {x} -24 {z} sift:prismatic_tide_block run setblock 0 189 0 minecraft:redstone_block\n'
            for x in range(bx,bx+32) for z in range(bz,bz+32))+
            'setblock 1 189 0 minecraft:diamond_block\n')
print('Installed 36 CI-only scan functions covering 36,864 waterline positions')
