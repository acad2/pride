import itertools
from utilities import cast

S_BOX = bytearray(256)
INVERSE_S_BOX = bytearray(256)
INDICES = dict((key_size, range(key_size)) for key_size in (8, 16, 32, 64))
REVERSE_INDICES = dict((key_size, tuple(reversed(INDICES[key_size]))) for key_size in (8, 16, 32, 64))

for number in range(256):
    output = pow(251, number, 257) % 256
    S_BOX[number] = (output)
    INVERSE_S_BOX[output] = number
    
def block_rotation(input_bytes):    
    bits = cast(input_bytes, "binary")        
    return bytearray(int(bits[index::8], 2) for index in range(8))
    
def derive_round_key(key, key_xor):           
    for index, key_byte in enumerate(key):        
        key[index] = S_BOX[index ^ key_xor ^ key_byte]           
                   
def substitution(input_bytes, xor_sum, indices):        
    for index in indices:        
        xor_sum ^= input_bytes[index]# input_bytes[index] # remove the current byte from the xor sum         
        input_bytes[index] ^= S_BOX[xor_sum] # generate a psuedorandom byte from everything but the current byte + combine with current byte
        xor_sum ^= input_bytes[index] # include byte XOR psuedorandom_byte in the xor sum         
       
def process_message(data, indices):
    xor_sum = 0
    for byte in data:
        xor_sum ^= byte
    
    for index in indices:
        xor_sum ^= data[index]
        data[index] ^= S_BOX[index ^ xor_sum]
        xor_sum ^= data[index]

def encrypt(plaintext, key):  
    indices = INDICES[len(key)] # (0, 1, 2, ..., N) where N = length of key or the blocksize
    key = bytearray(key)
    plaintext = block_rotation(plaintext)  
    key_xor = 0
    data_xor = 0
    for index, key_byte in enumerate(key):
        key_xor ^= key_byte
        data_xor ^= plaintext[index]
        
    derive_round_key(key, key_xor)           
    process_message(plaintext, indices)
    
    xor_sum = 0 
    for index, data_byte in enumerate(plaintext):               
        xor_sum ^= data_byte ^ key[index]
    substitution(plaintext, xor_sum, indices)    
    return bytes(plaintext)
    
def decrypt(ciphertext, key):               
    indices = REVERSE_INDICES[len(key)]
    key = bytearray(key)
    key_xor = 0
    for index, key_byte in enumerate(key):
        key_xor ^= key_byte
        
    derive_round_key(key, key_xor)  
    ciphertext = bytearray(ciphertext) 
    xor_sum = 0          
    for index, key_byte in enumerate(key):               
        xor_sum ^= ciphertext[index] ^ key_byte
    substitution(ciphertext, xor_sum, indices)  

    process_message(ciphertext, indices)
    return bytes(block_rotation(bytes(ciphertext)))
    
def test_encrypt_decrypt():
    data = "\x00" * 7
    key = ("\x00" * 7) + "\x00"
    for count in range(256):
        _data = data + chr(count)
        ciphertext = encrypt(_data, key)    
        plaintext = decrypt(ciphertext, key)
        assert plaintext == _data, (ciphertext, plaintext, _data)
        print ciphertext
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    