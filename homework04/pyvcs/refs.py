import pathlib
import typing as tp

def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    gd=pathlib.Path(gitdir)
    pathlib.Path(gd/pathlib.Path(ref)).touch()
    f = open(pathlib.Path(gd/ref), "w")
    f.write(new_value)
    f.close()

def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    gd=pathlib.Path(gitdir)
    s=f"ref: {ref}"
    pathlib.Path(gd/pathlib.Path(name)).touch()
    f = open(pathlib.Path(gd/ref), "w")
    f.write(s)
    f.close()

def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:    
    gd=pathlib.Path(gitdir)
    if refname=="HEAD":
        gd=gd/refname
        f=open(gd,"r")
        q=f.read()
        q=q[5:]
        q=q[:-1]
        f.close()
        file=open(gitdir/q,"r")
        q=file.read()
        file.close()
    if refname=="refs/heads/master":
        f=open((gd/refname).absolute())
        q=f.read()
        f.close()
    return q

def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    gd=pathlib.Path(gitdir)
    gd=gd/"refs/heads/master"
    if gd.exists():
        f= open(gd, "r")
        q=f.read()
        f.close()
        return q  



def is_detached(gitdir: pathlib.Path) -> bool:
    if not pathlib.Path.exists(gitdir/"HEAD"):
            return False
    else:
        gd=gitdir/"HEAD"
        f=open(gd,"r")
        q=f.read()
        if q[0:5] != "ref: ":
            return True
    return False


        

def get_ref(gitdir: pathlib.Path) -> str:
    p=gitdir
    p=p/"HEAD"
    file=open(p,"r")
    q=file.read()
    if q[:5]=="ref: ":
        q=q[5:-1]
    file.close()
    return q
