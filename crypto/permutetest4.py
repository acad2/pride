def permute(left_byte, right_byte, key_byte, modifier):        
    right_byte = (right_byte + key_byte + modifier) & 65535
    left_byte = (left_byte + (right_byte >> 8)) & 65535
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535
    return left_byte, right_byte

# psuedocode for permute:    
#def permute(a, b, c):
#    b += c
#    a += b >> 8
#    a ^= rotate_right(b, 3)
    
def invert_permute(left_byte, right_byte, key_byte, modifier):    
    left_byte ^= ((right_byte >> 3) | (right_byte << (16 - 3))) & 65535   
    left_byte = (65536 + (left_byte - (right_byte >> 8))) & 65535       
    right_byte = (65536 + (right_byte - key_byte - modifier)) & 65535   
    return left_byte, right_byte
    
def permute_subroutine(data, key, index, modifier):    
    data[index - 1], data[index] = permute(data[index - 1], data[index], key[index], modifier)    
    
def invert_permute_subroutine(data, key, index, modifier):    
    data[index - 1], data[index] = invert_permute(data[index - 1], data[index], key[index], modifier)    
    
def permutation(data, key, modifier):        
    for round in range(2):
        for index in reversed(range(len(data))):        
            permute_subroutine(data, key, index, modifier)            
    
def invert_permutation(data, key, modifier):    
    for round in range(2):
        for index in range(len(data)):
            invert_permute_subroutine(data, key, index, modifier)            
    
def crypt_bytes(data, key, tag, rounds=1):
    size = len(data)    
    for index in range(size):
        data[index] = (data[index] & 255) | (tag[index] << 8)                      
    
    key = key[:]        
    for round in range(rounds):                      
        permutation(key, key, round)    
        permutation(data, key, round)        
            
    for index in range(size):    
        tag[index] = data[index] >> 8
                
def decrypt_bytes(data, key, tag, rounds=1):
    size = len(data)    
    for index in range(size):
        data[index] = (data[index] & 255) | (tag[index] << 8)        
        
    keys = []
    key = key[:]
    for round in range(rounds):        
        permutation(key, key, round)        
        keys.append(key[:])
        
    for round in reversed(range(rounds)):           
        invert_permutation(data, keys[round], round)                        
        
    for index in range(size):
        tag[index] = data[index] >> 8           
   
import pride.crypto
from pride.crypto.utilities import replacement_subroutine

class Test_Cipher(pride.crypto.Cipher):
    
    def __init__(self, *args):
        super(Test_Cipher, self).__init__(*args)
        self.rounds = 1
        self.blocksize = 8
        
    def encrypt_block(self, data, key, tag):        
        _data = list(data)
        crypt_bytes(_data, key, tag, self.rounds)
        _data, tag = [byte & 255 for byte in _data], [byte >> 8 for byte in _data]
        replacement_subroutine(data, _data)
        replacement_subroutine(tag, data)
        
    def decrypt_block(self, data, key, tag):
        decrypt_bytes(data, key, tag, self.rounds)
        
        
def test_crypt_bytes():
    tag = [1, 1, 1, 1]
    data = [0, 0, 0, 0]            
    key = [0, 0, 0, 0]
    rounds = 2
    crypt_bytes(data, key, tag, rounds)
    print [byte & 255 for byte in data], [byte >> 8 for byte in data]
    decrypt_bytes(data, key, tag, rounds)
    print [byte & 255 for byte in data], [byte >> 8 for byte in data]
    
if __name__ == "__main__":
    test_crypt_bytes()
    Test_Cipher.test_metrics([0 for count in range(16)], "\x00" * 16)