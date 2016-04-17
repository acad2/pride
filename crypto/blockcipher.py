import pride.utilities
import pride.crypto

import itertools
from utilities import cast, slide, xor_sum, xor_subroutine

import random

def generate_s_box(function):
    S_BOX = bytearray(256)
    for number in range(256):    
        S_BOX[number] = function(number)        
    return S_BOX

#from scratch import aes_s_box as S_BOX    
S_BOX = generate_s_box(lambda number: pow(251, number, 257) % 256)
POWER_OF_TWO = dict((2 ** index, index) for index in range(9))
                        
def generate_round_key(key, constants):       
    """ Invertible round key generation function. """ 
    size = len(key)        
    for round in range(1):
        state = xor_sum(key)      
        for index in constants:        
            state ^= key[index]
            key[index] ^= S_BOX[state ^ S_BOX[index] ^ key[(index + 1) % size] ^ key[(index + 2) % size]]
            state ^= key[index]
    
def extract_round_key(key): 
    """ Non invertible round key extraction function. """
    xor_sum_of_key = xor_sum(key)    
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[S_BOX[key_byte] ^ S_BOX[index] ^ xor_sum_of_key]               
      
def shuffle(data, key): 
    n = len(data)
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)
        data[i], data[j] = data[j], data[i]
        
def substitute_bytes(data, key, round_constants, counter, mask): 
    """ Substitution portion of the cipher. Classifies as an even, complete,
        consistent, homeogenous, source heavy unbalanced feistel network. (I think?)
        (https://www.schneier.com/cryptography/paperfiles/paper-unbalanced-feistel.pdf)
        The basic idea is that each byte of data is encrypted based off 
        of every other byte of data around it.      
         
        Each byte is substituted, then a byte at a random location substituted,
        then the current byte substituted again. At each substitution, the output
        is fed back into the state to modify future outputs.
                        
        The ideas of time and spatial locality are introduced to modify how
        the random bytes are generated. Time is represented by the count of
        how many bytes have been enciphered so far. Space is indicated by the
        current index being operated upon.
        
        The S_BOX lookup could/should conceivably be replaced with a timing attack
        resistant non linear function. The default S_BOX is based off of
        modular exponentiation of 251 ^ x mod 257, which was basically
        selected at random and possesses a bad differential characteristic.

        The substitution steps are:
            
            - Remove the current byte from the state; If this is not done, the transformation is uninvertible
            - Generate an ephemeral byte to mix with the state; the ephemeral byte aims to preserve forward secrecy in
              the event the internal state is recovered (i.e. by differential attack)
            - Generate a psuedorandom byte from the state (everything but the current plaintext byte),
              then XOR that with current byte; then include current byte XOR psuedorandom_byte into the state 
            - This is done in the current place, then in a random place, then in the current place again. """            
    state = xor_sum(data) ^ xor_sum(key)    
    size = len(data)
    for index in counter:         
        place = round_constants[index]           
                
        # the counters are passed through the sbox to attempt to eliminate bias
        # simple byte ^ index would flip the low order bits more frequently then high order bits for smaller blocksizes       
        # S_BOX is applied twice to prevent index ^ place == 0 when index == place      
        present_modifier = S_BOX[S_BOX[S_BOX[index]] ^ S_BOX[place]]
                                
        state ^= data[place] ^ present_modifier
        ephemeral_byte = S_BOX[key[index] ^ S_BOX[state]] 
        data[place] ^= S_BOX[state ^ ephemeral_byte] # goal is forward secrecy in event of sbox input becoming known
        state ^= data[place] ^ present_modifier        
        
        second_place = round_constants[place]
        state ^= data[second_place] ^ present_modifier
        ephemeral_byte = S_BOX[key[index] ^ S_BOX[state]]
        data[second_place] ^= S_BOX[state ^ ephemeral_byte]
        state ^= data[second_place] ^ present_modifier
        
        state ^= data[place] ^ present_modifier
        ephemeral_byte = S_BOX[key[index] ^ S_BOX[state]] 
        data[place] ^= S_BOX[state ^ ephemeral_byte] # goal is forward secrecy in event of sbox input becoming known
        state ^= data[place] ^ present_modifier  

def attack(): 
    plaintext = bytearray("\x00" * 2)
    ciphertext = plaintext[:]
    key = ciphertext[:]
    encrypt_block(ciphertext, key)
   
    inverse_s_box = bytearray(len(S_BOX))
    for index, byte in enumerate(S_BOX):
        inverse_s_box[byte] = index
    
    for first_place_guess in (0, ):#1):
        for round_key_byte_guess in range(256):
            sbox_input = inverse_s_box[ciphertext[first_place_guess] ^ plaintext[first_place_guess]]
            sbox_output = S_BOX[sbox_input]
            for key_byte_guess in range(256):
                for state_guess in range(256):
                    ephemeral_byte = S_BOX[key_byte_guess ^ S_BOX[state_guess]]
                    if S_BOX[state_guess ^ ephemeral_byte] == sbox_output:                    
                        print "Found potential state/ephemeral byte: ", state_guess, ephemeral_byte
                        
                        
                    
    
def generate_default_constants(block_size):    
    constants = bytearray(block_size)
    for index in range(block_size):
        constants[index] = index
    return constants
        
def encrypt_block(plaintext, key, rounds=1, tweak=None): 
    blocksize = len(plaintext)
    tweak = tweak or generate_default_constants(blocksize)    
    online_keyschedule(plaintext, key[:], tweak, bytearray(range(rounds)), range(blocksize))    
       
def decrypt_block(ciphertext, key, rounds=1, tweak=None): 
    blocksize = len(ciphertext)
    constants = tweak or generate_default_constants(blocksize)
    upfront_keyschedule(ciphertext, key[:], constants, bytearray(reversed(range(rounds))), bytearray(reversed(range(blocksize))))
           
def generate_round_keys(key, rounds, tweak):
    round_keys = []    
    for round_number in rounds:
        generate_round_key(key, tweak)
        round_keys.append(key[:])        
    return round_keys          
            
def online_keyschedule(data, key, constants, rounds, counter):                      
    mask = (1 << POWER_OF_TWO[len(data)]) - 1 # byte & mask constrains byte to appropriate range    
    for round_number in rounds:        
        generate_round_key(key, constants)
        xor_subroutine(data, key)
        _crypt_block(key, constants, data, counter, mask)                
        xor_subroutine(data, key)
        
def upfront_keyschedule(data, key, constants, rounds, counter):
    round_keys = generate_round_keys(key, rounds, constants)        
    mask = (1 << POWER_OF_TWO[len(data)]) - 1
    for round_key_index in rounds:        
        round_key = round_keys[round_key_index]
        xor_subroutine(data, round_key)
        _crypt_block(round_key, constants, data, counter, mask)  
        xor_subroutine(data, round_key)
        
def _crypt_block(key, constants, data, counter, mask):        
    round_key = key[:]
    extract_round_key(round_key)                        
    
    round_constants = constants[:]        
    shuffle(round_constants, round_key)
    
    extract_round_key(round_key)        
    substitute_bytes(data, round_key, round_constants, counter, mask)        
        
def decrypt_block_embedded_decryption_key(ciphertext, final_round_key, rounds=1, tweak=None):
    blocksize = len(ciphertext)
    constants = tweak or generate_default_constants(blocksize)    
    online_keyschedule_embedded_decryption_key(ciphertext, final_round_key[:], constants, 
                                               bytearray(reversed(range(rounds))), bytearray(reversed(range(blocksize))))
                                               
def online_keyschedule_embedded_decryption_key(data, key, constants, rounds, counter):    
    reverse_constants = bytearray(reversed(constants))
    mask = (1 << POWER_OF_TWO[len(data)]) - 1
    for round_number in rounds:          
        xor_subroutine(data, key)
        _crypt_block(key, constants, data, counter, mask)
        xor_subroutine(data, key)
        generate_round_key(key, reverse_constants)

def generate_embedded_decryption_key(key, rounds, tweak):
    return generate_round_keys(key[:], rounds, tweak)[-1]    
    
class Test_Cipher(pride.crypto.Cipher):
    
    def __init__(self, key, mode, rounds=1, tweak=None):        
        self.key = key#; from os import urandom; self.key = urandom(len(key));        
        self.mode = mode
        if mode == "ella":
            self.blocksize = len(key) - 8
            self.mac_key = key[:8]
        else:
            self.blocksize = len(key)
            self.mac_key = None
        self.rounds = rounds        
        self.tweak = tweak
        self.iv = None
        
    def encrypt_block(self, plaintext, key):
        encrypt_block(plaintext, self.key, self.rounds, self.tweak)
        
    def decrypt_block(self, ciphertext, key):        
        decrypt_block(ciphertext, self.key, self.rounds, self.tweak)
            
    def encrypt(self, data, iv=None, tag=None):
        assert tag is None
        return super(Test_Cipher, self).encrypt(data, iv, self.mac_key)
        
    def decrypt(self, data, iv=None, tag=None):
        assert tag is None        
        mode = self.mode
        return super(Test_Cipher, self).decrypt(data[8:] if mode == "ella" else data, iv, data[:8] if mode == "ella" else None)
        
        
class Test_Embedded_Decryption_Cipher(Test_Cipher):
                
    def __init__(self, *args):
        super(Test_Embedded_Decryption_Cipher, self).__init__(*args)
        self.decryption_key = generate_embedded_decryption_key(self.key, range(self.rounds), self.tweak)
        
    def decrypt_block(self, ciphertext, key):
        return decrypt_block_embedded_decryption_key(ciphertext, self.decryption_key, self.rounds, self.tweak)
        
        
def test_Cipher():
    import random
    data = "\x00" * 255 #"Mac Code" + "\x00" * 7
    iv = key = ("\x00" * 255) + "\00"
    tweak = generate_default_constants(len(key))
   # random.shuffle(tweak)
    cipher = Test_Cipher(key, "cbc", 2, tweak)
    cipher2 = Test_Embedded_Decryption_Cipher(key, "cbc", 2, tweak)
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
        
        ciphertext2 = cipher2.encrypt(plaintext, iv)
        plaintext2 = cipher2.decrypt(ciphertext2, iv)
        assert plaintext2 == plaintext, plaintext2
        
def test_cipher_metrics():        
    Test_Cipher.test_metrics(randomize_key=False)#avalanche_test=False, randomness_test=False, bias_test=False, performance_test=False,
                             #period_test=True, randomize_key=True)    

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
    
def test_generate_round_key():
    constants = range(16)
    class Test_Cipher(pride.crypto.Cipher):
        
        def __init__(self, *args):
            super(Test_Cipher, self).__init__(*args)
            self.blocksize = 16            
            
        def encrypt_block(self, data, key):            
            generate_round_key(data, constants)                        
            return bytes(data)
            
    Test_Cipher.test_metrics()
    
    #key = bytearray(S_BOX[byte] for byte in bytearray(os.urandom(256)))#range(256))    
    #key_material = bytearray()
    #constants = generate_default_constants(256)
    #shuffle(constants, bytearray(os.urandom(256)))
    #for chunk in range(4096):
    #    generate_round_key(key, constants)
    #    key_material.extend(key[:])
    #   # print key
    #from pride.crypto.metrics import test_randomness, test_avalanche
    #test_randomness(bytes(key_material))
    #    
    #constants = generate_default_constants(16)
    #shuffle(constants, bytearray(os.urandom(16)))
    #def _test_interface(data):
    #    data = bytearray(data)             
    #    generate_round_key(data, constants)        
    #    return bytes(data)        
    #test_avalanche(_test_interface)
    
def test_extract_round_key():        
    class Test_Cipher(pride.crypto.Cipher):
        
        def __init__(self, *args):
            super(Test_Cipher, self).__init__(*args)
            self.blocksize = 16
            
        def encrypt_block(self, data, key):
            extract_round_key(data)            
            
    Test_Cipher.test_metrics()
    
    #key = bytearray(S_BOX[byte] for byte in range(256))
    #key_material = bytearray()
    #for chunk in range(4096):
    #    extract_round_key(key)
    #   # print key
    #    key_material.extend(key[:])
    #            
    #from pride.crypto.metrics import test_randomness, test_avalanche
    #test_randomness(bytes(key_material))       
    #
    #def _test_interface(data):
    #    data = bytearray(data)
    #    extract_round_key(data)
    #    return bytes(data)
    #test_avalanche(_test_interface)
    
if __name__ == "__main__":
#    test_generate_round_key()
 #   test_extract_round_key()
    #test_Cipher()
    #test_linear_cryptanalysis()
    #test_cipher_metrics()
    attack()