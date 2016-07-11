import hkdf
from pride.crypto.utilities import xor_subroutine

def encrypt(data, key, iv, associated_data='', hash_function="sha256"):
    data = bytearray(data)
    crypt(data, key, iv, associated_data, hash_function)
    return bytes(data), iv, associated_data, hash_function
    
def decrypt(cryptogram, key):
    ciphertext, iv, associated_data, hash_function = cryptogram
    ciphertext = bytearray(ciphertext)
    crypt(ciphertext, key, iv, associated_data, hash_function)
    return bytes(ciphertext)
    
def crypt(data, key, iv, associated_data, hash_function):    
    keystream = hkdf.hkdf(key, len(data), info=associated_data, salt=iv, hash_function=hash_function)      
    xor_subroutine(data, bytearray(keystream))
    
def test_encrypt_decrypt():
    data = "Message!"
    key = "\x00"
    other_data = "Testing!"
    cryptogram = encrypt(data, key, "\x00", other_data)
    print cryptogram
    plaintext = decrypt(cryptogram, key)
    assert plaintext == data, (plaintext, data)
    print plaintext
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    