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


def ExtractLoadzoneEntities(MapContainer):
    return {},{}
def OutputDataTable(Tag,ActivityDict,PackageCache,Cwd,H64Data):
    OutputtedEntities=[]
    WorldIdMap={}
    SMapBuffer=Tag.GetData(PackageCache)
    reader = Reader[SMapDataTable]().allocate()
    reader.feed(SMapBuffer.read(SMapDataTable.Length))
    SMapHeader = reader.build()
    MapEntries=SMapHeader.InstanceTable.ReadStruct(SMapBuffer,SMapDataEntry,0x10)
    for Entry in MapEntries:
        try:
            Name=ActivityDict[Entry.WorldID]
        except KeyError:
            Name=""
        OutputString=Entry.Rotation.ToRot()+","+Entry.Translation.ToTrans()+","+Name+"\n"
        EntityHash=binascii.hexlify(bytes(gf.hex_to_little_endian(str(hex(Entry.Entity.To32(H64Data).Hash))[2:]))).decode('utf-8')
        Outfile=open(Cwd+"/Maps/Instances/"+EntityHash+".txt","a")
        Outfile.write(OutputString)
        OutputtedEntities.append(Entry.Entity.To32(H64Data))
        WorldIdMap[Entry.WorldID] = [Entry.Rotation,Entry.Translation]
    return OutputtedEntities,WorldIdMap



@dataclass
class SMapDataTable:
    Length=0x18
    FileSize: U64
    InstanceTable: TablePointer2

@dataclass
class SMapDataEntry:   #80809885
    Length = 0x90
    Start = None
    Rotation: Vector4
    Translation: Vector4
    Unk20: Annotated[list[U32], 4]
    Entity: TagHash64
    Unk38: Annotated[list[U32], 14]
    WorldID: U64
    ExtraResource: RelativePointerWithClass


@dataclass
class SBubbleParent:
    u=1

@dataclass
class SMapContainer:
    u=1