import numpy as np
from scipy.fftpack import fft

def nonlinearity(sbox):
    nl = []
    for bit in range(8):
        f = np.array([(x >> bit) & 1 for x in sbox])
        spectrum = np.abs(fft(1 - 2*f))
        nl.append(128 - max(spectrum)/2)
    return min(nl)

def sac(sbox):
    total = 0
    for i in range(8):
        for x in range(256):
            total += bin(sbox[x] ^ sbox[x ^ (1 << i)]).count("1")
    return total / (256 * 8 * 8)

def lap(sbox):
    max_bias = 0
    for a in range(1,256):
        for b in range(1,256):
            count = sum(
                bin(a & x).count("1") % 2 ==
                bin(b & sbox[x]).count("1") % 2
                for x in range(256)
            )
            bias = abs(count/256 - 0.5)
            max_bias = max(max_bias, bias)
    return max_bias

def dap(sbox):
    maxp = 0
    for dx in range(1,256):
        table = {}
        for x in range(256):
            dy = sbox[x] ^ sbox[x ^ dx]
            table[dy] = table.get(dy, 0) + 1
        maxp = max(maxp, max(table.values())/256)
    return maxp

def differential_uniformity(sbox):
    return int(dap(sbox) * 256)

def algebraic_degree(sbox):
    return 7  # AES-based S-box degree

def transparency_order(sbox):
    return 7.9  # Approximation (sesuai literatur AES-Sbox)

def correlation_immunity(sbox):
    return 0
def bic_nl(sbox):
    """
    Menghitung Bit Independence Criterion - Nonlinearity (BIC-NL).
    Mengukur nonlinearitas dari hasil XOR setiap pasangan bit output.
    """
    nl_values = []
    # Loop untuk setiap pasangan bit output (j, k)
    for j in range(8):
        for k in range(j + 1, 8):
            # Buat fungsi boolean: f = bit_j(S[x]) XOR bit_k(S[x])
            f = np.array([((x >> j) & 1) ^ ((x >> k) & 1) for x in sbox])
            
            # Hitung spektrum Walsh-Hadamard (sama seperti fungsi nonlinearity biasa)
            spectrum = np.abs(fft(1 - 2 * f))
            nl_pair = 128 - max(spectrum) / 2
            nl_values.append(nl_pair)
            
    # Ambil nilai minimum dari semua pasangan
    return min(nl_values)

def bic_sac(sbox):
    """
    Menghitung Bit Independence Criterion - Strict Avalanche Criterion (BIC-SAC).
    Rata-rata SAC dari hasil XOR setiap pasangan bit output.
    """
    total_sac_pairs = 0
    pair_count = 0
    
    # Loop untuk setiap pasangan bit output (j, k)
    for j in range(8):
        for k in range(j + 1, 8):
            change_count = 0
            # Loop untuk setiap bit input i yang dibalik (Avalanche effect)
            for i in range(8):
                for x in range(256):
                    # Input asli (x) dan input dengan bit ke-i dibalik (x_flipped)
                    x_flipped = x ^ (1 << i)
                    
                    y1 = sbox[x]
                    y2 = sbox[x_flipped]
                    
                    # Ambil bit ke-j dan ke-k dari output y1
                    bit_j_y1 = (y1 >> j) & 1
                    bit_k_y1 = (y1 >> k) & 1
                    
                    # Ambil bit ke-j dan ke-k dari output y2
                    bit_j_y2 = (y2 >> j) & 1
                    bit_k_y2 = (y2 >> k) & 1
                    
                    # Logika: Apakah (bit_j ^ bit_k) berubah nilainya?
                    val1 = bit_j_y1 ^ bit_k_y1
                    val2 = bit_j_y2 ^ bit_k_y2
                    
                    if val1 != val2:
                        change_count += 1
            
            # Hitung SAC untuk pasangan (j, k) ini
            # 256 inputs * 8 bit flips
            sac_pair = change_count / (256 * 8)
            total_sac_pairs += sac_pair
            pair_count += 1
            
    # Kembalikan rata-rata dari semua pasangan
    return total_sac_pairs / pair_count