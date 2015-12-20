import os

from cryptography.exceptions import InvalidTag, InvalidSignature
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF, HKDFExpand
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import openssl
BACKEND = openssl.backend

class SecurityError(Exception): pass

class InvalidPassword(SecurityError): pass

def random_bytes(count):
    """ Generates count cryptographically secure random bytes """
    return os.urandom(count)
    
def hash_function(algorithm_name, backend=BACKEND):
    """ Returns a Hash object of type algorithm_name from 
        cryptography.hazmat.primitives.hashes """
    return hashes.Hash(getattr(hashes, algorithm_name)(), backend=backend)
    
def key_derivation_function(salt, algorithm="SHA256", length=32, 
                            iterations=100000, backend=BACKEND):
    """ Returns an key derivation function object from
        cryptography.hazmat.primitives.kdf.pbkdf2 """
    return PBKDF2HMAC(algorithm=getattr(hashes, algorithm)(),
                      length=length, salt=salt, iterations=iterations,
                      backend=backend)
      
def hkdf_expand(algorithm="SHA256", length=256, info='', backend=BACKEND):
    """ Returns an hmac based key derivation function (expand only) from
        cryptography.hazmat.primitives.hkdf. """
    return HKDFExpand(algorithm=getattr(hashes, algorithm)(),
                      length=length, info=info, backend=BACKEND)

def apply_mac(key, data, algorithm="SHA256", backend=BACKEND):
    """ Returns a message authentication code for verifying the integrity and
        authenticity of data by entities that possess the key. """
    hasher = HMAC(key, hash_function(algorithm), backend=backend)
    hasher.update(data)
    return hasher.finalize()
                    
def verify_mac(key, data, mac, algorithm="SHA256", backend=BACKEND):
    """ Verifies a message authentication code as obtained by apply_mac.
        Successful comparison indicates integrity and authenticity of the data. """
    hasher = HMAC(key, hash_function(algorithm), backend=backend)
    hasher.update(data)
    try:
        hasher.verify(mac)
    except InvalidSignature:
        return False
    else:
        return True
                            
def encrypt(data='', key='', iv=None, extra_data='', algorithm="AES",
            mode="GCM", backend=BACKEND, iv_size=16):
    """ Encrypts data with the specified key. Returns packed encrypted bytes.
        If an iv is not supplied a random one of iv_size will be generated.
        By default, the GCM mode of operation is used and the iv is 
        automatically included in the extra_data authenticated by the mode. """
    assert data and key
    iv = iv or random_bytes(iv_size)
    encryptor = Cipher(getattr(algorithms, algorithm)(key), 
                       getattr(modes, mode)(iv), 
                       backend=BACKEND).encryptor()
    if mode == "GCM":
        extra_data = iv + extra_data
        encryptor.authenticate_additional_data(extra_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    try:
        return pack_data(ciphertext, iv, encryptor.tag, extra_data)
    except AttributeError:
        return pack_data(ciphertext, iv)
    
def decrypt(packed_encrypted_data, key, algorithm="AES",
            mode="GCM", backend=BACKEND):
    """ Decrypts packed encrypted data as returned by encrypt with the same key. 
        If extra data is present, returns plaintext, extra_data. If not,
        returns plaintext."""
    ciphertext, iv, tag, extra_data = unpack_data(packed_encrypted_data,
                                                  4 if mode == "GCM" else 2)
    if mode == "GCM" and not tag:
        raise ValueError("Tag not supplied for GCM mode")
    mode_args = (iv, tag) if mode == "GCM" else (iv, )
    decryptor = Cipher(getattr(algorithms, algorithm)(key), 
                       getattr(modes, mode)(*mode_args), 
                       backend=BACKEND).decryptor()
    if mode == "GCM":
        decryptor.authenticate_additional_data(extra_data)
        # remove implicitly/automatically authenticated iv from extra_data
        extra_data = extra_data[len(iv):]
    if extra_data:
        return (decryptor.update(ciphertext) + decryptor.finalize(), extra_data)     
    else:
        return decryptor.update(ciphertext) + decryptor.finalize()      

def pack_data(*args): # copied from pride.utilities 
    """ Pack arguments into a stream, prefixed by size headers.
        Resulting bytestream takes the form:
            
            size1 size2 size3 ... sizeN data1data2data3...dataN
            
        The returned bytestream can be unpacked via unpack_data to
        return the original contents, in order. """
    sizes = []
    for arg in args:
        sizes.append(str(len(arg)))
    return ' '.join(sizes + [args[0]]) + ''.join(str(arg) for arg in args[1:])
    
def unpack_data(packed_bytes, size_count):
    """ Unpack a stream according to its size header """
    sizes = packed_bytes.split(' ', size_count)
    packed_bytes = sizes.pop(-1)
    data = []
    for size in (int(size) for size in sizes):
        data.append(packed_bytes[:size])
        packed_bytes = packed_bytes[size:]
    return data
            
def test_packed_encrypted_data():
    data = "This is some fantastic test data"
    key = random_bytes(32)
    packed_encrypted_data = encrypt(data, key)
    plaintext = decrypt(packed_encrypted_data, key)
    assert plaintext == data
    
if __name__ == "__main__":
    test_packed_encrypted_data()