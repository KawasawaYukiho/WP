### simpleBase64

#### 一、解题思路

```
Linux里用 strings 提取
发现自定义 Base64 表，大写字母 ROT13 偏移
把密文字符按自定义表位置映射回标准表
再标准 Base64 解码
```

#### 二、分析过程

##### 2.1 strings 提取

```bash
strings simplebase | grep -E "flag|==|NOPQ|wrong"
```

```
DIqUD1ETr3AcGKNkZ19PLKAyAwEsAIELHx1nFSH2IwyGsD==
This is flag!!
This is wrong
NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/
```

<img src="附件/images/simpleBase64/strings.png" alt="strings 提取">

##### 2.2 自定义表

```
标准表：ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
自定义：NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/
```

大小写字母都偏移了 13（ROT13）
数字和 `+/` 位置不变

##### 2.3 换表解码

```python
import base64
custom = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/'
std    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
ct = 'DIqUD1ETr3AcGKNkZ19PLKAyAwEsAIELHx1nFSH2IwyGsD=='
mapped = ''.join(std[custom.index(c)] for c in ct.rstrip('='))
print(base64.b64decode(mapped + '==').decode())
```

#### 三、最终 Flag

```
AWGCTF{siMp13_Base64_5TXRMZHU6V9S}
```
