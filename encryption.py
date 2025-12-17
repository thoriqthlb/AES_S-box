import secrets

def generate_key():
    return secrets.token_bytes(16)

def encrypt(plaintext, sbox, key):
    data = plaintext.encode()
    out = []
    for i,b in enumerate(data):
        out.append(sbox[b ^ key[i % len(key)]])
    return bytes(out)

def decrypt(ciphertext, sbox, key):
    inv = [0]*256
    for i,v in enumerate(sbox):
        inv[v] = i
    out = []
    for i,b in enumerate(ciphertext):
        out.append(inv[b] ^ key[i % len(key)])
    return bytes(out).decode(errors="ignore")
