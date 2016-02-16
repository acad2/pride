import itertools

from utilities import cast, rotate, slide 
        
def permutation(input_data, key, mode="forward"):        
    if mode == "forward":
        index_function = lambda index: (1 + index) * 8        
    else:
        assert mode == "invert"
        data_size = len(input_data)
        index_function = lambda index: (data_size - index) * 8
       # key = [-number for number in reversed(key)]
        
    output = cast(bytes(input_data), "binary") 
    for index, key_byte in enumerate(key):        
        output = rotate(output[:index_function(index)], key_byte) + output[index_function(index):]
    return cast(output, "bytes")
              
def substitution(data, key):      
    modifier = sum(key)    
    for index, byte in enumerate(data):                        
        data[index] ^= pow(251, (sum(data[:index]) ^ sum(data[index + 1:])) + 
                                (modifier ^ key[index]), 
                           257) % 256                              
 
# data_i = ROTATE(KM_i XOR data_i XOR (251 POWER ((ciphertext_i XOR plaintext_i) PLUS (modifier XOR key_i)) MODULO 257) MODULO 256)

def generate_round_keys(seed, key, rounds):
    round_keys = []     
    for round in range(rounds):
        substitution(seed, key)
        round_keys.append(seed[:])
    return round_keys
        
def xor(data, key):
    for index in range(len(data)):
        data[index] ^= key[index]
        
def crypt_block(block, round_keys, instructions):
    for round_key in round_keys:
        for instruction in instructions:
            instruction(block, round_key)
                       
def cipher(data, iv, round_keys, round_functions, rounds=1):
    block_size = len(round_keys[0])
    output = ''
    for block in slide(data, block_size):
        crypt_block(block, round_keys, round_functions)
        output += bytes(block)
    return output
    
def encrypt(data, key, iv, rounds=1, mode_of_operation=lambda input_block, output_block, key, iv: (input_block, output_block, key, iv)):        
    return cipher(bytearray(data), iv,
                  generate_round_keys(bytearray(key), bytearray(key), rounds),
                  (xor, substitution, permutation))                  
                   
def decrypt(data, key, iv, rounds=1, mode_of_operation=lambda input_block, output_block, key, iv: (input_block, output_block, key, iv)):
    # same as encryption, with the data, keys, and operations reversed    
    round_keys = [bytearray(reversed(round_key)) for round_key in 
                  reversed(generate_round_keys(bytearray(key), bytearray(key), rounds))]      
    return ''.join(reversed(cipher(bytearray(reversed(data)), iv, round_keys, (permutation, substitution, xor))))
                            
def test_block_cipher():
    data = "\x00" * 16
    iv = key = "\x00" * 16  
    #assert len(data) == len(key), (len(data), len(key))
    ciphertext = encrypt(data, key, iv)
    _data = decrypt(ciphertext, key, iv)
    print ciphertext    
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
    #test_performance(_hash_function)
    test_hash_function(_hash_function)
    
if __name__ == "__main__":
    #test_substitution()
    #test_permutation()
    test_block_cipher()
    #test_metrics()