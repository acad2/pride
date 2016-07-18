def rotate_left(x, r, bit_width=8, _mask=dict((bit_width, ((2 ** bit_width) - 1)) for bit_width in (8, 16, 32, 64, 128))):  
    r %= bit_width
    return ((x << r) | (x >> (bit_width - r))) & _mask[bit_width]

def rotate_right(x, r, bit_width=8, _mask=dict((bit_width, ((2 ** bit_width) - 1)) for bit_width in (8, 16, 32, 64, 128))): 
    r %= bit_width
    return ((x >> r) | (x << (bit_width - r))) & _mask[bit_width]
    
def round_function(left, right, key, index, mask=255, rotation_amount=5, bit_width=8):
    key ^= right                 
    right = rotate_left((right + key + index) & mask, rotation_amount, bit_width)                
    key ^= right
    
    key ^= left        
    left = (left + (right >> (bit_width / 2))) & mask                
    left ^= rotate_left(right, (index % bit_width) ^ rotation_amount)                    
    key ^= left
    return left, right, key    

def shuffle_bytes(_state, temp=list(range(16))):          
    temp[7] = _state[0] 
    temp[12] = _state[1]
    temp[14] = _state[2]
    temp[9] = _state[3]
    temp[2] = _state[4]
    temp[1] = _state[5]
    temp[5] = _state[6]
    temp[15] = _state[7]
    temp[11] = _state[8]
    temp[6] = _state[9]
    temp[13] = _state[10]
    temp[0] = _state[11]
    temp[4] = _state[12]
    temp[8] = _state[13]
    temp[10] = _state[14]
    temp[3] = _state[15]
            
    _state[:] = temp[:]
    
def prp(data, data_xor, data_size=16, turn_into_prf=False):
    shuffle_bytes(data)
    
    for index in range(data_size):
        left, right = data[index - 1], data[index]        
        if turn_into_prf:
            data_xor ^= right # remove so that the first key ^ right inside round_function puts it back into the sum
        left, right, data_xor = round_function(left, right, data_xor, index)    
        data[index - 1], data[index] = left, right   
        
    left, right = data[15], data[0]
    if turn_into_prf:
        data_xor ^= right 
    left, right, data_xor = round_function(left, right, data_xor, 0)
    data[15], data[0] = left, right
    return data_xor
           
def prf(data, data_xor, data_size=16):
    prp(data, data_xor, data_size, turn_into_prf=True)
    
def xor_sum(data):
    result = 0
    for byte in data:
        result ^= byte
    return result
    
def xor_subroutine(data, key):
    for index, byte in enumerate(key):
        data[index] ^= byte
        
def generate_round_key(key, round):
    key_xor_sum = prp(key, xor_sum(key))
    round_key = key[:]
    
    prf(round_key, key_xor_sum)
    return round_key
    
def encrypt(data, key, rounds=1, bit_width=8):
    key = key[:]
    round_keys = [generate_round_key(key, round) for round in range(rounds)]
    
    # less pythonic, but translates easier to C
    # round_keys = []
    # key_xor_sum = xor_sum(key)
    # for round in range(rounds):        
    #     round_keys.append(generate_round_key(key, round))
        
    for round_key in round_keys:
        xor_subroutine(data, round_key)
        prp(data, xor_sum(data))
        xor_subroutine(data, round_key)
   
def invert_round(left, right, key, index, mask=255, rotation_amount=5, bit_width=8):
    key ^= left    
    left ^= rotate_left(right, (index % bit_width) ^ rotation_amount)         
    left = (256 + (left - (right >> bit_width / 2))) & mask
    key ^= left;
    
    key ^= right        
    right = (256 + (rotate_right(right, rotation_amount, bit_width) - key - index)) & mask 
    key ^= right
    return left, right, key
    
def invert_shuffle_bytes(state, temp=list(range(16))):       
    temp[11] = state[0]
    temp[5] = state[1]
    temp[4] = state[2]
    temp[15] = state[3]
    temp[12] = state[4]
    temp[6] = state[5]
    temp[9] = state[6]
    temp[0] = state[7]
    temp[13] = state[8]
    temp[3] = state[9]
    temp[14] = state[10]
    temp[8] = state[11]
    temp[1] = state[12]
    temp[10] = state[13]
    temp[2] = state[14]
    temp[7] = state[15]
    
    state[:] = temp[:]
    
def invert_prp(data, data_xor, data_size=16):
    left, right = data[15], data[0]
    left, right, data_xor = invert_round(left, right, data_xor, 0)
    data[15], data[0] = left, right
    
    for index in reversed(range(data_size)):
        left, right = data[index - 1], data[index]
        left, right, data_xor = invert_round(left, right, data_xor, index)
        data[index - 1], data[index] = left, right
        
    invert_shuffle_bytes(data)
    return data_xor
    
def decrypt(data, key, rounds=1, bit_width=8):
    key = key[:]
    round_keys = reversed([generate_round_key(key, round) for round in range(rounds)])
    
    for round_key in round_keys:
        xor_subroutine(data, round_key)
        invert_prp(data, xor_sum(data))
        xor_subroutine(data, round_key)
    
def test_encrypt_decrypt():
    plaintext = bytearray("Testing!" * 2)
    key = bytearray("\x00" * 16)
    ciphertext = plaintext[:]
    encrypt(ciphertext, key)
    
    print "Ciphertext: ", ciphertext
    decrypt(ciphertext, key)
    assert ciphertext == plaintext, (ciphertext, plaintext)   
        

try:
    import pride.crypto
except ImportError:
    pass
else:
    class Test_Cipher(pride.crypto.Cipher):
                
                
        def __init__(self, *args):
            super(Test_Cipher, self).__init__(*args)
            self.blocksize = 16
            
        def encrypt_block(self, data, key, tag=None, tweak=None):        
            encrypt(data, key)    
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    try:
        Test_Cipher.test_metrics("\x00" * 16, "\x00" * 16)
    except NameError:
        pass
        
    