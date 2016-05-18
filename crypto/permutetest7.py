def permute(left_byte, right_byte, key_byte, modifier):                             
    right_byte = (right_byte + key_byte + modifier) & 65535
    left_byte = (left_byte + (right_byte >> 8)) & 65535
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
    return left_byte, right_byte
    
def diffusion_layer(data, _storage=[0] * 16): 
    for byte_index in range(16):     
        mask = 32768 >> byte_index        
        _byte = 0        
        for byte_position in range(16):            
            _byte |= (((data[byte_position] & mask) << byte_index) >> byte_position)
        _storage[byte_index] = _byte      
    
    diffuser = 0
    for index in range(16):
        byte = _storage[index]
        diffuser ^= byte
        data[index] = byte
    return diffuser
        
def xor_with_key(data, key):
    for index in range(16):
        data[index] ^= key[index]
        
def encrypt_bytes(data, key, tag, constants=tuple(0 for byte in range(256)), rounds=1):    
    for round in range(rounds):    
        xor_with_key(data, key)
        diffuser = diffusion_layer(data)  
        
        for index in range(16):
            diffuser ^= data[index]
            
            left_byte, right_byte = permute(constants[index], diffuser, key[index], index)
            left_byte, right_byte = permute(right_byte, left_byte, key[index], index)
            data[index] ^= right_byte
            tag[index] ^= left_byte
            
            diffuser ^= data[index]
                        
def decrypt_bytes(data, key, tag, constants=tuple(0 for byte in range(256)), rounds=1):
    diffuser = 0
    for index in range(16):
        diffuser ^= data[index]
        
    for round in range(rounds):
        for index in reversed(range(16)):
            diffuser ^= data[index]
            
            left_byte, right_byte = permute(constants[index], diffuser, key[index], index)
            left_byte, right_byte = permute(right_byte, left_byte, key[index], index)
            data[index] ^= right_byte
            tag[index] ^= left_byte
            
            diffuser ^= data[index]
        diffuser = diffusion_layer(data)
        xor_with_key(data, key)
        
def test_encrypt_bytes():
    rounds = 1
    data = ([0] * 13) + [0, 0, 1]
    plaintext = data[:]
    key = ([0] * 14) + [1, 0]
    tag = [0] * 16
    print data
    encrypt_bytes(data, key, tag, rounds=rounds)
    print data
    decrypt_bytes(data, key, tag, rounds=rounds)
    assert data == plaintext, data
    assert tag == [0] * 16, tag
    
if __name__ == "__main__":
    test_encrypt_bytes()
