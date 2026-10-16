### DNS

#### 一、思路

```
wireshark
过滤 dns 能找到一长串子域名
子域名只含 A-Z2-7  Base32 特征
去掉后缀 拼成整串 Base32 Base32 解码 zlib 解压
还原出 application.yml
```

#### 二、分析

##### 2.1 确认异常

Wireshark 打开 pcap

过滤 dns
前几百条是正常域名
596 号包出现异常查询名

```text
PDNBLSSBBLBDAECA2F6U4ELRFW2E3CRFK5IAITYQYZSGZC3VGJGGEFOFXNVZN77.
TWYNJQ52NVMZMVCXCSTLJZJBYHVMGWVDGTFU2YM2CQGOB4EVQ2YPUDTWPETI6TU.
523G745XF5B4BR4VLCETQLTIUSNZEE4XYXDA7ZC6TPFH5DNXGZLMY75UUUZGD45.
B6JCKM2L75KD6LXSLAQ.t.events.app-analytic
```

##### 2.2 定位 C2 域名

所有异常查询名尾部都固定为 `t.events.app-analytic`
也就是攻击者控制的 C2 域名
去掉后缀 `t.events.app-analytic` 剩下 4 段子域名就是外传数据


##### 2.3 解码还原

```python
import base64, zlib

qname = ("PDNBLSSBBLBDAECA2F6U4ELRFW2E3CRFK5IAITYQYZSGZC3VGJGGEFOFXNVZN77."
         "TWYNJQ52NVMZMVCXCSTLJZJBYHVMGWVDGTFU2YM2CQGOB4EVQ2YPUDTWPETI6TU."
         "523G745XF5B4BR4VLCETQLTIUSNZEE4XYXDA7ZC6TPFH5DNXGZLMY75UUUZGD45."
         "B6JCKM2L75KD6LXSLAQ")

b32 = qname.replace(".", "")                    # 去点，拼成整串
b32 += "=" * ((8 - len(b32) % 8) % 8)           # 补 padding
data = zlib.decompress(base64.b32decode(b32))   # Base32 解码 + zlib 解压
print(data.decode())                            # 输出明文
```

输出：

<img src="附件\images\DNS\输出.png" alt="脚本输出">

#### 三、最终 Flag

```
flag{dn5_4nd_1cmp_4r3_b0th_c2_ch4nn3l5}
```
