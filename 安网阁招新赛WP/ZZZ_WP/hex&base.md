### hex&base

#### 一、解题思路

```
  开头一长串 Base64（连续解两次）
  末尾一行空格分隔的十六进制字节
双层 Base64 解出来又是一段十六进制
hex 转 ASCII
```

#### 二、分析过程

##### 2.1 双层 Base64

Base64解一次得到的还是 Base64，再解一次

```python
import base64
s = "TmpZZ05tTWdOakVnTmpjZ04ySWdORGdnTmpVZ056Z2dOV1lnTkRJZ05qRWdOek1nTmpVZ016WWdNelFnTldZZ05ETWdObVlnTm1RZ05qSWdNekVnTm1VZ016UWdOelFnTXpFZ016QWdObVVnTldZZ016RWdOek1nTldZZ05EWWdOelVnTm1VZ04yUT0="
d1 = base64.b64decode(s)     # 解出一串新的 base64
d2 = base64.b64decode(d1)   # 再解一次
```

<img src="附件/images/hex&base/double_b64.png" alt="双层base64解码">

得到一行十六进制字节

```
66 6c 61 67 7b 48 65 78 5f 42 61 73 65 36 34 5f 43 6f 6d 62 31 6e 34 74 31 30 6e 5f 31 73 5f 46 75 6e 7d
```

##### 2.2 hex 转 ASCII

空格分隔的十六进制，两位一个字节

```python
bytes.fromhex("66 6c 61 67 7b 48 65 78 5f ... ").decode()
```

#### 三、最终 Flag

```
flag{Hex_Base64_Comb1n4t10n_1s_Fun}
```
