import base64

ciphertext = "ccwyjLHxxxcec1kkkxfncyyuj1Dxxxcrc1kjkKpbcywujLDxxxmec1kjkxfbccwyjLDcxtmrc1kkkKfbccwyj1Dxxxcec1kkkKpncyyujLDxxxcrvykkkxpbccwujLHcxtcrvykkkKfb"

# 自定义 Base64 表 -> 标准表
custom = "qwertyuiopasdfghjklzxcvbnmABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/"
std    = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
idx = {c: i for i, c in enumerate(custom)}

# 第1层：Base64 换表解码
s = ''.join(std[idx[c]] for c in ciphertext)
layer1 = base64.b64decode(s).decode()

# 第2层：凯撒 -7
layer2 = ''.join(chr((ord(c)-65-7)%26+65) for c in layer1)

# 第3层：维吉尼亚解密（MIXUP）
key = [ord(k)-65 for k in "MIXUP"]
layer3 = ''.join(chr((ord(c)-65-key[i%5])%26+65) for i, c in enumerate(layer2))

# 第4层：培根解码
bacon = {'AAAAA':'a','AAAAB':'b','AAABA':'c','AAABB':'d','AABAA':'e','AABAB':'f',
         'AABBA':'g','AABBB':'h','ABAAA':'i','ABAAB':'k','ABABA':'l','ABABB':'m',
         'ABBAA':'n','ABBAB':'o','ABBBA':'p','ABBBB':'q','BAAAA':'r','BAAAB':'s',
         'BAABA':'t','BAABB':'u','BABAA':'w','BABAB':'x','BABBA':'y','BABBB':'z'}
flag = ''.join(bacon[layer3[i:i+5]] for i in range(0, len(layer3), 5))
print(f"flag{{{flag}}}")