import gf
import scipy.spatial
import os
import sys
temp=os.getcwd()
temp=temp.split("\\")
output="/".join(temp[:len(temp)])
custom_direc=output
sys.path.append(output+"/ThirdParty")

# Type 27 subtype 0 files that have SDKV at 0x1C

"""
General notes
----
- Headers are in big endian
- "@" (40 00) precedes relative offsets or sizes usually

Header (big endian)
-----
0x0: zeros -> 0x10
0x10: distance to end of file
0x14: "TAG0"
0x18: 40 00 00 10
0x1C: "SDKV"
0x20: year "2018"
0x24: Jan 1st
0x28: 40 00 @
0x2A: uint16_t relative offset to TCRF definition
0x2C: "DATA", start of the data portion

TCRF header (presuming TCRF means reference) (big endian)
-----
0x0: 40 00 00 20
0x4: "TCRF"
0x8: zeros -> 0x20
0x20: distance to end of file
0x24: "INDX"
0x28: 40 00 @
0x2A: uint16_t relative offset to PTCH definition
0x2C: "ITEM"

PTCH header (big endian)
-----
0x0: 40 00 @
0x2: distance to end of file uint16_t
...
reading backwards, each uint32_t gives an offset from "DATA" to a set of coordinates, list of entries essentially
read backwards enough to hit a count of that and thats the list


----
Other notes:
- I think the height is given by the rounded coords in the sections that are very different to the other numbers
"""


def extract_ptch(f, origin,name):
    fb = f.read()

    # Getting PTCH offset so we can read it forwards
    o = gf.get_uint16_big(fb, 0x2A) + 0x2A
    item_offset = o + 0x2A
    broke=False
    if fb[item_offset:item_offset + 4] != b"ITEM":
        o = gf.get_uint24_big(fb, 0x29)+ 0x2A
        item_offset = o + 0x2A
        if fb[item_offset:item_offset + 4] != b"ITEM":
            broke=True
    item_end = gf.get_uint16_big(fb, item_offset - 2) + item_offset - 4
    ptch_offset = gf.get_uint16_big(fb, o + 0x28) + o + 0x28 + 2
    if fb[ptch_offset:ptch_offset + 4] != b"PTCH":
        broke=True
    print(broke)
    if broke == False:
        scale = [gf.get_float32(fb, 0xA0 + j * 4) for j in range(3)]
        offset = [gf.get_float32(fb, 0xB0 + j * 4) for j in range(4)]

        # 53: long group of coords, usually like 12 | 57: two coords | 72: empties
        # Reading ITEM
        # item_entries = {}
        # i = item_offset + 4
        # while i < item_end:
        #     while fb[i:i+4] != b"\x84\x00\x00\x20":
        #         i += 4
        #         continue
        #     unk_val = gf.get_uint32(fb, i)

        # a = 0

        # Reading PTCH
        entry_offsets = {}
        i = ptch_offset + 4
        while i < len(fb):
            unk = gf.get_uint32(fb, i)
            print(unk)
            offset_count = gf.get_uint32(fb, i + 4)
            print(offset_count)
            i += 8
            entry_offsets[unk] = []
            for k in range(offset_count):
                entry_offsets[unk].append(gf.get_uint32(fb, i) + 0x10)
                if unk == 53:
                    entry_offsets[unk][-1] += 8
                i += 4
            print("\n")

        coords = []
        real_coords = []
        min_coords = []
        max_coords = []
        min_coords.append([0, 0, -1])
        max_coords.append([0, 0, 1])
        cc = 53
        print(entry_offsets)
        try:
            entry_offsets[cc]
        except KeyError:
            u=1
            print("key error")
        else:
            for i in entry_offsets[cc]:
                index = gf.get_uint32(fb, i)
                ctype = gf.get_uint32(fb, i + 0x10)
                coord_count = gf.get_uint32(fb, i + 0x18)
                coord_count = 13
                coords.append([[gf.get_float32(fb, i + 0x30 + j * 4 + k * 16) for j in range(4)] for k in range(coord_count)])
                real_coords.extend([coords[-1][7], coords[-1][8], coords[-1][12], coords[-1][6], coords[-1][11], coords[-1][9],
                                    coords[-1][10]])
                # real_coords.extend(coords[-1])
                # min_coords.append(coords[-1][9])
                # max_coords.append(coords[-1][10])

            # real_coords_fixed = []
            # for c in real_coords:
            #     if not all([c[0] == y for y in c[1:]]):
            #         real_coords_fixed.append(c)
            # real_coords = real_coords_fixed


            try:
                convex_hull = scipy.spatial.ConvexHull([x[:2] for x in real_coords], qhull_options="Qc")
            except scipy.spatial.QhullError:
                u=1
                print("qhull error")
            else:

                # Defining top and bottom faces and verts
                write_verts = []
                write_faces = []
                for v in convex_hull.vertices:
                    rc = real_coords[v]
                    write_verts.append([rc[0], rc[1], rc[2] + min_coords[0][2]])  # Min
                num_verts = len(convex_hull.vertices)
                write_faces.append(range(num_verts))
                for v in convex_hull.vertices:
                    rc = real_coords[v]
                    write_verts.append([rc[0], rc[1], rc[2] + max_coords[0][2]])  # Max
                write_faces.append([x + num_verts for x in range(num_verts)])
                for i in range(num_verts):  # rest of faces
                    if i < num_verts - 1:
                        write_faces.append([i, i + num_verts, i + 1 + num_verts, i + 1])
                    else:
                        write_faces.append([i, i + num_verts, num_verts, 0])

                bl = origin
                #os.makedirs(f"ptch/1/", exist_ok=True)
                with open(custom_direc+"/Maps/Havok/"+name+".obj", "w") as q:
                    for v in write_verts:
                        q.write(
                            f"v {-(scale[0] * v[0] + offset[0] + bl[0])} {scale[2] * v[2] + offset[2] + bl[2]} {scale[1] * v[1] + offset[1] + bl[1]}\n")
                    for f in write_faces:
                        q.write(f"f {' '.join([str(x + 1) for x in f])}\n")
                    #for v in real_coords:
                    #    q.write(f"v {-(scale[0]*v[0]+offset[0] + base_location_0307_0922[0])} {scale[2]*v[2]+offset[2] + base_location_0307_0922[2]} {scale[1]*v[1]+offset[1] + base_location_0307_0922[1]}\n")


def ExtractHxk(file,name):
    origin=[0,0,0]
    extract_ptch(file, origin,name)
#extract_ptch(open(os.getcwd()+"/src/0441-0605.bin","rb"), [0,0,0],"0441-0605")