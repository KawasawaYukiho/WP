key = b"GUET2026"
cipher = bytes.fromhex("B78E7449DD89F0DE913C3F11B9E55ACFD858EEB2F989211D2C1A7D")

S = list(range(256))
j = 0
for i in range(256):
    j = (j + S[i] + key[i % 8]) % 256
    S[i], S[j] = S[j], S[i]

i = j = 0
result = []
for b in cipher:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    result.append(b ^ S[(S[i] + S[j]) % 256])

print(bytes(result).decode())
