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
        msg=self.command(cmd)
        print(name+" => "+repr(msg),flush=True)
        low=msg.lower()
        if not msg or any(x in low for x in (
           "unknown", "incorrect argument", "could not", "failed", "exception",
           "not a valid", "cannot find", "no dimension")):
            raise RuntimeError("Unexpected output from "+name+": "+msg)
        return msg
    def command(self,cmd):
        self.packet(502,2,cmd)
        for i in range(5):
            rid,typ,msg=self.read()
            if rid==502:
                return msg
        raise RuntimeError("No matching RCON response to "+cmd)
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
    # Natural tide must exist, with solid substrate beneath and open sky above.
    tide=sum(block_test(x,-24,z,"sift:prismatic_tide_block")[0] for x,z in samples)
    substrate=sum(not block_test(x,-53,z,"minecraft:air")[0] and
        not block_test(x,-53,z,"minecraft:lava")[0] and
        not block_test(x,-53,z,"sift:prismatic_tide_block")[0] for x,z in samples)
    if tide<3 or substrate!=len(samples):
        raise RuntimeError(f"Natural tide/substrate failed: tide={tide}, floor={substrate}")
    print(f"BASIN SURVEY: natural tide {tide}/{len(samples)}, solid Y-53 {substrate}/{len(samples)}",flush=True)
    sky=sum(block_test(x,310,z,"minecraft:air")[0] for x,z in samples)
    if sky!=len(samples):raise RuntimeError("Unexpected roof above the Sift")
    # Detect actual air-under-rock columns: density JSON alone cannot prove
    # that the narrow arch bands survive interpolation into generated blocks.
    overhangs=0
    for z in range(8,192,8):
        for x in range(8,192,8):
            if not block_test(x,40,z,"minecraft:air")[0]:continue
            if any(not block_test(x,y,z,"minecraft:air")[0] for y in (56,72,88,104)):
                overhangs+=1
    if overhangs<1:raise RuntimeError("No physical arch/overhang found in the survey")
    print(f"ARCH SURVEY: {overhangs} air-under-rock columns in 529 samples",flush=True)
    # Exhaustive scan of 192x192 columns from Y=-63 to -24, including the
    # vanilla lava altitude. fill is used as a counted query: zero replacements
    # is the only passing result, so a failing scan never hides a generation bug.
    for x in range(0,192,32):
        for z in range(0,192,32):
            for lo,hi in ((-63,-32),(-31,-24)):
                msg=c.command(f"execute in sift:sift run fill {x} {lo} {z} {x+31} {hi} {z+31} minecraft:air replace minecraft:lava")
                if "No blocks were filled" not in msg:
                    raise RuntimeError("LAVA SCAN FAILED at "+str((x,lo,z))+": "+msg)
    print("PASS: no vanilla lava in 1,474,560 generated basin blocks",flush=True)
    # The former WORLD_SURFACE bug put trunks and crossed plants directly on
    # the basin surface. Exhaustively reject these blocks at the waterline.
    for x in range(0,192,32):
        for z in range(0,192,32):
            for vegetation in ("scarlet_trunk","meadow_reed","scarlet_sprout","soul_bloom"):
                msg=c.command(f"execute in sift:sift run fill {x} -23 {z} {x+31} -23 {z+31} minecraft:air replace sift:{vegetation}")
                if "No blocks were filled" not in msg:
                    raise RuntimeError("Vegetation on basin surface: "+vegetation+": "+msg)
    print("PASS: no trunks/reeds/sprouts/blooms at the natural basin waterline",flush=True)

    # Flow and living-entity damage, independently from the natural basin.
    c.run("Build fluid test bed","execute in sift:sift run fill 0 190 0 5 190 5 sift:carapace_shale")
    c.run("Place flowing source","execute in sift:sift run setblock 2 191 2 sift:prismatic_tide_block")
    import time
    time.sleep(2)
    if not block_test(3,191,2,"sift:prismatic_tide_block")[0]:
        raise RuntimeError("Custom fluid did not flow sideways")
    c.run("Fill burn test bath","execute in sift:sift run fill 1 191 1 3 192 3 sift:prismatic_tide_block")
    c.run("Summon burn subject",'execute in sift:sift run summon minecraft:pig 2.5 191 2.5 {Tags:["sift_burn_test"],NoAI:1b,PersistenceRequired:1b}')
    def health():
        msg=c.command('execute in sift:sift run data get entity @e[tag=sift_burn_test,limit=1] Health')
        import re
        match=re.search(r": ([0-9.]+)f",msg)
        if not match:raise RuntimeError("Missing health response: "+msg)
        return float(match.group(1))
    before=health();time.sleep(1.2);after=health()
    if after>=before:raise RuntimeError("Tide did not damage the living test subject")
    fire=c.command('execute in sift:sift run data get entity @e[tag=sift_burn_test,limit=1] Fire')
    import re
    fire_ticks=re.search(r": (-?[0-9]+)s",fire)
    if not fire_ticks or int(fire_ticks.group(1))>0:
        raise RuntimeError("Vanilla orange fire unexpectedly active: "+fire)
    print(f"PASS: custom tide flows, health {before}->{after}, no vanilla fire ticks",flush=True)
    c.run("Remove burn subject","execute in sift:sift run kill @e[tag=sift_burn_test]")
    c.run("Clear fluid test bath","execute in sift:sift run fill 0 190 0 5 192 5 minecraft:air")
    c.run("Unforce 2D terrain grid","execute in sift:sift run forceload remove 0 0 191 191")
    c.sock.close()
    print("PASS: Sift chunk loaded, custom liquid block placed, chunk released",flush=True)
if __name__=="__main__":main()
