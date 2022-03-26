import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    workdir=pathlib.Path(workdir)
    wprkdir=workdir.absolute()
    if "GIT_DIR" in os.environ:
        pass
    else:
        os.environ["GIT_DIR"] = ".git"
    t=r=w=""
    o=0
    n=[]
    s=str(workdir)
    for i in range(len(s)):
        if (ord(s[i])==47 or ord(s[i])==92) and i!=0:
            o+=1
            n.append(w)
            w=""
        elif i!=0:
            w+=s[i]
    n.append(w)
    k=0
    for i in range(len(n)):
        if n[i]==os.environ["GIT_DIR"]:
            k=i
    if k!=0:
        i=o=0
        while i<=k+1:       
            if ord(s[o])==47 or ord(s[o])==92:
                i+=1
            r+=s[o]
            o+=1
        r=pathlib.Path(r)
        return r.absolute()
    else:
        for i in os.listdir(workdir):
            if i == os.environ["GIT_DIR"]:
                t= pathlib.Path("/")/os.environ["GIT_DIR"]
    if t=='':
        raise AssertionError("Not a git repository")
    else:
        return t.absolute()


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    workdir=pathlib.Path(workdir)
    workdir.absolute()    
    if not workdir.is_dir():
        raise AssertionError(f"{workdir} is not a directory")
    if "GIT_DIR" in os.environ:
        pass
    else:
        os.environ["GIT_DIR"] = ".git"
    gd=pathlib.Path(os.environ["GIT_DIR"])
    if not os.path.exists(workdir/gd):
        os.mkdir(gd)
    if not os.path.exists(workdir/gd/pathlib.Path("refs")):
        os.makedirs(gd/pathlib.Path("refs"))
    if not os.path.exists(workdir/gd/pathlib.Path("objects")):
        os.makedirs(gd/pathlib.Path("objects"))
    if not os.path.exists(workdir/gd/pathlib.Path("refs")/pathlib.Path("heads")):
        os.makedirs(gd/pathlib.Path("refs")/pathlib.Path("heads"))
    if not os.path.exists(workdir/gd/pathlib.Path("refs")/pathlib.Path("tags")):
        os.makedirs(gd/pathlib.Path("refs")/pathlib.Path("tags"))
    if not os.path.exists(pathlib.Path(workdir/gd/pathlib.Path("HEAD"))):
        pathlib.Path(gd/pathlib.Path("HEAD")).touch()
        q=pathlib.Path(workdir/gd/"HEAD")
        f = open(pathlib.Path(workdir/gd/pathlib.Path("HEAD")), "w")
        f.write("ref: refs/heads/master\n")
        f.close()    
    if not os.path.exists(pathlib.Path(workdir/gd/pathlib.Path("config"))):
        pathlib.Path(gd/pathlib.Path("config")).touch()
        q=pathlib.Path(workdir/gd/"config")
        f = open(pathlib.Path(workdir/gd/pathlib.Path("config")), "w")
        f.write("[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n")
        f.close()  
    if not os.path.exists(pathlib.Path(workdir/gd/pathlib.Path("desctiption"))):
        pathlib.Path(gd/pathlib.Path("description")).touch()
        q=pathlib.Path(workdir/gd/"description")
        f = open(pathlib.Path(workdir/gd/pathlib.Path("description")), "w")
        f.write("Unnamed pyvcs repository.\n")
        f.close()         

    return pathlib.Path(workdir/gd)
