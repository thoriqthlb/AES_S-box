import numpy as np

# AES irreducible polynomial x^8 + x^4 + x^3 + x + 1
IRRED_POLY = 0x11B

# CAES = 0x63 (99 desimal). Dalam urutan LSB-first [b0, b1, b2, b3, b4, b5, b6, b7]
# 0x63 adalah 01100011 biner, jika dibalik (LSB di index 0) menjadi:
CAES = np.array([1, 1, 0, 0, 0, 1, 1, 0], dtype=int)

AFFINE_MATRICES = {
    "K4": [
        "00000111","10000011","11000001","11100000",
        "01110000","00111000","00011100","00001110"
    ],
    "K44": [
        "01010111","10101011","11010101","11101010",
        "01110101","10111010","01011101","10101110"
    ],
    "K81": [
        "10100001","11010000","01101000","00110100",
        "00011010","00001101","10000110","01000011"
    ],
    "K111": [
        "11011100","01101110","00110111","10011011",
        "11001101","11100110","01110011","10111001"
    ],
    "K128": [
        "11111110","01111111","10111111","11011111",
        "11101111","11110111","11111011","11111101"
    ]
}

def gf_mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a <<= 1
        if hi:
            a ^= IRRED_POLY
        b >>= 1
    return p & 0xFF

def gf_inverse(a):
    if a == 0:
        return 0
    # Mencari invers perkalian dalam GF(2^8)
    for i in range(1, 256):
        if gf_mul(a, i) == 1:
            return i
    return 0

def affine_transform(x, matrix_rows):
    # Ubah integer ke vektor bit LSB-first [b0, b1, ..., b7]
    bits = np.array([(x >> i) & 1 for i in range(8)], dtype=int)
    
    # Matriks A dibentuk dari baris yang disediakan (string ke list of int)
    A = np.array([list(map(int, row)) for row in matrix_rows])
    
    # Operasi matriks: Y = (A * X + C) mod 2
    new_bits = np.mod(A @ bits + CAES, 2)
    
    # Kembalikan vektor bit ke bentuk integer (LSB-first)
    res = 0
    for i, bit in enumerate(new_bits):
        if bit:
            res |= (1 << i)
    return res

def generate_sbox(affine_name):
    if affine_name not in AFFINE_MATRICES:
        return None
    
    matrix = AFFINE_MATRICES[affine_name]
    sbox = []
    for x in range(256):
        inv = gf_inverse(x)
        val = affine_transform(inv, matrix)
        sbox.append(val)
    return sbox

# Contoh cara mencetak dalam format tabel 16x16
def print_sbox(sbox):
    for i in range(0, 256, 16):
        print(" ".join(f"{x:3}" for x in sbox[i:i+16]))

if __name__ == "__main__":
    # Uji coba menghasilkan S-box K4
    sbox_k4 = generate_sbox("K4")
    print("S-box K4 (Table 4):")
    print_sbox(sbox_k4)