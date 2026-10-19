#来自kongbeiqie.py
flag = ''
encode = 'YVYh]\x07@h\x0ehRwJVD\x07]s\x03D__ELzhY\x06_TP'
table = (19, 14, 10, 24, 27, 6, 5, 12, 11, 15, 9, 26, 30, 22, 16, 28,
         1, 13, 18, 2, 17, 21, 29, 4, 25, 7, 8, 23, 0, 3, 20)
XOR_KEY = 55

def enc(input):
    tmp = ''
    for i in range(len(input)):
        tmp = tmp + chr(ord(input[table[i]]) ^ XOR_KEY)
    return tmp

# enc(flag) == encode  => 
# flag[table[i]] = ord(encode[i]) ^ XOR_KEY
ans = [''] * 31
for i in range(31):
    ans[table[i]] = chr(ord(encode[i]) ^ XOR_KEY)
flag = ''.join(ans)
print(flag)
print(enc(flag) == encode)    # 校验结果是否正确
