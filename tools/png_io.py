"""Read our authored, non-interlaced 8-bit RGBA PNGs without CI dependencies."""
import struct,zlib

def read_rgba(path):
    data=path.read_bytes()
    if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Invalid PNG: '+str(path))
    offset=8;packed=b''
    while offset<len(data):
        size=struct.unpack('>I',data[offset:offset+4])[0]
        kind=data[offset+4:offset+8];part=data[offset+8:offset+8+size]
        if kind==b'IHDR':
            width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',part)
            if (depth,color,interlace)!=(8,6,0):raise ValueError('Expected RGBA PNG')
        elif kind==b'IDAT':packed+=part
        offset+=size+12
    decoded=zlib.decompress(packed);stride=width*4;previous=bytearray(stride);rows=[]
    def paeth(a,b,c):
        p=a+b-c;da,db,dc=abs(p-a),abs(p-b),abs(p-c)
        return a if da<=db and da<=dc else b if db<=dc else c
    for y in range(height):
        start=y*(stride+1);ft=decoded[start];row=bytearray(decoded[start+1:start+stride+1])
        for x in range(stride):
            a=row[x-4] if x>=4 else 0;b=previous[x];c=previous[x-4] if x>=4 else 0
            predictor=(0,a,b,(a+b)//2,paeth(a,b,c))[ft]
            row[x]=(row[x]+predictor)&255
        rows.append([tuple(row[x:x+4]) for x in range(0,stride,4)])
        previous=row
    return rows
