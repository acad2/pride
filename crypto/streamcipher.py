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
    
def prp(data, mask=255, rotation_amount=5, bit_width=8):    
    key = decorrelation_layer(data, bit_width)        
    for index in range(len(data)):
        #left, right = data[index], data[(index + 1) % 16]
        #key ^= right
        #right = rotate_left((right + key + index) & mask, rotation_amount, bit_width)     
        #key ^= right ^ left
        #left = (left + (right >> (bit_width / 2))) & mask
        #key ^= left
        #
        #data[index], data[(index + 1) % 16] = left, right
        
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
                  
def stream_cipher(seed, key, output_size=16, size=(8, 255, 5)):     
    key = list(key)
    seed = list(seed)
    key_xor = xor_sum(key)    
    bit_width, mask, rotation_amount = size    
    
    output = list()
    block_count, extra = divmod(output_size, len(seed) * (bit_width / 8))
    
    for block in range(block_count + 1 if extra else block_count):        
        key_xor = prp(key, mask, rotation_amount, bit_width) 
        round_key = key[:]
        prf(round_key, key_xor, mask, rotation_amount, bit_width)
                
        xor_subroutine(seed, round_key)                           
        seed_xor = prp(seed, mask, rotation_amount, bit_width)        
        #prf(seed, seed_xor, mask, rotation_amount, bit_width)        
        xor_subroutine(seed, round_key)
        
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
    
    def encrypt(self, data, key, iv): 
        assert iv, (type(iv), iv)        
        output = list(bytearray(data))                
        encrypt(output, list(bytearray(key)), list(bytearray(iv)), (8, 255, 5))# (64, 0xFFFFFFFFFFFFFFFF, 40))        
        return bytes(output)
    
    def decrypt(self, data, iv=None, tag=None, tweak=None):
        assert iv
        output = bytearray(data)
        decrypt(output, self.key, bytearray(iv))
        return bytes(output)
     
    @classmethod
    def test_encrypt_decrypt(cls, *args, **kwargs):
        cipher = cls(*args, **kwargs)
        
        message = bytearray(16)
        iv = bytearray(16)        
        message[-1] = 1
        
        ciphertext = cipher.encrypt(message, iv)        
        print ciphertext
        plaintext = cipher.decrypt(ciphertext, iv)
        assert message == plaintext, (message, plaintext)
        print "Passed encrypt/decrypt test"
        
    @classmethod
    def test_performance(cls, *args, **kwargs):  
        from metrics import test_cipher_performance
        cipher = cls("\x00" * 16, None)
        test_cipher_performance((32, 1500, 4096, 1024 * 1024), cipher.encrypt, "\x00" * 16, "\x00" * 16)
    
    @classmethod
    def test_metrics(cls, *args, **kwargs):
        from metrics import test_stream_cipher
        cipher = cls(*args, **kwargs)
        test_stream_cipher(cipher.encrypt, "\x00" * 16, "\x00" * 16)
        
        
def test_stream_cipher_diffusion():
    seed = bytearray(16)
    key = seed[:]
    seed2 = key[:]  
    seed3 = key[:]
    seed[-1] = 1
    seed2[-2] = 1 
    seed3[-2] = 2
    data = bytearray(stream_cipher(seed, key))
    data2 = bytearray(stream_cipher(seed2, key))
    data3 = bytearray(stream_cipher(seed3, key))
   # print data
   # print
   # print data2
   # print
   # print data3
    
    seed = bytearray(16)
    key = seed[:]
    seed2 = seed[:]
    key2 = seed[:]
    key2[-1] = 1
    
    data = bytearray(stream_cipher(seed, key))
    data2 = bytearray(stream_cipher(seed2, key2))
    
    print [format(byte, 'b').zfill(8) for byte in data]
    print
    print [format(byte, 'b').zfill(8) for byte in data2]
    
    
if __name__ == "__main__":
    #Stream_Cipher.test_encrypt_decrypt("\x00" * 16, "stream!")
    Stream_Cipher.test_metrics("\x00" * 16, "\x00" * 16)
    #Stream_Cipher.test_performance()
    #test_stream_cipher_diffusion()
    