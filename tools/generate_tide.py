#!/usr/bin/env python3
"""Generate original iridescent fluid still/flow textures (PNG), bucket sprite, metadata."""
from pathlib import Path
import struct,zlib,math,colorsys,json
root=Path("src/main/resources/assets/sift")
def chunk(t,d):return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
def save_png(path,size,pixel,height=None):
    height=height or size
    path.parent.mkdir(parents=True,exist_ok=True)
    scan=b"".join(b"\x00"+b"".join(bytes(pixel(x,y)) for x in range(size)) for y in range(height))
    head=struct.pack(">IIBBBBB",size,height,8,6,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",head)+chunk(b"IDAT",zlib.compress(scan,9))+chunk(b"IEND",b""))
def rainbow(x,y,n,phase=0.0,flow=False):
    # Seamless moving aurora ribbons. Broad color changes and low contrast
    # remove the old bright oval/checker motif; the loop also joins in time.
    xx=2*math.pi*x/n; yy=2*math.pi*y/n
    warp=.45*math.sin(yy+phase)+.22*math.sin(xx-yy-phase)
    ribbon=math.sin(xx+warp+phase)
    # Most iridescence changes over time rather than forming contrasting
    # patches in each repeated block. Spatial ribbons stay deliberately faint.
    drift=.21*math.sin(phase)+.038*ribbon+.020*math.sin(yy-xx+phase)
    hue=(.57+drift)%1.0
    saturation=.18+.020*math.sin(yy+phase)
    value=.72+.012*math.sin(xx+yy-phase)
    r,g,b=colorsys.hsv_to_rgb(hue,saturation,value)
    pearl=.012*(1+math.sin((yy if flow else xx)+warp-phase))
    return tuple(min(255,round(255*(c+pearl))) for c in (r,g,b))+(232,)
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
for name in ("fr_fr","en_us"):
    f=root/"lang"/(name+".json")
    payload=json.loads(f.read_text(encoding="utf-8"))
    payload["item.sift.prismatic_tide_bucket"] = (
        "Seau de marée prismatique" if name=="fr_fr" else "Prismatic Tide Bucket"
    )
    f.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Generated 32-frame seamless aurora fluid animations, overlay, bucket and translations")
