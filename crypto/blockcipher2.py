from utilities import xor_sum, rotate_left, rotate_right, slide, xor_subroutine, integer_to_bytes, bytes_to_words, words_to_bytes
    
def prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in range(len(data)):
        byte = data[index]
        key ^= byte                
        data[index] = rotate_left((byte + key + index) & mask, rotation_amount, bit_width)
        key ^= data[index]            
    return key
        
def prf(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in range(len(data)):        
        new_byte = rotate_left((data[index] + key + index) & mask, rotation_amount, bit_width)    
        key ^= new_byte
        data[index] = new_byte            
            
def xor_subroutine2(data, key):
    data_xor = 0
    for index, byte in enumerate(key):
        data[index] ^= byte
        data_xor ^= data[index]
    return data_xor
    
def encrypt(data, key, rounds=1, size=(8, 255, 5)):     
    key = key[:]
    round_key = list(bytearray(len(key)))
    key_xor = xor_sum(key)
    data_xor = xor_sum(data)
    bit_width, mask, rotation_amount = size    
    
    for round in range(rounds):       
        key_xor = prp(key, key_xor, mask, rotation_amount, bit_width) # generate key        
        round_key[:] = key[:] # maintain invertible keyschedule
                
        prf(round_key, key_xor, mask, rotation_amount, bit_width) # one way extraction: class 2B keyschedule

        data_xor = xor_subroutine2(data, round_key) # pre-whitening                   
        data_xor = prp(data, data_xor, mask, rotation_amount, bit_width) # high diffusion prp     
        data_xor = xor_subroutine2(data, round_key) # post_whitening
        
def invert_prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in reversed(range(len(data))):
        byte = data[index]
        key ^= byte        
        data[index] = ((mask + 1) + (rotate_right(byte, rotation_amount, bit_width) - key - index)) & mask
        key ^= data[index]
    return key
    
def decrypt(data, key, rounds=1, size=(8, 255, 5)):
    round_keys = []
    key = key[:]
    round_key = list(bytearray(len(key)))
    key_xor = xor_sum(key)
    data_xor = xor_sum(data)
    bit_width, mask, rotation_amount = size
    
    for round in range(rounds):
        key_xor = prp(key, key_xor, mask, rotation_amount, bit_width)
        round_key[:] = key[:]
        prf(round_key, key_xor, mask, rotation_amount, bit_width)
        round_keys.append(round_key[:])
      
    for round in reversed(range(rounds)):
        round_key = round_keys[round]

        data_xor = xor_subroutine2(data, round_key)        
        data_xor = invert_prp(data, data_xor, mask, rotation_amount, bit_width) 
        data_xor = xor_subroutine2(data, round_key)               
        
def test_encrypt_decrypt():
    data = bytearray(16)    
    key = bytearray(16)
    rounds = 16
    byte_size = 4
    bit_size = byte_size * 8
    size = (bit_size, ((2 ** bit_size) - 1), bit_size - 5)
    data = bytes_to_words(data, byte_size)
    key = bytes_to_words(key, byte_size)
    plaintext = data[:]
    
    encrypt(data, key, rounds, size)
    
    print ''.join(bytes(integer_to_bytes(block, byte_size)) for block in data)
    
    decrypt(data, key, rounds, size)
    assert data == plaintext, (data, plaintext)
        
def test_invert_prp():
    data = bytearray("Testing!")
    data_xor = prp(data, xor_sum(data))
    invert_prp(data, data_xor)
    assert data == "Testing!", data
    
def test_prp_cycle_length():
    from utilities import find_cycle_length_subroutine
    print len(find_cycle_length_subroutine(prp, bytearray("\x00\x01\x00"), 3))
    
def test_prp_metrics():
    from utilities import slide, xor_subroutine
    def test_hash(data):
        output = bytearray(16)        
        for block in slide(bytearray(data), 16):            
            prp(block, xor_sum(block))
            xor_subroutine(output, block)
        return bytes(output)
        
    from metrics import test_hash_function
    test_hash_function(test_hash)
        
def test_prp_s_box():  
    import collections
    
    s_box = collections.defaultdict(bytearray)
    rounds = 4
    for ending in range(256):
        data = bytearray(16)
        data[-1] = ending
        for round in range(rounds):            
            prp(data, xor_sum(data))                  
            s_box[round].append(data[-2])
    
    from differential import find_best_differential
    from linear import calculate_linearity

    for round in range(rounds):
        _s_box = s_box[round]
        print "Best differential after {} rounds: ".format(round + 1), find_best_differential(_s_box)
        print "Linearity after {} rounds: ".format(round + 1), calculate_linearity(_s_box)
    
def test_prf():    
    def test_hash(data):
        output = bytearray(16)        
        key = xor_sum(bytearray(data[:16]))
        for block in slide(bytearray(data), 16):            
            prf(block, xor_sum(block))            
            xor_subroutine(output, block)        
        return bytes(output)
        
    from metrics import test_hash_function
    test_hash_function(test_hash)
    
if __name__ == "__main__":
    #test_invert_prp()
    #test_prp_cycle_length()
    #test_prp_metrics()    
    #test_prp_s_box()
    test_encrypt_decrypt()
    #test_prf()    
    