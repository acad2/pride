from utilities import xor_sum, rotate_left, rotate_right, slide, xor_subroutine, integer_to_bytes, bytes_to_words
    
def prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in range(len(data)):
        byte = data[index]
        key ^= byte                
        data[index] = rotate_left((byte + key + index) & mask, rotation_amount, bit_width)
        key ^= data[index]            
    return key
    
def prp8(data, key):
    return prp(data, key)
    
def prp64(data, key, mask=((2 ** 64) - 1)):            
    return prp(data, key, mask, 64 - 5, 64)        
    
def invert_prp64(data, key, mask=((2 ** 64) - 1)):
    return invert_prp(data, key, mask, 64 - 5, 64)
    
def test_prp64():
    data = list(bytearray(16))
    data[-8] = 1    
    data[:] = bytes_to_words(data, 8)    
    _data = data[:]
    
    key = prp64(data, xor_sum(data))
    invert_prp64(data, key)
    assert _data == data, (data, _data)
    
def prf(data, key, mask=255, rotation_amount=5, bit_width=8):
    new_key = 0
    for index in range(len(data)):        
        new_byte = rotate_left((data[index] + key + new_key + index) & mask, rotation_amount, bit_width)
        new_key ^= new_byte
        key ^= new_byte
        data[index] = new_byte
    return new_key
    
def test_prf():    
    def test_hash(data):
        output = bytearray(16)
        key = xor_sum(bytearray(data[:16]))
        for block in slide(bytearray(data), 16):
            prf(block, xor_sum(block))
            xor_subroutine(output, block)
        return bytes(data)
    from metrics import test_hash_function
    test_hash_function(test_hash)
    
    
def encrypt(data, key, rounds=1):     
    key = key[:]
    round_key = bytearray(16)
    key_xor = xor_sum(key)
    data_xor = xor_sum(data)
    for round in range(rounds):       
        key_xor = prp(key, key_xor) # generate key        
        round_key[:] = key[:] # maintain invertible keyschedule
                
        round_key_xor = prf(round_key, key_xor) # one way extraction: class 2B keyschedule
       # data_xor ^= round_key_xor
       # print "\nRound key:\n", round_key
       # print "Pre whitening:\n", data
        xor_subroutine(data, round_key) # pre-whitening                   
       # print "Applying prp:\n", data, data_xor
        print "Before prp:\n", data, data_xor
        data_xor = prp(data, data_xor ^ round_key_xor) # high diffusion prp     
        print "After prp:\n", data, data_xor
       # print "Post whitening:\n", data
        xor_subroutine(data, round_key) # post_whitening
        
def decrypt(data, key, rounds=1):
    round_keys = []
    key = key[:]
    round_key = bytearray(16)
    key_xor = xor_sum(key)
    data_xor = xor_sum(data)
    for round in range(rounds):
        key_xor = prp(key, key_xor)
        round_key[:] = key[:]
        round_key_xor = prf(round_key, key_xor)
        round_keys.append((round_key_xor, round_key[:]))
    print "\nDecrypting"    
    for round in reversed(range(rounds)):
        round_key_xor, round_key = round_keys[round]
       # print "\nRound key:\n", round_key
       # print "Removing post whitening\n: ", data
        xor_subroutine(data, round_key)
        print "Inverting prp:\n", data, data_xor
        data_xor = invert_prp(data, data_xor) 
        print "After inversion:\n", data, data_xor
    #    print "Removing pre whitening\n: ", data
        xor_subroutine(data, round_key)
        #print "    After: \n", data
       # data_xor ^= round_key_xor
        
def test_encrypt_decrypt():
    data = bytearray(16)
    plaintext = data[:]
    key = bytearray(16)
    rounds = 1
    
    encrypt(data, key, rounds)
    print "Ciphertext: "
    print data
    
    decrypt(data, key, rounds)
    assert data == plaintext, data
    
def invert_prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in reversed(range(len(data))):
        byte = data[index]
        key ^= byte        
        data[index] = ((mask + 1) + (rotate_right(byte, rotation_amount, bit_width) - key - index)) & mask
        key ^= data[index]
    return key
    
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
    
    
if __name__ == "__main__":
    #test_invert_prp()
    #test_prp_cycle_length()
    #test_prp_metrics()    
    #test_prp_s_box()
    #test_encrypt_decrypt()
    #test_prf()
    test_prp64()
    