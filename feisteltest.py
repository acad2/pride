import hashlib

import pride

def xor(string_one, string_two):
    #result = ''
    #print len(string_one), len(string_two)
    #for index, character in enumerate(string_one):
    #    print index, character
    #    result += chr(ord(character) ^ ord(string_two[index]))
    return ''.join(chr(ord(character) ^ ord(string_two[index])) for
                   index, character in enumerate(string_one))
  
def padded(message, block_size): 
    if len(message) < block_size:
        message += "\x00" * (block_size - len(message))
    return message

def encrypt_block(plaintext, key, block_size, round_function, round_count): 
    half_size = block_size / 2    
    left_half = plaintext[:half_size]
    right_half = plaintext[half_size:block_size]
    
    for round_number in range(round_count):
        # apply round function to left half
        left_round_function = round_function()                
        left_round_function.update(left_half + key)
        # xor result with right half
        right_half = xor(right_half, left_round_function.digest())
        
        # apply round function to right half
        right_round_function = round_function()
        right_round_function.update(right_half + key)
        # xor result with left half
        left_half = xor(left_half, right_round_function.digest())
        
    if not round_count % 2: # even number of rounds
        left_half, right_half = right_half, left_half # swap the left/right
    return left_half + right_half
        
def decrypt_block(ciphertext, key, block_size, round_function, round_count):
    half_size = block_size / 2
    left_half = ciphertext[:half_size]
    right_half = ciphertext[half_size:block_size]

    if not round_count % 2: # even number of rounds
        left_half, right_half = right_half, left_half # swap the left/right
        
    for round_number in range(round_count):            
        # apply round function to right half
        right_round_function = round_function()                
        right_round_function.update(right_half + key)
        # xor result with left half
        left_half = xor(left_half, right_round_function.digest())
        
        # apply round function to right half
        left_round_function = round_function()
        left_round_function.update(left_half + key)
        # xor result with left half
        right_half = xor(right_half, left_round_function.digest())                
    return left_half + right_half

    
class Feistel_Network(pride.base.Base):
    
    defaults = {"round_function" : "sha512", "round_count" : 4}
    
    def _get_block_size(self):
        return getattr(hashlib, self.round_function)().digestsize
    block_size = property(_get_block_size)
            
    def encrypt(self, plaintext, key):
        block_size = self.block_size
        if len(plaintext) % block_size:
            raise ValueError("Unpadded plaintext supplied to encrypt")
        round_function = getattr(hashlib, self.round_function)
        round_count = self.round_count
        ciphertext = ''
        while plaintext:
            ciphertext += encrypt_block(plaintext[:block_size], key, block_size,
                                        round_function, round_count)
            plaintext = plaintext[block_size:]
        return ciphertext
        
    def decrypt(self, ciphertext, key):
        block_size = self.block_size
        round_function_factory = getattr(hashlib, self.round_function)
        round_count = self.round_count
        plaintext = ''
        while ciphertext:
            plaintext += decrypt_block(ciphertext[:block_size], key, block_size,
                                       round_function_factory, round_count)
            ciphertext = ciphertext[block_size:]
        return plaintext
        
        
if __name__ == "__main__":
    f = Feistel_Network()
    key = "\x00" * 32
    data = padded("This is some awesome test data", f.block_size)
    ciphertext = f.encrypt(data, key)
    _data = f.decrypt(ciphertext, key)
    assert data == _data
    
    