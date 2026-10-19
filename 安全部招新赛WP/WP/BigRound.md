### BigRound

#### 一、思路

```
Win32 GUI 转盘程序
DIE 查壳：PE64 GUI 程序，链接 user32/gdiplus/gdi32/kernel32，无壳
用 Cheat Engine 附加进程，扫描积分值定位内存地址，改成 100000
再转一次触发 cmp 判断，拿到 flag
```

#### 二、分析

##### 2.1 运行程序

运行 `BigRound.exe`

提示： 你只要得到100000分就能获得flag了，是不是很简单
窗口显示当前积分、已转次数，点"转动转盘"后加一点积分

##### 2.2 DIE 查壳

用 Detect It Easy 打开 `BigRound.exe`

| 项目 | 内容 |
|---|---|
| 文件类型 | PE64，Windows GUI 程序 |
| 链接 DLL | `USER32.dll` / `GDI32.dll` / `gdiplus.dll` / `KERNEL32.dll` |
| 壳 | 无壳 |

##### 2.3 IDA64

Search `Alt+B` 搜中文字节
搜 '通关' 的 UTF-16LE 字节`1A 90 73 51`，查看交叉引用
到sub_140004E20看伪代码

<img src="附件\images\BigRound\Snipaste_2026-10-06_15-35-28.png" alt="伪代码" >

```c
v16 = v14 + *(_DWORD *)lpMem;    // 加奖励
*v15 = v16;
if ( v17 < 100000 )
    // 奖励到账
else
    {
        *((_BYTE *)lpMem + 20) = 1;   // 解锁
        sub_140001E20(lpText);        // 解密 flag
        MessageBoxW(hWnd, v18, ...);  // 弹窗
    }
```

就可以知道判断逻辑
MessageBoxW，在运行时产生一个窗口，放flag
看sub_140001E20的加密逻辑，静态分析很难得flag

##### 2.4 Cheat Engine 改积分内存

用 CE 找值改值,让程序自己弹 MessageBox
先正常运行 `BigRound.exe`，积分初始值1337

Cheat Engine点左上角找到 `BigRound.exe`进程
value填1337，first scan
左侧栏得到一个地址，对应存放积分的值的地址
把值改成100001，再转一次得到flag 

#### 三、最终 Flag

```
GUET{H0w_t0_U5e_D3bugger_0r_1DA}
```
