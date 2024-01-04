from dataclasses import dataclass, fields, field
import os,sys,Package,binascii,Pickle
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from common import *


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
class SStringBank: #F1998080
    Length = 0x48
    FileSize: U32
    Unk04: U32
    StringPart: TablePointer2 #0x10 Start
    Unk18: Annotated[bytes,16]
    RawString: TablePointer2
    StringMetaData: TablePointer2
    Start=None

def FindDevStrings(Ent,FileName,PackageCache):
    FileStrings=[]
    while True:
        Check=binascii.hexlify(bytes(Ent.read(4))).decode()
        if Check == "65008080":
            Ent.seek(Ent.tell()+8)
            while True:
                tempBuffer=[]
                while True:
                    Val=binascii.hexlify(bytes(Ent.read(1))).decode()
                    if Val == "00":
                        String=binascii.unhexlify("".join(tempBuffer)).decode()
                        break
                    tempBuffer.append(Val)
                FileStrings.append([gf.FNVString(String),String])
                EndCheck=binascii.hexlify(bytes(Ent.read(1))).decode()
                if EndCheck == "":
                    break
                else:
                    Ent.seek(Ent.tell()-1)
        elif Check == "":
            break
    return FileStrings
def FnvGen():
    t_pool = mp.Pool(mp.cpu_count())
    import Util
    FnvDict={}
    _args = [(Ent[1],Ent[0],Util.PackageCache) for Ent in Package.GetAllBungieFiles(Util.PackageCache,Util.path)]
    result=t_pool.starmap_async(FindDevStrings, _args)
    StringDB=[]
    for value in result.get():
        for v in value:
            StringDB.append(v)
    for entry in StringDB:
        FnvDict[int(entry[0])] = entry[1]
    Pickle.WritePickle(FnvDict,"FNVs",Util.Cwd)

def StringGen():
    t_pool = mp.Pool(mp.cpu_count())
    import Util
    StringDict={}
    _args = [(Ent[1],Ent[0],Util.PackageCache) for Ent in Package.GetFilesWithReference(Util.PackageCache,0x808099ef,Util.path)]
    result=t_pool.starmap_async(ProcessStrings, _args)
    StringDB=[]
    for value in result.get():
        for v in value:
            StringDB.append(v)
    file=open(Util.Cwd+"/Storage/output.txt","w")
    for entry in StringDB:
        try:
            file.write(str(" // ".join(entry))+"\n")
        except UnicodeEncodeError:
            file.write(str(entry[0])+" // "+str(entry[1]+" // ?\n"))
        else:
            StringDict[int(entry[1])] = entry[2]
    file.close()
    Pickle.WritePickle(StringDict,"Strings",Util.Cwd)


def ProcessStrings(Ent,FileName,PackageCache): #idk just need 2 params
    reader = Reader[SStringContainer]().allocate()
    reader.feed(Ent.read(SStringContainer.Length))
    StringContainer = reader.build()
    StringList=[]
    if StringContainer.EULang.Hash != 0:
        StringHashes=StringContainer.HashTable.ReadStruct(Ent,Unk80800070,0x10)
        BankData=StringContainer.EULang.GetData(PackageCache)
        reader = Reader[SStringBank]().allocate()
        reader.feed(BankData.read(SStringBank.Length))
        StringBank = reader.build()
        StringParts=StringBank.StringPart.ReadStruct(BankData,SStringPart,0x10)
        StringMetaData=StringBank.StringMetaData.ReadStruct(BankData,SStringMeta,0x40)
        Index=0
        HashIndex=0
        for Data in StringMetaData:
            StringBuffer=""
            for j in range(Data.PartCount):
                StringBuffer=StringBuffer+(StringParts[Index].ReadRawString(BankData).decode())
                Index+=1
            StringList.append([FileName,str(StringHashes[HashIndex].Val),StringBuffer])
            HashIndex+=1
    return StringList


    

def QuitOut(top):
    sys.exit()


@dataclass
class SStringMeta:
    Length=0x10
    Offset: I32
    Unk04: Annotated[bytes,4]
    PartCount: U16


@dataclass
class SStringPart: #F7998080
    Length=0x20
    Unk0: Annotated[bytes,8]
    RawStringOffset: RelativePointer
    Unk0C: U32
    Unk10: DestinyHash
    StringBytes: U16
    StringChars: U16
    Start=None
    def ReadRawString(self,Buffer):
        Buffer.seek(self.Start+self.RawStringOffset.Offset+0x8)
        return Buffer.read(self.StringBytes)
        





@dataclass
class SStringContainer: 
    Length = 0x50
    FileSize: U32
    Unk04: U32
    HashTable: TablePointer2
    EULang: TagHash
    Start=None
