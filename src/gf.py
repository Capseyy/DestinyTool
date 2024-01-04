import os,struct,binascii,fnvhash,ast
import Util
def ReadFloat32(Input):
    try:
        num=struct.unpack('!f', bytes.fromhex(binascii.hexlify(bytes(hex_to_little_endian(Input))).decode('utf-8')))[0]
    except struct.error:
        return 0
    else:
        return num
def stripZeros(txt):
    if txt == "0000":
        return("0")
    elif txt == "00000000":
        return("0")
    elif txt == "00":
        return("0")
    else:
        temp=list(txt)
        count=0
        index=0
        #print(temp)
        for char in temp:
            if char == "0":
                index+=1
                
            else:
                break
        #print("".join(temp[index:]))
        return str("".join(temp[index:]))
def hex_to_little_endian(hex_string):
    little_endian_hex = bytearray.fromhex(hex_string)[::-1]
    return little_endian_hex
def get_uint16_big(file,offset):
    return int.from_bytes(file[offset:offset+2],"big")

def fill_hex_with_zeros(s, desired_length):
    return ("0"*desired_length + s)[-desired_length:]

def fill_hex_with_zeros_big(s, desired_length):
    return (s+"0"*desired_length)[:desired_length]

def get_float32(file,offset):
    Dat=binascii.hexlify(bytes(file[offset:offset+4])).decode()
    flipped=binascii.hexlify(bytes(hex_to_little_endian(Dat))).decode('utf-8')
    return struct.unpack('!f', bytes.fromhex(flipped))[0]
def get_flipped_bin(h, length):
    if length % 2 != 0:
        print("Flipped bin length is not even.")
        return None
    return h[:length][::-1]


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def get_uint32(hx, offset):
    return int.from_bytes(hx[offset:offset+4], byteorder='little')
def get_int32(hx, offset):
    return int.from_bytes(hx[offset:offset+4], byteorder='little')


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

def get_int16(hx, offset):
    return int.from_bytes(hx[offset:offset+2], byteorder='little')
def get_uint24_big(hx, offset):
    return int.from_bytes(hx[offset:offset+3], byteorder='big')
def Hex_String(Num):
    Hex_Digits = "0123456789abcdef"
    return ''.join([
        Hex_Digits[(Num & 0xF000) >> 12],
        Hex_Digits[(Num & 0xF00) >> 8],
        Hex_Digits[(Num & 0xF0) >> 4],
        Hex_Digits[Num & 0xF]
    ])

def FNVString(fnv_string):
    return fnvhash.fnv1_32(fnv_string.encode())


def Flip(Hash):
    return binascii.hexlify(bytes(hex_to_little_endian(Hash))).decode('utf-8')
def binary_search_single(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1        
def binary_search2(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid][0]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid][0]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1    
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
 
    while low <= high:
 
        mid = (high + low) // 2
        if int(arr[mid][1]) < x:
            low = mid + 1
 
        # If x is smaller, ignore right half
        elif int(arr[mid][1]) > x:
            high = mid - 1
 
        # means x is present at mid
        else:
            return mid
    # If we reach here, then the element was not present
    return -1
