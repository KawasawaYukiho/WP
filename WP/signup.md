### signup

#### 一、思路

```
DIE 查壳发现节区名是 VMP0/VMP1  伪装成 VMProtect
但二进制里能搜到 UPX! 标记，本质还是 UPX 压缩
手动把节区名改回 UPX0/UPX1，upx -d 脱壳
反汇编  key 是 "GUET2026"，输入长度必须 27 字节
校验逻辑是 RC4 加密后和 .rdata 段的密文做 memcmp
提取密文，用 RC4 解密直接得到 flag
```

#### 二、分析过程

##### 2.1 查壳

用 DIE 查壳能发现是 UPX加壳，直接upx -d解压会报错
DIE看区块，发现节区名是 VMP0/VMP1 和 UPX 对不上

本质还是 UPX 压缩，只是节区名被改成了 VMP 
直接跑 `upx -d` 会报错
因为 UPX 会校验节区名

##### 2.2 修复节区名脱壳

在010把第一个节区名从 `VMP0` 改成 `UPX0`，第二个从 `VMP1` 改成 `UPX1`
保存再用`upx -d`得到脱壳后的signup.exe

```bash
upx -d SignUp.exe
```

##### 2.3 反汇编

用 IDA64 打开，找到 `input what you think:` 字符串的交叉引用，定位到start函数

关键逻辑：
```c
//把 "GUET2026" 复制到栈上作为 key
memcpy(buf, "GUET2026", 9);

//读取用户输入
printf("this is just a easy upx, right?\n");
printf("input what you think:");
fgets(input, 0x80, stdin);

//去掉换行符，长度必须正好 27 字节
len = strcspn(input, "\n");
if (len != 27) return 1;

//RC4(key="GUET2026", keylen=8, input, output)
rc4_crypt("GUET2026", 8, input, output);

//和预设密文比较，相等则输出 yes
if (memcmp(output, ciphertext, 27) == 0) 
{
    printf("yes\n");
}
```

##### 2.4  RC4 算法

进入变换函数 `sub_140011145`跳转后真正实现在 `0x140011AD0`
反汇编可以发现RC4的加密算法

```c
  if ( a1 && a3 && a4 && a2 )  //a1 = key = GUET2026
                               //a2 = keylen = 8
  {
    for ( j = 0; j < 0x100; ++j )
      v9[j + 16] = j;         //v9 是 S盒
    for ( j = 0; j < 0x100; ++j )
    {
      v16 = (unsigned __int8)v9[j + 16] + v11;      //v16 = S[i] + j
      v11 = (unsigned __int8)(*(_BYTE *)(a1 + j % a2) + v16);
      v13 = (unsigned __int8)v9[j + 16];    //v13 暂存 S[i]
      v9[j + 16] = v9[v11 + 16];
      v9[v11 + 16] = v13;
    }                           //这里完成RSA 初始化S表
    
    j = 0;                      // RC4 里的 i
    v11 = 0;                    // RC4 里的 j
    for ( k = 0; k < a5; ++k )      //a5 数据长度27  k 计数器
    {
      j = (unsigned __int8)(j + 1);                 // i = (i + 1) % 256
      v11 = (unsigned __int8)(v9[j + 16] + v11);    // j = (j + S[i]) % 256

      v14 = (unsigned __int8)v9[j + 16];        //v14 暂存S[i]
      v9[j + 16] = v9[v11 + 16];                
      v9[v11 + 16] = v14;                     //swap(S[i], S[j])

      v15 = (unsigned __int8)v9[(unsigned __int8)(v9[v11 + 16] + v9[j + 16]) + 16];
      //v15 = 密钥流字节k  k = S[(S[i] + S[j]) % 256]
      *(_BYTE *)(a4 + k) = v15 ^ *(_BYTE *)(a3 + k);
    }                          //output[k] = input[k] ^ v15;
                               //a3 = input | a4 = output = input加密后的结果
  }
```

##### 2.5 提取密文并解密
<img src="附件\images\signup\Snipaste_2026-10-05_16-23-20.png">

密文在 `.rdata` 段 `0x14001ABB0`，共 27 字节：

```
B7 8E 74 49 DD 89 F0 DE 91 3C 3F 11 B9 E5 5A CF
D8 58 EE B2 F9 89 21 1D 2C 1A 7D
```

key 是 `"GUET2026"`（8 字节）。RC4 加解密对称，直接用同样的 key 解密密文：

```python
key = b"GUET2026"
cipher = bytes([0xB7, 0x8E, 0x74, 0x49, 0xDD, 0x89, 0xF0, 0xDE,
                0x91, 0x3C, 0x3F, 0x11, 0xB9, 0xE5, 0x5A, 0xCF,
                0xD8, 0x58, 0xEE, 0xB2, 0xF9, 0x89, 0x21, 0x1D,
                0x2C, 0x1A, 0x7D])

# KSA
S = list(range(256))
j = 0
for i in range(256):
    j = (j + S[i] + key[i % len(key)]) % 256
    S[i], S[j] = S[j], S[i]

# PRGA
i = j = 0
plaintext = []
for byte in cipher:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    k = S[(S[i] + S[j]) % 256]
    plaintext.append(byte ^ k)

print(bytes(plaintext))
```

运行输出：

```
b'GUET{1s_0nly_@_e@sy_P@cked}'
```

回到程序里输入这个字符串验证，程序输出 `yes`，校验通过

#### 三、最终 Flag

```
GUET{1s_0nly_@_e@sy_P@cked}
```

