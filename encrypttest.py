import random

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
backend = openssl.backend
BACKEND = backend

def encrypt(data='', key='', unencrypted_authenticated_data='', iv_size=12):
    assert data and key
    iv = random._urandom(iv_size)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), 
                       backend=backend).encryptor()
    encryptor.authenticate_additional_data(iv + unencrypted_authenticated_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (ciphertext, encryptor.tag, iv + unencrypted_authenticated_data)
    
def decrypt(ciphertext, key, iv, tag, unencrypted_authenticated_data=''):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), 
                       backend=backend).decryptor()
    decryptor.authenticate_additional_data(iv + unencrypted_authenticated_data)
    return decryptor.update(ciphertext) + decryptor.finalize()
    
key = random._urandom(32)
shared_key = random._urandom(32)
other_key = random._urandom(32)
#encrypted_key, tag, iv = encrypt(shared_key, key)
#twice_encrypted_key, second_tag, second_iv = encrypt(encrypted_key, other_key)
#once_decrypted_key = decrypt(twice_encrypted_key, key, iv, tag)
#decrypted_key = decrypt(once_decrypted_key, other_key, second_iv, second_tag)
#assert decrypted_key == shared_key

def _encrypt(data='', key='', iv_size=16):
    assert data and key
    iv = random._urandom(iv_size)
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv), 
                       backend=BACKEND).encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return ciphertext, iv
    
def _decrypt(ciphertext='', key='', iv=None):
    assert ciphertext and key and iv
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv),
                       backend=BACKEND).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

print "Shared key: ", shared_key   
print 
once_encrypted_key, key_iv = _encrypt(shared_key, key)   
print "Encrypted shared key once: ", once_encrypted_key 
print
print "First encryption using iv: ", key_iv
print
twice_encrypted_key, other_key_iv = _encrypt(once_encrypted_key, other_key)
print "Encrypted shared key 2x  : ", twice_encrypted_key
print
print "Next encryption using iv : ", other_key_iv
print
_once_encrypted_key = _decrypt(twice_encrypted_key, key, key_iv)
print "Decrypted key once: ", _once_encrypted_key
print
_shared_key = _decrypt(_once_encrypted_key, other_key, other_key_iv)
print "Decrypted shared key: ", _shared_key
assert _shared_key == shared_key