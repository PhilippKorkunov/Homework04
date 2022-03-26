import os
import pathlib
import stat
import time
import typing as tp
import hashlib
import binascii

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    a=index
    q=b""
    for i in range(len(a)):
        s=""
        g=a[i]
        mode=g.mode
        p=""
        while mode>0:
            p+=str(mode%8)
            mode=mode//8
        mode=p[::-1]        
        sha=g.sha1
        name=g.name
        n=name.split("/")
        name=n[len(n)-1]
        s+=mode+" "+name+"\0"
        s=s.encode()
        s+=sha
        h=hash_object(s,"tree",False)
        h=bytes.fromhex(h)
        if len(n)==1:
            q+=s
            f=open(name,"r")
            e=f.read()
            e=e.encode()
            f.close()
            hash_object(e,"blob",True)
        if len(n)>1:
            z=""
            for i in range(1,len(n)-1):
                m=""
                name=str(n[len(n)-2-i])
                mode="40000"
                m+=mode+" "+name+"\0"
                m=m.encode()
                m+=h
                h=hash_object(m,"tree",False)
                h=h=binascii.unhexlify(h)
            name=str(n[0])
            mode="40000"
            z+=mode+" "+name+"\0"
            z=z.encode()
            z+=h
            hash_object(s,"tree",True)
            q+=z
    return hash_object(q,"tree",True)
    
    
    
def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    commenttime = str(int(time.mktime(time.localtime()))) + " " + str(time.strftime("%z", time.gmtime()))
    string = "tree "
    string += tree
    string += "\nauthor "
    string += author
    string += " "
    string += commenttime
    string += "\ncommitter "
    string += author
    string += " "
    string += commenttime
    string += "\n\n"
    string += message
    string += "\n"
    return hash_object(string.encode(), "commit", True)
