#!/usr/bin/env python3
"""Small offline GitHub Actions RCON smoke client. No external dependencies.
Exercise loading one real Sift chunk and placing the custom registered fluid.
"""
import socket,struct,sys
HOST,PORT="127.0.0.1",25575
PASSWORD="sift-ci-only"
class Rcon:
    def __init__(self):
        self.sock=socket.create_connection((HOST,PORT),timeout=30)
        self.sock.settimeout(45)
    def packet(self,request_id,type_id,body):
        payload=struct.pack("<ii",request_id,type_id)+body.encode("utf-8")+b"\x00\x00"
        self.sock.sendall(struct.pack("<i",len(payload))+payload)
    def read(self):
        def exact(n):
            buf=b""
            while len(buf)<n:
                part=self.sock.recv(n-len(buf))
                if not part:raise ConnectionError("Server closed RCON unexpectedly")
                buf+=part
            return buf
        length=struct.unpack("<i",exact(4))[0]
        if not 10<=length<=65536:raise RuntimeError("Invalid response length "+str(length))
        raw=exact(length)
        rid,typ=struct.unpack("<ii",raw[:8])
        return rid,typ,raw[8:-2].decode("utf-8","replace")
    def authenticate(self):
        self.packet(501,3,PASSWORD)
        for i in range(4):
            rid,typ,msg=self.read()
            if rid==501:return
            if rid==-1:raise RuntimeError("RCON auth refused")
        raise RuntimeError("No auth response")
    def run(self,name,cmd):
        self.packet(502,2,cmd)
        for i in range(5):
            rid,typ,msg=self.read()
            if rid==502:
                print(name+" => "+repr(msg),flush=True)
                low=msg.lower()
                if not msg or any(x in low for x in (
                   "unknown", "incorrect argument", "could not", "failed", "exception",
                   "not a valid", "cannot find", "no dimension")):
                    raise RuntimeError("Unexpected output from "+name+": "+msg)
                return msg
        raise RuntimeError("No matching RCON response to "+name)
def main():
    c=Rcon();c.authenticate()
    c.run("Generate Sift chunk","execute in sift:sift run forceload add 0 0")
    c.run("Place custom tide in Sift","execute in sift:sift run setblock 0 145 0 sift:prismatic_tide_block")
    c.run("Unforce chunk","execute in sift:sift run forceload remove 0 0")
    # Cross-sectional survey of the actual generated terrain, not a static JSON test.
    # Two orthogonal strips cross the low-frequency tectonic noise field.
    c.run("Generate canyon strip X","execute in sift:sift run forceload add 0 0 255 15")
    c.run("Generate canyon strip Z","execute in sift:sift run forceload add 0 0 15 255")
    def block_test(x,y,z,block):
        c.packet(502,2,f"execute in sift:sift if block {x} {y} {z} {block}")
        for attempt in range(6):
            rid,kind,msg=c.read()
            if rid==502:
                return "Test passed" in msg, msg
        raise RuntimeError("Survey timeout querying " + str((x,y,z)))
    points=sorted(set([(x,8) for x in range(24,249,8)] +
                      [(8,z) for z in range(24,249,8)]))
    shallow=0; deep_air=0; solid_floor=0; ceiling_air=0
    strips={"x":[],"z":[]}
    for x,z in points:
        is_air,_=block_test(x,40,z,"minecraft:air")
        if is_air:deep_air+=1
        surface,_=block_test(x,100,z,"minecraft:air")
        if not surface:shallow+=1
        floor,_=block_test(x,-59,z,"minecraft:bedrock")
        if floor:solid_floor+=1
        sky,_=block_test(x,310,z,"minecraft:air")
        if sky:ceiling_air+=1
        strips["x" if z==8 else "z"].append("V" if is_air else "#")
    print("TERRAIN SURVEY, actual seed: sampled",len(points),"columns",flush=True)
    print("TERRAIN SURVEY at Y40: canyon/air",deep_air,"solid",len(points)-deep_air,flush=True)
    print("TERRAIN SURVEY at Y100: solid plateau",shallow,"air",len(points)-shallow,flush=True)
    print("TERRAIN SURVEY at Y310: open sky",ceiling_air,flush=True)
    print("TERRAIN CROSS SECTION X:", "".join(strips["x"]),flush=True)
    print("TERRAIN CROSS SECTION Z:", "".join(strips["z"]),flush=True)
    c.run("Unforce canyon strip X","execute in sift:sift run forceload remove 0 0 255 15")
    c.run("Unforce canyon strip Z","execute in sift:sift run forceload remove 0 0 15 255")
    # Broader 2D survey: distinguish concentrated rifts from terrain carved everywhere.
    c.run("Generate 2D terrain grid","execute in sift:sift run forceload add 0 0 191 191")
    samples=[(x,z) for z in range(8,192,24) for x in range(8,192,24)]
    deep=[];mid=[];high=[]
    for x,z in samples:
        deep.append(block_test(x,40,z,"minecraft:air")[0])
        mid.append(not block_test(x,75,z,"minecraft:air")[0])
        high.append(not block_test(x,100,z,"minecraft:air")[0])
    print("2D TERRAIN GRID: air Y40",sum(deep),"/",len(deep),flush=True)
    print("2D TERRAIN GRID: solid Y75",sum(mid),"/",len(mid),flush=True)
    print("2D TERRAIN GRID: solid Y100",sum(high),"/",len(high),flush=True)
    for row in range(8):
        print("2D RIFTS z=%3d:"%(8+24*row),
             "".join("V" if deep[row*8+i] else "#" for i in range(8)),
             "| PLATEAUS", "".join("P" if mid[row*8+i] else "." for i in range(8)),
             flush=True)
    # The fixed-seed survey must show canyons AND plateaus rather than one empty basin.
    if not (6<=sum(deep)<=38 and sum(mid)>=20 and sum(high)>=6):
        raise RuntimeError("Canyon-to-plateau balance failed: revise density masks")
    c.run("Unforce 2D terrain grid","execute in sift:sift run forceload remove 0 0 191 191")
    c.sock.close()
    print("PASS: Sift chunk loaded, custom liquid block placed, chunk released",flush=True)
if __name__=="__main__":main()
