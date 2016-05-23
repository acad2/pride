from utilities import cast

def _setup(data, key, bit_width_and_mask=(64, (2 ** 64) - 1)):
    bit_width, mask = bit_width_and_mask    
    size = len(data) / 2    
    left = right = 0
    for index in reversed(range(size)):               
        left |= data[index] << (8 * (size - 1 - index))
        right |= data[index + size] << (8 * (size - 1 - index))
        #key ^= key[index] << (8 * index)
        #key ^= key[index + size] << (   
    #left = cast(cast(bytes(data[:size]), "binary"), "integer")
    
    
    #right = cast(cast(bytes(data[size:]), "binary"), "integer")
    key = cast(cast(bytes(key), "binary"), "integer")
    diffuser = left ^ right ^ key
    return left, right, key, diffuser, mask, bit_width
    
def pbox(word):
    binary_word = cast(word, "binary")
    return int(''.join(binary_word[offset::8] for offset in range(8)), 2)
    
def encrypt(data, key, bit_width_and_mask=(64, (2 ** 64) - 1), rounds=5):  
    (left, right, 
     key, diffuser, 
     mask, bit_width) = _setup(data, key, bit_width_and_mask)
    
    for round in range(rounds):          
        diffuser ^= right        
        right = (right + key + diffuser) & mask        
        diffuser ^= right ^ left                
        
        left = (left + (right >> 8)) & mask
        left ^= ((right >> 5) | (right << (bit_width - 5))) & mask                
        diffuser ^= left
        
        left, right = right, left        
        
    left, right = right, left  
    return bytearray(cast(left, "bytes") + cast(right, "bytes"))
    
def decrypt(data, key, bit_width_and_mask=(64, (2 ** 64) - 1), rounds=5):
    (left, right, 
     key, diffuser, 
     mask, bit_width) = _setup(data, key, bit_width_and_mask)   
    
    for round in range(rounds): 
        
        diffuser ^= left                
        left ^= ((right >> 5) | (right << (bit_width - 5))) & mask
        left = (mask + 1 + (left - (right >> 8))) & mask
        
        diffuser ^= left ^ right                        
        right = (mask + 1 + ((right - key) - diffuser)) & mask        
        diffuser ^= right
        
        left, right = right, left    
        
    left, right = right, left
    return bytearray(cast(left, "bytes") + cast(right, "bytes"))
        
def test_permute():    
    data = bytearray("\x01" * 16)
    key = bytearray("\x01" * 16)
    ciphertext = encrypt(data, key)        
    print "Ciphertext:\n", ciphertext
        
    plaintext = decrypt(ciphertext, key)
    print "Plaintext: ", plaintext
    
import pride.crypto
from pride.crypto.utilities import replacement_subroutine

class Test_Cipher(pride.crypto.Cipher):
        
    def __init__(self, *args):
        super(Test_Cipher, self).__init__(*args)
        self.size_constants = (64, (2 ** 64) - 1)
        self.rounds = 4
        self.blocksize = 16
        
    def encrypt_block(self, data, key, tag=None, tweak=None):            
        ciphertext = encrypt(data, self.key, self.size_constants, self.rounds)
        print "Ciphertext: ", ciphertext
        replacement_subroutine(data, bytearray(ciphertext))
                
    def decrypt_block(self, data, key, tag=None, tweak=None):
        plaintext = decrypt(data, self.key, self.size_constants, self.rounds)
        replacement_subroutine(data, bytearray(plaintext))
                
if __name__ == "__main__":
    test_permute()
    #Test_Cipher.test_encrypt_decrypt("\x00" * 16, "cbc")
    #Test_Cipher.test_metrics("\x00" * 16, "\x00" * 16)