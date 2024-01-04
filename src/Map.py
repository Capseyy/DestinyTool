from dataclasses import dataclass, fields, field
import os,sys,Package,binascii
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from common import *
from Strings import ProcessStrings
import Util, Havok
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

def OutputDataTable(Data,ActivityDict,PackageCache,Cwd,H64Data):
    OutputtedEntities=[]
    WorldIdMap={}
    Tag=Data[0]
    GlobalWorldID=Data[1]
    GlobalRotation=Data[2]
    GlobalTranslation=Data[3]
    SMapBuffer=Tag.GetData(PackageCache)
    reader = Reader[SMapDataTable]().allocate()
    reader.feed(SMapBuffer.read(SMapDataTable.Length))
    SMapHeader = reader.build()
    MapEntries=SMapHeader.InstanceTable.ReadStruct(SMapBuffer,SMapDataEntry,0x10)
    for Entry in MapEntries:
        if Entry.WorldID == 18446744073709551615: #0xfffffffffffff
            Entry.WorldID = GlobalWorldID
        try:
            Name=ActivityDict[Entry.WorldID]
        except KeyError:
            Name=""
        OutputString=Entry.Rotation.ToRot()+","+Entry.Translation.ToTrans()+","+Name+"\n"
        EntityHash=binascii.hexlify(bytes(gf.hex_to_little_endian(str(hex(Entry.Entity.To32(H64Data).Hash))[2:]))).decode('utf-8')
        Outfile=open(Cwd+"/Maps/Instances/"+EntityHash+".txt","a")
        Outfile.write(OutputString)
        OutputtedEntities.append(Entry.Entity.To32(H64Data))
        Outfile.close()
        WorldIdMap[Entry.WorldID] = [Entry.Rotation,Entry.Translation]
        if Entry.ExtraResource.offset != 0:
            ExtraResourceType=Entry.ExtraResource.GetType(SMapBuffer,Entry.Start+0x78)
            if ExtraResourceType == 0x80809121:   #HavokFile
                HavokResource=Entry.ExtraResource.ReadStruct(SMapBuffer,Unk80809121,Entry.Start+0x78)
                HavokData=HavokResource.HavokTag.GetData(PackageCache)
                HavokHash=binascii.hexlify(bytes(gf.hex_to_little_endian(str(hex(HavokResource.HavokTag.Hash))[2:]))).decode('utf-8')
                Havok.ExtractHxk(HavokData,HavokHash)
                Outfile=open(Cwd+"/Maps/Instances/"+HavokHash+".txt","a")
                Outfile.write(OutputString)
                Outfile.close()


    return [OutputtedEntities,WorldIdMap]

@dataclass
class Unk80809121:
    Length = 0x20
    Unk00: Annotated[list[U32], 4]
    HavokTag: TagHash
    Unk14: U32


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