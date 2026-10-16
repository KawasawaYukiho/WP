### DynamicDebugging?

#### 一、思路

```
dynamicdebugging.exe 是个点击计数 GUI 程序
要点击 100000 次
IDA 动态调试
在 count >= 100000 处下断点
把栈上的 count 改成 0x186A0（100000）
F9 下一步，得到flag
```

#### 二、分析

##### 2.1 程序逻辑

在IDA里搜索字符串100000，可以找到核心逻辑
按钮点击处理核心

```c
  if ( *(int *)ArgList >= 100000 )      // 在此处下断点
      {
        sub_4014C0();
        *(_DWORD *)ArgList = 0;
        SetWindowTextA(::hWnd, ::String);
      }
```

用动态调试改计数器

##### 2.2 方法一：IDA下断点改值

F9 启动程序
选Local Windows Debugger
回 GUI 点一下按钮
程序在断点处停止
<img src="附件/images/DynamicDebugging_/Snipaste_2026-10-08_15-08-13.png" alt="断点">
找到存点击数的变量Arglist dd 1
菜单 `View → Open subviews → Hex Dump`
在 Dump 窗口按 G，跳转到 `4051A8` 计数器的内存地址
<img src="附件/images/DynamicDebugging_/Snipaste_2026-10-08_15-14-36.png" alt="断点">
按右键 edit 进入编辑模式
把前 4 个字节`01 00 00 00`改成hex的100000

```
A0 86 01 00
```
再右键  apply changes

F9 继续，弹flag
<img src="附件/images/DynamicDebugging_/Snipaste_2026-10-07_11-14-46.png" alt="找到计数逻辑">


##### 2.3 方法二：Cheat Engine 改内存
运行exe程序后，在CE找到程序的进程
点几下按钮
value框输入当前的点击次数，first scan
左侧框得到一些内存地址
再点一次按钮，就能定位到存点击次数的内存地址
然后把下方框的value改成100000
<img src="附件/images/DynamicDebugging_/Snipaste_2026-10-07_11-13-11.png" alt="内存地址" width="400">

<img src="附件/images/DynamicDebugging_/Snipaste_2026-10-07_11-14-36.png" alt="改value" width="400">
点击按钮刷新验证逻辑，得到flag

#### 三、最终 Flag

```
CTF{H4ck3r_Th1s_Is_F0n}
```
