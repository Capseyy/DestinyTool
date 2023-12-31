from dataclasses import dataclass, fields, field
import os,sys,Package,binascii
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from common import *
from Strings import ProcessStrings
from Model import VertexBuffer,IndexBuffer,UVBuffer
temp=os.getcwd()
temp=temp.split("\\")
output="/".join(temp[:len(temp)])
sys.path.append(output+"/ThirdParty")
from fbx import FbxManager
import FbxCommon

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

def ExtractEntity(Tag,PackageCache):
    EntityBuffer=Tag.GetData(PackageCache)
    reader = Reader[SEntity]().allocate()
    reader.feed(EntityBuffer.read(SEntity.Length))
    Entity = reader.build()
    EntityResources=Entity.ResourceTable.ReadStruct(Entity,Unk80809ACD,0x10)
    HasMesh=False
    for EntityResource in EntityResource:
        ResourceData=EntityResource.ResourceTag.GetData(PackageCache)
        reader = Reader[SEntityResource]().allocate()
        reader.feed(ResourceData.read(SEntityResource.Length))
        EntityResourceObject = reader.build()
        ResourceType18=EntityResourceObject.Resource0x18.GetType(ResourceData,0x18)
        if ResourceType18 == 0x80806d8f: #model mesh
            ModelResource=EntityResourceObject.Resource0x18.ReadStruct(ResourceData,Unk80806D8F,0x18)
            ModelResourceData=ResourceData
            HasMesh = True
    if HasMesh == True:
        ExternalMaterialMaps=ModelResource.ExternalMaterialMapTable.ReadStruct(ModelResourceData,SExternalMaterialMapEntry,ModelResource.Start+0x3C8)
        ExternalMaterials=ModelResource.ExternalMaterialMapTable.ReadStruct(ModelResourceData,Unk80800014,ModelResource.Start+0x408)
        EntityModelBuffer=ModelResource.MeshFile.GetData(PackageCache)
        reader = Reader[SEntityModel]().allocate()
        reader.feed(EntityModelBuffer.read(SEntityModel.Length))
        EntityModel = reader.build()
        Meshes = EntityModel.ModelMeshes.ReadStruct(EntityModelBuffer,SEntityModelMesh,0x18)



@dataclass
class SEntityModel:
    Length = 0xA0
    FileSize: U64
    Unk08: Annotated[list[U32], 2]
    ModelMeshes: TablePointer2
    Unk20: Vector4
    Unk30: Annotated[list[U32], 8]
    ModelScale: Vector4
    ModelTranslation: Vector4
    TexcoordScale: Vector4
    TexcoordTranslation: Vector4

@dataclass
class SEntityModelMesh:
    Length = 0x80
    VertexPositionBuffer: VertexBuffer
    UVBuffer: UVBuffer
    WeightBuffer: VertexBuffer
    Unk0C: TagHash
    IndexBuffer: IndexError
    ColorBuffer: VertexBuffer
    SPSBukker: VertexBuffer #Single Pass Skinning
    Unk1C: U32
    PartsTable: TablePointer2

@dataclass
class SEntityModelMeshParts:
    Length = 0x24
    Material: TagHash
    VarientShaderIndex: U16
    PrimitiveType: U16
    IndexOffset: U32
    IndexCount: U32
    Unk10: U32
    ExternalIdentifier: U16
    Unk16: U16
    Flags: I32
    GearDyeChangeColorIndex: U8
    ELodCatagory: U8
    Unk1E: U8
    LodRun: U8
    Unk20: U32


@dataclass
class SEntity:
    Length=0x98
    FileSize: U64
    ResourceTable: TablePointer2
    UnkTable0x18: TablePointer2
    Unk28: Annotated[list[U32], 4]
    EntityID: U32
    Unk4C: U32
    UnkTable50: TablePointer2
    UnkTable60: TablePointer2
    UnkTable70: TablePointer2
    Unk80: U32
    Unk84: TagHash #Global?
    Unk88: U32


@dataclass
class Unk80806D8F:  #Entity Mesh Resource
    Length = 0x450
    Unk00: Annotated[list[U32], 137]
    MeshFile: TagHash #0x224
    Unk228: Annotated[list[U32], 98]
    ExternalMaterialMapTable: TablePointer2
    Unk3D0: Annotated[list[U32], 8]
    Unk3F0: TablePointer2
    ExternalMaterials: TablePointer2


@dataclass
class Unk80800014:
    Length = 4
    MaterialTag: TagHash

@dataclass
class SExternalMaterialMapEntry:
    Length = 0xC
    MaterialCount: U32
    MaterialStartIndex: U32
    Unk08: U32

@dataclass
class Unk80809ACD:
    Length=0xC
    ResourceTag: TagHash


@dataclass
class SEntityResource: #069b8080
    Length = 160
    FileSize: U32
    Unk04: Annotated[list[U32], 5]
    Resource0x18: RelativePointerWithClass #0x18
    Unk1C: U32
    Table1: TablePointer2
    Table2: TablePointer2
    Table3: TablePointer2
    Unk40: Annotated[list[U32], 12]
    StringFile: TagHash
    FnvDict = {}
    def GenerateFnvDict(self,PackageCache):
        StringDict={}
        if self.StringFile.Hash != 0xffffffff:
            StringFileBuffer=self.StringFile.GetData(PackageCache)
            reader = Reader[Unk8080806B]().allocate()
            reader.feed(StringFileBuffer.read(Unk8080806B.Length))
            StringFile = reader.build()
            StringTables=StringFile.StringTable.ReadStruct(StringFileBuffer,Unk80809D02,0x10)
            for Table in StringTables:
                if Table.StringPointer.offset != 0:
                    String=Table.ReadString(StringFileBuffer)
                    StringFnv=gf.FNVString(String)
                    StringDict[StringFnv] = String
        return StringDict


@dataclass
class Unk8080806B:
    Length=0x20
    FileSize: U64
    StringTable: TablePointer2

@dataclass
class Unk80809D02:   #EntityResStringTable in ^
    Length=0x10
    Start=None
    StringPointer: RelativePointerWithClass
    Unk04: U32
    UnkPointer: RelativePointerWithClass
    def ReadString(self,Buffer):
        Type=self.StringPointer.GetType(Buffer,self.Start)
        if Type == 0x8080894d:
            StringClass = self.StringPointer.ReadStruct(Buffer,Unk8080894D,self.Start)
            print(StringClass.Start)
            String=StringClass.StringOffset.ReadString(Buffer,StringClass.Start)
        return String

@dataclass
class Unk8080894D:
    Length=0x18
    StringOffset: RelativePointer
    Unk04: U32
    ResHash: TagHash
    UnkType: U32
    UnkOffset: U32

@dataclass
class Unk808098FA:
    Start=None
    Length = 120
    Unk0: TagHash #Self Reference
    Unk04: Annotated[list[U32], 3]
    DestinationString: StringHash
    Unk14: U32
    BubbleString: StringHash
    Unk1C: U32
    PhaseHash1: U32
    PhaseHash2: U32
    GlobalFnv: FnvHash
    Unk2C: U32
    GlobalWorldID: U64
    Unk38: U32
    Unk3999: TagHash
    Unk40: I64
    Unk239B: TagHash
    Unk4C: Annotated[list[U32], 3]
    WorldIDTable: TablePointer2
    Unk68: Annotated[list[U32], 2]
    RawStringOffset: RelativePointer
    Name = "Unknown"
    def ReadPhaseName(self,Buffer):
        ResetPos=Buffer.tell()
        Buffer.seek(self.Start+self.RawStringOffset.Offset+112)
        self.Name=ReadDevString(Buffer)
        Buffer.seek(ResetPos)
        return self.Name

@dataclass
class Unk80809905:
    Length = 0x10
    Fnv: U32
    Unk04: U32
    WorldID: U64


@dataclass
class Unk808098EF:
    Length = 0x78
    Start= None
    Unk0: TagHash #Self Reference
    Unk04: Annotated[list[U32], 3]
    DestinationString: StringHash
    Unk14: U32
    BubbleString: StringHash
    Unk1C: U32
    PhaseHash1: U32
    PhaseHash2: U32
    GlobalFnv: FnvHash
    Unk2C: U32
    GlobalWorldID: U64
    Unk38: U32
    Unk3999: TagHash
    Unk40: I64
    Unk239B: TagHash
    Unk4C: Annotated[list[U32], 3]
    WorldIDTable: TablePointer2




@dataclass
class Unk808092D8:   #Activity entity spawner
    Start=None
    Length = 0x190
    Unk0: TagHash #Self Reference
    Unk04: Annotated[list[U32], 3]
    DestinationString: StringHash
    Unk14: U32
    BubbleString: StringHash
    Unk1C: U32
    PhaseHash1: U32
    PhaseHash2: U32
    GlobalFnv: FnvHash
    Unk2C: U32
    GlobalWorldID: U64
    Unk38: U32
    Unk3999: TagHash
    Unk40: I64
    Unk239B: TagHash
    Unk44: Annotated[list[U32], 7]
    AttributesTable: TablePointer2
    Unk1699: TagHash
    Unk7C: Annotated[list[U32], 2]
    DataTable: TagHash
    Unk88: Annotated[list[U32], 2]
    GlobalRotation: Vector4
    GlobalTranslation: Vector4
    #Todo bunch more 239b's

@dataclass
class Unk80809956: #AttributeTable
    Length = 0x18
    SelfReference: TagHash
    Class: U32
    AbsOffset: U32
    Unk0C: U32
    AttributeOffset: RelativePointerWithClass






