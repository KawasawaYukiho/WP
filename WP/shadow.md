### shadow

#### 一、思路

给了一个 Linux shadow 口令文件和它的旧备份，alice 的密码是 6 位纯数字
哈希算法是 `SHA256(salt + password)`，直接暴力枚举 000000~999999 就能跑出来。

```
shadow.bak 里 alice 的 salt 和 hash
  提取 salt=35712258, hash=cd4693...
  枚举 6 位纯数字密码
  SHA256(salt + password) 逐个比对
  匹配到就是密码
```

#### 二、分析

##### 2.1 分析加密算法

`用户名:$7$salt$hash`，题目说`$7` 表示 SHA256-crypt算法
为`hash = SHA256(salt + password)`，即盐值和密码拼接后做一轮 SHA-256

##### 2.1 提取 alice 的盐和哈希

从 `shadow.bak` 得到 alice 的数据
或者shadow原件也可以,算出来的口令是一样的

salt = `35712258`
target_hash = `cd46936c5c396f66b2971b12d427563a3b0d9a671a8ee0e9eb7e809571d3ddb7`

##### 2.3 枚举 6 位纯数字口令

6 位纯数字一共 100 万种,直接py暴力跑

```python
import hashlib  # 导入哈希库

# 已知的盐值，和口令拼接后再做哈希
salt = "35712258"

#暴力计算求哪个 6 位数字口令能算出这个hash
target_hash = "cd46936c5c396f66b2971b12d427563a3b0d9a671a8ee0e9eb7e809571d3ddb7"

# 枚举所有可能的 6 位数字口令
for i in range(1000000):
    password = str(i).zfill(6)  # 把不够6位的数字补齐成 6 位字符串

    # 按题目规则  salt + password，然后计算 SHA-256，转成十六进制字符串
    hash = hashlib.sha256((salt + password).encode()).hexdigest()

    # 哈希和目标哈希一致，则输出口令
    if hash == target_hash:
        print(f"口令: {password}")   # 输出明文口令
        break
```
输出:

```
口令: 231741
```

#### 三、最终 Flag

```
flag{231741}
```
