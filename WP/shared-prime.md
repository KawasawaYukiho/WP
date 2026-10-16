### shared-prime

#### 一、思路

两个 RSA 公钥模数 n1、n2 共用了同一个素数 p（n1 = p·q1，n2 = p·q2）求 gcd(n1, n2) 最大公约数,就能拿到 p，然后分解 n1，算出私钥 d，解密密文 c

```
n1 = p·q1,  n2 = p·q2
  gcd(n1, n2) = p
  q1 = n1 / p
  φ(n1) = (p-1)(q1-1)
  d = e^(-1) mod φ(n1)   模逆元
  m = c^d mod n1
```

#### 二、分析

##### 2.1 题目给的数据

```
n1、n2 由同一个素数 p 生成
n1 = 0xdc0b771f...
n2 = 0xf5043da7...
e  = 65537
c  = 0xd4a5d048... 密文
```

##### 2.2 RSA的原理
选两个大素数 p、q：

```
n = p × q
φ(n) = (p-1)(q-1)
```

选一个小奇数 e（通常 65537），求它的逆元 d

```
(e×d) % φ(n) == 1
d = e⁻¹ mod φ(n)
```

公钥 = (e, n)，公开
私钥 = (d, n)，保密

用公钥 e 加密消息 m，得到密文 c

```
c = m^e mod n
```

收到密文 c，用私钥 d 解密：

```
m = c^d mod n
```

`(m^e)^d ≡ m (mod n)`，所以加解密能互逆
题目说了n1和n2有一个共同素数p，gcd函数求最大公约数就可以求出p
RSA 的加解密指数必须满足 e * d ≡ 1 (mod φ(n))

##### 2.3  py脚本


```python
from math import gcd
from Crypto.Util.number import long_to_bytes

n1 = int("dc0b771fb17a99afab6081ce478a38382edd0aad7496b423a75df913d8bc36e64180389909e7ddf0d156584e5b9a823729664c14a83b45c8c84b96a382cdeaf1e5e12b2e098f5e63004e34143f15ffaa2520a7a3e28f16707853710a04d55f96f44d9365e80796b693afbb5a96b2134311e0e34da22d8dc76098c6d49fe337a02f2833aaa325ef1d5de79a15b99f64e34ab2f31f24df6da2155a84ab732707ca5abe9c7d3f005d1e86cb3a9ce56147fcc3f525bada7e409bfdad5628a789fff9c274f291616bc62d9ec2abf30984d498705a39499ed792dba94a6e99db8d7bf1f8b6c0a8a56d2068946c4a5899dcaa5a43f89d7f18885333002cd594c9a9df61", 16)
# a
n2 = int("f5043da7c46df94a6d4aa0677e3191af2bd43f93634ed109551a8a8998c4fc75a1a34992a5d6b79e4f81814ebaf83b1359e66d7f9fea8299529eb1c366d463f9a32df7eee88395d3002f061ecc89aa690a3ea070442e836671d080adccb87f01d7075e94665cf9bb18258ef5bb8f621690741224a096ead2c2610de4081f78668c1db40c2d7ab9239f1c4e647926ee8013fb95e6b823139f48d08b28a0a545568d1915b019340e15237486c2b281ef1718210999102a7f1f103d03dbefd7298c3e2cee8bb13dd080f212ee32bdb797aaa16efb6f3a7dc36fb434f81a2af2cd33992bf226ecf7a4dfa9cc9558824dc40bf3f9cf8776de24067ea308ab0af47013", 16)
# b
c  = int("d4a5d04812e658ad726baeb8dc64e8e769b167ae7dffa5f18f1bcc28220795ec0271bb02448895ab36b2e54ff36fcf99090d2f178d37c0d459b4daaafb69c13274c4a92fb34d5a130b2e4258db3f7a0bfd0fbae9b348e67b695f5b0880a595f53e45db571a480429e7d42bd8f57b1eb6811de8f61846d6153890e03ba4adc17824ff6c0a10463227a59a36d0389066b6aecdbaaacf0accb7b4dafe25d289ec752802c88a1c3775d347c22b2d38f0eae8a824f60a0f922203bbb5f3f94656d5501fcf4745bcb95d65871759f34fa6a7dd50cdeab53044127d8ab39f74c07279e970381b2453034a14869326d67314dd508b439b2dffb1085df0309a865f2650d1", 16)
e = 65537

p = gcd(n1, n2)   #最大共约数,共享素数p
q1 = n1 // p    # 分解 n1 求 q1
phi = (p - 1) * (q1 - 1)    # phi个数与n1互质
d = pow(e, -1, phi)     # py这里的 -1 是模逆元运算
m = pow(c, d, n1)     # c的d次方，取模得到明文m
print(long_to_bytes(m))     # 大整数按字节转成可读的 ASCII 字符串
```
得到

```
b'HJSEC{sh4r3d_pr1m3_br34ks_rs4}'
```

#### 三、最终 Flag

```
HJSEC{sh4r3d_pr1m3_br34ks_rs4}
```
