from dataclasses import dataclass, fields, field
import os,sys,Package,binascii
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from common import *
from Strings import ProcessStrings
import Util
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


@dataclass
class VertexBuffer:
    Header: TagHash

@dataclass
class IndexBuffer:
    Header: TagHash

@dataclass
class UVBuffer:
    Header: TagHash