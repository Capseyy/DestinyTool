from dataclasses import dataclass, fields, field
import os,sys,Package,binascii,ast,struct
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
class VertexHeader:
    Length = 0xC
    DataSize: U32
    Stride: U16
    Type: U16
    DeadBeef: U32
    Buffer=None
    def GetUsedVerts(self,VertDict):
        VertList=[]
        for Entry,Unk in VertDict.items():
            VertList.append(Entry)
        Verts={}
        if self.Type == 1:
            if self.Stride == 24:
                for Vert in VertList:
                    self.Buffer.seek(self.Stride*Vert)
                    x=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    y=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    z=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    Vec=Vector3()
                    Vec.x=x
                    Vec.y=y
                    Vec.z=z
                    Verts[Vert] = Vec
            elif self.Stride == 48:
                for Vert in VertList:
                    self.Buffer.seek(self.Stride*Vert)
                    x=struct.unpack('<f', self.Buffer.read(4))/32767
                    y=struct.unpack('<f', self.Buffer.read(4))/32767
                    z=struct.unpack('<f', self.Buffer.read(4))/32767
                    Vec=Vector3()
                    Vec.x=x
                    Vec.y=y
                    Vec.z=z
                    Verts[Vert] = Vec
            else:
                for Vert in VertList:
                    self.Buffer.seek(self.Stride*Vert)
                    x=struct.unpack('<f', self.Buffer.read(4))/32767
                    y=struct.unpack('<f', self.Buffer.read(4))/32767
                    z=struct.unpack('<f', self.Buffer.read(4))/32767
                    Vec=Vector3()
                    Vec.x=x
                    Vec.y=y
                    Vec.z=z
                    Verts[Vert] = Vec
        elif self.Type == 0:
            if self.Stride == 24:
                for Vert in VertList:
                    self.Buffer.seek(self.Stride*Vert)
                    x=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    y=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    z=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                    Vec=Vector3()
                    Vec.x=x
                    Vec.y=y
                    Vec.z=z
                    Verts[Vert] = Vec
            #elif Stride == 48:
            #    for i in range(int(VBufferSize/int(Stride))):
            #        s = binascii.hexlify(bytes(VBuffer.read(int(Stride)))).decode()
            #        Data=[s[i:i+8] for i in range(0, len(s), 8)]
            #        #print(MeshScale)
            #        print(Data)
            #        x= ReadFloat32(Data[0])*(MeshScale)
            #        y= ReadFloat32(Data[1])*(MeshScale)
            #        z= ReadFloat32(Data[2])*(MeshScale)
            #        Verts.append([x,y,z,VertCount])
            #        #print([x,y,z,VertCount])
            #        VertCount+=1f07dbb80
            else:
                try:
                    LenTest=int(self.DataSize/int(self.Stride))

                except ZeroDivisionError:
                    print("Error for in buffer")
                else:
                    for Vert in VertList:
                        self.Buffer.seek(self.Stride*Vert)
                        x=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                        y=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                        z=int.from_bytes(self.Buffer.read(2),byteorder='little',signed=True)/32767
                        Vec=Vector3()
                        Vec.x=x
                        Vec.y=y
                        Vec.z=z
                        Verts[Vert] = Vec
                    
        return Verts
        

@dataclass
class IndexHeader:
    Length = 0x18
    Unk0: U8
    BitLength: U8
    Unk02: U16
    Unk04: U32
    DataSize: U16
    DeadBeef: U32
    Buffer=None
    def ReadFaces(self,IndexCount,IndexOffset,PrimitiveType):
        IndexData=[]
        if self.BitLength == 1:
            is32=True
        else:
            is32=False
        if PrimitiveType == 5:
            if is32 == False:
                triCount=0
                self.Buffer.seek(IndexOffset*2)
                if binascii.hexlify(bytes(self.Buffer.read(2))).decode() != "ffff":
                    try:
                        self.Buffer.seek(self.Buffer.tell()-2)
                    except OSError:
                        u=1
                Start=self.Buffer.tell()
                while (self.Buffer.tell()+4-Start) < (IndexCount*2):
                    i1=binascii.hexlify(bytes(self.Buffer.read(2))).decode()
                    i2=binascii.hexlify(bytes(self.Buffer.read(2))).decode()
                    i3=binascii.hexlify(bytes(self.Buffer.read(2))).decode()
                    if i3 == "ffff":
                        triCount=0
                        continue
                    if i1 == "":
                        break
                    if i2 == "":
                        break
                    if i3 == "":
                        break
                    i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i1))).decode('utf-8')))
                    i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i2))).decode('utf-8')))
                    i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i3))).decode('utf-8')))
                    if triCount % 2 == 0:
                        IndexData.append([i1,i2,i3])
                    else:
                        IndexData.append([i2,i1,i3])
                    self.Buffer.seek(self.Buffer.tell()-4)
                    triCount+=1
                    if len(IndexData) == IndexCount:
                        break
            else:
                triCount=0
                self.Buffer.seek(IndexOffset*4)
                Start=self.Buffer.tell()
                while (self.Buffer.tell()+8-Start) < (IndexCount*4):
                    i1=binascii.hexlify(bytes(self.Buffer.read(4))).decode()
                    i2=binascii.hexlify(bytes(self.Buffer.read(4))).decode()
                    i3=binascii.hexlify(bytes(self.Buffer.read(4))).decode()
                    if i3 == "ffffffff":
                        triCount=0
                        continue
                    temp=[i1,i2,i3]
                    if "" in temp:
                        break
                    i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i1))).decode('utf-8')))
                    i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i2))).decode('utf-8')))
                    i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(i3))).decode('utf-8')))
                    if triCount % 2 == 0:
                        IndexData.append([i1,i2,i3])
                    else:
                        IndexData.append([i2,i1,i3])
                    self.Buffer.seek(self.Buffer.tell()-8)
                    triCount+=1
                    if len(IndexData) == IndexCount:
                        break
        else:
            if is32 == False:
                self.Buffer.seek(IndexOffset*2)
                for j in range(0,int(IndexCount),3):
                    s = binascii.hexlify(bytes(self.Buffer.read(6))).decode()
                    Inds=[s[i:i+4] for i in range(0, len(s), 4)]
                    if len(Inds) < 3:
                        break
                    i1=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[0]))).decode('utf-8')))
                    i2=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[1]))).decode('utf-8')))
                    i3=ast.literal_eval("0x"+gf.stripZeros(binascii.hexlify(bytes(gf.hex_to_little_endian(Inds[2]))).decode('utf-8')))
                    IndexData.append([i1,i2,i3])
            else:
                self.Buffer.seek(IndexOffset*4)
                for j in range(0,int(IndexCount),3):
                    if len(IndexData) >= (int(IndexCount/3)):
                        break
                    i1=int.from_bytes(self.Buffer.read(4),"little")
                    i2=int.from_bytes(self.Buffer.read(4),"little")
                    i3=int.from_bytes(self.Buffer.read(4),"little")
                    IndexData.append([i1,i2,i3])
        return IndexData

