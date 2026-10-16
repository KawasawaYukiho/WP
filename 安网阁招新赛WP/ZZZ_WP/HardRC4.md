### HardRC4（魔改 RC4 + 反调试）

#### 一、思路

```
ELF64 无壳，符号未 strip
反调试：读 /proc/self/status 查 TracerPid（两道）
静态抠 rc4_key 与 cipher
识别魔改 PRGA（下标用 XOR 而非 ADD）
离线重算 keystream，XOR 出 flag
```

---

#### 二、解题

##### 2.1 文件信息

`file` 看是 **ELF 64-bit x86-64**（Linux 程序，不是 Windows PE），16 KB，符号表没 strip。`strings` 直接暴露了一堆关键信息：

```
/proc/self/status
TracerPid:
[-] debugger detected, bye!
[+] encrypted flag (%d bytes):
[+] keystream ready (%d bytes), fnv1a32 = %08X
[*] the keystream itself is never printed. press Enter to quit.
NoDebug!
```

符号表里能看到：`main`、`rc4_keystream.constprop.0`、`cipher`、`rc4_key`、`being_traced`。

##### 2.2 反调试为什么"调不起来"

`being_traced()` 就是打开 `/proc/self/status`，找 `TracerPid:` 那行，把后面的数字转成 int——只要不是 0，就说明有调试器 attach 着，程序直接 `puts("[-] debugger detected, bye!")` 退出。

所以 gdb / lldb 一 attach 就被甩。这就是题目吐槽的"你怎么调试不了呢"。

更坑的是 `main` 里 `being_traced()` 被调了**两次**：

```asm
11D2  call being_traced      ; 第一次
11D9  test eax,eax / jne -> "debugger detected" 退出
... 打印密文 ...
1378  call rc4_keystream     ; 算 keystream
1380  call being_traced      ; 第二次
1387  je   13D5              ; 没调试 -> 跳过下面这段
1389  ... 真正的"解密/出 flag"逻辑 ...   ; 只有检测到调试才执行
```

也就是：**真正吐 flag 的代码被作者故意放在"检测到调试器才走"的分支里**。你把第一个反调试 patch 掉让它"正常跑"，反而走的是无调试分支，啥都不给。flag 字符串本身就是提示：`patch both checks or you get garbage`——两个检查都得 patch。

嫌麻烦就别跟它斗，静态复算。

##### 2.3 抠 key 和密文

符号没 strip，直接读 `.symtab`：

| 符号 | 地址 | 大小 | 内容 |
|---|---|---|---|
| `rc4_key` | 0x2160 | 8 | `NoDebug!` |
| `cipher`  | 0x2180 | 42 | 待解密密文 |
| `keystream` | 0x4040(.bss) | 42 | 运行时生成，不落盘 |

```
rc4_key = 4E 6F 44 65 62 75 67 21  = "NoDebug!"
cipher  = bd44281a31f9a910bb9d08df19c8ec0b182ce104e9a646717b6d025b71080ee60036115fb78709d110b3
```

##### 2.4 魔改的地方：PRGA 下标

KSA 部分（main 里 0x1340 那个循环）是**标准**的：S 先初始化成 0..255，然后
`j = (j + S[i] + key[i % 8]) & 0xff`，swap S[i]/S[j]。

但 `rc4_keystream`（0x1650）的 PRGA 被改了一处——标准 RC4 取密钥流字节是
`K = S[(S[i] + S[j]) & 0xff]`，这里反汇编出来是：

```asm
16A0  movzx r11d, byte [rdi+rcx]   ; S[j]
16A5  mov     [rax], r11b           ; swap S[i]=S[j]
16A8  mov     [rdi+rcx], dl         ; S[j]=old S[i]
16AB  xor     dl, [rax]            ; dl = oldS[i] ^ oldS[j]   ← 异或！
16B0  movzx   eax, byte [rdi+rdx]   ; K = S[ oldS[i] ^ oldS[j] ]
16B4  mov     [rsi-1], al
```

下标用的是 **`S[i] ^ S[j]`** 而不是加法。用标准 RC4 解会得到一堆乱码，这就是坑。

##### 2.5 离线复算

```python
def mod_rc4(key, n=42):
    S = list(range(256)); j = 0
    # KSA（标准）
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    # PRGA（魔改：下标用异或）
    i = j = 0; out = bytearray()
    for _ in range(n):
        i = (i + 1) & 0xFF
        oi = S[i]
        j = (j + oi) & 0xFF
        oj = S[j]
        S[i], S[j] = oj, oi
        out.append(S[(oi ^ oj) & 0xFF])   # ← XOR 不是 +
    return bytes(out)

key = b"NoDebug!"
ct  = bytes.fromhex("bd44281a31f9a910bb9d08df19c8ec0b182ce104e9a646717b6d025b71080ee60036115fb78709d110b3")
ks  = mod_rc4(key, len(ct))
flag = bytes(a ^ b for a, b in zip(ct, ks))
print(flag.decode())
```

输出：

```
flag{p4tch_b0th_ch3cks_0r_y0u_g3t_g4rb4g3}
```

42 字节，全可打印 ASCII。

> 备选动态路线：用 `gdb -p` 之前先 patch 掉两处 `being_traced` 的判断（或直接在程序里把 `/proc/self/status` 打开的 `fopen` 改成打开 `/dev/null`），再跑就能让那个"调试器才走"的分支把 flag 吐出来。本质和上面离线复算等价。

---

#### 三、最终 flag

```
flag{p4tch_b0th_ch3cks_0r_y0u_g3t_g4rb4g3}
```
