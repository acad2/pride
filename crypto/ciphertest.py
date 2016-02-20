import itertools
from utilities import cast

def block_rotation(input_bytes):
    bits = cast(input_bytes, "binary")    
    return bytearray(int(bits[index::8], 2) for index in range(8))
    
def derive_round_key(key):    
    key_xor = 0
    for index, key_byte in key:
        key_xor ^= key_byte    
    return [(index, pow(251, index ^ key_xor ^ key_byte,  257)) for index, key_byte in key]
    
def substitution(input_bytes, key, indices):
    xor_sum = 0                    
    for index, key_byte in key:           
        xor_sum ^= input_bytes[index] ^ key_byte
        
    for index in indices:
        xor_sum ^= input_bytes[index] # remove the current byte from the xor sum               
        input_bytes[index] ^= pow(251, xor_sum, 257) % 256 # generate a psuedorandom byte from everything but the current byte + combine with current byte
        xor_sum ^= input_bytes[index] # include byte XOR psuedorandom_byte in the xor sum         
    
def encrypt(data, key):
    #_key = bytearray("\x00" * len(key))
    #substitution(_key, bytearray(key))
    plaintext = block_rotation(data)        
    key = derive_round_key([(index, ord(byte)) for index, byte in enumerate(key)])
    substitution(plaintext, key, [index for index in range(len(key))])
    return bytes(plaintext)
    
def decrypt(data, key):    
    #_key = bytearray("\x00" * len(key))
    #substitution(_key, bytearray(key))    
    keysize = len(key) - 1
    key = derive_round_key([(keysize - index, ord(byte)) for index, byte in enumerate(reversed(key))])
    ciphertext = bytearray(data)
    substitution(ciphertext, key, [keysize - index for index in range(keysize + 1)])    
    return bytes(block_rotation(bytes(ciphertext)))
    
def test_encrypt_decrypt():
    data = ("\x00" * 7) + "\x00"
    key = ("\x00" * 7) + "\x00"
    ciphertext = encrypt(data, key)    
    plaintext = decrypt(ciphertext, key)
    assert plaintext == data, (ciphertext, plaintext, data)
    print ciphertext
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    