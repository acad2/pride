from utilities import xor_sum, rotate_left, rotate_right, slide, xor_subroutine, integer_to_bytes, bytes_to_words, words_to_bytes

def shuffle_bytes(_state, temp=list(range(16))):          
    temp[7] = _state[0] 
    temp[12] = _state[1]
    temp[14] = _state[2]
    temp[9] = _state[3]
    temp[2] = _state[4]
    temp[1] = _state[5]
    temp[5] = _state[6]
    temp[15] = _state[7]
    temp[11] = _state[8]
    temp[6] = _state[9]
    temp[13] = _state[10]
    temp[0] = _state[11]
    temp[4] = _state[12]
    temp[8] = _state[13]
    temp[10] = _state[14]
    temp[3] = _state[15]
            
    _state[:] = temp[:]
        
def bit_mixing(data, start=0, direction=1, bit_width=8):
    size = len(data)
    index = start
    key = 0
    for counter in range(size):
        data[(index + 1) % size] ^= rotate_left(data[index], (index % bit_width), bit_width)
        key ^= data[(index + 1) % size]
        index += direction
    return key
    
def decorrelation_layer(data, bit_width):
    key = bit_mixing(data, 0, 1, bit_width)    
    shuffle_bytes(data)
    return key
    
def prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    key = decorrelation_layer(data, bit_width)
    for index in range(len(data)):
        byte = data[index]
        key ^= byte                          
        data[index] = rotate_left((byte + key + index) & mask, rotation_amount, bit_width)        
        key ^= data[index]                    
    return key
        
def prf(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in range(len(data)):        
        new_byte = rotate_left((data[index] + key + index) & mask, rotation_amount, bit_width)    
        key ^= new_byte
        data[index] = new_byte            
            
def xor_subroutine2(data, key):
    data_xor = 0
    for index, byte in enumerate(key):
        data[index] ^= byte
        data_xor ^= data[index]
    return data_xor
    
def stream_cipher(seed, key, output_size=16, size=(8, 255, 5)):     
    key = key[:]
    seed = seed[:]
    key_xor = xor_sum(key)    
    bit_width, mask, rotation_amount = size    
    
    output = bytearray()
    block_count, extra = divmod(output_size, len(seed) * (bit_width / 8))
    for block in range(block_count + 1 if extra else block_count):        
        key_xor = prp(key, key_xor, mask, rotation_amount, bit_width) # generate key                       
        key_xor = prf(key, key_xor, mask, rotation_amount, bit_width) # one way extraction: class 2B keyschedule
        
        xor_subroutine(seed, key) # pre-whitening                   
        prf(seed, xor_sum(seed), mask, rotation_amount, bit_width) # high diffusion prp             
        xor_subroutine2(seed, key) # post_whitening
        
        output.extend(seed[:])
    return output
    
def encrypt(data, key, seed, size=(8, 255, 5)):
    key_material = seed[:]    
    xor_subroutine(data, stream_cipher(key_material, key, len(data), size))    
    
def decrypt(data, key, seed, size=(8, 255, 5)):
    key_material = seed[:]    
    xor_subroutine(data, stream_cipher(key_material, key, len(data), size))    
               

import pride.crypto

class Stream_Cipher(pride.crypto.Cipher):
    
    def encrypt(self, data, iv=None, tag=None, tweak=None): 
        assert iv, (type(iv), iv)
        output = bytearray(data)
        encrypt(output, self.key, bytearray(iv))        
        return bytes(output)
    
    def decrypt(self, data, iv=None, tag=None, tweak=None):
        assert iv
        output = bytearray(data)
        decrypt(output, self.key, bytearray(iv))
        return bytes(output)
     
    @classmethod
    def test_encrypt_decrypt(cls, *args, **kwargs):
        cipher = cls(*args, **kwargs)
        
        message = bytearray(range(16))
        iv = bytearray(16)        
                
        ciphertext = cipher.encrypt(message, iv)        
        plaintext = cipher.decrypt(ciphertext, iv)
        assert message == plaintext, (message, plaintext)
        print "Passed encrypt/decrypt test"
        
if __name__ == "__main__":
    #Stream_Cipher.test_encrypt_decrypt("\x00" * 16, "stream!")
    Stream_Cipher.test_metrics("\x00" * 16, "\x00" * 16)
    