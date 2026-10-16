### logs

#### 一、思路

```
两个文件中搜flag
发现攻击者的IP
在45.147.230.71里继续找
Cookie、UA、body这3个部分

```

#### 二、分析

##### 2.1 搜flag

<img src="附件\images\logs\flag1.png" alt="Referer">

`%7B` 也就是 `{`
```
flag{th3_l0g5_
```

##### 2.2 找 Cookie、UA、body
仔细看能发现这些flag片段
<img src="附件\images\logs\flag2.png" alt="Cookie">
```
last_search = 4r3_4lw4y5_
```
<img src="附件\images\logs\flag3.png" alt="UA">

```
w4tch1ng_
```
<img src="附件\images\logs\flag4.png" alt="body">

`eTB1fQ==` base64 解码是 `y0u}`

#### 三、最终 Flag

```
flag{th3_l0g5_4r3_4lw4y5_w4tch1ng_y0u}
```
