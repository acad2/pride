import pride.utilities
import pride.crypto

import itertools
from utilities import cast, slide, xor_sum

import random
S_BOX, INVERSE_S_BOX = bytearray(256), bytearray(256)
INDICES = dict((key_size, zip(range(key_size), range(key_size))) for key_size in (8, 16, 32, 64, 128, 256))
REVERSE_INDICES = dict((key_size, zip(reversed(range(key_size)), reversed(range(key_size))))
                        for key_size in (8, 16, 32, 64, 128, 256))
                            
for number in range(256):
    output = pow(251, number, 257) % 256
    S_BOX[number] = (output)
    INVERSE_S_BOX[output] = number  
               
def generate_round_key(data):       
    cdef int index, byte
    return bytearray(S_BOX[byte ^ ((2 ** index) % 256)] for index, byte in enumerate(data))        
        
def extract_round_key(key): 
    """ Non invertible round key extraction function. """
    cdef int xor_sum_of_key, index, key_byte
    xor_sum_of_key = xor_sum(key)    
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[ ((2 ** index) % 256) ^ xor_sum_of_key]               

def substitution(input_bytes, key, indices): 
    cdef int size, xor_sum_of_data, time, place, random_place, time_constant
    
    size = len(input_bytes)
    xor_sum_of_data = xor_sum(input_bytes) ^ xor_sum(key)    
    for time, place in indices:
        # the steps are:
        # remove the current byte from the xor sum; If this is not done, the transformation is uninvertible
        # generate a psuedorandom byte from everything but the current plaintext byte then XOR it with current byte
        # include current byte XOR psuedorandom_byte into the xor sum 
        # ; This is done in a random place, in the current place, then in the random place again     
        
        # The "time" counter acts like a nonce which will cause distinct output from
        # input that is otherwise identical (i.e. 00000000...)
        # xoring the counter directly would cause the low order bits to shuffle
        # more then the high order bits. (2 ** time) % 256 produces power of 2
        # outputs which will eliminate bias in power of 2 sized inputs.
        time_constant = (2 ** time) % 256 # could be a table lookup
        
        # Find a random location based off of the entropy in this location at this time
        # The modulo size operation does not bias the S_BOX output if the S_BOX is
        # a straight 8x8 mapping. The potential outputs are the range 0-256, which
        # modulo a power of 2 results in equally distributed output
        random_place = S_BOX[key[place] ^ time_constant] % size              
                
        # Manipulate the state at the random location
        xor_sum_of_data ^= input_bytes[random_place]
        input_bytes[random_place] ^= S_BOX[xor_sum_of_data ^ random_place]
        xor_sum_of_data ^= input_bytes[random_place]
        
        # Manipulate the state at the current place and time
        xor_sum_of_data ^= input_bytes[place]
        input_bytes[place] ^= S_BOX[xor_sum_of_data ^ S_BOX[place] ^ time_constant]
        xor_sum_of_data ^= input_bytes[place]                
                        
        # Manipulate the random location again - this must be done for symmetry
        # This could probably be asymmetric at the cost of increased code size
        xor_sum_of_data ^= input_bytes[random_place]
        input_bytes[random_place] ^= S_BOX[xor_sum_of_data ^ random_place]
        xor_sum_of_data ^= input_bytes[random_place]             
          
def encrypt_block(plaintext, key, rounds=1, tweak=None): 
    #p_box(plaintext)
    _crypt_block(plaintext, key, tweak or INDICES[len(key)], range(rounds))
    
def decrypt_block(ciphertext, key, rounds=1, tweak=None):  
    _crypt_block(ciphertext, key, tweak or REVERSE_INDICES[len(key)], list(reversed(range(rounds))))
    #p_box(ciphertext)
    
def _crypt_block(data, key, indices, rounds):      
    round_keys = []
    for round in rounds:        
        key = generate_round_key(key)
        round_keys.append(key)        
        
    for round_key_index in rounds:
        round_key = round_keys[round_key_index]        
        extract_round_key(round_key)                  
        substitution(data, round_key, indices) 
        
#from unrolledblockcipher import encrypt_block, decrypt_block
        
class Test_Cipher(pride.crypto.Cipher):
    
    def __init__(self, key, mode, rounds=1, tweak=None):
        self.key = key
        self.mode = mode
        self.rounds = rounds
        blocksize = len(key)
        tweak = self.tweak = tweak or zip(range(blocksize), range(blocksize))
        self.reversed_tweak = tuple(reversed(tweak))
        
    def encrypt_block(self, plaintext, key):
        return encrypt_block(plaintext, key, self.rounds, self.tweak)
        
    def decrypt_block(self, ciphertext, key):
        return decrypt_block(ciphertext, key, self.rounds, self.reversed_tweak)
            
def test_Cipher():
    import random
    data = "\x00" * 7 #"Mac Code" + "\x00" * 7
    iv = key = ("\00" * 7) + "\00"
    tweak = range(len(key))
   # random.shuffle(tweak)
    tweak = zip(range(len(tweak)), tweak)
    cipher = Test_Cipher(key, "cbc", 1, tweak)
    size = 2
    for count in range(1):
        plaintext = data + chr(count)
        real_ciphertext = cipher.encrypt(plaintext, iv)  
        
    #    for location in range(size):
    #        correct_bytes = real_ciphertext[location:location +size]
    #        
    #        for modification in (''.join(chr(byte) for byte in bytes) for bytes in itertools.product(*(range(256)for count in range(size)))):#, range(256)):
    #            attacked_ciphertext = pride.utilities.splice(modification, into=real_ciphertext, at=location)            
    #            invalid_plaintext = cipher.decrypt(attacked_ciphertext, iv) 
    #            if invalid_plaintext[:8] == "Mac Code" and modification != correct_bytes:
    #                print "Mac code collision", correct_bytes, modification, invalid_plaintext, plaintext

        real_plaintext = cipher.decrypt(real_ciphertext, iv)
        print real_ciphertext
        print                   
        assert real_plaintext == plaintext, (plaintext, real_plaintext)
        
        
def test_cipher_metrics():
    from metrics import test_block_cipher
    test_block_cipher(Test_Cipher)          
    
def test_linear_cryptanalysis():       
    from pride.crypto.utilities import xor_parity
    
    def _test_random_data():
        import os
        outputs = []
        for key_count, key in enumerate(slide(os.urandom(16 * 256), 16)):
            ciphertext = os.urandom(16 * 65535)        
            pride.utilities.print_in_place(str(key_count / 256.0) + '% complete; Current bias: {}'.format(float(outputs.count(1)) / (outputs.count(0) or 1)))
            for index, block in enumerate(slide(os.urandom(16 * 65535), 16)):
                outputs.append(1 if xor_parity(block) ^ xor_parity(ciphertext[index * 16:(index + 1) * 16]) else 0)

        zero_bits = outputs.count(0)
        one_bits = outputs.count(1)
        print float(one_bits) / zero_bits, one_bits, zero_bits                
        
    def _test_encrypt():
        data = "\x00" * 14
        key = ("\x00" * 15)  
        outputs = []
        for key_count, key_byte in enumerate(range(256)):
            _key = bytearray(key + chr(key_byte))
            key_parity = xor_parity(_key)
            pride.utilities.print_in_place(str(key_count / 256.0) + '% complete; Current bias: {}'.format(float(outputs.count(1)) / (outputs.count(0) or 1)))
            for count in range(65535):            
                _data = bytearray(data + cast(cast(count, "binary").zfill(16), "bytes"))
                plaintext = _data[:]
            #  print len(_data), count
                encrypt_block(_data, _key)
                ciphertext = _data[:]
                plaintext_parity = xor_parity(plaintext)        
                ciphertext_parity = xor_parity(ciphertext)
                outputs.append(1 if plaintext_parity ^ ciphertext_parity == key_parity else 0)
    
        zero_bits = outputs.count(0)
        one_bits = outputs.count(1)
        print float(one_bits) / zero_bits, one_bits, zero_bits    
    
    _test_encrypt()
    
if __name__ == "__main__":
    #test_Cipher()
    #test_linear_cryptanalysis()
    test_cipher_metrics()
    #test_random_metrics()
    #test_aes_metrics()