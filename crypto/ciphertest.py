import pride.utilities
import pride.crypto

import itertools
from utilities import cast, slide, xor_sum

S_BOX, INVERSE_S_BOX = bytearray(256), bytearray(256)
INDICES = dict((key_size, zip(range(key_size), range(key_size))) for key_size in (8, 16, 32, 64, 128, 256))
REVERSE_INDICES = dict((key_size, zip(reversed(range(key_size)), reversed(range(key_size))))
                        for key_size in (8, 16, 32, 64, 128, 256))

for number in range(256):
    output = pow(251, number, 257) % 256
    S_BOX[number] = (output)
    INVERSE_S_BOX[output] = number  
    
def p_box(input_bytes):    
    """ Data concentrating permutation box. Evenly distributes input bits amongst output. """
    bits = cast(bytes(input_bytes), "binary")      
    # if a 64 bit block was acceptable, the operation would be this simple:
    #   for index, byte in enumerate(int(bits[index::8], 2) for index in range(8)):
    #       input_bytes[index] = byte  
    
    bit_count = len(bits)
    word_size = bit_count / 8
    word_size_in_bytes = word_size / 8
    for index in range(8):
        bits_at_index = bits[index::8]
        _index = index * word_size_in_bytes    
        
        for offset, _bits in enumerate(slide(bits_at_index, 8)):   
            input_bytes[_index + offset] = int(_bits, 2)
           
def generate_round_key(data):       
    """ Invertible round key generation function. Using an invertible key 
        schedule offers a potential advantage to embedded devices. """
    return bytearray(S_BOX[byte ^ (2 ** (index % 8))] for index, byte in enumerate(data))        
        
def extract_round_key(key): 
    """ Non invertible round key extraction function. """
    xor_sum_of_key = xor_sum(key)    
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[(2 ** (index % 8)) ^ xor_sum_of_key]               
    
def substitution(input_bytes, key, indices): 
    """ Substitution portion of the cipher. Classifies as a source heavy 
        unbalanced feistel network. The basic idea is that each byte of
        data is encrypted based off of every other byte of data around it,
        along with the round key. The ensures a high level of diffusion, 
        which may indicate resistance towards differential cryptanalysis
        (https://www.schneier.com/cryptography/paperfiles/paper-unbalanced-feistel.pdf
         namely page 14)        
         
        The rate of confusion, which is defined in the paper above as:
         "The  rate  of  confusion  of  a  consistent  UFN2 is  the  minimum
          number of times per cycle that any bit can occur in the target block"
          
        Where a cycle is defined as: 
         "A cycle is the number of rounds necessary for each bit in the block 
          to have been part of both the source and target blocks at least once"
          
        Each bit is guaranteed to be a part of the source block at least once,
        as the bytes are simply enumerated. Each bit is part of the target
        block every time it is not part of the source.
        
        In addition to the simple enumeration of bytes, at each step, both
        before and after the current byte is encrypted, a byte at a random
        location is encrypted as well. Supposing the distribution of the 
        random selection is not biased, each bit should on average be
        part of the source block 3 times per round.
                        
        Each random byte used to encrypt the data is fed back into the state 
        to further modify future outputs.
        
        The ideas of time and spatial locality are introduced to modify how
        the random bytes are generated. Time is represented by the count of
        how many bytes have been enciphered so far. Space is indicated by the
        current index being operated upon.
        
        By default, the order in which bytes are operated upon is in linear.
        Modification of the indices could be used as to facilitate a tweakable
        block cipher.
        
        The S_BOX lookup could conceivably be replaced with a timing attack
        resistant non linear function. The default S_BOX is based off of
        modular exponentiation of 251 ^ x mod 257."""
        
    size = len(input_bytes)
    xor_sum_of_data = xor_sum(input_bytes) ^ xor_sum(key)    
    for time, place in indices:
        # the steps are:
        # remove the current byte from the xor sum; If this is not done, the transformation is uninvertible
        # generate a psuedorandom byte from everything but the current plaintext byte then XOR it with current byte
        # include current byte XOR psuedorandom_byte into the xor sum 
        # ; This is done in a random place, in the current place, then in the random place again
        random_place = S_BOX[key[time] ^ place] % size
        random_place_now = random_place ^ time
             
        xor_sum_of_data ^= input_bytes[random_place]
        input_bytes[random_place] ^= S_BOX[xor_sum_of_data ^ random_place_now]
        xor_sum_of_data ^= input_bytes[random_place]
        
        xor_sum_of_data ^= input_bytes[place]
        input_bytes[place] ^= S_BOX[xor_sum_of_data ^ S_BOX[place] ^ time]
        xor_sum_of_data ^= input_bytes[place]                
        
        xor_sum_of_data ^= input_bytes[random_place]
        input_bytes[random_place] ^= S_BOX[xor_sum_of_data ^ random_place_now]
        xor_sum_of_data ^= input_bytes[random_place]   
          
def encrypt_block(plaintext, key, rounds=1):         
    return _crypt_block(plaintext, key, INDICES[len(key)], range(rounds))

def decrypt_block(ciphertext, key, rounds=1):    
    return _crypt_block(ciphertext, key, REVERSE_INDICES[len(key)], list(reversed(range(rounds))))
    
def _crypt_block(data, key, indices, rounds):    
    round_keys = []
    for round in rounds:
        key = generate_round_key(key)
        round_keys.append(key)
    
    for round_key_index in rounds:
        round_key = round_keys[round_key_index]
        
        extract_round_key(round_key)       
      #  p_box(key)        
        substitution(data, round_key, indices) 
        
class Test_Cipher(pride.crypto.Cipher):
    
    encrypt_block = staticmethod(encrypt_block)
    decrypt_block = staticmethod(decrypt_block)
            
def test_encrypt_decrypt_block():
    from os import urandom
    data = "\x00" * 31
    key = bytearray(("\x00" * 31) + "\x00")
    for count in range(256):
        _data = bytearray(data + chr(count))
        plaintext = bytes(_data)
        encrypt_block(_data, key)    
        ciphertext = bytes(_data)
        decrypt_block(_data, key)
        _plaintext = bytes(_data)
        assert plaintext == _plaintext, (plaintext, _plaintext)
      #  print ciphertext#, [byte for byte in bytearray(ciphertext)]
      #  print
    
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
    test_encrypt_decrypt_block()
    #test_linear_cryptanalysis()
    #test_cipher_metrics()
    #test_random_metrics()
    #test_aes_metrics()