### xor的数学题

#### 一、思路

```
题目给了密文 enc 和密钥生成式
key = 2 * 3^(n-1) - 1，n = 10^6
Python 大整数快速幂算出 key
long_to_bytes 转成大端字节串
取前 30 字节和 enc 逐字节异或
```

#### 二、分析

##### 2.1 密文与密钥

```python
enc = b'\x65\xa9\x8a\x29\xd4\xef\xcf\x26\xa1\x41\x94\xab\x29\xd6\x45\xd1' \
      b'\xe7\x91\xfa\xdc\x01\xaa\x7c\x8d\x61\x34\x9e\xf9\xa6\x5a'

n = 10**6
key = 2 * pow(3, n - 1) - 1
```

`pow(3, 999999)` 是一个约 47 万位二进制的巨大整数
乘 2 减 1 后 `long_to_bytes` 展开成 198121 字节

##### 2.2 只取高 30 字节异或

`long_to_bytes` 是大端序，最高位字节排在最前面
密文只有 30 字节，`zip` 到 enc 结束就停
实际只用到了 key 的前 30 个字节（最高位）：

```python
from Crypto.Util.number import long_to_bytes
# 没有 Crypto.Util.number 就先在 cmd 下载
# pip install pycryptodome

key_bytes = long_to_bytes(key)          # 198121 字节
flag = bytes([x ^ y for x, y in zip(enc, key_bytes)])
print(flag)
```

key 的高 30 字节为 `03c5eb4eaf9cfe4bd12df1f445e72be2d3e3a5ae32c909ff1307f09a9527`和 enc 异或即得明文字符串

输出：

```
b'flag{s1mple_l1n34r_r3curr3nc3}'
```

`simple linear recurrence`线性递推
和题目"xor的数学题"呼应
密钥靠一个递推/幂式生成

#### 三、最终 Flag

```
flag{s1mple_l1n34r_r3curr3nc3}
```

[解题脚本](附件/script/xor的数学题/solve.py)
