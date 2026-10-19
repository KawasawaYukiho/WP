enc = bytes.fromhex("7821352D093A1B6C39011A3B2844200C2B024A335231706F5E002D1801174C00021C130E13")
key = b"H0w_t0_3ncrypt?"[::-1]
flag = bytes([enc[i] ^ key[i % 15] for i in range(37)])
print(flag.decode())
