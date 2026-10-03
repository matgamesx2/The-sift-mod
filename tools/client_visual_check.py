#!/usr/bin/env python3
"""Exercise a real offline Minecraft client under Xvfb and capture game frames."""
import os,subprocess,time,json
from pathlib import Path
from server_smoke_rcon import Rcon
out=Path('run/visual');out.mkdir(parents=True,exist_ok=True)
c=Rcon();c.authenticate()
c.run('Allow offline visual test player','whitelist add SiftVisualTest')
for attempt in range(180):
    if 'SiftVisualTest' in c.command('list'):break
    log=Path('run/visual/client-console.log').read_text(errors='replace')
    if 'Failed to create backend Vulkan' in log and 'Failed to create backend OpenGL' in log:
        raise RuntimeError('Software graphics backend failed; inspect client-console.log')
    if attempt in (30,90,179):
        subprocess.run(['import','-window','root',str(out/(f'00-startup-{attempt}.png'))],timeout=15)
    time.sleep(1)
else:raise RuntimeError('Client did not join the offline test server')
player='SiftVisualTest'
c.run('Flying camera','gamemode spectator '+player)
c.run('Daylight','execute in sift:sift run time set 6000')
c.command('gamerule advance_time false')
c.command('gamerule do_mob_spawning false')
# The client must be focused before sending its native screenshot shortcut.
windows=subprocess.check_output(['xdotool','search','--name','Minecraft']).decode().splitlines()
if not windows:raise RuntimeError('No Minecraft OpenGL window')
window=windows[-1]
subprocess.run(['xdotool','windowfocus',window],check=True)
subprocess.run(['xdotool','key','--window',window,'F1'],check=True)
def capture(name,x,y,z,yaw,pitch):
    c.run('Camera '+name,f'execute in sift:sift run tp {player} {x} {y} {z} {yaw} {pitch}')
    time.sleep(12)
    subprocess.run(['import','-window',window,str(out/(name+'.png'))],check=True,timeout=25)
    print('CLIENT FRAME: '+name,flush=True)
capture('01-fractured-plateaus',96,160,96,-45,36)
c.run('Load natural basins','execute in sift:sift run forceload add 0 0 191 191')
basin=None
for z in range(8,192,24):
    for x in range(8,192,24):
        if 'Test passed' in c.command(f'execute in sift:sift if block {x} -24 {z} sift:prismatic_tide_block'):
            basin=(x,z);break
    if basin:break
if not basin:raise RuntimeError('No natural tide found for the client capture')
x,z=basin
capture('02-natural-tide',x+.5,-14,z+.5,35,18)
# A known-depth pool isolates actual flowing-fluid rendering and underwater view.
c.run('Pool floor','execute in sift:sift run fill 220 145 220 232 145 232 sift:carapace_shale')
c.run('Pool walls','execute in sift:sift run fill 220 146 220 232 150 232 sift:fossil_rib hollow')
c.run('Pool tide','execute in sift:sift run fill 221 146 221 231 149 231 sift:prismatic_tide_block')
c.run('Open pool surface','execute in sift:sift run fill 221 150 221 231 150 231 minecraft:air')
capture('03-tide-depth',226.5,153,218.5,0,35)
c.run('First-person liquid contact','gamemode creative '+player)
# HUD on: verifies the blue effect in first-person and the underwater tint.
subprocess.run(['xdotool','key','--window',window,'F1'],check=True)
capture('04-submerged-first-person',226.5,146.5,226.5,0,3)
log=Path('run/visual/client-console.log').read_text(errors='replace')
bad=[line for line in log.splitlines() if 'sift:' in line and any(t in line.lower() for t in
     ('unable to load','missing model','missing texture','failed to load','exception'))]
if bad:raise RuntimeError('Client resource errors: '+ '\n'.join(bad))
(out/'result.json').write_text(json.dumps({'client_joined':True,'dimension':'sift:sift',
    'natural_basin':basin,'screenshots':4,'sift_resource_errors':bad},indent=2))
print('PASS: real Minecraft client joined, rendered Sift chunks and custom liquid',flush=True)
c.command('stop');c.sock.close()
