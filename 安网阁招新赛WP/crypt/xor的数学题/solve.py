from Crypto.Util.number import long_to_bytes

enc = b'\x65\xa9\x8a\x29\xd4\xef\xcf\x26\xa1\x41\x94\xab\x29\xd6\x45\xd1\xe7\x91\xfa\xdc\x01\xaa\x7c\x8d\x61\x34\x9e\xf9\xa6\x5a'

n = 10**6
key = 2 * pow(3, n - 1) - 1      # 注意是 n-1，不是 n
key_bytes = long_to_bytes(key)

flag = bytes([x ^ y for x, y in zip(enc, key_bytes)])
print(flag)