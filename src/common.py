from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from dataclasses import dataclass, fields, field
import gf,Package,io,binascii,ast
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
import Util

def ParseTag(combo_box,PackageCache,GlobalStringDict,FnvDict):
    Hash=combo_box.get()
    Tag=TagHash(ast.literal_eval("0x"+gf.Flip(Hash)))
    Data=Tag.GetData(PackageCache)
    Length = len(Data.read())//4
    for i in range(Length):
        Data.seek(i*4)
        Hash=int.from_bytes(Data.read(4),"little")
        try:
            print("STR:",GlobalStringDict[Hash],"at",str(hex(i*4)))
        except KeyError:
            u=1
        try:
            print("Fnv:",FnvDict[Hash],"at",str(hex(i*4)))
        except KeyError:
            u=1


def SearchVal(combo_box):
    Value=combo_box.get()
    Value="".join(Value.split(" "))
    if (len(Value) == 8) or (len(Value) == 16):
        t_pool = mp.Pool(mp.cpu_count())
        import Util
        FnvDict={}
        _args = [(Ent[1],Ent[0],Value) for Ent in Package.GetAllBungieFiles(Util.PackageCache,Util.path)]
        result=t_pool.starmap_async(SearchEntry, _args)
        result.get()

def SearchEntry(Buffer,Name,Value):
    BufferData=binascii.hexlify(bytes(Buffer.read())).decode()
    temp=[BufferData[i:i+8] for i in range(0, len(BufferData), 8)]
    for i in range(len(temp)):
        if len(Value) == 8:
            if str(temp[i]) == str((Value).lower()):
                print("Found in entry: "+Name+" @"+str(hex(i*4)))
        elif len(Value) == 16:
            try:
                temp[i]+temp[i+1]
            except IndexError:
                break
            if str(temp[i]+temp[i+1]) == str((Value.lower())):
                print("Found in entry: "+Name+" @"+str(hex(i*4)))
        else:
            print("Unsupported search criteria")
def ReadDevString(Buffer):
    Start=Buffer.tell()
    Buffer.seek(Start)
    tempBuffer=[]
    String="Unknown"
    while True:
        Val=binascii.hexlify(bytes(Buffer.read(1))).decode()
        if Val == "00" or Val == "":
            String=binascii.unhexlify("".join(tempBuffer)).decode()
            break
        tempBuffer.append(Val)
    return String

def GetEntryData(Hash):
    pkg=gf.Package_ID(Hash)
    ent=gf.Entry_ID(Hash)

@dataclass
class ExtendedHash:
    Hash32: U32
    Unk04: U32
    Hash64: U64
    ToTagHash=None
    def To32(self):
        import Util
        if self.Hash64 != 0:
            self.ToTagHash=Util.H64Data[self.Hash64]
            return self.ToTagHash

@dataclass
class RelativePointerWithClass:
    Start=None
    offset: U32
    Type=None
    def ReadStruct(self,Buffer,Struct,StartingOffset):
        TableData=None
        if self.offset != 0:
            Buffer.seek(self.offset+StartingOffset)
            reader = Reader[Struct]().allocate()
            TableStart=Buffer.tell()
            reader.feed(Buffer.read(Struct.Length))
            TableEntry=reader.build()
            TableEntry.Start=TableStart
            TableData = TableEntry
        return TableData
    def GetType(self,Buffer,StartingOffset):
        Buffer.seek(self.offset+StartingOffset-4)
        self.Type = int.from_bytes(Buffer.read(4),"little")
        return self.Type


@dataclass
class Vector4:
    x: F32
    y: F32
    z: F32
    w: F32
    def ToTrans(self):
        return str(self.x)+","+str(self.y)+","+str(self.z)+","+str(self.w)
    def ToRot(self):
        return str(self.x)+","+str(self.y)+","+str(self.z)+","+str(self.w)

@dataclass
class Vector3:
    x = 0
    y = 0
    z = 0

@dataclass
class FnvHash:
    Hash: U32


@dataclass
class DestinyHash:
    Hash: U32
    Start=None

@dataclass
class StringHash:
    Hash: U32
    def GetString(self):
        u=1
        #Todo


@dataclass
class TagHash:
    Hash: U32
    Start=None
    def GetData(self,PackageCache):
        return io.BytesIO(Package.GetFileData(self.Hash,PackageCache))
    def OutputData(self,PackageCache):
        Package.unpack_entry_ext(self.Hash,PackageCache)
    def GetReferenceData(self,PackageCache):
        Entry=Package.GetEntryA(self.Hash,PackageCache)
        return io.BytesIO(Package.GetFileData(Entry.Tag,PackageCache))
    

@dataclass
class TagHash64:
    Hash64: U64
    ToTagHash = None
    def To32(self,H64Data):
        if self.Hash64 != 0:
            self.ToTagHash=H64Data[self.Hash64]
            return self.ToTagHash

@dataclass
class Unk80800070:
    Length = 4
    Val: U32
    Start=None

@dataclass
class RelativePointer:
    Offset: U32
    Start=None
    def ReadString(self,Buffer,Start):
        Buffer.seek(Start+self.Offset)
        String=ReadDevString(Buffer)
        return String

@dataclass
class TablePointer2:
    count: U32
    unk04: U32
    offset: U32
    unk0C: U32
    start = 0
    def ReadStruct(self,Buffer,Struct,StartingOffset):
        TableData=[]
        if self.offset != 0:
            Buffer.seek(self.offset+0x10+StartingOffset)
            for j in range(self.count):
                reader = Reader[Struct]().allocate()
                TableStart=Buffer.tell()
                reader.feed(Buffer.read(Struct.Length))
                TableEntry=reader.build()
                TableEntry.Start=TableStart
                TableData.append(TableEntry)
        return TableData
