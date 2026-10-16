### ezrsa

#### 一、思路

```
题目直接给 p、q、e、c
标准 RSA：n=pq，phi=(p-1)(q-1)
d = e^-1 mod phi
m = c^d mod n，long_to_bytes 还原
```

#### 二、分析

##### 2.1 已知

```
p = 7707951187943043160357159566209...
q = 8263418573002770823945846443750...
e = 65537
c = 5552879745401742663071681180792...
```
p、q 已知，不需要分解 n

##### 2.2 求私钥解密

```python
from Crypto.Util.number import long_to_bytes

n = p * q
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)     # d是私钥
m = pow(c, d, n)        # m是解出来的明文
print(long_to_bytes(m))
```

#### 三、最终 Flag

```
flag{This_is_RSA}
```

[解题脚本](附件/script/ezrsa/solve.py)
