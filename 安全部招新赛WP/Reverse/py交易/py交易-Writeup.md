# py 交易

>PyInstaller逆向 & py字节码反汇编
>题目主要考察PE overlay .pyc反汇编置换 XOR 逆运算

---

## 一、解题思路总览

题目给出一个 Windows 可执行文件 `danke.exe`。运行后提示输入 flag。在DIE会发现OVERLAY的信息很大

## 二、识别：PyInstaller 打包结构与 PE overlay

PyInstaller 生成的 exe 本质上是一个 Windows PE 文件。它把 Python 解释器（`python3xx.dll`）、标准库压缩包和我们自己的脚本字节码都**附加在 PE 文件最后一节的后面**，这段附加数据称为 **overlay**。

| 偏移位置 | 结构 | 说明 |
|---|---|---|
| 文件开头 | DOS Header（64 字节） | 以 `MZ` 开头；其中 `0x3C` 处的 `e_lfanew` 指向 PE 头 |
| e_lfanew 处 | PE Signature `"PE\0\0"` + FILE_HEADER + OPTIONAL_HEADER | 描述节表数量、可选头大小等 |
| 其后 | Section Table（节表） | 每个节 40 字节，记录各节在文件中的位置与大小 |
| 节原始数据之后 | **OVERLAY（附加数据）** | PyInstaller 把 PYZ 归档与脚本字节码都放在这里，正是我们要提取的部分 |

> **关键点：** PyInstaller 并没有对脚本字节码做高强度加密，只是把它们按特定格式归档在 overlay 里。因此不需要复杂的脱壳，直接用解包即可还原出 `.pyc` 文件。

---

## 三、解包：pyinstxtractor 提取 pyc

使用经典工具 `pyinstxtractor.py` 对 `danke.exe` 解包：

```powershell
# 在 PowerShell 中执行
python pyinstxtractor.py danke.exe
```

![pyinstxtractor 解包结果](image/decompress.png)

从输出可以读到几条关键信息：

- PyInstaller version **2.1+**，Python version **3.14**；
- 归档长度 9033113 字节，共找到 67 个文件；
- **Possible entry point: kongbeiqie.pyc** —— 这就是题目主脚本编译后的字节码；
- 解包完成后生成目录 `danke.exe_extracted/`，里面除了一堆 `.pyd`、`.dll` 和标准库归档 `PYZ.pyz`，根目录下就躺着我们要的 `kongbeiqie.pyc`。

---

## 四、反汇编：用 marshal + dis 读懂 pyc

`.pyc` 是 Python 编译后的字节码文件，它不能直接当源码读，但 Python 自带两个标准库可以把它"反汇编"成人类可读的指令：

- `marshal`：Python 内置的序列化模块，`.pyc` 里的 code object 就是用 marshal 格式存的；
- `dis`：反汇编模块，把 code object 翻译成 `LOAD_CONST` / `STORE_NAME` 这类指令。

### 4.1 .pyc 文件结构

```
┌─────────────────────────┐
│ 头部 (16 字节)          │  ← magic number + flags + 时间戳/源文件哈希
├─────────────────────────┤
│ marshal 序列化的 code    │  ← 从这里开始才是真正的 Python 对象
└─────────────────────────┘
```

前 4 字节是 magic number（标识 Python 版本，本例对应 3.14）；接着 4 字节是 flags；最后 8 字节是时间戳或源文件哈希，**共 16 字节**。这 16 字节不是 marshal 数据，如果直接 `marshal.load()` 会读到 magic number 而报错，所以必须先用 `f.read(16)` 跳过。

### 4.2 一条命令完成反汇编

```bash
# -c 表示直接执行引号内代码，不落盘
python -c "import marshal,dis; \
f=open('kongbeiqie.pyc','rb'); \
f.read(16); \
dis.dis(marshal.load(f))"
```

这条命令等价于：

```python
import marshal, dis

f = open('kongbeiqie.pyc', 'rb')   # 二进制只读打开
f.read(16)                          # 跳过 pyc 头部，文件指针后移 16 字节
code = marshal.load(f)              # 反序列化得到模块级 code object
dis.dis(code)                       # 反汇编为可读指令
```

### 4.3 反汇编结果关键片段

反汇编输出很长，核心是以下几部分。首先是模块级常量：

```text
LOAD_CONST   1 ('YVYh]\x07@h\x0ehRwJVD\x07]s\x03D__ELzhY\x06_TP')
STORE_NAME   1 (encode)            # 目标密文，长度 31

LOAD_CONST   9 ((19,14,10,24,27,6,5,12,11,15,9,26,30,22,16,28,
                 1,13,18,2,17,21,29,4,25,7,8,23,0,3,20))
STORE_NAME   2 (table)             # 31 个元素的置换表

LOAD_SMALL_INT 55
STORE_NAME   3 (XOR_KEY)           # 异或密钥 = 55
```

主流程判断输入：

```text
LOAD_NAME  (input)  
STORE_NAME (flag)     # flag = input()
len(flag) != 31      打印 'Length Wrong!!' 并返回
final = enc(flag)
if final == encode:  打印 'Wow,you get the right flag!!'
else:                打印 'Sorry,Your input is Wrong'
```

最关键的 `enc` 函数循环体：
对应源码：tmp += chr(ord (input [table[i] ] ) ^ XOR_KEY)
```text
LOAD_FAST_BORROW   0 (input)
LOAD_GLOBAL        8 (table)
LOAD_FAST_BORROW   2 (i)
BINARY_OP          26 ([])         # input[table[i]]
CALL               1               # ord(...)
LOAD_GLOBAL        10 (XOR_KEY)
BINARY_OP          12 (^)          # ^ 55
CALL               1               # chr(...)
BINARY_OP           0 (+)          # tmp += ...
```

> **算法还原：** 对输入 flag 的第 `i` 个输出字符，先按置换表 `table[i]` 取到 flag 中的某个字符，取 ASCII 后与 `55` 异或，再转回字符拼起来。即：
>
> `output[i] = chr( ord( flag[ table[i] ] ) ^ 55 )`

---

## 五、还原校验脚本 encrypt.py

根据反汇编结果，我们可以把校验逻辑还原成正常的 Python 源码（命名为 `encrypt.py`）：

```python
flag = ''
encode = 'YVYh]\x07@h\x0ehRwJVD\x07]s\x03D__ELzhY\x06_TP'
table = (19, 14, 10, 24, 27, 6, 5, 12, 11, 15, 9, 26, 30, 22,
         16, 28, 1, 13, 18, 2, 17, 21, 29, 4, 25, 7, 8, 23, 0, 3, 20)
XOR_KEY = 55

def enc(input):
    tmp = ''
    for i in range(len(input)):
        tmp += chr(ord(input[table[i]]) ^ XOR_KEY)
    return tmp

if __name__ == '__main__':
    print('Please input your flag:')
    flag = input()
    if len(flag) != 31:
        print('Length Wrong!!')
    else:
        final = enc(flag)
        if final == encode:
            print('Wow,you get the right flag!!')
        else:
            print('Sorry,Your input is Wrong')
```

可见程序只接受长度为 31 的字符串，且要求 `enc(flag) == encode`。我们没有 oracle 可以爆破，但这个算法完全可逆，直接逆推即可。

---

## 六、逆推求解 solve.py

加密过程是：`encode[i] = flag[table[i]] ^ 55`。异或同一常数两次即还原，所以：

```text
flag[ table[i] ] = ord( encode[i] ) ^ 55
```

注意这里不是简单地把 `encode` 整体异或 55 —— 因为中间还隔着一层**置换**。输出的第 `i` 位对应的是原 flag 的第 `table[i]` 位。所以要开一个长度 31 的数组，按 table 把每个字符"放回原位"，最后再 join：

```python
# solve.py —— 逆向求解
encode = 'YVYh]\x07@h\x0ehRwJVD\x07]s\x03D__ELzhY\x06_TP'
table = (19, 14, 10, 24, 27, 6, 5, 12, 11, 15, 9, 26, 30, 22, 16, 28,
         1, 13, 18, 2, 17, 21, 29, 4, 25, 7, 8, 23, 0, 3, 20)
XOR_KEY = 55

ans = [''] * 31
for i in range(31):
    ans[table[i]] = chr(ord(encode[i]) ^ XOR_KEY)   # 按置换表归位
flag = ''.join(ans)

print(flag)
print(enc(flag) == encode)      # 回代校验，确认还原正确
```

---

## 七、运行得到 Flag

```bash
$ python solve.py
hjsc{w0_nen9_Da_sh4ngha1_M@j0r}
True
```

最后一行 `True` 表示把还原出的 flag 再走一遍 `enc()`，结果与目标 `encode` 完全一致，证明求解正确。

> **Flag：`hjsc{w0_nen9_Da_sh4ngha1_M@j0r}`**

---

## 八、知识点小结

1. **PyInstaller 打包识别：** 带 `python3xx.dll`、文件异常大、overlay 里含 PYZ 归档的 exe，基本可判定为 PyInstaller 产物，用 `pyinstxtractor.py` 解包即可。
2. **.pyc 反汇编：** 用 `marshal.load()` 读 code object 前必须先 `f.read(16)` 跳过 16 字节头部；再用 `dis.dis()` 反汇编。Python 3.10+ 的字节码（如 `LOAD_FAST_BORROW`、`BINARY_OP`）只要抓住 `LOAD_CONST/STORE_NAME/CALL` 几类指令就能还原逻辑。
3. **置换 + XOR 的可逆性：** XOR 是对合运算（异或两次还原）；置换表 `table` 是一个排列，逆运算就是"按 `table[i]` 把字符写回第 `table[i]` 个位置"。两层都可逆，因此无需爆破即可直接还原明文。
