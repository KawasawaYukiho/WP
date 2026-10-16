#include <stdint.h>
#include <string.h>

// 数据段
uint8_t byte_404000[19] = {
    0x66, 0x6c, 0x61, 0x67, 0x7b, 0x55, 0x6e, 0x64, 0x65, 0x72,
    0x73, 0x74, 0x61, 0x6e, 0x64, 0x69, 0x6e, 0x67, 0x5f
};

uint8_t byte_404020[31] = {
    0x23, 0x31, 0x31, 0x27, 0x2f, 0x20, 0x2e, 0x3b, 0x1d, 0x2e,
    0x23, 0x2c, 0x25, 0x37, 0x23, 0x25, 0x27, 0x1d, 0x2b, 0x31,
    0x1d, 0x2b, 0x2f, 0x32, 0x2d, 0x30, 0x36, 0x23, 0x2c, 0x36,
    0x3f
};

uint8_t byte_404030[9] = {
    0x63, 0x6f, 0x72, 0x72, 0x65, 0x63, 0x74, 0x21, 0x7d
};

char buf[64] = {0};

void start(void)
{
    int i;
    int idx = 0;                 // 对应 rdi 的偏移

    // ---- 第 1 段：复制 19 字节 ----
    for (i = 0; i < 19; i++) {
        buf[idx++] = byte_404000[i];
    }

    // ---- 第 2 段：恒真判断（编译后等价于无条件跳转到 XOR 分支）----
    int eax = 0x2a + 0x16;       // 42 + 22 = 64
    if (eax != 0x40) goto loc_401080;

    int ebx = 0x10 << 2;         // 16 << 2 = 64
    if (eax != ebx) goto loc_401080;

    int ecx = 0x39 - 0x20;       // 57 - 32 = 25
    if (ecx > 0x18) {            // 25 > 24 成立
        goto loc_401050;
    }
    goto loc_401080;

loc_401050:
    // ---- 第 3 段：XOR 解密 31 字节 ----
    for (i = 0; i < 31; i++) {
        buf[idx++] = byte_404020[i] ^ 0x42;
    }
    goto loc_4010b0;

loc_401080:
    // ---- 干扰分支：复制 9 字节（本程序不会执行）----
    for (i = 0; i < 9; i++) {
        buf[idx++] = byte_404030[i];
    }
    // 落到 loc_4010b0

loc_4010b0:
    buf[idx] = '\0';             // 字符串结束符
    return;
}