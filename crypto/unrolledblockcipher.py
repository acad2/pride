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
          
def encrypt_block(plaintext, key, rounds=1, tweak=None): 
    # p_box
    # Data concentrating permutation box. Evenly distributes input bits amongst output. """
    bits = cast(bytes(plaintext), "binary")      
    
    bit_count = len(bits)
    word_size = bit_count / 8
    word_size_in_bytes = word_size / 8
    for index in range(8):
        bits_at_index = bits[index::word_size]
        _index = index * word_size_in_bytes    
        
        for offset, _bits in enumerate(slide(bits_at_index, 8)):   
            plaintext[_index + offset] = int(_bits, 2)
            
    _crypt_block(plaintext, key, tweak or INDICES[len(key)], range(rounds))
    
def decrypt_block(ciphertext, key, rounds=1, tweak=None):  
    _crypt_block(ciphertext, key, tweak or REVERSE_INDICES[len(key)], list(reversed(range(rounds)))) 
    
    # p_box
    # Data concentrating permutation box. Evenly distributes input bits amongst output. """
    bits = cast(bytes(ciphertext), "binary")      
    
    bit_count = len(bits)
    word_size = bit_count / 8
    word_size_in_bytes = word_size / 8
    for index in range(8):
        bits_at_index = bits[index::word_size]
        _index = index * word_size_in_bytes    
        
        for offset, _bits in enumerate(slide(bits_at_index, 8)):   
            ciphertext[_index + offset] = int(_bits, 2)
            
def _crypt_block(data, key, indices, rounds):    
    round_keys = []
    size = len(key)
    for round in rounds:
        # generate_round_key
        # Invertible round key generation function. Using an invertible key 
        # schedule offers a potential advantage to embedded devices.
        next_key = bytearray(size)
        for index, byte in enumerate(key):
            next_key[index] = S_BOX[byte ^ ((2 ** index) % 256)]
        round_keys.append(next_key)        
        key = next_key  
        
    for round_key_index in rounds:
        round_key = round_keys[round_key_index]
        
        # extract_round_key
        # Non invertible round key extraction function.
        xor_sum_of_key = xor_sum(round_key)    
        for index, key_byte in enumerate(round_key):        
            round_key[index] = S_BOX[((2 ** index) % 256) ^ xor_sum_of_key]                              
        
        xor_sum_of_data = xor_sum(data) ^ xor_sum(round_key)    
        for time, place in indices:
            time_constant = (2 ** time) % 256         
            random_place = S_BOX[round_key[place] ^ time_constant] % size              
                            
            xor_sum_of_data ^= data[random_place]
            data[random_place] ^= S_BOX[xor_sum_of_data ^ random_place]
            xor_sum_of_data ^= data[random_place]
                    
            xor_sum_of_data ^= data[place]
            data[place] ^= S_BOX[xor_sum_of_data ^ S_BOX[place] ^ time_constant]
            xor_sum_of_data ^= data[place]                
    
            xor_sum_of_data ^= data[random_place]
            data[random_place] ^= S_BOX[xor_sum_of_data ^ random_place]
            xor_sum_of_data ^= data[random_place]          
    