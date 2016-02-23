import itertools
from utilities import cast, slide

S_BOX = bytearray(256)
INVERSE_S_BOX = bytearray(256)
INDICES = dict((key_size, range(key_size)) for key_size in (8, 16, 32, 64))
REVERSE_INDICES = dict((key_size, tuple(reversed(INDICES[key_size]))) for key_size in (8, 16, 32, 64))

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
    
def derive_round_key(key):    
    xor_sum_of_key = xor_sum(key)
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[index ^ xor_sum_of_key ^ key_byte]           
    block_rotation(key)
    
def substitution(input_bytes, key, indices):   
    xor_sum_of_data = xor_sum(input_bytes)
    for index in indices:        
        xor_sum_of_data ^= input_bytes[index]# input_bytes[index] # remove the current byte from the xor sum             
        input_bytes[index] ^= INVERSE_S_BOX[index ^ key[index]] ^ S_BOX[xor_sum_of_data] # generate a psuedorandom byte from everything but the current byte + combine with current byte
        xor_sum_of_data ^= input_bytes[index] # include byte XOR psuedorandom_byte in the xor sum         
       
def xor_with_key(data, key):    
    for index, byte in enumerate(key):
        data[index] ^= byte    
        
def encrypt(plaintext, key):  
    # indices = INDICES[len(key)] # (0, 1, 2, ..., N) where N = length of key or the blocksize    
    return crypt_block(plaintext, key, INDICES[len(key)])

def decrypt(ciphertext, key):    
    return crypt_block(ciphertext, key, REVERSE_INDICES[len(key)])
    
def crypt_block(data, key, indices):    
    key = bytearray(key)
    data = bytearray(data)
    
    derive_round_key(key)                
    xor_with_key(data, key)
    substitution(data, key, indices)           
    xor_with_key(data, key)
   
    return bytes(data)
    
def test_encrypt_decrypt():
    data = "\x00" * 15
    key = ("\x00" * 15) + "\x00"
    for count in range(5):
        _data = data + chr(count)
        ciphertext = encrypt(_data, key)    
        plaintext = decrypt(ciphertext, key)
        assert plaintext == _data, (ciphertext, plaintext, _data)
        print ciphertext#, [byte for byte in bytearray(ciphertext)]
        print
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    