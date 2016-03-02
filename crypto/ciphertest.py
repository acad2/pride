import pride.utilities

import itertools
from utilities import cast, slide

S_BOX, INVERSE_S_BOX = bytearray(256), bytearray(256)
INDICES = dict((key_size, range(key_size)) for key_size in (8, 16, 32, 64, 128))
REVERSE_INDICES = dict((key_size, tuple(reversed(INDICES[key_size]))) for key_size in (8, 16, 32, 64, 128))

for number in range(256):
    output = pow(251, number, 257) % 256
    S_BOX[number] = (output)
    INVERSE_S_BOX[output] = number
    
def block_rotation(input_bytes):    
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
    
def xor_sum(data):
    _xor_sum = 0
    for byte in data:
        _xor_sum ^= byte
    return _xor_sum
       
def generate_round_key(data):   
    return bytearray(S_BOX[byte ^ (2 ** (index % 8))] for index, byte in enumerate(data))        
        
def extract_round_key(key):    
    xor_sum_of_key = xor_sum(key)
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[(2 ** (index % 8)) ^ xor_sum_of_key ^ key_byte]           
    block_rotation(key)
    
def substitution(input_bytes, key, indices):   
    xor_sum_of_data = xor_sum(input_bytes)
    key_xor = xor_sum(key)
    for index in indices:        
        # remove the current byte from the xor sum; If this is not done, the transformation is uninvertible
        # generate a psuedorandom byte from everything but the current plaintext byte then XOR it with current byte
        # include current byte XOR psuedorandom_byte into the xor sum         
        xor_sum_of_data ^= input_bytes[index]        
        input_bytes[index] ^= INVERSE_S_BOX[key_xor ^ INVERSE_S_BOX[index << 1]] ^ S_BOX[key[index] ^ xor_sum_of_data]     
        xor_sum_of_data ^= input_bytes[index] 
       
def xor_with_key(data, key):    
    for index, byte in enumerate(key):
        data[index] ^= byte    
      
def bit_shuffle(data, key, indices):
    for index in indices:
        data = rotate(data[:index], key[index]) + data[index:]
    return data
    
def encrypt_block(plaintext, key, rounds=1):  
    # indices = INDICES[len(key)] # (0, 1, 2, ..., N) where N = length of key or the blocksize       
    return crypt_block(plaintext, key, INDICES[len(key)], [index for index in range(rounds)])

def decrypt_block(ciphertext, key, rounds=1):    
    return crypt_block(ciphertext, key, REVERSE_INDICES[len(key)], list(reversed([index for index in range(rounds)])))
    
def crypt_block(data, key, indices, rounds):    
    round_keys = []
    for round in rounds:
        key = generate_round_key(key)
        round_keys.append(key)
    
    for round_key_index in rounds:
        round_key = round_keys[round_key_index]
        
        extract_round_key(round_key)                
        xor_with_key(data, round_key) # add key to data        
        substitution(data, round_key, indices) # encrypt data with itself  
        xor_with_key(data, round_key) # remove key from data      
    
def xor_parity(data):
    bits = [int(bit) for bit in cast(bytes(data), "binary")]
    parity = bits[0]
    for bit in bits[1:]:
        parity ^= bit
    return parity
    
def test_encrypt_decrypt_block():
    data = "\x00" * 7
    key = bytearray(("\x00" * 7) + "\x00")
    for count in range(5):
        _data = bytearray(data + chr(count))
        plaintext = bytes(_data)
        encrypt_block(_data, key)    
        ciphertext = bytes(_data)
        decrypt_block(_data, key)
        _plaintext = bytes(_data)
        assert plaintext == _plaintext, (plaintext, _plaintext)
        print ciphertext#, [byte for byte in bytearray(ciphertext)]
        print
    
def test_linear_cryptanalysis():       
    
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
    test_linear_cryptanalysis()