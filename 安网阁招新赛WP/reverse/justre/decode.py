import base64

# 程序运行时实际使用的表（标准表经过 caesar_shift_table 变换后）
runtime_table = "HIJKLMNOPQRSTUVWXYZABCDEFGtuvwxyzabcdefghijklmnopqrs4567890123+/"
standard_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# 建立 runtime_table → standard_table 的映射
trans = str.maketrans(runtime_table, standard_table)

cipher = "yDw8FiGnFNYkG7q0ug9iFNmoxfezFfUoDiX="

# 1. 用运行时表映射回标准 Base64
std_b64 = cipher.translate(trans)
print("标准Base64:", std_b64)

# 2. 补位（密文长度已是4的倍数，不用补）
data = base64.b64decode(std_b64)
print("解码结果:", data)
print("hex:", data.hex())