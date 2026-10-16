### asm

#### 一、解题思路

```
看汇编
先原样复制 19 字节 "flag{Understanding_"
中间是一串恒为真的判断，决定走哪个分支
实际走到 XOR 分支，31 字节 ^ 0x42
```

#### 二、分析过程

##### 2.1 flag前半段

```asm
lea rsi, [byte_404000]
mov ecx, 19
; 循环 19 次原样拷贝
```
`byte_404000`

```
66 6c 61 67 7b 55 6e 64 65 72 73 74 61 6e 64 69 6e 67 5f
= "flag{Understanding_"
```

##### 2.2 分支判断

```asm
mov eax, 0x2a      ; 42
add eax, 0x16      ; 64 = 0x40
cmp eax, 0x40
jne loc_401080     ; 相等，不跳

mov ebx, 0x10
shl ebx, 2         ; 64
cmp eax, ebx
jne loc_401080     ; 相等，不跳

mov ecx, 0x39
sub ecx, 0x20      ; 25
cmp ecx, 0x18
jg loc_401050      ; 25 > 24 成立，跳到 XOR 分支
```

走 `loc_401050`
`loc_401080`

##### 2.3 XOR 解密 31 字节

```asm
lea rsi, [byte_404020]
mov ecx, 31
; 每个字节 al ^= 0x42
```

```python
data = [0x23,0x31,0x31,0x27,0x2f,0x20,0x2e,0x3b,0x1d,0x2e,
        0x23,0x2c,0x25,0x37,0x23,0x25,0x27,0x1d,0x2b,0x31,
        0x1d,0x2b,0x2f,0x32,0x2d,0x30,0x36,0x23,0x2c,0x36,0x3f]
print(''.join(chr(b ^ 0x42) for b in data))
# assembly_language_is_important}
```

#### 三、最终 Flag

```
flag{Understanding_assembly_language_is_important}
```
