### orange

#### 一、解题思路

```
orange_with_wav.png 体积很大 7.9MB
PNG 尾部拼接了一段 WAV
010editor分离
得到extracted.png 和 sound.wav
用 Audacity 看sound.wav
解码摩斯密码得flag
PNG  EXIF/iTXt 能发现彩蛋
```

#### 二、分析过程

##### 2.1 分离 PNG 与 WAV

`orange_with_wav.png` 有 7.9MB
用010分离

`extracted.png` 图片本身
`sound.wav` 6MB

##### 2.2 音频频谱图

用 Audacity 打开 `sound.wav`

<img src="附件/images/orange/spectrogram.png" alt="音频频谱图" >
明显的长短摩斯密码，对照表解码出

```
maodie&doro99
```

##### 2.3 彩蛋

 `extracted.png` 元数据

```
EXIF:
  Camera Make: 0232
  DateTimeOriginal: 2026:08:01 11:45:14

iTXt Comment: 你发现了彩蛋：doro喜欢orange，maodie也是orange
```

#### 三、最终 Flag

```
flag{maodie&doro99}
```
