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
        encryptor.authenticate_additional_data(iv + extra_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    try:
        return (ciphertext, iv + extra_data, encryptor.tag)
    except AttributeError:
        return (ciphertext, iv)
    
def decrypt(ciphertext, key, iv, tag=None, extra_data='', algorithm="AES",
            mode="GCM", backend=BACKEND):
    if mode == "GCM" and not tag:
        raise ValueError("Tag not supplied for GCM mode")
    mode_args = (iv, tag) if mode == "GCM" else (iv, )
    decryptor = Cipher(getattr(algorithms, algorithm)(key), 
                       getattr(modes, mode)(*mode_args), 
                       backend=BACKEND).decryptor()
    if mode == "GCM":
        decryptor.authenticate_additional_data(iv + extra_data)
    return decryptor.update(ciphertext) + decryptor.finalize()
            