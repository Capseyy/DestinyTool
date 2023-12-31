from dataclasses import dataclass, fields, field
import os,sys,Package,binascii
from bytechomp import Reader, dataclass, Annotated, serialize
import multiprocessing as mp
from common import *
from Strings import ProcessStrings
from Entity import SEntityResource,Unk808098FA,Unk808092D8,Unk80809956,Unk80809905,Unk808098EF,ExtractEntity
from Map import OutputDataTable, ExtractLoadzoneEntities
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


def ActivityListGen(Window):
    import Util
    ActivityNames={}
    NamedTags=Package.GetNamedTags(Util.PackageCache,Util.path)
    for Tag in NamedTags:
        if Tag.Reference == 0x80808e8e:
            if "." in Tag.Name:
                ActivityNames[Tag.Name] = Tag
    Window.ActList=ActivityNames
    Window.ActivityMenu()


def GetScriptTableName(Script,PackageCache):
    Buffer2=Script.ActivityEntityParent.GetData(PackageCache)
    reader = Reader[Unk80808E89]().allocate()
    reader.feed(Buffer2.read(Unk80808E89.Length))
    EntityParent = reader.build()
    ActivityGlobalEntityBuffer=EntityParent.EntityGlobal.GetData(PackageCache)
    reader = Reader[Unk80808EBE]().allocate()
    reader.feed(ActivityGlobalEntityBuffer.read(Unk80808EBE.Length))
    EntityGlobals = reader.build()
    EntityResourceParents=EntityGlobals.EntityResources.ReadStruct(ActivityGlobalEntityBuffer,Unk80808942,0x10)
    ParentBuffer=EntityResourceParents[0].EntityResourceParent.GetData(PackageCache)
    reader = Reader[Unk80808943]().allocate()
    reader.feed(ParentBuffer.read(Unk80808943.Length))
    EntityParent = reader.build()
    EntityResourceBuffer=EntityParent.EntityResource.GetData(PackageCache)
    reader = Reader[SEntityResource]().allocate()
    reader.feed(EntityResourceBuffer.read(SEntityResource.Length))
    EntityResource = reader.build()
    EntResource1Type = EntityResource.Resource0x18.GetType(EntityResourceBuffer,0x18)
    if EntResource1Type == 0x808098fa:
        EntResource1=EntityResource.Resource0x18.ReadStruct(EntityResourceBuffer,Unk808098FA,0x18)
        return [EntResource1.ReadPhaseName(EntityResourceBuffer),EntityResourceParents]
    else:
        return ["Unknown",EntityResourceParents]

def GetEncounterList(Window,input,ActList):
    import Util
    DevNameDict={}
    DevNames=[]
    t_pool = mp.Pool(mp.cpu_count())
    ActivityTag=ActList[input.get()]
    Buffer=ActivityTag.Hash.GetData(Util.PackageCache)
    reader = Reader[SActivity]().allocate()
    reader.feed(Buffer.read(SActivity.Length))
    Activity = reader.build()
    Activity.GetStringContainer()
    PhaseTables=Activity.PhaseTable.ReadStruct(Buffer,Unk80808926,0x48)
    for Phase in PhaseTables:
        PhaseScriptTables=Phase.EncounterScript.ReadStruct(Buffer,Unk80808948,Phase.Start+80)
        _args = [(Script,Util.PackageCache) for Script in PhaseScriptTables]
        result=t_pool.starmap_async(GetScriptTableName, _args)
        for value in result.get():
            temp=value[0].split("\\")
            DevNames.append(temp[len(temp)-1])
            DevNameDict[temp[len(temp)-1]] = value[1]
    BubbleTables=Activity.BubbleTable.ReadStruct(Buffer,Unk80808924,0x58)    
    for Bubble in BubbleTables:
        ScriptTables=Bubble.ScriptTable.ReadStruct(Buffer,Unk80808948,Bubble.Start+0x20)
        _args = [(Script,Util.PackageCache) for Script in ScriptTables]
        result=t_pool.starmap_async(GetScriptTableName, _args)
        for value in result.get():
            temp=value[0].split("\\")
            DevNames.append(temp[len(temp)-1])
            DevNameDict[temp[len(temp)-1]] = value[1]
    Window.DevNameDict=DevNameDict
    Window.EncounterMenu()

def ExtractEncounter(combo_box,DevNameDict,PackageCache):
    import Util
    LoadzoneWorldIDs,EntitiesToRip=ExtractLoadzoneEntities()
    t_pool = mp.Pool(mp.cpu_count())
    TagsToParse=DevNameDict[combo_box.get()]
    DataToProcess=[]
    DataTables=[]
    _args = [(Tag,PackageCache) for Tag in TagsToParse]
    result=t_pool.starmap_async(ParseEntityFile, _args)
    for value in result.get():
        DataToProcess.append(value)
    ActivityDict={}
    for Entry in DataToProcess:
        if Entry.StringDict != {}:
            for Key,Value in Entry.StringDict.items():
                ActivityDict[Key]=Value
    for Entry in DataToProcess:
        if Entry.DataTable != None:
            try:
                Name=ActivityDict[Entry.GroupFnv.Hash]
            except KeyError:
                Name=""
            DataTables.append(Entry.DataTable)
    _args = [(Entry,ActivityDict,PackageCache,Util.Cwd,Util.H64Data) for Entry in DataTables]
    result=t_pool.starmap_async(OutputDataTable, _args)
    for value in result.get():
        try:
            EntitiesToRip[value[0].Hash]
        except KeyError:
            EntitiesToRip[value[0].Hash] = value[0]
        for wid,vecs in value[1].items():
            LoadzoneWorldIDs[wid] = vecs
    _args = [(Entity,PackageCache) for Hash,Entity in EntitiesToRip.items()]
    result=t_pool.starmap_async(ExtractEntity, _args)

             


def ParseEntityFile(Tag,PackageCache):
    Data=InstanceData()
    ParentBuffer=Tag.EntityResourceParent.GetData(PackageCache)
    reader = Reader[Unk80808943]().allocate()
    reader.feed(ParentBuffer.read(Unk80808943.Length))
    Parent = reader.build()
    EntityResourceBuffer=Parent.EntityResource.GetData(PackageCache)
    reader = Reader[SEntityResource]().allocate()
    reader.feed(EntityResourceBuffer.read(SEntityResource.Length))
    EntityResource = reader.build()
    ResourceType = EntityResource.Resource0x18.GetType(EntityResourceBuffer,0x18)
    if ResourceType == 0x808098fa: #WID Instancer
        Resource=EntityResource.Resource0x18.ReadStruct(EntityResourceBuffer,Unk808098FA,0x18)
        StringDict=EntityResource.GenerateFnvDict(PackageCache)
        Data.GroupFnv=Resource.GlobalFnv
        Data.GroupWorldID=Resource.GlobalWorldID
        MappedWorldID=Resource.WorldIDTable.ReadStruct(EntityResourceBuffer,Unk80809905,Resource.Start+0x60)
        for Mapping in MappedWorldID:
            try:
                String=StringDict[Mapping.Fnv]
            except KeyError:
                u=1
            else:
                StringDict[Mapping.WorldID]=String
        Data.StringDict=StringDict
    elif ResourceType == 0x808092d8: #Entity Spawner
        Resource=EntityResource.Resource0x18.ReadStruct(EntityResourceBuffer,Unk808092D8,0x18)
        StringDict=EntityResource.GenerateFnvDict(PackageCache)
        Data.StringDict=StringDict
        Data.GroupFnv=Resource.GlobalFnv
        Data.GroupWorldID=Resource.GlobalWorldID
        Data.DataTable=Resource.DataTable
        Data.DefaultRotation=Resource.GlobalRotation
        Data.DefaultTranslation=Resource.GlobalTranslation
        #Attributes
        print("Instanced Entity in Table : "+str(Resource.DataTable.Hash))
    elif ResourceType == 0x808098ef:  #WID Instancer #2
        Resource=EntityResource.Resource0x18.ReadStruct(EntityResourceBuffer,Unk808098EF,0x18)
        StringDict=EntityResource.GenerateFnvDict(PackageCache)
        Data.GroupFnv=Resource.GlobalFnv
        Data.GroupWorldID=Resource.GlobalWorldID
        MappedWorldID=Resource.WorldIDTable.ReadStruct(EntityResourceBuffer,Unk80809905,Resource.Start+0x60)
        for Mapping in MappedWorldID:
            try:
                String=StringDict[Mapping.Fnv]
            except KeyError:
                u=1
            else:
                StringDict[Mapping.WorldID]=String
        Data.StringDict=StringDict
    else:
        print("Not implemented act res type: "+str(hex(ResourceType)))
    return Data


class InstanceData:
    GroupFnv=None
    GroupWorldID=None
    DataTable=None
    DefaultRotation=None
    DefaultTranslation=None
    SRMaps=[]
    CombatantTables=[]
    AttributeTables=[]
    StringDict={}
    PointPlacements=[]
    FAPlacements=[]
    ImportedBuffEntities=[]
    DeviceMappings=[]



@dataclass
class SActivity:
    Start=None
    Length = 0x88
    Filesize: U32
    Unk04: U32
    DestinationString: StringHash
    ActivityString: StringHash
    Unk10: Annotated[bytes,8]
    Directive: RelativePointer
    Unk1C: U32
    DestinationGlobal: ExtendedHash
    Unk30: TablePointer2 #00978080  Activity Variable Stuff
    PhaseTable: TablePointer2 #28898080 Phase_ Activity Scripts
    BubbleTable: TablePointer2 #24898080 Actual Activity Scripts + Loadzone
    Unk60: Annotated[bytes,20]
    UnkEntity: TagHash
    AmbientActivity: ExtendedHash
    StringContainer = None
    def GetStringContainer(self):
        import Util
        Buffer=self.DestinationGlobal.To32().GetData(Util.PackageCache)
        reader = Reader[Unk80808E8B]().allocate()
        reader.feed(Buffer.read(Unk80808E8B.Length))
        TagGlobal = reader.build()
        Strings=ProcessStrings(TagGlobal.DestinationStrings.To32().GetData(Util.PackageCache),str(hex(self.DestinationGlobal.ToTagHash.Hash)),Util.PackageCache)
        StringMap={}
        for String in Strings:
            StringMap[int(String[1])]=String[2]
        self.StringContainer=StringMap

        

@dataclass
class Unk80808E8B:
    Start=None
    Length = 0x78
    FileSize: U32
    Unk04: U32
    DestinationString: U32
    Unk0C: U32
    DestinationStrings: ExtendedHash

@dataclass
class Unk80808926:
    Start=None
    Length = 0x68
    DestinationString: StringHash
    ActivityString: StringHash
    BubbleString: StringHash
    Unk0C: Annotated[list[U32], 9]
    Unk30: FnvHash
    Unk34: Annotated[list[U32], 5]
    EncounterScript: TablePointer2


@dataclass
class Unk80808924:
    Start=None
    Length = 0x38
    DestinationString: StringHash
    ActivityString: StringHash
    BubbleString: StringHash
    Unk0C: U32
    Unk10: RelativePointer
    Unk14: U32
    ScriptTable: TablePointer2  #48898080
    StaticLoadTable: TablePointer2 # 1D898080

@dataclass
class Unk8080891D:
    Start=None
    StaticContainer: ExtendedHash

@dataclass
class Unk80808948:
    Start=None
    Length = 0x18
    DestinationString: StringHash
    ActivityString: StringHash
    BubbleString: StringHash
    PhaseHash1: U32
    PhaseHash2: U32
    ActivityEntityParent: TagHash

@dataclass
class Unk80808E89:
    Start=None
    Length = 0x90
    FileSize: U32
    Unk04: Annotated[list[U32], 5]
    EntityGlobal: TagHash

@dataclass
class Unk80808EBE:
    Start=None
    Length = 32
    FileSize: U32
    Unk04: U32
    EntityResources: TablePointer2


@dataclass
class Unk80808942:
    Start=None
    Length = 4
    EntityResourceParent: TagHash


@dataclass
class Unk80808943:
    Start=None
    Length = 0x28
    FileSize: U32
    Unk04: U32
    ResourceDescription: FnvHash
    Unk0C: Annotated[list[U32], 5]
    EntityResource: TagHash









    
    

    