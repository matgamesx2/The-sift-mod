#!/usr/bin/env python3
"""Generate original iridescent fluid still/flow textures (PNG), bucket sprite, metadata."""
from pathlib import Path
import struct,zlib,math,json
from png_io import read_rgba
root=Path("src/main/resources/assets/sift")
def chunk(t,d):return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
def save_png(path,size,pixel,height=None):
    height=height or size
    path.parent.mkdir(parents=True,exist_ok=True)
    scan=b"".join(b"\x00"+b"".join(bytes(pixel(x,y)) for x in range(size)) for y in range(height))
    head=struct.pack(">IIBBBBB",size,height,8,6,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",head)+chunk(b"IDAT",zlib.compress(scan,9))+chunk(b"IEND",b""))
# Authored dark iridescent details are advected through a periodic distortion
# field, rather than drawing a stationary pastel sine-wave floor. Real texture
# alpha exposes the rock below; highlights stay sparse and shift independently.
art=read_rgba(Path("tools/art/tide_detail.png"))
ART=len(art)
def sample(u,v):
    u%=ART;v%=ART
    x,y=int(u),int(v);fx,fy=u-x,v-y
    return tuple((art[y][x][c]*(1-fx)+art[y][(x+1)%ART][c]*fx)*(1-fy)+
        (art[(y+1)%ART][x][c]*(1-fx)+art[(y+1)%ART][(x+1)%ART][c]*fx)*fy
        for c in range(3))
def rainbow(x,y,n,phase=0.0,flow=False):
    xx=2*math.pi*x/n;yy=2*math.pi*y/n
    # Integer spatial frequencies tile, circular advection closes frame 31->0.
    warp_x=2.3*math.sin(yy+phase)+1.2*math.sin(2*xx-yy-phase)
    warp_y=2.1*math.cos(xx-phase)+1.1*math.sin(xx+2*yy+phase)
    shift=5.0 if flow else 2.8
    u=x*ART/n+warp_x+shift*math.sin(phase)
    v=y*ART/n+warp_y+shift*math.cos(phase)
    r,g,b=sample(u,v)
    # Reflection strength derives from the painted caustics, not a stripe mask.
    glow=max(0.0,(max(r,g,b)-75)/180)**1.35
    ripple=.5+.5*math.sin(xx+yy+phase+math.sin(xx-2*yy-phase))
    tint=.5+.5*math.sin(phase+xx*.0)
    red=18+.29*r+glow*(17+10*tint)
    green=35+.34*g+glow*15
    blue=54+.35*b+glow*(12+8*ripple)
    alpha=145+round(35*glow)
    return tuple(min(255,round(c)) for c in (red,green,blue))+(alpha,)
tex=root/"textures/block"
SIZE,FRAMES=128,32
for name in ("still","flow"):
    p=tex/("prismatic_tide_"+name+".png")
    save_png(p,SIZE,lambda x,y:rainbow(x,y%SIZE,SIZE,
        2*math.pi*(y//SIZE)/FRAMES,name=="flow"),SIZE*FRAMES)
    p.with_suffix(".png.mcmeta").write_text(json.dumps({"animation":{
        "width":SIZE,"height":SIZE,"frametime":3,"interpolate":True}},indent=2)+"\n")
save_png(tex/"prismatic_tide_overlay.png",SIZE,lambda x,y:rainbow(x,y,SIZE))
def bucket(x,y):
    cx=abs(x-8)
    in_bucket=4<=y<=13 and 2<=x<=13 and (y<7 or cx<=5)
    if not in_bucket:return (0,0,0,0)
    if y<7:return rainbow(x,y,16)
    if x in (2,13) or y==13:return (60,73,105,255)
    return (118,153,178,255)
save_png(root/"textures/item/prismatic_tide_bucket.png",16,bucket)
p=root/"models/item/prismatic_tide_bucket.json"
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps({"parent":"minecraft:item/generated","textures":{
    "layer0":"sift:item/prismatic_tide_bucket"}},indent=2)+"\n")
q=root/"items/prismatic_tide_bucket.json"
q.parent.mkdir(parents=True,exist_ok=True)
q.write_text(json.dumps({"model":{"type":"minecraft:model",
    "model":"sift:item/prismatic_tide_bucket"}},indent=2)+"\n")
# LiquidBlock is rendered by the fluid renderer, but every block state still
# needs a baked block model. Empty geometry prevents missing-model warnings.
for relative,value in (
    ("blockstates/prismatic_tide_block.json",{"variants":{"":{
        "model":"sift:block/prismatic_tide_empty"}}}),
    ("models/block/prismatic_tide_empty.json",{"parent":"minecraft:block/block",
        "textures":{"particle":"sift:block/prismatic_tide_still"},"elements":[]})):
    f=root/relative;f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(value,indent=2)+"\n")
for name in ("fr_fr","en_us"):
    f=root/"lang"/(name+".json")
    payload=json.loads(f.read_text(encoding="utf-8"))
    payload["item.sift.prismatic_tide_bucket"] = (
        "Seau de marée prismatique" if name=="fr_fr" else "Prismatic Tide Bucket"
    )
    f.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Generated 32-frame dark translucent iridescent fluid animations, overlay, bucket and translations")
