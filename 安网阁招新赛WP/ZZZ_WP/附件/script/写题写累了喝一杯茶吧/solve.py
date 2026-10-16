import struct

# 写题写累了喝一杯茶吧 —— 标准 TEA 解密
# 程序把 16 字节 flag 分成两组各 8 字节做 TEA 加密，再与 .rdata 里的 cipher 比较
# key 为 .rdata 中的 ASCII 字符串 "teatime!teatime!"

def tea_dec(block, k):
    v0, v1 = struct.unpack('<II', block)
    s = 0xC6EF3720          # 32 * 0x9E3779B9（解密初始和）
    for _ in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + s) ^ ((v0 >> 5) + k[3]))) & 0xFFFFFFFF
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + s) ^ ((v1 >> 5) + k[1]))) & 0xFFFFFFFF
        s = (s - 0x9e3779b9) & 0xFFFFFFFF
    return struct.pack('<II', v0, v1)

# .rdata 中的 cipher（16 字节）
c = bytes([0x89, 0x73, 0x95, 0x16, 0x2C, 0xE9, 0xA7, 0xB8,
           0x8E, 0x14, 0xBB, 0xD3, 0xBA, 0x54, 0x3A, 0xE6])

# .rdata 中的 key（16 字节 ASCII，按小端拆成 4 个 32 位字）
k = struct.unpack('<IIII', b'teatime!teatime!')

flag = tea_dec(c[:8], k) + tea_dec(c[8:], k)
print(flag)
