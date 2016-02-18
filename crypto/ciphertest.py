from utilities import cast

def block_rotation(input_bytes):
    bits = cast(input_bytes, "binary")    
    return bytearray(int(bits[index::8], 2) for index in range(8))
    
def substitution(input_bytes, key):
    xor_sum = 0
    for index, byte in enumerate(key):       
        xor_sum ^= input_bytes[index] ^ byte
        input_bytes[index] ^= byte          
             
    # xor_sum = B_0 xor K_0 xor B_1 xor K_1 ...
    for index, byte in enumerate(input_bytes):      
        xor_sum ^= byte        
        input_bytes[index] ^= pow(251, xor_sum, 257) % 256
        xor_sum ^= input_bytes[index]
    
    for index, byte in enumerate(key):
        input_bytes[index] ^= byte      
    
def encrypt(data, key):
    _key = bytearray("\x00" * len(key))
    substitution(_key, bytearray(key))
    plaintext = block_rotation(data)    
    substitution(plaintext, bytearray(_key))    
    return bytes(plaintext)
    
def decrypt(data, key):    
    _key = bytearray("\x00" * len(key))
    substitution(_key, bytearray(key))
    ciphertext = bytearray(reversed(data))
    key = bytearray(reversed(_key))
    substitution(ciphertext, key)    
    return bytes(block_rotation(reversed(bytes(ciphertext))))
    
def test_encrypt_decrypt():
    data = ("\x00" * 7) + "\x00"
    key = "\x00" * 8
    ciphertext = encrypt(data, key)    
    plaintext = decrypt(ciphertext, key)
    assert plaintext == data
    print ciphertext
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    