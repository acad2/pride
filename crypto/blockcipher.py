import pride.utilities
import pride.crypto

import itertools
from utilities import cast, slide, xor_sum

import random

def generate_s_box(function):
    S_BOX = bytearray(256)
    for number in range(256):    
        S_BOX[number] = function(number)        
    return S_BOX

S_BOX = generate_s_box(lambda number: ((251 * pow(251, number, 257)) + 1) % 256)
POWER_OF_TWO = dict((2 ** index, index) for index in range(9))
                        
def generate_round_key(data):       
    """ Invertible round key generation function. Using an invertible key 
        schedule offers a potential advantage to embedded devices. """    
    return bytearray(S_BOX[byte ^ S_BOX[index]] for index, byte in enumerate(data))        
        
def extract_round_key(key): 
    """ Non invertible round key extraction function. """
    xor_sum_of_key = xor_sum(key)    
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[S_BOX[index] ^ xor_sum_of_key]               

def swap_bytes(input_bytes, place, random_byte, required_bits):           
    random_place = random_byte >> (8 - required_bits)        
    input_bytes[place], input_bytes[random_place] = input_bytes[random_place], input_bytes[place]
    
def shuffle(data, key):
    required_bits = POWER_OF_TWO[len(data)]
    for index, byte in enumerate(key):
        swap_bytes(data, index, byte, required_bits)
        
def substitute_bytes(input_bytes, key, indices, counter): 
    """ Substitution portion of the cipher. Classifies as an even, complete,
        consistent, homeogenous, source heavy unbalanced feistel network. (I think?)
        The basic idea is that each byte of data is encrypted based off 
        of every other byte of data around it, along with the round key. 
        The ensures a high level of diffusion, which may indicate resistance
        towards differential cryptanalysis as indicated by:
         (https://www.schneier.com/cryptography/paperfiles/paper-unbalanced-feistel.pdf
          namely page 14)        
         
        Each byte is substituted, then a byte at a random location substituted,
        then the current byte substituted again. At each substitution, the output
        is fed back into the state to modify future outputs.
                        
        The ideas of time and spatial locality are introduced to modify how
        the random bytes are generated. Time is represented by the count of
        how many bytes have been enciphered so far. Space is indicated by the
        current index being operated upon.
        
        The S_BOX lookup could conceivably be replaced with a timing attack
        resistant non linear function. The default S_BOX is based off of
        modular exponentiation of 251 ^ x mod 257, which can be computed
        silently in situations where it is required."""        
    size = len(input_bytes)
    size_minus_one = size - 1    
    required_bits = POWER_OF_TWO[size]
    state = xor_sum(input_bytes) ^ xor_sum(key)        
    for index in counter: 
        time = index
        place = indices[index]
        
        # swap two random bytes
        # the right shift by 8 - required_bits produces values in the ranges of
        # powers of 2 (2, 4, 8, 16, 32, etc) without modular arithmetic/branches
        # the state is included because bytes are swapped at the end, and if 
        # the same values were supplied, the bytes swapped here would be undone
        swap_place = (((size_minus_one - index) ^ state) & ((2 ** required_bits) - 1)) | place        
        swap_bytes(input_bytes, indices[swap_place], key[swap_place], required_bits)
        
        # the substitution steps are:
        # remove the current byte from the state; If this is not done, the transformation is uninvertible
        # generate a psuedorandom byte from the state (everything but the current plaintext byte),
        # then XOR it with current byte; then include current byte XOR psuedorandom_byte into the state 
        # ; This is done in the current place, then in a random place, then in the current place again.     
        
        # The "time" counter acts like a nonce which will cause distinct output from
        # input that is otherwise identical (i.e. 00000000...)
        # xoring the counter directly would cause the low order bits to shuffle
        # more then the high order bits, introducing bias.
        time_constant = S_BOX[key[index]]                          
        place_constant = S_BOX[key[(index + 1) % size]] 
        present_modifier = time_constant ^ place_constant
        
        # Find a random location based off of the entropy in this location at this time
        random_place = S_BOX[key[place] ^ time_constant] >> 8 - required_bits         
        
        state ^= input_bytes[place]
        input_bytes[place] ^= S_BOX[state ^ present_modifier]
        state ^= input_bytes[place]                                     

        # Manipulate the state at the random place       
        state ^= input_bytes[random_place]
        input_bytes[random_place] ^= S_BOX[state ^ random_place]
        state ^= input_bytes[random_place]                
       
        # manipulate the current location again - required for symmetry
        state ^= input_bytes[place]
        input_bytes[place] ^= S_BOX[state ^ present_modifier]
        state ^= input_bytes[place]  
        
        swap_place = (((size_minus_one - index) ^ state) & ((2 ** required_bits) - 1)) | place        
        swap_bytes(input_bytes, indices[swap_place], key[swap_place], required_bits)
          
def generate_default_constants(block_size):    
    constants = bytearray(block_size)
    for index in range(block_size):
        constants[index] = index
    return constants
        
def encrypt_block(plaintext, key, rounds=1, tweak=None): 
    blocksize = len(plaintext)
    tweak = tweak or generate_default_constants(blocksize)
    _crypt_block(plaintext, key, tweak, bytearray(range(rounds)), range(blocksize))    
       
def decrypt_block(ciphertext, key, rounds=1, tweak=None): 
    blocksize = len(ciphertext)
    constants = tweak or generate_default_constants(blocksize)
    _crypt_block(ciphertext, key, constants, bytearray(reversed(range(rounds))), bytearray(reversed(range(blocksize))))
        
def _crypt_block(data, key, constants, rounds, counter):      
    round_keys = []
    for round in rounds:        
        key = generate_round_key(key)
        round_keys.append(key)        
    
    for round_key_index in rounds:
        round_key = round_keys[round_key_index]        
        extract_round_key(round_key)                
        
        round_constants = constants[:]
        shuffle(round_constants, round_key)
        substitute_bytes(data, round_key, round_constants, counter) 
        
class Test_Cipher(pride.crypto.Cipher):
    
    def __init__(self, key, mode, rounds=1, tweak=None):        
        self.key = key
        self.mode = mode
        self.rounds = rounds        
        self.tweak = tweak 
            
    def encrypt_block(self, plaintext, key):
        return encrypt_block(plaintext, key, self.rounds, self.tweak)
        
    def decrypt_block(self, ciphertext, key):
        return decrypt_block(ciphertext, key, self.rounds, self.tweak)
            
def test_Cipher():
    import random
    data = "\x00" * 255 #"Mac Code" + "\x00" * 7
    iv = key = ("\x00" * 255) + "\00"
    tweak = generate_default_constants(len(key))
   # random.shuffle(tweak)
    cipher = Test_Cipher(key, "cbc", 2, tweak)
    size = 2
    for count in range(5):
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
    
def test_cipher_performance():
    from metrics import test_prng_performance
    _cipher = Test_Cipher("\x00" * 16, 'cbc')
    test_prng_performance(lambda data, output_size: _cipher.encrypt("\x00" * output_size, "\x00" * 16))
    
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
    test_Cipher()
    #test_cipher_performance()
    #test_linear_cryptanalysis()
    test_cipher_metrics()
    #test_random_metrics()
    #test_aes_metrics()