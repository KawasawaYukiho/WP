### 简单的SMC

#### 一、解题思路

```
teach_smc.exe 是 SMC 自修改代码程序
DIE 看到导入 VirtualProtect，是 SMC 特征
IDA 找到解密 stub，把 .text 段改成可写，36 字节全部 XOR 0x90
模拟解密后，看到校验函数是 cmp input, 0x3039
0x3039 = 12345
输入 12345 得 good!
```

#### 二、分析过程

##### 2.1 DIE 查壳

导入表里有 `VirtualProtect`
是 SMC 自修改代码特征
<img src="附件\images\简单的SMC\Snipaste_2026-10-09_13-15-14.png" alt="DIE看import">

##### 2.2 SMC 解密 stub
IDA在import找到VirtualProtect
<img src="附件\images\简单的SMC\Snipaste_2026-10-09_13-19-53.png" alt="IDA的import">

<img src="附件\images\简单的SMC\Snipaste_2026-10-09_13-41-04.png" alt="stub">

上面框：改内存权限
```asm
push 40h              ; 可写可执行
push 1000h            ; 4KB
push offset sub_401080; 从 0x401080 开始
call VirtualProtect   ; 把代码段改成可写
```
中间循环
```
loc_4010E9:
cmp [ebp+var_C], 24h   ; i >= 36?
jge loc_40110B         ; 到 36 次就跳出循环
```

左下框：解密循环体
```
mov edx, offset sub_401080
add edx, [ebp+var_C]   ; edx = 0x401080 + i
movsx eax, byte ptr [edx]
xor eax, 90h           ; 当前字节 ^ 0x90
mov ecx, offset sub_401080
add ecx, [ebp+var_C]
mov [ecx], al          ; 写回原地址
jmp loc_4010E0         ; i++，回中间框继续判断
```

##### 2.3 反汇编

要解密的 36 个字节就在 `0x401080` 开始
Hex View 跳到 `0x401080`
<img src="附件\images\简单的SMC\Snipaste_2026-10-09_14-08-22.png">

把那 36 个字节每个 XOR `0x90`

`C5 1B 7C C1 11 ED 98 A9 A0 90 90 E5 99 57 D5 6C`
`91 90 90 90 7B 97 57 D5 6C 90 90 90 90 1B D5 6C`
`1B 75 CD 53`
与90h进行异或，得到
`55 8B EC 51 81 7D 08 39 30 00 00 75 09 C7 45 FC`
`01 00 00 00 EB 07 C7 45 FC 00 00 00 00 8B 45 FC`
`8B E5 5D C3`

把解密后的字节重新反汇编

```asm
push ebp
mov  ebp, esp
push ecx
cmp  dword ptr [ebp+8], 0x3039   ; 输入 == 12345?
jne  short 失败
mov  [ebp-4], 1                   ; 返回 1
jmp  short 结束
失败:
mov  [ebp-4], 0                   ; 返回 0
结束:
mov  eax, [ebp-4]
mov  esp, ebp
pop  ebp
ret
```

`0x3039 = 12345`
读入整数，等于 12345 就输出 `good!`

##### 2.4 运行验证

```
> teach_smc.exe
12345
good!
```


#### 三、最终 Flag

```
AWGCTF{12345}
```

