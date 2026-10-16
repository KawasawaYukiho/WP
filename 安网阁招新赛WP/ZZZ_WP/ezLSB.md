### ezLSB

#### 一、思路

```
 LSB 最低有效位隐写
用 SteSolve 提取 RGB 三通道 bit plane 0
按行、LSB First、RGB 顺序得hex
hex 解码即 flag
```

#### 二、分析

##### 2.1 LSB 原理

PNG 的每个像素由 R/G/B 三个字节组成，每个字节最低位（bit 0）对颜色几乎无影响，可以用来藏信息

##### 2.2 SteSolve 提取

用 SteSolve 打开 `doyouknow.png`，Extract 设置：

Bit Planes：Red / Green / Blue 的 bit 0 全部勾选
Extract By：Row 按行
Bit Order：LSB First
Bit Plane Order：RGB

点 Preview 后出现 hex dump：

```
666c61677b6c7362 5f656173795f3230 32367d00...
```

```
flag{lsb_easy_2026}
```

<img src="附件/images/ezLSB/stego_extract.png" alt="SteSolve 提取 LSB" >


#### 三、最终 Flag

```
flag{lsb_easy_2026}
```
