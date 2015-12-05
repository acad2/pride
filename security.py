from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
BACKEND = openssl.backend

class SecurityError(Exception): pass

def hash_function(algorithm_name):
    return hashes.Hash(getattr(hashes, algorithm_name)(), backend=BACKEND)
    
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
            
def hkdf_expand(hash_function="SHA256", length=256, info='', backend=BACKEND):
    return HKDFExpand(algorithm=getattr(hashes, hash_function)(),
                      length=length, info=info, backend=BACKEND)