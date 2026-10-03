#!/usr/bin/env python3
"""Generate original iridescent fluid still/flow textures (PNG), bucket sprite, metadata."""
from pathlib import Path
import struct,zlib,math,colorsys,json
root=Path("src/main/resources/assets/sift")
def chunk(t,d):return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
def save_png(path,size,pixel):
    path.parent.mkdir(parents=True,exist_ok=True)
    scan=b"".join(b"\x00"+b"".join(bytes(pixel(x,y)) for x in range(size)) for y in range(size))
    head=struct.pack(">IIBBBBB",size,size,8,6,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",head)+chunk(b"IDAT",zlib.compress(scan,9))+chunk(b"IEND",b""))
def rainbow(x,y,n):
    # Seamless low-saturation color field; avoids checkerboard when tiled.
    xx=2*math.pi*x/n; yy=2*math.pi*y/n
    drift=.19*math.sin(xx)+.14*math.cos(yy)+.09*math.sin(xx+yy)
    hue=(.55+drift+.045*math.cos(xx*2-yy))%1.0
    r,g,b=colorsys.hsv_to_rgb(hue,.35,.93)
    pearl=.045*(1.0+math.cos(xx-yy))
    return (min(255,int(255*(r+pearl))),
            min(255,int(255*(g+pearl))),
            min(255,int(255*(b+pearl))),174)
tex=root/"textures/block"
save_png(tex/"prismatic_tide_still.png",64,lambda x,y:rainbow(x,y,64))
save_png(tex/"prismatic_tide_flow.png",64,lambda x,y:rainbow(x,y,64))
save_png(tex/"prismatic_tide_overlay.png",64,lambda x,y:rainbow(x,y,64))
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
print("Generated 3 iridescent fluid textures, bucket icon and translations")
