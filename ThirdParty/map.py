from dataclasses import dataclass, fields, field
import numpy as np
from typing import List
import gf
import os, json
from ctypes import cdll, c_char_p, create_string_buffer
from Crypto.Cipher import AES
import binascii
import io
import fnmatch
import time, ast
import ast
import struct, subprocess
#path = "E:\SteamLibrary\steamapps\common\Destiny2\packages" #Path to your packages folder.
path="D:/oldd2/packages"
#path="E:/SteamLibrary/steamapps/common/Destiny2/packages"
custom_direc = "C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/MapExtracter/data/" #Where you want the bin files to go
oodlepath = "E:\oo2core_9_win64.dll" #Path to Oodle DLL in Destiny 2/bin/x64.dle DLL in Destiny 2/bin/x64.
global StrData, Hash64Data
file=open("outputold.txt","r")
data=file.read()
StrData=data.split("\n")
file.close()
filelist = []


for file in os.listdir(path)[::-1]:
    if fnmatch.fnmatch(file,'w64_dungeon_powder*'):       #Customize this to what pkgs you need 2. Can wildcard with * for all packages, or all of a certain type.
        filelist.append(file)
        #print(file) #for debugging
def ReadHash64():
    file=open("h64.txt","r")
    data=file.read()
    Hash64Data=data.split("\n")
    return Hash64Data
def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex

def Hash64(packagesPath):
    file1=open("h64.txt","w")
    filelist = []
    for file in os.listdir(packagesPath)[::-1]:
        if fnmatch.fnmatch(file,'w64_*'):
            filelist.append(file)
    pkgIDs = set()
    hash64Table = {}
    # Getting all packages
    count=0
    for entry in filelist:
        count+=1
        pkgPath = packagesPath+"/"+entry
        with open(pkgPath, "rb") as pkgFile:
            # Hash64 Table
            pkgFile.seek(0xB8)
            hash64TableCountBytes = pkgFile.read(4)
            hash64TableCount = struct.unpack("<I", hash64TableCountBytes)[0]
            if hash64TableCount == 0:
                #print("empty")
                continue
            hash64TableOffsetBytes = pkgFile.read(4)
            hash64TableOffset = struct.unpack("<I", hash64TableOffsetBytes)[0]
            hash64TableOffset += 64 + 0x10

            for i in range(hash64TableOffset, hash64TableOffset + hash64TableCount * 0x10, 0x10):
                pkgFile.seek(i)
                h64ValBytes = pkgFile.read(8)
                h64Val = struct.unpack("<Q", h64ValBytes)[0]
                hValBytes = pkgFile.read(4)
                hVal = struct.unpack("<I", hValBytes)[0]
                file1.write(str(hex(h64Val))+": "+str(hex(hVal))+"\n")
    file1.close()

class LoadZone:
    def __init__(self,Name):
        self.FileName=Name
        self.Statics=[]
        self.StaticMeta=[]
        self.PullStatics()
        self.ExtractFBX()
        #if ans.upper() == "Y":
        #self.RipStatics()
        self.PullStaticMeta()
        self.PullStaticData()
        self.OutputCFG()
        #print(self.Statics)
        #print(str(len(self.Statics)))

    def PullStatics(self):
        print(self.FileName)
        file=open(custom_direc+self.FileName,"rb")
        Data=binascii.hexlify(bytes(file.read())).decode()
        Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
        count=0
        for Hash in Data:
            if Hash == "bd938080":
                for Hash2 in Data[count+2:len(Data)]:
                    if Hash2 == "b89f8080":
                        break
                    else:
                        if Hash2 == "00000000":
                            break
                        else:
                            self.Statics.append(Hash2)
                break
            count+=1
        #print("STATLEN")
        #print(len(self.Statics))
        #print(self.Statics)
    def PullStaticMeta(self):
        file=open(custom_direc+self.FileName,"rb")
        Data=binascii.hexlify(bytes(file.read())).decode()
        Data=[Data[i:i+16] for i in range(0, len(Data), 16)]
        count=0
        self.StaticMeta=[]
        for StaticDat in Data:
            if "286d8080" in StaticDat:
                self.StaticMeta=Data[count+1:len(Data)]
            count+=1
        #print("META")
        #print(self.StaticMeta)

    def OutputCFG(self):
        CFG=open("config.txt","w")
        CFG.close()
        CFG=open("config.txt","a")
        count=0
        countAll=0
        print(len(self.StaticMeta))
        print(len(self.StaticData))
        print(len(self.Statics))
        count=0
        
        for Static in self.StaticMeta:
            Data=[Static[i:i+4] for i in range(0, len(Static), 4)]  #Static[0] Count [1]-Offset [2]=Index 3[unk]
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Data[0]))).decode('utf-8')
            flipped2=binascii.hexlify(bytes(hex_to_little_endian(Data[2]))).decode('utf-8')
            NumofInstance=ast.literal_eval("0x"+stripZeros(flipped))
            Index=ast.literal_eval("0x"+stripZeros(flipped2))
            file=open("C:/Users/sjcap/Desktop/MyUnpacker/DestinyUnpackerNew/new/MapExtracter/data/Statics/Instances/"+self.Statics[Index]+".inst","w")
      
            for i in range(NumofInstance):
                data=",".join(self.StaticData[count])
                text=str(data)
                file.write(text+"\n")
                count+=1
            file.close()
            
            
    def PullStaticData(self):
        self.StaticData=[]
        file=open(custom_direc+self.FileName,"rb")
        print(self.FileName)
        Data=binascii.hexlify(bytes(file.read())).decode()
        file.close()
        Data=[Data[i:i+32] for i in range(0, len(Data), 32)]
        print(Data[0])
        count=0
        dataStarted=False
        for Line in Data:
            temp=[Line[i:i+8] for i in range(0, len(Line), 8)]
            #print(temp)
            if "406d8080" in temp:
                dataStarted=True
                countStart=count
            if dataStarted ==True:
                if "b89f8080" in temp:
                    countEnd=count
                    tempData=Data[countStart+1:countEnd]
                    break
            count+=1
        Data="".join(tempData)
        Data=[Data[i:i+128] for i in range(0, len(Data), 128)]
        for StatDat in Data:
            temp=[StatDat[i:i+2] for i in range(0, len(StatDat), 2)]
            Rotations="".join(temp[0:16])
            Position="".join(temp[16:28])
            Scale="".join(temp[28:40])
            RotDat=[Rotations[i:i+8] for i in range(0, len(Rotations), 8)]
            rotX=binascii.hexlify(bytes(hex_to_little_endian(RotDat[0]))).decode('utf-8')
            rotY=binascii.hexlify(bytes(hex_to_little_endian(RotDat[1]))).decode('utf-8')
            rotZ=binascii.hexlify(bytes(hex_to_little_endian(RotDat[2]))).decode('utf-8')
            rotW=binascii.hexlify(bytes(hex_to_little_endian(RotDat[3]))).decode('utf-8')
            PosDat=[Position[i:i+8] for i in range(0, len(Position), 8)]
            PosX=binascii.hexlify(bytes(hex_to_little_endian(PosDat[0]))).decode('utf-8')
            PosY=binascii.hexlify(bytes(hex_to_little_endian(PosDat[1]))).decode('utf-8')
            PosZ=binascii.hexlify(bytes(hex_to_little_endian(PosDat[2]))).decode('utf-8')
            ScaleDat=[Scale[i:i+8] for i in range(0, len(Scale), 8)]
            ScaleX=binascii.hexlify(bytes(hex_to_little_endian(ScaleDat[0]))).decode('utf-8')
            rotX=struct.unpack('!f', bytes.fromhex(rotX))[0]
            rotY=struct.unpack('!f', bytes.fromhex(rotY))[0]
            rotZ=struct.unpack('!f', bytes.fromhex(rotZ))[0]
            rotW=struct.unpack('!f', bytes.fromhex(rotW))[0]
            PosX=struct.unpack('!f', bytes.fromhex(PosX))[0]
            PosY=struct.unpack('!f', bytes.fromhex(PosY))[0]
            PosZ=struct.unpack('!f', bytes.fromhex(PosZ))[0]
            ScaleX=struct.unpack('!f', bytes.fromhex(ScaleX))[0]
            self.StaticData.append([str(rotX),str(rotY),str(rotZ),str(rotW),str(PosX),str(PosY),str(PosZ),str(ScaleX)])
            
    def ExtractFBX(self):
        for Static in self.Statics:
            #attempt to pull
            print(Static)
            flipped=binascii.hexlify(bytes(hex_to_little_endian(Static))).decode('utf-8')
            new=ast.literal_eval("0x"+flipped)
            PkgID=Hex_String(Package_ID(new))
            EntryID=Hex_String(Entry_ID(new))
            DirName=PkgID.upper()+"-"+EntryID.upper()+".model"
            for File in os.listdir(custom_direc):
                if File == DirName:
                    Model=open(custom_direc+"/"+File,"rb")
                    Data=binascii.hexlify(bytes(Model.read())).decode()
                    Data=[Data[i:i+8] for i in range(0, len(Data), 8)]
                    SubfileHash=Data[2]
                    flipped=binascii.hexlify(bytes(hex_to_little_endian(SubfileHash))).decode('utf-8')
                    new=ast.literal_eval("0x"+flipped)
                    PkgID=Hex_String(Package_ID(new))
                    EntryID=Hex_String(Entry_ID(new))
                    DirName=PkgID.upper()+"-"+EntryID.upper()+".sub"
                    print(DirName)
                    #model exists
            break
            
    def RipStatics(self):
        for Static in self.Statics:
            cmd="d2staticextractor.exe -p "+path+" -o "+custom_direc+"/Statics/Statics -i "+Static
            print(cmd)
            ans=subprocess.call(cmd, shell=True)
            print(ans)
            try:
                os.rename(custom_direc+"/Statics/Statics/"+Static.lower()+".fbx",custom_direc+"/Statics/Statics/"+Static.upper()+".fbx")
            except FileNotFoundError:
                print("L")
        
                
def Package_ID(Hash):
    ID = (Hash >> 13) & 0xFFF

    if (ID & 0x800) > 0 and (ID & 0x400) > 0:
        return ID & 0xBFF
    elif (ID & 0x400) == 0:
        return (ID & 0x3FF) | 0x400
    elif (ID & 0x200) == 0:
        return ID & 0x1FF
    elif (ID & 0x400) > 0:
        return ID & 0x3FF
    else:
        raise Exception("Unknown package encoding configuration.")
    
def Entry_ID(Hash):
    return Hash & 0x1FFF

def Hex_String(Num):
    Hex_Digits = "0123456789abcdef"
    return ''.join([
        Hex_Digits[(Num & 0xF000) >> 12],
        Hex_Digits[(Num & 0xF00) >> 8],
        Hex_Digits[(Num & 0xF0) >> 4],
        Hex_Digits[Num & 0xF]
    ])                
                
def stripZeros(txt):
    temp=list(txt)
    count=0
    for char in temp:
        if char == "0":
            temp.remove("0")
        else:
            break
    return "".join(temp)
            
    
        

def get_file_typename(file_type, file_subtype, ref_id, ref_pkg):
    if file_type == 8:
        return '8080xxxx Structure File'
    elif file_type == 33:
        return 'DirectX Bytecode Header'
    elif file_type == 41:
        return 'DirectX Bytecode Data'
    else:
        return 'Unknown'


def calculate_pkg_id(entry_a_data):
    ref_pkg_id = (entry_a_data >> 13) & 0x3FF
    ref_unk_id = entry_a_data >> 23

    ref_digits = ref_unk_id & 0x3
    if ref_digits == 1:
        return ref_pkg_id
    else:
        return ref_pkg_id | 0x100 << ref_digits


# All of these decoding functions use the information from formats.c on how to decode each entry
def decode_entry_a(entry_a_data):
    ref_id = entry_a_data & 0x1FFF
    # ref_pkg_id = (entry_a_data >> 13) & 0x3FF
    ref_pkg_id = calculate_pkg_id(entry_a_data)
    ref_unk_id = (entry_a_data >> 23) & 0x1FF

    return np.uint16(ref_id), np.uint16(ref_pkg_id), np.uint16(ref_unk_id)


def decode_entry_b(entry_b_data):
    file_subtype = (entry_b_data >> 6) & 0x7
    file_type = (entry_b_data >> 9) & 0x7F
    #print(entry_b_data)
    return np.uint8(file_type), np.uint8(file_subtype)


def decode_entry_c(entry_c_data):
    starting_block = entry_c_data & 0x3FFF
    #print(starting_block)
    starting_block_offset = ((entry_c_data >> 14) & 0x3FFF) << 4
    return starting_block, starting_block_offset


def decode_entry_d(entry_c_data, entry_d_data):
    file_size = (entry_d_data & 0x3FFFFFF) << 4 | (entry_c_data >> 28) & 0xF
    unknown = (entry_d_data >> 26) & 0x3F

    return np.uint32(file_size), np.uint8(unknown)


class OodleDecompressor:
    """
    Oodle decompression implementation.
    Requires Windows and the external Oodle library.
    """

    def __init__(self, library_path: str) -> None:
        """
        Initialize instance and try to load the library.
        """
        if not os.path.exists(library_path):
            raise Exception("Could not open Oodle DLL, make sure it is configured correctly.")

        try:
            self.handle = cdll.LoadLibrary(library_path)
        except OSError as e:
            raise Exception(
                "Could not load Oodle DLL, requires Windows and 64bit python to run."
            ) from e

    def decompress(self, payload: bytes) -> bytes:
        """
        Decompress the payload using the given size.
        """
        force_size = int('0x40000', 16)
        output = create_string_buffer(force_size)
        self.handle.OodleLZ_Decompress(
            c_char_p(payload), len(payload), output, force_size,
            0, 0, 0, None, None, None, None, None, None, 3)
        return output.raw


class PkgHeader:
    def __init__(self, pbin):
        self.PackageID = gf.get_int16(pbin, 0x10)
        self.PackageIDH = gf.fill_hex_with_zeros(hex(self.PackageID)[2:], 4)
        self.PatchID = gf.get_int16(pbin, 0x30)

        self.EntryTableOffset = gf.get_int32(pbin, 0x44)
        # self.EntryTableLength = get_int_hex(0x48, phex)
        self.EntryTableSize = gf.get_int32(pbin, 0x60)
        self.EntryTableLength = self.EntryTableSize * 0x16

        self.BlockTableSize = gf.get_int32(pbin, 0x68)
        self.BlockTableOffset = gf.get_int32(pbin, 0x6C)


@dataclass
class SPkgEntry:
    EntryA: np.uint32 = np.uint32(0)
    EntryB: np.uint32 = np.uint32(0)
    EntryC: np.uint32 = np.uint32(0)
    EntryD: np.uint32 = np.uint32(0)

    '''
     [             EntryD              ] [             EntryC              ] 
     GGGGGGFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFEEEE EEEEEEEE EEDDDDDD DDDDDDDD

     [             EntryB              ] [             EntryA              ]
     00000000 00000000 TTTTTTTS SS000000 CCCCCCCC CBBBBBBB BBBAAAAA AAAAAAAA

     A:RefID: EntryA & 0x1FFF
     B:RefPackageID: (EntryA >> 13) & 0x3FF
     C:RefUnkID: (EntryA >> 23) & 0x1FF
     D:StartingBlock: EntryC & 0x3FFF
     E:StartingBlockOffset: ((EntryC >> 14) & 0x3FFF) << 4
     F:FileSize: (EntryD & 0x3FFFFFF) << 4 | (EntryC >> 28) & 0xF
     G:Unknown: (EntryD >> 26) & 0x3F

     Flags (Entry B)
     S:SubType: (EntryB >> 6) & 0x7
     T:Type:  (EntryB >> 9) & 0x7F
    '''


@dataclass
class SPkgEntryDecoded:
    ID: np.uint16 = np.uint16(0)
    FileName: str = ''
    FileType: str = ''
    RefID: np.uint16 = np.uint16(0)  # uint13
    RefPackageID: np.uint16 = np.uint16(0)  # uint9
    RefUnkID: np.uint16 = np.uint16(0)  # uint10
    Type: np.uint8 = np.uint8(0)  # uint7
    SubType: np.uint8 = np.uint8(0)  # uint3
    StartingBlock: np.uint16 = np.uint16(0)  # uint14
    StartingBlockOffset: np.uint32 = np.uint32(0)  # uint14
    FileSize: np.uint32 = np.uint32(0)  # uint30
    Unknown: np.uint8 = np.uint8(0)  # uint6
    EntryA: int = ''


@dataclass
class SPkgEntryTable:
    Entries: List[SPkgEntryDecoded] = field(default_factory=list)  # This list of of length [EntryTableSize]


@dataclass
class SPkgBlockTableEntry:
    ID: int = 0  # 0x0
    Offset: np.uint32 = np.uint32(0)  # 0x4
    Size: np.uint32 = np.uint32(0)  # 0x8
    PatchID: np.uint16 = np.uint16(0)  # 0xC
    Flags: np.uint16 = np.uint16(0)  # 0xE
    Hash: List[np.uint8] = field(default_factory=list)  # [0x14] = 20  # 0x22
    GCMTag: List[np.uint8] = field(default_factory=list)  # [0x10] = 16  # 0x32


@dataclass
class SPkgBlockTable:
    Entries: List[SPkgBlockTableEntry] = field(default_factory=list)  # This list of length [BlockTableSize]


class Package:
    BLOCK_SIZE = int('0x40000', 16)

    AES_KEY_0 = [
        "0xD6", "0x2A", "0xB2", "0xC1", "0x0C", "0xC0",
        "0x1B", "0xC5", "0x35", "0xDB", "0x7B",
        "0x86", "0x55", "0xC7", "0xDC", "0x3B",
    ]
    AES_KEY_1 = [
        "0x3A", "0x4A", "0x5D", "0x36", "0x73", "0xA6",
        "0x60", "0x58", "0x7E", "0x63", "0xE6",
        "0x76", "0xE4", "0x08", "0x92", "0xB5",
    ]

    def __init__(self, package_directory):
        self.package_directory = package_directory
        if '_en_' in self.package_directory:
            self.t_package_id = self.package_directory[-13:-9]
        else:
            self.t_package_id = self.package_directory[-10:-6]
        self.package_header = None
        self.entry_table = None
        self.block_table = None
        self.all_patch_ids = []
        self.max_pkg_bin = None
        self.nonce = None
        self.aes_key_0 = binascii.unhexlify(''.join([x[2:] for x in self.AES_KEY_0]))
        self.aes_key_1 = binascii.unhexlify(''.join([x[2:] for x in self.AES_KEY_1]))

    def extract_package(self, custom_direc, extract=True, largest_patch=True):
        self.get_all_patch_ids()
        if largest_patch:
            self.set_largest_patch_directory()
        print(f"Extracting files for {self.package_directory}")

        self.max_pkg_bin = open(self.package_directory, 'rb').read()
        self.package_header = self.get_header()
        self.entry_table = self.get_entry_table()
        self.block_table = self.get_block_table()

        if extract:
            self.process_blocks(custom_direc)

    def get_all_patch_ids(self):
        all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if self.t_package_id in x]
        all_pkgs.sort()
        self.all_patch_ids = [int(x[-5]) for x in all_pkgs]

    def set_largest_patch_directory(self):
        if 'unp1' in self.package_directory:
            all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if x[:-6] in self.package_directory]
        else:
            all_pkgs = [x for x in os.listdir(self.package_directory.split('/w64')[0]) if self.t_package_id in x]
        sorted_all_pkgs, _ = zip(*sorted(zip(all_pkgs, [int(x[-5]) for x in all_pkgs])))
        self.package_directory = self.package_directory.split('/w64')[0] + '/' + sorted_all_pkgs[-1]
        return

    def get_header(self):
        """
        Given a pkg directory, this gets the header data and uses SPkgHeader() struct to fill out the fields of that struct,
        making a header struct with all the correct data.
        :param pkg_dir:
        :return: the pkg header struct
        """
        header_length = int('0x16F', 16)
        # The header data is 0x16F bytes long, so we need to x2 as python reads each nibble not each byte
        header = self.max_pkg_bin[:header_length]
        pkg_header = PkgHeader(header)
        #print(pkg_header)
        return pkg_header

    def get_entry_table(self):
        """
        After we've got the header data for each pkg we know where the entry table is. Using this information, we take each
        row of 16 bytes (128 bits) as an entry and separate the row into EntryA, B, C, D for decoding
        :param pkg_data: the hex data from pkg
        :param entry_table_size: how long this entry table is in the pkg data
        :param entry_table_offset: hex offset for where the entry table starts
        :return: the entry table made
        """

        entry_table = SPkgEntryTable()
        entries_to_decode = []
        entry_table_start = self.package_header.EntryTableOffset
        entry_table_data = self.max_pkg_bin[entry_table_start:entry_table_start+self.package_header.EntryTableLength]
        #table=open("entrytable.bin","wb")
        #table.write(entry_table_data)
        #time.sleep(60)
        #print(self.package_header.EntryTableSize)
        #for i in range(0, self.package_header.EntryTableSize * 16, 16):
        #    print(entry_table_data,)
        for i in range(0, self.package_header.EntryTableSize * 16, 16):
            entry = SPkgEntry(gf.get_int32(entry_table_data, i),
                              gf.get_int32(entry_table_data, i+4),
                              gf.get_int32(entry_table_data, i+8),
                              gf.get_int32(entry_table_data, i+12))
            #print(entry)
            entries_to_decode.append(entry)
        #print(len(entries_to_decode))
        #time.sleep(10)
        entry_table.Entries = self.decode_entries(entries_to_decode)
        return entry_table

    def decode_entries(self, entries_to_decode):
        """
        Given the entry table (and hence EntryA, B, C, D) we can decode each of them into data about each (file? block?)
        using bitwise operators.
        :param entry_table: the entry table struct to decode
        :return: array of decoded entries as struct SPkgEntryDecoded()
        """
        entries = []
        count = 0
        for entry in entries_to_decode:
            # print("\n\n")
            #useful=["0x808093ad","0x80806d44","0x80806d40","0x80808707","0x80806d30"]
            ref_id, ref_pkg_id, ref_unk_id = decode_entry_a(entry.EntryA)
            #if hex(entry.EntryA) in useful:
            file_type, file_subtype = decode_entry_b(entry.EntryB)
            starting_block, starting_block_offset = decode_entry_c(entry.EntryC)
            file_size, unknown = decode_entry_d(entry.EntryC, entry.EntryD)
            file_name = f"{self.package_header.PackageIDH}-{gf.fill_hex_with_zeros(hex(count)[2:], 4)}"
            file_typename = get_file_typename(file_type, file_subtype, ref_id, ref_pkg_id)

            decoded_entry = SPkgEntryDecoded(np.uint16(count), file_name, file_typename,
                                             ref_id, ref_pkg_id, ref_unk_id, file_type, file_subtype, starting_block,
                                             starting_block_offset, file_size, unknown, hex(entry.EntryA))
            entries.append(decoded_entry)
            #print("Here")
            #if len(entries) > 50:
             #   print(entries)
              #  time.sleep(60)
            count += 1
            
            #(count)
        return entries

    def get_block_table(self):
        block_table = SPkgBlockTable()
        block_table_data = self.max_pkg_bin[self.package_header.BlockTableOffset:self.package_header.BlockTableOffset + self.package_header.BlockTableSize*48]
        reduced_bt_data = block_table_data
        for i in range(self.package_header.BlockTableSize):
            block_entry = SPkgBlockTableEntry(ID=i)
            for fd in fields(block_entry):
                if fd.type == np.uint32:
                    value = gf.get_int32(reduced_bt_data, 0)
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[4:]
                elif fd.type == np.uint16:
                    value = gf.get_int16(reduced_bt_data, 0)
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[2:]
                elif fd.type == List[np.uint8] and fd.name == 'Hash':
                    flipped = gf.get_flipped_bin(reduced_bt_data, 20)
                    value = [c for c in flipped]
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[20:]
                elif fd.type == List[np.uint8] and fd.name == 'GCMTag':
                    flipped = gf.get_flipped_bin(reduced_bt_data, 16)
                    value = [c for c in flipped]
                    setattr(block_entry, fd.name, value)
                    reduced_bt_data = reduced_bt_data[16:]
            block_table.Entries.append(block_entry)
        return block_table

    def process_blocks(self, custom_direc):
        all_pkg_bin = []
        for i in self.all_patch_ids:
            bin_data = open(f'{self.package_directory[:-6]}_{i}.pkg', 'rb').read()
            all_pkg_bin.append(bin_data)

        self.set_nonce()
        #print(all_pkg_bin)
        self.output_files(all_pkg_bin, custom_direc)

    def decrypt_block(self, block, block_bin):
        if block.Flags & 0x4:
            key = self.aes_key_1
        else:
            key = self.aes_key_0
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        plaintext = cipher.decrypt(block_bin)
        #print(str(plaintext).split("\\x"))
        #time.sleep(10)
        return plaintext

    def set_nonce(self):
        nonce_seed = [
            0x84, 0xDF, 0x11, 0xC0,
            0xAC, 0xAB, 0xFA, 0x20,
            0x33, 0x11, 0x26, 0x99,
        ]

        nonce = nonce_seed
        package_id = self.package_header.PackageID

        nonce[0] ^= (package_id >> 8) & 0xFF
        nonce[1] = 0xEA
        nonce[11] ^= package_id & 0xFF


        self.nonce = binascii.unhexlify(''.join([gf.fill_hex_with_zeros(hex(x)[2:], 2) for x in nonce]))

    def decompress_block(self, block_bin):
        decompressor = OodleDecompressor(oodlepath)
        decompressed = decompressor.decompress(block_bin)
        return decompressed

    def output_files(self, all_pkg_bin, custom_direc):
        
        for entry in self.entry_table.Entries[::-1]:
            #print(entry)
            current_block_id = entry.StartingBlock
            block_offset = entry.StartingBlockOffset
            block_count = int(np.floor((block_offset + entry.FileSize - 1) / self.BLOCK_SIZE))
            last_block_id = current_block_id + block_count
            file_buffer = b''  # string of length entry.Size
            while current_block_id <= last_block_id:
                current_block = self.block_table.Entries[current_block_id]
                if current_block.PatchID not in self.all_patch_ids:
                    print(f"Missing PatchID {current_block.PatchID}")
                    return
                current_pkg_data = all_pkg_bin[self.all_patch_ids.index(current_block.PatchID)]
                current_block_bin = current_pkg_data[current_block.Offset:current_block.Offset + current_block.Size]
                # We only decrypt/decompress if need to
                if current_block.Flags & 0x2:
                    # print('Going to decrypt')
                    current_block_bin = self.decrypt_block(current_block, current_block_bin)
                if current_block.Flags & 0x1:
                    # print(f'Decompressing block {current_block.ID}')
                    current_block_bin = self.decompress_block(current_block_bin)
                if current_block_id == entry.StartingBlock:
                    file_buffer = current_block_bin[block_offset:]
                else:
                    file_buffer += current_block_bin
                #print(file_buffer)
                current_block_id += 1
            #print(entry.EntryA)
            #print(entry.FileName.upper())
            fileFormat=""
            if entry.EntryA == "0x808093ad":  #0x28 leads to modelocclusionbounds                         #LHash->Dt->
                fileFormat=".load"
            elif entry.EntryA == "0x80806d44":
                fileFormat=".model"
            elif entry.EntryA == "0x80806d30":  #modelData
                fileFormat=".sub"
            elif entry.EntryA == "0x80808707":   #contains all data to make map  points to .dt 's
                fileFormat=".Lhash"
            elif entry.EntryA == "0x80809883":   #A map data table, containing data entries  85988080 table for Entities and Statics 0x90 per  DynStaMapPointers
                fileFormat=".dt"
            elif entry.EntryA == "0x8080891e":   #1 per load  Name at 0x18
                fileFormat=".top"
            elif entry.EntryA == "0x80808701":
                fileFormat=".mref"
            elif entry.EntryA == "0x808093b1":
                fileFormat=".occlu"
            elif entry.EntryA == "0x80806a0d":  #points to .Load
                fileFormat=".test"
            elif entry.EntryA == "0x80806cc9":
                fileFormat=".charm"
            else:
                fileFormat=".bin"
            #fileFormat=".bin"
            #if entry.Type == 40:
            #    if entry.SubType == 4:
            #        fileFormat=".vbuff"
            #    elif entry.SubType == 6:
            #        fileFormat=".ibuff"
            #fileFormat=".bin"
            #if entry.FileName.upper() == "03C3-16EC":
                #print(entry.EntryA)
                #print(f'{custom_direc}{self.package_directory.split("/w64")[-1][1:-6]}/{entry.FileName.upper()}'+fileFormat)
            if fileFormat != ".bin":
                file = io.FileIO(f'{custom_direc}/{entry.FileName.upper()}'+fileFormat, 'wb')
                # print(entry.FileSize)
                if entry.FileSize != 0:
                    writer = io.BufferedWriter(file, buffer_size=entry.FileSize)
                    writer.write(file_buffer[:entry.FileSize])
                    writer.flush()
                else:
                    with open(f'{custom_direc}/{entry.FileName.upper()}'+fileFormat, 'wb') as f:
                        f.write(file_buffer[:entry.FileSize])
            #print(f"Wrote to {entry.FileName} successfully")

def InitialiseFiles(loadfile):
    lengths=[]
    for File in os.listdir(custom_direc):
        if File != "Statics":
            if File.lower() == loadfile:
                Load=LoadZone(File)
                lengths.append([File,str(len(Load.Statics))])
                break
                #print(Load.FileName)
    #print(lengths)
def TryNewFile():
    lengths=[]
    Rotations=[]
    Translations=[]
    DynamicHashes=[]
    LoadNames=[]
    for File in os.listdir(custom_direc):
        if File != "Statics":
             if File.split(".")[1] == "top":
                 file=open(custom_direc+"/"+File,"rb")
                 file.seek(0x8)
                 Hash=binascii.hexlify(bytes(file.read(4))).decode()
                 flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                 new=ast.literal_eval("0x"+flipped)
                 RefHash=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".mref"
                 file.seek(0x18)
                 Hash=binascii.hexlify(bytes(file.read(4))).decode()
                 file.close()
                 flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                 new=ast.literal_eval("0x"+flipped)
                 LoadHash=new
                 StringTxt=""
                 possibleNames=[]
                 for String in StrData:
                     Lines=String.split(": ")
                     try:
                         Lines[1]
                     except IndexError:
                         pass
                     else:
                         if Lines[0] == str(new):
                             StringTxt=Lines[1]
                             possibleNames.append(StringTxt)
                             
                 LoadNames.append([str([possibleNames]),File,RefHash])
    count=0
    for Load in LoadNames:
        file=open(custom_direc+"/"+Load[2],"rb")#mref
        print(Load[2])
        Data=binascii.hexlify(bytes(file.read())).decode()
        data=[Data[i:i+32] for i in range(0, len(Data), 32)]
        LoadHashes=[]
        First=True
        #print(len(data))
        for Line in data:
            split=[Line[i:i+8] for i in range(0, len(Line), 8)]
            if split[0].lower() == "ffffffff":
                Hash=str(split[2])+str(split[3])
                flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                #print(flipped)
                for Line1 in Hash64Data:
                    Lines=Line1.split(": ")
                    #print(Lines)
                    if Lines[0].lower() == str("0x"+flipped):
                        LhashFile=Lines[1]
                        LoadNames[count].append(LhashFile)
                        break
        count+=1     
                    
    #print(LoadNames)           
    count=0    
    for Load in LoadNames:
        count+=1
        print(str(count)+" "+Load[0]+Load[2])
    answer=int(input("Enter which Load you want to pull from: "))
    SubLoads=LoadNames[answer-1][3:]
    count5=1
    LoadFiles=[]
    print(SubLoads)
    for SubLoad in SubLoads:
        num=ast.literal_eval(SubLoad)
        Name=Hex_String(Package_ID(num))+"-"+Hex_String(Entry_ID(num))+".lhash"
        for File in os.listdir(custom_direc):
            if File != "Statics":
                if File.lower() == Name:  #change back to LHash
                    Tables=[]
                    file=open(custom_direc+"/"+File,"rb")
                    file.seek(0x50)
                    dat=binascii.hexlify(bytes(file.read())).decode()
                    Data=[dat[i:i+8] for i in range(0, len(dat), 8)]
                    for Hash in Data:
                        flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                        num=ast.literal_eval("0x"+flipped)
                        Name=Hex_String(Package_ID(num))+"-"+Hex_String(Entry_ID(num))
                        if Name not in Tables:
                            Tables.append(Name)
                    count=0
                    for Table in Tables:
                        for File in os.listdir(custom_direc):
                            if File != "Static":
                                if Table.lower() == File.split(".")[0].lower():
                                    #print(File)
                                    H64=""
                                    StaticLz=""
                                    file=open(custom_direc+"/"+File,"rb")
                                    length=binascii.hexlify(bytes(file.read())).decode()
                                    file.close()
                                    if len(length) < 144:
                                        continue
                                    File=open(custom_direc+"/"+File,"rb")
                                    File.seek(0x20)
                                    Num=binascii.hexlify(bytes(File.read(8))).decode()
                                    flipped=binascii.hexlify(bytes(hex_to_little_endian(Num))).decode('utf-8')
                                    Length=ast.literal_eval("0x"+stripZeros(flipped))
                                    File.seek(0x30)
                                    #Data=binascii.hexlify(bytes(File.read(288*int(Length)))).decode()
                                    dat=[]
                                    count=0
                                    for i in range(Length):
                                        count+=1
                                        temp=binascii.hexlify(bytes(File.read(144))).decode()
                                        dat.append(temp)
                                        #print(temp)
                                    for Model in dat:
                                        Dat=[Model[i:i+8] for i in range(0, len(Model), 8)]
                                        #print(Dat)
                                        QuatX=(struct.unpack("<I", bytes.fromhex(Dat[0]))[0])*-1
                                        QuatY=(struct.unpack("<I", bytes.fromhex(Dat[1]))[0])*-1
                                        QuatZ=(struct.unpack("<I", bytes.fromhex(Dat[2]))[0])*-1
                                        QuatW=struct.unpack("<I", bytes.fromhex(Dat[3]))[0]
                                        fx=struct.unpack("<I", bytes.fromhex(Dat[4]))[0]
                                        fy=struct.unpack("<I", bytes.fromhex(Dat[5]))[0]
                                        fz=struct.unpack("<I", bytes.fromhex(Dat[6]))[0]
                                        lzscale=struct.unpack("<I", bytes.fromhex(Dat[7]))[0]
                                        Rotations.append([QuatX,QuatY,QuatZ,QuatW])
                                        Translations.append([fx,fy,fz,lzscale])
                                        File.read(4)
                                        Ref=binascii.hexlify(bytes(File.read(4))).decode()
                                        if Ref == "c96c8080":
                                            File.read(16)
                                            Hash=binascii.hexlify(bytes(File.read(4))).decode()
                                            File.close()
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                                            new=ast.literal_eval("0x"+flipped)
                                            DirName=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))
                                            #print(DirName+".test")
                                            File=open(custom_direc+"/"+DirName+".test","rb")
                                            File.seek(0x8)
                                            Hash=binascii.hexlify(bytes(File.read(4))).decode()
                                            #print(Hash)
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
                                            new=ast.literal_eval("0x"+flipped)
                                            DirName2=Hex_String(Package_ID(new))+"-"+Hex_String(Entry_ID(new))+".load"
                                            #print(DirName)
                                            File.close()
                                            #print(DirName2)
                                            File=open(custom_direc+"/"+DirName2,"rb")
                                            File.seek(0x50)
                                            Length=binascii.hexlify(bytes(File.read(2))).decode()
                                            File.close()
                                            flipped=binascii.hexlify(bytes(hex_to_little_endian(Length))).decode('utf-8')
                                            new=ast.literal_eval("0x"+stripZeros(flipped))
                                            print(str(count5)+" "+str(SubLoad)+" Instances: "+str(new))
                                            count5+=1
                                            LoadFiles.append(DirName2)
                                        
    #print(LoadFiles)                                       
    ans2=int(input("Enter which Load to extract from: "))
    InitialiseFiles(LoadFiles[ans2-1])
    
                
        

def unpack_all(path, custom_direc):
    all_packages = filelist
    i=0
    for thing in range(len(all_packages)):
        #print(i)
        if "video" in all_packages[i].split("_"):
            all_packages.remove(all_packages[i]) #videos break???
        else:
            i+=1
    #print(all_packages)
    single_pkgs = dict()
    for pkg in all_packages:
        single_pkgs[pkg[:-6]] = pkg
    #print(single_pkgs.items())
    for pkg, pkg_full in single_pkgs.items():
        pkg = Package(f'{path}/{pkg_full}')
        pkg.extract_package(extract=True, custom_direc=custom_direc)
    print("done")
global ans

if __name__ == '__main__':
    ans=input("Do you need to unpack the game? Y/N :")
    if ans.upper() == "Y":
        unpack_all(path, custom_direc)
        Hash64(path)
    Hash64Data=ReadHash64()
    TryNewFile()

