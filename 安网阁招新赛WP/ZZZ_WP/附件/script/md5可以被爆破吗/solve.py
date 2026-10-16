from hashlib import md5
from itertools import product
import string

target = "fa660823d358e52306a3f370c371b2a1"
prefix = "MD5canbecra"

for combo in product(string.ascii_lowercase, repeat=4):
    suffix = ''.join(combo)
    flag = prefix + suffix
    if md5(flag.encode()).hexdigest() == target:
        print("flag:", flag)
        break