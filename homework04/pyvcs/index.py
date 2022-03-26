import hashlib
import operator
import os
import pathlib
import struct
import typing as tp
import binascii
from collections import namedtuple

from pyvcs.objects import hash_object
from unittest import TestCase
TestCase.maxDiff = None


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str
    
    def pack(self) -> bytes:
        ctime_s=self.ctime_s
        ctime_n=self.ctime_n
        mtime_s=self.mtime_s
        mtime_n=self.mtime_n
        dev=self.dev
        ino=self.ino
        mode=self.mode
        uid=self.uid
        gid=self.gid
        size=self.size
        sha1=self.sha1
        flags=self.flags
        name=str(self.name)
        value=struct.pack("!10i",ctime_s,ctime_n,mtime_s,mtime_n,dev,ino,mode,uid,gid,size)
        value+=sha1
        value+=struct.pack("!h",flags)
        s=name.encode()
        l=len(name)+3
        l=str(l)+"s"
        value+=struct.pack(l,s)
        return value
    

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        k=struct.unpack("!10i",data[0:40])
        s=data[40:60]
        p=struct.unpack("!h",data[60:62])
        p=p[0]
        l=str(len(data)-62-3)
        l=l+"s"
        t=struct.unpack(l,data[62:len(data)-3])
        t=t[0]
        t=t.decode()
        return GitIndexEntry(
            ctime_s=k[0],
            ctime_n=k[1],
            mtime_s=k[2],
            mtime_n=k[3],
            dev=k[4],
            ino=k[5],
            mode=k[6],
            uid=k[7],
            gid=k[8],
            size=k[9],
            sha1=s,
            flags=p,
            name=t)
    
def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    gd=pathlib.Path(gitdir/"index")
    if os.path.exists(gd):
        f=open(gd,"br")
        q=f.read()
        a1=q[8:12]
        l=q[12:84]
        a1=struct.unpack("!i",a1)
        a1=a1[0]
        l=""
        a=[]
        q1=str(q)
        for i in range(len(q1)):
            if q1[i]==chr(92):
                a.append(l)
                l=""
            else:
                l+=q1[i]
        l=""
        b=[]
        for i in range(len(a)):
            if len(a[i])>3:
                p=a[i]
                l=p[3:len(p)]
            for j in range(len(l)):
                if l[j]==".":
                    b.append((l))
                    break
            l=""
        for i in range(len(b)):
            b[i]=len(b[i])+3
        x=0
        b1=[]
        for i in range(a1):
            l=q[12+x:74+x+b[i]]
            x+=62+b[i]
            l=GitIndexEntry.unpack(l)
            b1.append(l)
        return b1
    else:
        return []


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    gd=pathlib.Path(gitdir/"index")   
    a=entries
    l=len(a)   
    value=b"DIRC\x00\x00\x00\x02"
    value+=struct.pack("!i",l)
    for i in range(len(a)):
        value+=GitIndexEntry.pack(a[i])
    hash_object = hashlib.sha1(value)
    hex_dig = hash_object.hexdigest()
    h=binascii.unhexlify(hex_dig)
    value+=h
    if not os.path.exists(gd):
        pathlib.Path(gd).touch()
    f = open(gd, "wb")
    f.write(value)
    f.close()  

def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    ind=read_index(gitdir)
    l=""
    if details==False:
        for i in range(len(ind)):
            a=ind[i]
            l+=str(a.name)
            l+="\n"
        print(l)
    if details==True:
        for i in range(len(ind)):
            a=ind[i]
            m=a.mode
            p=""
            while m>0:
                p+=str(m%8)
                m=m//8
            p=p[::-1]
            s=a.sha1
            s=str(s.hex())
            l=str(a.name)
            k=p+" "+s+" "+"0"+"\t"+l
            print(k)


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    a=[]
    for i in range(len(paths)):
        p=str(paths[i])
        paths[i]=p
    paths.sort()
    for i in range(len(paths)):
        paths[i]=pathlib.Path(paths[i])
        p=pathlib.Path(paths[i])
        f=open(p,"r")
        q=f.read()
        q=q.encode()
        hashs=hash_object(q,"blob",True)
        v=os.stat(paths[i])
        sha=binascii.unhexlify(hashs)
        if len(str(paths[i]).replace("\\" , "/"))>=7:
            fl=7
        else:
            fl=len(str(paths[i]).replace("\\" , "/"))
        en=GitIndexEntry(
            ctime_s=v[9],
            ctime_n=0,
            mtime_s=v[8],
            mtime_n=0,
            dev=v[2],
            ino=v[1],
            mode=v[0],
            uid=v[4],
            gid=v[5],
            size=v[6],
            sha1=sha,
            flags=fl,
            name=str(paths[i]).replace("\\" , "/")
        )
        f.close()
        a.append(en)
    write_index(gitdir,a)
    pass
