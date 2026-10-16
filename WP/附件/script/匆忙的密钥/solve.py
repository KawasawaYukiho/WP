from math import isqrt
from Crypto.Util.number import inverse, long_to_bytes, isPrime

# ============================================================
# 题目数据（来自 匆忙的密钥.txt）
# ============================================================
n = int("128238150108052472971107509871501016687988927864918262138868046480163613798632355139985981976662480300710530454772760612038397547791656528394404617136997918435337816829254365979998999271329107900358983183976875337477886150419905532163253782516831853481674653012279771019498880575085696755934298779035029630941")
e = 65537
c = int("6a8f0814c53fe588ffca775504aa70354b9f2c3f2875247179559cc50f3bddb28f90a90c951c829b01ca3f0398366e2f29920e74332e06f279c1297fbbe32597f2919e40eed1c8ddbe2cc24a058dc96da2b8b845fea8b79401ebe5c9d50cd74264c41552f665ed063bc57267e4b9964f603d8882c63b96c06110b74f90a4dff8", 16)

print(f"n bit length = {n.bit_length()}")
print(f"e = {e}")
print()

# ============================================================
# 第一步：把 n 按 64 位字拆开，观察结构
# ============================================================
# n 是 1024 位 = 16 个 64 位字
# word[0] 是最高 64 位，word[15] 是最低 64 位
words = []
temp = n
for i in range(16):
    words.append(temp & ((1 << 64) - 1))
    temp >>= 64
words.reverse()  # words[0] = 最高位

print("=== n 的 64 位字结构 ===")
for i, w in enumerate(words):
    marker = " ← 非零" if w != 0 else ""
    print(f"  word[{i:2d}] = {w:016x}{marker}")
print()

# ============================================================
# 第二步：从 n 中提取三段
# ============================================================
# p = A * 2^448 + B,  q = C * 2^448 + D
# n = p*q = A*C * 2^896 + (A*D + B*C) * 2^448 + B*D
#
# 对应到 n 的字：
#   最高 128 位 = A*C
#   中间部分     = A*D + B*C
#   最低 128 位 = B*D

AC = n >> 896                           # A*C（最高 128 位）
rest = n - AC * (1 << 896)
middle = rest >> 448                    # A*D + B*C
BD = rest & ((1 << 448) - 1)            # B*D（最低 128 位）

print(f"A*C      = {hex(AC)}")
print(f"A*D+B*C  = {hex(middle)}")
print(f"B*D      = {hex(BD)}")
print()

# ============================================================
# 第三步：分解 A*C，找所有因数对 (A, C)
# ============================================================
# A 和 C 都是 64 位数（p、q 的最高 64 位）
# 先对 AC 做质因数分解，再枚举所有因数，挑两边都是 64 位的
print("=== 分解 A*C ===")
print(f"A*C = {AC}")

# 分解质因数
def factorize(x):
    factors = {}
    d = 2
    while d * d <= x:
        while x % d == 0:
            factors[d] = factors.get(d, 0) + 1
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        factors[x] = factors.get(x, 0) + 1
    return factors

factors = factorize(AC)
print(f"质因数分解: {factors}")

# 枚举所有因数
divisors = [1]
for prime, exp in factors.items():
    new_divs = []
    for dv in divisors:
        mul = 1
        for k in range(exp + 1):
            new_divs.append(dv * mul)
            mul *= prime
    divisors = new_divs

# 筛选两边都是 64 位数 [2^63, 2^64) 的因数对
pairs = []
for d in divisors:
    other = AC // d
    if 2**63 <= d < 2**64 and 2**63 <= other < 2**64:
        pairs.append((d, other))

print(f"64 位因数对 ({len(pairs)} 组):")
for a, cc in pairs:
    print(f"  A = {hex(a)}, C = {hex(cc)}")
print()

# ============================================================
# 第四步：对每组 (A, C)，列二次方程求 B
# ============================================================
# 已知：
#   A*C = AC
#   A*D + B*C = middle
#   B*D = BD
#
# 消去 D：D = (middle - B*C) / A
# 代入 B*D = BD：
#   B * (middle - B*C) / A = BD
#   C*B^2 - middle*B + A*BD = 0
#
# 解二次方程：B = (middle ± sqrt(middle^2 - 4*C*A*BD)) / (2*C)

print("=== 求解 ===")
found = False
for A, C in pairs:
    discriminant = middle * middle - 4 * C * A * BD
    if discriminant < 0:
        continue
    sqrt_d = isqrt(discriminant)
    if sqrt_d * sqrt_d != discriminant:
        continue  # 不是完全平方数，跳过

    for sign in [1, -1]:
        numerator = middle + sign * sqrt_d
        if numerator <= 0:
            continue
        if numerator % (2 * C) != 0:
            continue
        B = numerator // (2 * C)
        if B <= 0 or B >= 2**64:
            continue
        if BD % B != 0:
            continue
        D = BD // B
        if D <= 0 or D >= 2**64:
            continue

        # 验证
        if A * D + B * C != middle:
            continue
        if B * D != BD:
            continue

        print(f"找到解！")
        print(f"  A = {hex(A)}")
        print(f"  B = {hex(B)}")
        print(f"  C = {hex(C)}")
        print(f"  D = {hex(D)}")

        # 还原 p, q
        p = A * (1 << 448) + B
        q = C * (1 << 448) + D

        print(f"\n  p = {hex(p)}")
        print(f"  q = {hex(q)}")
        print(f"  p 是素数: {isPrime(p)}")
        print(f"  q 是素数: {isPrime(q)}")
        print(f"  p*q == n: {p*q == n}")

        # 解密
        phi = (p - 1) * (q - 1)
        d_key = inverse(e, phi)
        m = pow(c, d_key, n)
        flag = long_to_bytes(m)

        print(f"\n  解密明文: {flag}")
        found = True
        break
    if found:
        break

if not found:
    print("未找到解")
