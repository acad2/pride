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
 
def block_cipher_encrypt(data, key):    
    data = substitution(permutation(data, key), key)    
    return data
    
def block_cipher_decrypt(data, key):    
    data = permutation(''.join(reversed(substitution(''.join(reversed(data)), 
                                                     ''.join(reversed(key))))),
                       key, "invert")    
    return data
    
def test_block_cipher():
    data = ("\x00" * 15) + "\x00"
    key = "0123456789ABCDEF"    
    assert len(data) == len(key), (len(data), len(key))
    ciphertext = block_cipher_encrypt(data, key)
    _data = block_cipher_decrypt(ciphertext, key)
    #print ciphertext
    #print
    #print _data
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