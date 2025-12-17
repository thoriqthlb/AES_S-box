import numpy as np

# AES irreducible polynomial x^8 + x^4 + x^3 + x + 1
IRRED_POLY = 0x11B
CAES = np.array([1,1,0,0,0,1,1,0], dtype=int)

AFFINE_MATRICES = {
    "K4": [
        "00000111","10000011","11000001","11100000",
        "01110000","00111000","00011100","00001111"
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

def gf_inverse(a):
    if a == 0:
        return 0
    for i in range(1,256):
        if gf_mul(a, i) == 1:
            return i

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

def affine_transform(x, matrix):
    bits = np.array(list(map(int, f"{x:08b}")))
    A = np.array([list(map(int, row)) for row in matrix])
    return np.mod(A @ bits + CAES, 2)

def generate_sbox(affine_name):
    matrix = AFFINE_MATRICES[affine_name]
    sbox = []
    for x in range(256):
        inv = gf_inverse(x)
        bits = affine_transform(inv, matrix)
        sbox.append(int("".join(map(str,bits)),2))
    return sbox
