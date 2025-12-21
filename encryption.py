import secrets

Nb, Nk, Nr = 4, 4, 10
RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]

# ================= KEY =================
def generate_key():
    return secrets.token_bytes(16)

# ================= GF(2^8) =================
def xtime(a):
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else (a << 1)

def gf_mul(a, b):
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        a = xtime(a)
        b >>= 1
    return r & 0xFF

# ================= KEY EXPANSION =================
def key_expansion(key, sbox):
    key = list(key)
    w = [key[i:i+4] for i in range(0,16,4)]
    for i in range(Nk, Nb*(Nr+1)):
        temp = w[i-1].copy()
        if i % Nk == 0:
            temp = temp[1:] + temp[:1]
            temp = [sbox[b] for b in temp]
            temp[0] ^= RCON[i//Nk - 1]
        w.append([w[i-Nk][j] ^ temp[j] for j in range(4)])
    return w

# ================= AES OPERATIONS =================
def add_round_key(state, w, r):
    for c in range(4):
        for r2 in range(4):
            state[r2][c] ^= w[r*4 + c][r2]

def sub_bytes(state, sbox):
    for r in range(4):
        for c in range(4):
            state[r][c] = sbox[state[r][c]]

def inv_sub_bytes(state, inv_sbox):
    for r in range(4):
        for c in range(4):
            state[r][c] = inv_sbox[state[r][c]]

def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]
    state[2] = state[2][2:] + state[2][:2]
    state[3] = state[3][3:] + state[3][:3]

def inv_shift_rows(state):
    state[1] = state[1][-1:] + state[1][:-1]
    state[2] = state[2][-2:] + state[2][:-2]
    state[3] = state[3][-3:] + state[3][:-3]

def mix_columns(state):
    for c in range(4):
        a = [state[r][c] for r in range(4)]
        t = a[0]^a[1]^a[2]^a[3]
        u = a[0]
        a[0] ^= t ^ gf_mul(a[0]^a[1],2)
        a[1] ^= t ^ gf_mul(a[1]^a[2],2)
        a[2] ^= t ^ gf_mul(a[2]^a[3],2)
        a[3] ^= t ^ gf_mul(a[3]^u,2)
        for r in range(4):
            state[r][c] = a[r]

def inv_mix_columns(state):
    for c in range(4):
        a = [state[r][c] for r in range(4)]
        col = [
            gf_mul(a[0],0x0E)^gf_mul(a[1],0x0B)^gf_mul(a[2],0x0D)^gf_mul(a[3],0x09),
            gf_mul(a[0],0x09)^gf_mul(a[1],0x0E)^gf_mul(a[2],0x0B)^gf_mul(a[3],0x0D),
            gf_mul(a[0],0x0D)^gf_mul(a[1],0x09)^gf_mul(a[2],0x0E)^gf_mul(a[3],0x0B),
            gf_mul(a[0],0x0B)^gf_mul(a[1],0x0D)^gf_mul(a[2],0x09)^gf_mul(a[3],0x0E)
        ]
        for r in range(4):
            state[r][c] = col[r]

# ================= TRACE FORMAT =================
def fmt(state):
    return [[f"{state[r][c]:02X}" for c in range(4)] for r in range(4)]

# ================= ENCRYPT + TRACE =================
def aes_encrypt_trace(pt, key, sbox):
    trace = []
    state = [[pt[r+4*c] for c in range(4)] for r in range(4)]
    w = key_expansion(key, sbox)

    r0 = {"round":0,"Start":fmt(state)}
    add_round_key(state,w,0)
    r0["AddRoundKey"]=fmt(state)
    trace.append(r0)

    for rnd in range(1, Nr):
        ri={"round":rnd,"Start":fmt(state)}
        sub_bytes(state,sbox); ri["SubBytes"]=fmt(state)
        shift_rows(state); ri["ShiftRows"]=fmt(state)
        mix_columns(state); ri["MixColumns"]=fmt(state)
        add_round_key(state,w,rnd); ri["AddRoundKey"]=fmt(state)
        trace.append(ri)

    r10={"round":Nr,"Start":fmt(state)}
    sub_bytes(state,sbox); r10["SubBytes"]=fmt(state)
    shift_rows(state); r10["ShiftRows"]=fmt(state)
    add_round_key(state,w,Nr); r10["AddRoundKey"]=fmt(state)
    trace.append(r10)

    return bytes(state[r][c] for c in range(4) for r in range(4)), trace

# ================= DECRYPT + TRACE =================
def aes_decrypt_trace(ct, key, sbox):
    inv_sbox = [0]*256
    for i,v in enumerate(sbox):
        inv_sbox[v]=i

    trace=[]
    state=[[ct[r+4*c] for c in range(4)] for r in range(4)]
    w=key_expansion(key,sbox)

    r10={"round":10,"Start":fmt(state)}
    add_round_key(state,w,10)
    r10["AddRoundKey"]=fmt(state)
    trace.append(r10)

    for rnd in range(9,0,-1):
        ri={"round":rnd,"Start":fmt(state)}
        inv_shift_rows(state); ri["InvShiftRows"]=fmt(state)
        inv_sub_bytes(state,inv_sbox); ri["InvSubBytes"]=fmt(state)
        add_round_key(state,w,rnd); ri["AddRoundKey"]=fmt(state)
        inv_mix_columns(state); ri["InvMixColumns"]=fmt(state)
        trace.append(ri)

    r0={"round":0,"Start":fmt(state)}
    inv_shift_rows(state); r0["InvShiftRows"]=fmt(state)
    inv_sub_bytes(state,inv_sbox); r0["InvSubBytes"]=fmt(state)
    add_round_key(state,w,0); r0["AddRoundKey"]=fmt(state)
    trace.append(r0)

    return bytes(state[r][c] for c in range(4) for r in range(4)), trace
