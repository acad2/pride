import itertools

from utilities import cast, rotate, slide 
        
#def permutation(input_data, key, mode="forward"):    
#    key = bytearray(key)
#    if mode == "forward":
#        index_function = lambda index: (1 + index) * 8        
#    else:
#        assert mode == "invert"
#        data_size = len(input_data)
#        index_function = lambda index: (data_size - index) * 8
#        key = [-number for number in reversed(key)]
#        
#    output = cast(bytes(input_data), "binary")
#    key_material = itertools.cycle(key)
#    key_byte = lambda: next(key_material)  
# 
#    for index, byte in enumerate(input_data):
#        _key_byte = key_byte()        
#        output = rotate(output[:index_function(index)], _key_byte) + output[index_function(index):]
#    return cast(output, "bytes")
              
def substitution(data, key):      
    modifier = sum(key)
    for index, byte in enumerate(data):                
        data[index] ^= pow(251, modifier ^ sum(data[:index]) ^ sum(data[index + 1:]) ^ key[index], 257) % 256      
 
# data_i = data_i XOR S(k_m XOR k_i XOR data1 XOR data2)
#1 = 0 XOR 1 = S(k_m XOR k_i XOR data1 XOR data2) = k_m XOR k_i XOR data1 XOR data2

def apply_round(data, key):        
    substitution(data, key)
    substitution(data, key)
          
def crypt_block(data_block, round_keys):  
    for round_key in round_keys:  
        apply_round(data_block, round_key)                    
            
def generate_round_keys(key, rounds):
    round_keys = [key[:]]
    round_key = key   
    for round in range(rounds):
        apply_round(round_key, key)   
        round_keys.append(round_key[:])
    return round_keys
    
def cipher(data, key, iv, rounds=1, mode="encrypt",
           mode_of_operation=lambda input_block, output_block, key, iv: (input_block, output_block, key, iv)):
    output = ''
    block_size = len(key)
    key = bytearray(key)
    round_keys = generate_round_keys(key, rounds)
    if mode == "decrypt":
        round_keys = [bytearray(reversed(round_key)) for round_key in reversed(round_keys)]
        data = reversed(data)
                
    for block in slide(bytearray(data), block_size):
        crypt_block(block, round_keys)
        output += bytes(block)
        block, output, key, iv = mode_of_operation(block, output, key, iv)
    return output
    
def encrypt(data, key, iv, rounds=1, mode_of_operation=lambda input_block, output_block, key, iv: (input_block, output_block, key, iv)):
    return cipher(data, key, iv, rounds, mode_of_operation)

def decrypt(ciphertext, key, iv, rounds=1, mode_of_operation=lambda input_block, output_block, key, iv: (input_block, output_block, key, iv)):
    return cipher(ciphertext, key, iv, rounds, "decrypt", mode_of_operation)
                            
def test_block_cipher():
    data = (("\x00" * 15) + "\x00")
    iv = key = "0123456789ABCDEF"    
    #assert len(data) == len(key), (len(data), len(key))
    ciphertext = encrypt(data, key, iv)
    _data = decrypt(ciphertext, key, iv)
    print ciphertext
    print
    print _data
    assert data == _data
    
    #for x in xrange(256):
    #    data = data[:15] + chr(x)
    #    print block_cipher_encrypt(data, key)
    
def test_substitution():
    data = "test data"
    key = "Test key "
    _data = substitution(data, key)    
   # print _data   
    __data = ''.join(reversed(substitution(''.join(reversed(_data)), ''.join(reversed(key)))))
   # print __data
    
def test_permutation():
    data = "test data"
    key = bytearray("Test key ")
    _data = permutation(data, key)
    __data = permutation(_data, key, "invert")
    #print _data
    #print __data
    assert __data == data
    
def test_metrics():
    key = "\x00" * 16           
    keysize = len(key)
    def _hash_function(input_data, output_size=32):
        output = ''        
        input_data = input_data.zfill(keysize)
        while len(output) < output_size:
            output += encrypt(input_data, key, key)
            input_data = output[-keysize:]     
        return output
    from metrics import test_hash_function, test_performance
    test_performance(_hash_function)
    #test_hash_function(_hash_function)
    
if __name__ == "__main__":
    #test_substitution()
    #test_permutation()
    test_block_cipher()
    test_metrics()