def rotate_left(T, amount):
    binary = format(T, 'b').zfill(8)
    return binary[amount:] + binary[:amount]
    
def S_function(x, y, delta):
    T = (x + y + delta) % 256
    return rotate_left(T, 2)
    
def fk_function(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    fkt = a1 ^ a0
    fk2 = a2 ^ a3
    fk1 = S_function(fkt, fk2 ^ b0, 1)
    fk2 = S_function(fk2, fk1 ^ b1, 0)
    fk0 = S_function(a0, fk1 ^ b2, 0)
    fk3 = S_function(a3, fk2 ^ b3, 1)
    return ''.join((fk0, fk1, fk2, fk3))
    
def f_function(a, b):
    f1 = a[1] ^ b[0] ^ a[0]
    f2 = a[2] ^ b[1] ^ a[3]
    f1 = S_function(f1, f2, 1)
    f2 = S_function(f2, f1, 0)
    f0 = S_function(a[0], f1, 0)
    f3 = S_function(a[3], f2, 1)
    return ''.join((f0, f1, f2, f3))
    
def key_processing(key):
    half_size = len(key) / 2
    a, b = key[:half_size], key[half_size:]
    K = [a[0] + b[0]]
    D = ["\x00" * 4]
    for r in range(1, 8):
        index = r - 1
        for i in range(0, 15):
            D[r] = a[index]
            a[r] = b[index]
            b[r] = fk_function(a[index], b[index] ^ d[index])
            #K[2 * index] = (b[r ** 0] + b[r ** 1])
            #K[(2 *index) + 1] = (b[r ** 2] + b[r ** 3])
            #yield K[2 * index]
            #yield K[(2 * index) + 1]
            K.append(b[r][0] + b[r][1])
            K.append(b[r][2] + b[r][3])
            
def encrypt(P, key):
    half_size = len(P) / 2
    keys = key_processing(key)
    null = "\x00" * 4
    P = P ^ ''.join(keys[8], keys[9], keys[10], keys[11])
    P = P ^ (null, P[:half_size])
    
    L, R = [P[:half_size]], [P[half_size:]]
    for r in range(1, 8):
        R[r] = L[r - 1] ^ f_function(R[r - 1], K[r - 1])
        L[r] = R[r - 1]
    _C = (R[8] + L[8]) ^ (null, R[8])
    R[8] = _C[:half_size]
    L[8] = _C[half_size:]
    _C = (R[8] + L[8]) ^ (K[12], K[13], K[14], K[15])
    R[8] = _C[:half_size]
    L[8] = _C[half_size:]
    return R[8] + L[8]
    
def decrypt(ciphertext, key):
    half_size = len(ciphertext) / 2
    K = key_processing(key)
    null = "\x00" * 4
    R8 = ciphertext[:half_size]
    L8 = ciphertext[half_size:]
    _C = (R8 + L8) ^ (K[12], K[13], K[14], K[15])
    R8 = _C[:half_size]
    L8 = _C[half_size:]
    _C = (R8 + L8) ^ (null + R8)
    
    for r in (8, 7, 6, 5, 4, 3, 2, 1):
        