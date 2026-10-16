### upx

#### 一、思路

```
魔改 UPX 壳识别  pack header 魔数被改
010 修魔数 + upx -d 脱壳
RC4 对称解密
```

---

#### 二、分析

##### 2.1 DIE 查壳

DIE 识别为 64 位 Windows 控制台程序，UPX 压缩
但节区名 / 魔数被改了，标准 UPX 的魔数应该是 `UPX!`（`55 50 58 21`）

跑 `upx -d challenge.exe` 会报错

```
CantUnpackException: file is possibly modified/hacked/protected; take care!
```

##### 2.2 定位被改的魔数

全局搜文本 `UPX` ， 4 处

| 文件偏移 | 字节 | 身份 | 操作 |
|---|---|---|---|
| `0x188` | `55 50 58 ??` | PE 节区名 #1 | 不用改 |
| `0x1B0` | `55 50 58 ??` | PE 节区名 #2 | 不用改 |
| `0x1D8` | `55 50 58 ??` | PE 节区名 #3 | 不用改 |
| `0x205` | `55 50 58 ??` | UPX pack header 魔数 后面是 `0D 24 0E 09 FB 9F 69 E2…` 二进制头 | 改 |

节区名 前 3 个：后面是 `00 00 00 00 xx xx 00 00` 这种节表字段
真魔数 第 4 个，`0x205`：后面是非零二进制数据 `0D 24 0E 09 FB 9F 69 E2 FE BC 64 C3…`

##### 2.3 010 手动修 + 脱壳

十六进制编辑器跳到文件偏移 `0x208`

```
55 50 58 21      ; "UPX!"
```
<img src="附件\images\upx\Snipaste_2026-10-15_21-52-02.png" alt="修复模数">

upx脱壳：

```bash
upx -d challenge.exe
```
<img src="附件\images\upx\Snipaste_2026-10-15_22-02-00.png" alt="UPX脱壳">


##### 2.4 找 key 和密文

脱壳后是 MinGW 编译的 x64 程序

```
Input your flag:
[+] Correct! You beat the shell and the algorithm :)
[-] Wrong! length is %d, but the flag is %d bytes
[-] Wrong! Did you unpack me first?
```

符号里有 `rc4_init`、`cipher`
算法是 RC4 ， 输入长度不对的串，程序会提示 flag 长度是 52 字节

`.rdata` 里两段关键数据：

RC4 **key**（17 字节）

```
55 50 58 5F 35 68 33 6C 6C 5F 34 6E 64 5F 52 43 34
= "UPX_5h3ll_4nd_RC4"
```

RC4 **密文**（52 字节）

```
3B 33 70 A9 4F 86 CE 8A 33 E7 1C 27 80 3E 5A 45
85 77 3C 88 D5 FB EC 19 81 C6 59 DA 0F 5D 70 F8
5D B8 C4 2E B7 62 D9 7A CC D5 6F 7F 29 ED 14 B6
EA D8 07 F6
```

核心校验：用同一 key 把 flag 重新 RC4 加密，与文件里的密文逐字节一致

##### 2.5 RC4 

标准 RC4（KSA + PRGA），key = `UPX_5h3ll_4nd_RC4`：

```python
def rc4(key, data):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    i = j = 0; out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

key = b"UPX_5h3ll_4nd_RC4"
ct = bytes([0x3B,0x33,0x70,0xA9,0x4F,0x86,0xCE,0x8A,0x33,0xE7,0x1C,0x27,
            0x80,0x3E,0x5A,0x45,0x85,0x77,0x3C,0x88,0xD5,0xFB,0xEC,0x19,
            0x81,0xC6,0x59,0xDA,0x0F,0x5D,0x70,0xF8,0x5D,0xB8,0xC4,0x2E,
            0xB7,0x62,0xD9,0x7A,0xCC,0xD5,0x6F,0x7F,0x29,0xED,0x14,0xB6,
            0xEA,0xD8,0x07,0xF6])
print(rc4(key, ct).decode())
```

输出：

```
flag{7h15_15_7h3_c0mb1n4710n_0f_5h3ll_4nd_4lg0r17hm}
```


#### 三、最终 flag

```
flag{7h15_15_7h3_c0mb1n4710n_0f_5h3ll_4nd_4lg0r17hm}
```
