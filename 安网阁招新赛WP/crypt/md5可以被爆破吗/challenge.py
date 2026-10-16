from hashlib import md5
from secret import flag

# 已知一个 flag 的格式为：
# MD5canbecra???? 
# 其中 ???? 是未知的 4 个字符，且这 4 个字符均为小写字母。
# 同时你还知道flag的完整md5值

print("known:", flag[:-4]) # MD5canbecra
print("md5:", md5(flag.encode()).hexdigest())# fa660823d358e52306a3f370c371b2a1