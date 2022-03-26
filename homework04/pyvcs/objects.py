import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    if fmt=="blob":
        s=data.decode()
        k=f"blob {len(s)}\0"
        data=k+s
        hash_object = hashlib.sha1(data.encode())
        hex_dig = hash_object.hexdigest()
        h=str(hex_dig)
        a=h[0]+h[1]
        b=""
        for i in range(2,len(h)):
            b+=h[i]
    if fmt=="tree":
        s=data
        k=f"tree {len(s)}\0"
        data=k.encode()+s
        hash_object = hashlib.sha1(data)
        hex_dig = hash_object.hexdigest()
        h=str(hex_dig)
        a=h[0]+h[1]
        b=""
        for i in range(2,len(h)):
            b+=h[i]
    if fmt=="commit":
        s=data
        k=f"commit {len(s)}\0"
        data=k.encode()+s
        hash_object = hashlib.sha1(data)
        hex_dig = hash_object.hexdigest()
        h=str(hex_dig)
        a=h[0]+h[1]
        b=""
        for i in range(2,len(h)):
            b+=h[i]            
    if write==True:
        gd=repo_find()
        obj=gd/"objects"
        if not os.path.exists(obj/pathlib.Path(a)):
            os.mkdir(obj/pathlib.Path(a))
        if not os.path.exists(obj/pathlib.Path(a)/pathlib.Path(b)):
            pathlib.Path(obj/pathlib.Path(a)/pathlib.Path(b)).touch()
            f = open(obj/pathlib.Path(a)/pathlib.Path(b), "wb")
            if fmt=="blob":
                p=zlib.compress(data.encode())
            if fmt=="tree" or  fmt=="commit":
                p=zlib.compress(data,-1)
            f.write(p)
            f.close()
    return hex_dig

def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    obj=obj_name
    if len(obj)<4 or len(obj)>41:
        raise AssertionError(f"Not a valid object name {obj_name}")
    gd=gitdir
    gd=gd/"objects"
    a=obj[0]+obj[1]
    b=""
    for i in range(2,len(obj)):
        b+=obj[i]
    n=os.listdir(gd/pathlib.Path(a))
    t=p=[]
    for i in range(len(n)):
        k=n[i]
        s=t=""
        for j in range(len(b)):
            s+=k[j]
        if b==str(s):
            for j in range(len(k)):
                t+=k[j]
            t=a+t
            p.append(t)
    if len(t)==0:
        raise AssertionError(f"Not a valid object name {obj_name}")
    return p
    

def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    return resolve_object(obj_name, gitdir)[0]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    path = find_object(sha, gitdir)
    f=open(gitdir/"objects"/path[0:2]/path[2:],"rb")
    q=f.read()
    q=zlib.decompress(q)
    ind= q.find(b" ")
    a=q.find(b"\x00")
    content = q[a+1:]
    fmt = q[:ind].decode()
    f.close()
    return fmt, content 

def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    a = []
    while len(data) > 0:
        fmt = data[:6].decode()
        data = data[6:]
        if fmt == "100644" or fmt=="100755":
            data = data[1:]
        ind = data.find(b"\x00")
        a.append((int(fmt), data[:ind].decode(), data[ind+1:ind+21].hex()))
        data = data[ind+21:]
    return a

def cat_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    v=str(data)
    i=0
    q=[]
    while True:
        s=m=p=l=""
        if i<len(v)-10:
            for j in range(5):
                if v[i+j].isdigit():
                    s+=v[i+j]
        if s=="40000":
            m="0"+s
            i+=6
        if i<len(v)-10:
            for j in range(6):
                if v[i+j].isdigit():
                    p+=v[i+j]
        if p=="100644" or p=="100755":
            m=p
            i+=7
        if m!="":
            while v[i]!="\\":
                l+=v[i]
                i+=1
            c=[m,l]
            q.append(c)
        i+=1
        if i==len(v):
            break
    t=0
    for i in range(len(data)):
        if data[i]==0:
            if t>=1:
                q[t-1].append(data[i+1:i+21].hex())
            t+=1
    return q

def cat_file(obj_name: str, pretty: bool = True) -> None:
    sha=obj_name
    path=pathlib.Path(sha[0:2])
    path=path/sha[2:len(sha)]
    path="objects"/path
    path=pathlib.Path(repo_find()/path)
    f=open(path,"rb")
    q=f.read()
    q=zlib.decompress(q)
    f.close()
    v=str(q)
    if v[2]=="b":
        q=q[8:]
        print(q.decode())
    if v[2]=="t":
        q=cat_tree(q)
        for i in range(len(q)):
            if q[i][0]=="040000":
                z=q[i][0]+" "+"tree"+" "+q[i][2]+"\t"+q[i][1]
            if q[i][0]=="100644" or q[i][0]=="100755":
                z=q[i][0]+" "+"blob"+" "+q[i][2]+"\t"+q[i][1]
            print(z)
    if v[2]=="c":
        i=0
        while True:
            if q[i]==0:
                t=i+1
                break
            i+=1
                
        print(q[t:].decode())
    pass

        
        
        
def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    fmt, content = read_object(tree_sha, gitdir)
    objects = read_tree(content)
    arr = []
    for i in objects:
        if i[0] == 100644:
            arr.append((i[1], i[2]))
        else:
            sub_objects = find_tree_files(i[2], gitdir)
            for j in sub_objects:
                arr.append((i[1] + "/" + j[0], j[1]))
    return arr

def commit_parse(raw: bytes, start: int = 0, dct=None):
    pass
