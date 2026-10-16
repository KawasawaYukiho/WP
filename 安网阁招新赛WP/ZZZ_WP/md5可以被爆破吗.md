### md5可以被爆破吗

#### 一、思路

```
flag 前缀已知 MD5canbecra
后 4 位是小写字母
已知完整 MD5 值
4 位小写字母只有 26^4 ≈ 45 万种
枚举算 MD5 比对
```

#### 二、分析

##### 2.1 题目信息

```python
# 已知：flag 形如 MD5canbecra????
# ???? 为 4 个小写字母
# 完整 md5 = fa660823d358e52306a3f370c371b2a1
```

##### 2.2 暴力枚举

```python
from hashlib import md5
from itertools import product
import string

target = "fa660823d358e52306a3f370c371b2a1"
prefix = "MD5canbecra"

for combo in product(string.ascii_lowercase, repeat=4):
    flag = prefix + ''.join(combo)
    if md5(flag.encode()).hexdigest() == target:
        print("flag:", flag)
        break
```

枚举 45 万种组合很快跑完
命中 `MD5canbecracked`

#### 三、最终 Flag

```
flag{MD5canbecracked}
```

[AI脚本](附件/script/md5可以被爆破吗/solve.py)
