def permute(left_byte, right_byte, key_byte, modifier):        
    right_byte = (right_byte + key_byte + modifier + 1) & 65535
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
    right_byte = (65536 + (right_byte - key_byte - modifier - 1)) & 65535   
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
    
def encrypt_bytes(data, key, tag, rounds=1):
    size = len(data)    
    assert isinstance(data, list), type(data)
    assert isinstance(key, list), type(key)
    for index in range(size):
        data[index] = (data[index] & 255) | (tag[index] << 8)                      
    
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
    
    def _get_key(self):
        return list(self._key)
    def _set_key(self, value):
        self._key = value
    key = property(_get_key, _set_key)
    
    def __init__(self, *args):
        super(Test_Cipher, self).__init__(*args)
        self.rounds = 1
        self.blocksize = 8
        
    def encrypt_block(self, data, key, tag):        
        _data = list(data)        
        encrypt_bytes(_data, list(key), tag, self.rounds)
        _data, _tag = self.separate_data_and_tag(_data)
        replacement_subroutine(data, _data)
        #replacement_subroutine(tag, _tag)
        
    def decrypt_block(self, data, key, tag):        
        _data = list(data)
        decrypt_bytes(_data, list(key), tag, self.rounds)
        _data, _tag = self.separate_data_and_tag(_data)
        replacement_subroutine(data, _data)
        #replacement_subroutine(tag, _tag)        
        
    def encrypt(self, data, iv=None, tag=None, authenticated_data=''): 
        assert tag is not None
        ciphertext = super(Test_Cipher, self).encrypt(data, iv, tag)
        if authenticated_data:
            super(Test_Cipher, self).encrypt(authenticated_data, iv, tag)
        return ciphertext            
        
    def decrypt(self, ciphertext, iv, tag, initial_tag, authenticated_data=''):
        plaintext = super(Test_Cipher, self).decrypt(ciphertext, iv, tag)
        if authenticated_data:
            super(Test_Cipher, self).encrypt(authenticated_data, iv, tag)
        assert tag == initial_tag, (tag, initial_tag)
        return plaintext
        
    def hash(self, data, tag=None): 
        tag = tag or ([0] * self.blocksize)
        self.encrypt(bytearray(data), "\x00" * self.blocksize, tag)
        return ''.join((chr(byte) for byte in tag))
        
    def separate_data_and_tag(self, _data):
        return [byte & 255 for byte in _data], [byte >> 8 for byte in _data]
        
    @classmethod
    def test_encrypt_decrypt(cls, *args, **kwargs):
        cipher = cls(*args, **kwargs)
        message = "\x00" * 16
        iv = "\x00" * 16
        tag = [0 for byte in range(8)]
        initial_tag = tag[:]
        ciphertext = cipher.encrypt(message, iv, tag)        
        plaintext = cipher.decrypt(ciphertext, iv, tag, initial_tag)
        assert message == plaintext, (message, plaintext)
        
def test_crypt_bytes():
    tag = [1, 1, 1, 1]
    data = [0, 0, 0, 0]            
    key = [0, 0, 0, 0]
    rounds = 2
    encrypt_bytes(data, key, tag, rounds)
    print [byte & 255 for byte in data], [byte >> 8 for byte in data]
    decrypt_bytes(data, key, tag, rounds)
    print [byte & 255 for byte in data], [byte >> 8 for byte in data]
    
def test_cipher_hash():
    cipher = Test_Cipher([0 for byte in range(16)], "ecb")
    cipher.blocksize = 16
    print cipher.hash("\x00", [0xff] * 16)
   
    from metrics import test_hash_function
    test_hash_function(cipher.hash)
    
if __name__ == "__main__":
    #test_crypt_bytes()
    test_cipher_hash()
    #Test_Cipher.test_encrypt_decrypt([0 for byte in range(16)], "cbc")
    #Test_Cipher.test_metrics([0 for count in range(16)], "\x00" * 16)