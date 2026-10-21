### capture

#### 一、思路
```
wireshark查看
pcap1 过滤 HTTP 发现 X-password 请求头（base64 解码得密码）和 GET /files/secret.zip
pcap2 追踪 TCP 流 → 提取完整的 secret.zip
用密码解压 secret.zip → 得到 hidden.png
分析hidden.png 发现LSB隐写的flag
```

#### 二、分析

##### 2.1 pcap1找有效信息

wireshark里，capture_1.pcap，过滤 `http`，在 `POST /upload HTTP/1.1` 请求里发现字段

```
X-password: UEBzc3cwcmQyMDI2
```

<img src="images/capture/x_password.png" alt="X-password 请求头" width="500">

base64解码得到 `P@ssw0rd2026`

`GET /files/secret.zip` 请求了一个secret.zip，但是不完整 

zip 包的后半段数据不在这个 pcap 里

##### 2.2 pcap2TCP流找完整secret.zip

发现是PK，.zip后缀的文件
<img src="附件/images/capture/find_zip.png" alt="zip 文件头" width="600">

`capture_2.pcap`  右键包，追踪流 ，TCP stream，显示为原始数据，然后另存为`secret.zip`
<img src="附件/images/capture/tcp_stream.png" alt="提取TCP流" width="400">

##### 2.3 解压zip  分析隐写

密码 `P@ssw0rd2026` 解压 `secret.zip`
zsteg分析`hidden.png`发现LSB隐写flag
<img src="附件/images/capture/zsteg.png" alt="zsteg结果" >

#### 三、最终flag
`Flag{L5B_1s_N0t_H4rd_2_F1nd}`