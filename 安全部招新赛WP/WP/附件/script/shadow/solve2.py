import hashlib  # 哈希库

# 已知的盐值，和口令拼接后再做哈希
salt = "0f9fd014"

#暴力计算求哪个 6 位数字口令能算出这个hash
ture_hash = "d0b53d421c50a45a5ef735b4725c2c9a123862779c50e95d284c476bdf469b29"

# 枚举所有可能的 6 位数字口令
for i in range(1000000):
    password = str(i).zfill(6)  # zero-fill,在字符串的左边补零到6位

    # salt与password进行拼接转字节串，然后计算 SHA-256，转成十六进制字符串
    hash = hashlib.sha256((salt + password).encode()).hexdigest()

    # 哈希和目标哈希一致，则输出口令
    if hash == ture_hash:
        print(f"口令: {password}")
        break