import itertools

from utilities import cast, rotate, slide 
        
def permutation(input_data, key, mode="forward"):    
    key = bytearray(key)
    if mode == "forward":
        index_function = lambda index: (1 + index) * 8        
    else:
        assert mode == "invert"
        data_size = len(input_data)
        index_function = lambda index: (data_size - index) * 8
        key = [-number for number in reversed(key)]
        
    output = cast(bytes(input_data), "binary")
    key_material = itertools.cycle(key)
    key_byte = lambda: next(key_material)  
 
    for index, byte in enumerate(input_data):
        _key_byte = key_byte()        
        output = rotate(output[:index_function(index)], _key_byte) + output[index_function(index):]
    return cast(output, "bytes")
        
def substitution(data, key):
    data = bytearray(data)    
    key = bytearray(key)
    key_material = itertools.cycle(key)
    key_byte = lambda: next(key_material)
    modifier = len(data) + sum(key)
    for index, byte in enumerate(data):        
        other_bytes = sum(data[:index]) ^ sum(data[index + 1:])                
        data[index] ^= pow(251, (modifier ^ other_bytes) ^ key_byte() , 257) % 256  
    return bytes(data)    
 
def encryption_round(data, key):    
    return substitution(permutation(data, key), key)        
    
def decryption_round(data, key):    
    return permutation(''.join(reversed(substitution(''.join(reversed(data)), 
                                                     ''.join(reversed(key))))),
                       key, "invert")    

def block_encrypt(plaintext_block, key, rounds=4):
    ciphertext = plaintext_block
    round_key = key    
    for round in range(rounds):
        ciphertext = encryption_round(ciphertext, round_key)
        round_key = encryption_round(round_key, key)
    return ciphertext
    
def block_decrypt(ciphertext_block, key, rounds=4):
    round_keys = [key]
    round_key = key
    for round in range(rounds - 1):
        round_key = encryption_round(round_key, key)
        round_keys.append(round_key)

    for round_key in reversed(round_keys):
        ciphertext_block = decryption_round(ciphertext_block, round_key)        
    return ciphertext_block
        
def encrypt(data, key, iv, mode_of_operation=lambda ciphertext, block, key, iv: (ciphertext, key, iv)):
    ciphertext = ''
    block_size = len(key)
    for block in slide(data, block_size):
        ciphertext += block_encrypt(block, key)
        ciphertext, key, iv = mode_of_operation(ciphertext, block, key, iv)
    return ciphertext

def decrypt(ciphertext, key, iv, mode_of_operation=lambda ciphertext, block, key, iv: (ciphertext, key, iv)):
    plaintext = ''
    block_size = len(key)
    for block in slide(ciphertext, block_size):
        plaintext += block_decrypt(block, key)
        ciphertext, key, iv = mode_of_operation(ciphertext, block, key, iv)
    return plaintext
            
def test_block_cipher():
    data = (("\x00" * 15) + "\x00") * 6
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
    
if __name__ == "__main__":
    #test_substitution()
    #test_permutation()
    test_block_cipher()