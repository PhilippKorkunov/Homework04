import os
import pathlib
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    update_index(gitdir, paths)

def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    index=read_index(gitdir)
    tree=write_tree(gitdir,index)
    sha=commit_tree(gitdir,tree,message,author=author)
    if not is_detached(gitdir):
        ref=get_ref(gitdir)
    else:
        ref=gitdir/"HEAD"
    update_ref(gitdir,ref,sha)
    return sha


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    ref = get_ref(gitdir)
    if os.path.isfile(gitdir/ref):
        f=open(gitdir/ref,"r")
        ref=f.read()
        f.close()
    a=read_object(ref,gitdir)
    fmt=a[0]
    content=a[1].decode()
    objects = find_tree_files(content[5:45], gitdir)
    dirs = gitdir.absolute().parent
    for i in range(len(objects)):
        b=objects[i]
        b=b[0]
        os.remove(dirs / b)
        next_path = pathlib.Path(b).parent 
        while len(next_path.parents) > 0:
            os.rmdir(next_path)
            next_path = pathlib.Path(next_path).parent
    f=open(gitdir / "HEAD","w")
    f.write(obj_name)
    f.close()
    c=read_object(obj_name, gitdir)
    fmt=c[0]
    new_content=c[1].decode() 
    objects = find_tree_files(new_content[5:45], gitdir)
    for i in range(len(objects)):
        z = len(pathlib.Path(b).parents)
        par_path = dirs
        k=objects[i]
        for j in range(z - 2, -1, -1):
            par_path /= pathlib.Path(k[0]).parents[j]
            if not os.path.isdir(par_path):
                os.mkdir(par_path)
        z = len(pathlib.Path(b).parents)
        par_path = dirs
        for j in range(z - 2, -1, -1):
            par_path /= pathlib.Path(k[0]).parents[j]
            if not os.path.isdir(par_path):
                os.mkdir(par_path)
        fmt, obj_content = read_object(k[1], gitdir)
        if fmt == "blob":
            pathlib.Path(dirs / k[0]).touch()
            f=open(dirs / k[0],"w")
            f.write(obj_content.decode())
            f.close()
        else:
            os.mkdir(dirs / k[0])
