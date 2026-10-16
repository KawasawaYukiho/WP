### flower

#### 一、思路

```
DIE 查壳：32 位 PE，无壳
找 "flag> " 字符串交叉引用，定位主函数
主函数调用 0x401000 做校验
有花指令干扰
跳过花指令读核心循环：29 次异或校验
三个数组都在 .rdata 数据段，不受花指令影响
提取三个数组，推导公式写脚本解出 flag
```

#### 二、分析过程

##### 2.1 运行看反应

输出

```
A small flower garden is waiting for the correct key.
flag> XXX
The flowers stay closed.
```

输入任意错误内容，输出 `The flowers stay closed.`

##### 2.2 DIE 查壳,定位主函数

32 位 Windows PE 控制台程序，无壳，体积只有 9KB

搜字符串 `flag> `，找到交叉引用在 `0x401144`，往上就是主函数
打印欢迎信息和 `flag> ` 提示
fgets 读取输入
strcspn 去掉换行符
调用 `sub_401000` 校验输入
校验成功打印 `The garden opens.`，失败打印 `The flowers stay closed.`

##### 2.3 花指令

进入校验函数 `sub_401000`，有大量花指令

```asm
call    $+5
add     [esp+1Ch+var_1C], 8
retn
```

call 压入返回地址  add 把栈上的返回地址加  ret 跳转到修改后的地址
对程序运行无影响，对 IDA 静态分析破坏栈平衡
导致函数截断,无法自动反编译

##### 2.4 手动反汇编

```c
bool sub_401000(char *str)
{
    int len = strlen(str);
    if (len != 0x1D)          // 长度必须是 29
        return false;

    char acc = 0;             // var_1
    for (int i = 0; i < 0x1D; i++)
    {
        int idx = (i * 7 + 3) % 0x19;              // 取模 25
        char c = byte_4021A0[i];                   // arr2偏移
        char v = byte_402180[idx];                 // arr1混淆
        v ^= str[c];                               // 与输入串异或
        v ^= byte_4021C0[i];                       // arr3异或
        acc |= v;                                  
        // 累积 OR,如果结果acc不是0,则input的某一步错误
    }
    return acc == 0;          // 全部为 0 才算通过
}
```
这里`ebx` 当循环计数器,0到29

```c
arr1[(7 * ebx + 3) % 25] ^ input[arr2[ebx] ] ^ arr3[ebx]  =  0
input[arr2[ebx] ] = arr1[(7 * ebx+3) % 25] ^ arr3[ebx]
```

花指令只在 `.text` 代码段里，三个关键数组在 `.rdata` 数据段

##### 2.7 提取三个数组  脚本解flag

```python
arr1 = [44, 177, 250, 64, 46, 209, 223, 59, 55, 31, 67, 86, 72, 173, 218, 231, 123, 74, 51, 62, 48, 18, 152, 212, 156]
arr2 = [12, 3, 28, 0, 18, 8, 5, 15, 1, 23, 10, 6, 20, 4, 16, 2, 27, 9, 13, 21, 7, 17, 14, 24, 11, 19, 22, 26, 25]
arr3 = [31, 23, 55, 219, 156, 224, 99, 148, 74, 74, 186, 225, 44, 69, 218, 114, 147, 216, 100, 101, 108, 115, 78, 180, 107, 112, 28, 35, 195]
#arr1是混淆,arr2是flag的位置打乱表,arr3是flag密文
flag = [0] * 29
for ebx in range(29):  #0到28
    edx = (7 * ebx + 3) % 25
    pos = arr2[ebx]
    flag[pos] = arr1[edx] ^ arr3[ebx]

print(bytes(flag).decode())
```

输出：

```
GUET{S0_M@ny_Junk_C0d3_1n_it}
```

回到程序里输 flag，程序输出 `The garden opens.`,验证通过

#### 三、最终 Flag

```
GUET{S0_M@ny_Junk_C0d3_1n_it}
```
