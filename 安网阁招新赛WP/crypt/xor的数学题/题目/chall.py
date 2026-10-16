from Crypto.Util.number import long_to_bytes

flag = b'flag{???}'


def gen_key(base, n):
    a = [base]
    for _ in range(n - 1):
        new_val = 3 * a[-1] + 2
        a.append(new_val)
    return a[-1]


n = 10**6
key = gen_key(1, n)
enc = bytes([x ^ y for x, y in zip(flag, long_to_bytes(key))])
# enc = b'\x65\xa9\x8a\x29\xd4\xef\xcf\x26\xa1\x41\x94\xab\x29\xd6\x45\xd1\xe7\x91\xfa\xdc\x01\xaa\x7c\x8d\x61\x34\x9e\xf9\xa6\x5a'
