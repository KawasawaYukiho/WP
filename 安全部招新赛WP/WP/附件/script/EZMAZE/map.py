map_data = [0x58, 0x28, 0x47, 0xD2, 0x84, 0x7D, 0x70, 0x07, 
            0xD1, 0x12, 0x2F, 0x52, 0xAA, 0x47, 0x58, 0xA6,
            0x3D, 0x3E, 0x24, 0x33, 0x32, 0x0B, 0x1E, 0x13, 
            0x07, 0x19, 0x20, 0x0E, 0x18, 0x0A, 0x08, 0x1F, 
            0x17, 0x3B, 0x08, 0x0D, 0x1C]

def is_wall(x, y):
    idx = x + 11 * y
    byte = map_data[idx >> 3]
    bit = (byte ^ 0xA7) >> (idx & 7) & 1
    return bit == 1

print("MAP,S=起点(1,1), E=终点(8,9), #=墙, .=非墙):")
print("   " + "".join([f"{x:2d}" for x in range(11)]))
for y in range(11):
    row = f"{y:2d} "        #打印行号,后面追加地图数据
    for x in range(11):
        if (x, y) == (1, 1):
            row += " S"
        elif (x, y) == (8, 9):
            row += " E"
        elif is_wall(x, y):
            row += " #"
        else:
            row += " ."
    print(row)