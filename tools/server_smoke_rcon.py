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
    c.sock.close()
    print("PASS: Sift chunk loaded, custom liquid block placed, chunk released",flush=True)
if __name__=="__main__":main()
