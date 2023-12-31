
import sys,os,ast
sys.path.append(os.getcwd()+"/src")
import gf, Util
from UI import Window
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from bytechomp.datatypes import (
    U8,  # 8-bit unsigned integer
    U16,  # 16-bit unsigned integer
    U32,  # 32-bit unsigned integer
    U64,  # 64-bit unsigned integer
    I8,  # 8-bit signed integer
    I16,  # 16-bit signed integer
    I32,  # 32-bit signed integer
    I64,  # 64-bit signed integer
    F16,  # 16-bit float
    F32,  # 32-bit float
    F64,  # 64-bit float
)

global CWD,PackageCache,H64Data






if __name__ == "__main__":
    Util.init()
    root=Window(Util.Cwd,Util.PackageCache)
    root.MainWindow()