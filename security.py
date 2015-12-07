import random

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
BACKEND = openssl.backend

class SecurityError(Exception): pass

class InvalidPassword(SecurityError): pass

def hash_function(algorithm_name):
    return hashes.Hash(getattr(hashes, algorithm_name)(), backend=BACKEND)
    
def key_derivation_function(salt, algorithm="SHA256", length=32, 
                            iterations=100000, backend=BACKEND):
    return PBKDF2HMAC(algorithm=getattr(hashes, algorithm)(),
                      length=length, salt=salt, iterations=iterations,
                      backend=backend)
      
def hkdf_expand(algorithm="SHA256", length=256, info='', backend=BACKEND):
    return HKDFExpand(algorithm=getattr(hashes, algorithm)(),
                      length=length, info=info, backend=BACKEND)

def apply_mac(key, data, algorithm="SHA256"):
    return hmac.new(key, data, getattr(hashes, algorithm)).digest()  
                    
def verify_mac(key, data, mac, algorithm="SHA256"):
    return hmac.compare_digests(mac, hmac.new(key, data,
                                getattr(hashes, algorithm)).digest())
                                                  
def encrypt(data='', key='', iv=None, extra_data='', algorithm="AES",
            mode="GCM", backend=BACKEND, iv_size=16):
    assert data and key
    iv = iv or random._urandom(iv_size)
    encryptor = Cipher(getattr(algorithms, algorithm)(key), 
                       getattr(modes, mode)(iv), 
                       backend=BACKEND).encryptor()
    if mode == "GCM":
        extra_data = iv + extra_data
        encryptor.authenticate_additional_data(extra_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    try:
        return pack_encrypted_data(ciphertext, iv, encryptor.tag, extra_data)
    except AttributeError:
        return pack_encrypted_data(ciphertext, iv)
    
def decrypt(packed_encrypted_data, key, algorithm="AES",
            mode="GCM", backend=BACKEND):
    ciphertext, iv, tag, extra_data = unpack(packed_encrypted_data)
    if mode == "GCM" and not tag:
        raise ValueError("Tag not supplied for GCM mode")
    mode_args = (iv, tag) if mode == "GCM" else (iv, )
    decryptor = Cipher(getattr(algorithms, algorithm)(key), 
                       getattr(modes, mode)(*mode_args), 
                       backend=BACKEND).decryptor()
    if mode == "GCM":
        decryptor.authenticate_additional_data(extra_data)
    return decryptor.update(ciphertext) + decryptor.finalize()         

def pack_encrypted_data(ciphertext, iv, tag='', extra_data=''):
    # ciphertext_size = str(len(ciphertext))
    # iv_size = str(len(iv))
    # tag_size = str(len(tag))
    # extra_data_size = str(len(extra_data))
    # return (ciphertext_size + ' ' + iv_size + ' ' + tag_size + ' ' + 
    #         extra_data_size + ' ' + ciphertext + iv + tag + extra_data)
    # the below does the above without assigning a bunch of unused names
    return ' '.join((str(len(ciphertext)), str(len(iv)), 
                     str(len(tag)), str(len(extra_data)), ciphertext)) + iv + tag + extra_data
                     
def unpack(packed_bytes):
    ciphertext_size, iv_size, tag_size, extra_data_size, packed_bytes = packed_bytes.split(' ', 4)
    ciphertext_size = int(ciphertext_size)
    iv_size = int(iv_size)
    tag_size = int(tag_size)
    extra_data_size = int(extra_data_size)
    end_of_iv = ciphertext_size + iv_size
    end_of_tag = end_of_iv + tag_size
    end_of_extra_data = end_of_tag + extra_data_size
    # ciphertext = packed_bytes[:ciphertext_size]        
    # iv = packed_bytes[ciphertext_size:end_of_iv]
    # tag = packed_bytes[end_of_iv:end_of_tag]
    # extra_data = packed_bytes[end_of_tag:end_of_extra_data]
    # return ciphertext, iv, tag, extra_data
    # the below returns the same as above without assigning a bunch of otherwise unused names
    return (packed_bytes[:ciphertext_size], packed_bytes[ciphertext_size:end_of_iv],
            packed_bytes[end_of_iv:end_of_tag], packed_bytes[end_of_tag:end_of_extra_data])
            
def test_packed_encrypted_data():
    import random
    data = "This is some fantastic test data"
    key = random._urandom(32)
    packed_encrypted_data = encrypt(data, key)
    plaintext = decrypt(packed_encrypted_data, key)
    assert plaintext == data
    
if __name__ == "__main__":
    test_packed_encrypted_data()