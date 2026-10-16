# -*- coding: utf-8 -*-
"""crypto-不可逆的加密 —— 解密脚本"""

def encrypt(n):
    if n % 2 == 1:            # 奇数字符
        return (5 * n + 3) // 3
    else:                     # 偶数字符
        return (5 * n + 2) // 4

enc = [
    128, 135, 162, 172, 206, 60, 125, 125,
    159, 65, 138, 125, 159, 169, 148, 86,
    138, 159, 82, 192, 159, 143, 86, 148,
    86, 143, 192, 82, 123, 135, 86, 209,
]

# 正向是整除（//）一对多，反查时优先选可打印字符
table = {}
for n in range(32, 127):
    table.setdefault(encrypt(n), n)

flag = "".join(chr(table[c]) for c in enc)
print(flag)
