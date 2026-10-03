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
    h=((x/n)*0.48+(y/n)*0.57 + .06*math.sin(x*.5+y*.3))%1
    r,g,b=colorsys.hsv_to_rgb(h,.48,.95)
    shine=.08*math.sin(.68*x-.39*y)
    return (int(255*min(1,r+shine)),int(255*min(1,g+shine)),
            int(255*min(1,b+shine)),205)
tex=root/"textures/block"
save_png(tex/"prismatic_tide_still.png",16,lambda x,y:rainbow(x,y,16))
save_png(tex/"prismatic_tide_flow.png",32,lambda x,y:rainbow(x,y,32))
save_png(tex/"prismatic_tide_overlay.png",16,lambda x,y:rainbow(x,y,16))
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
