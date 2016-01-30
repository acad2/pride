""" Provides authenticated encryption and decryption functions using only the python standard library.
    To be used in situations where the cryptography module cannot be installed, usually for permission reasons. """
    
import itertools
import hashlib
import hmac
import os

TEST_KEY = "\x00" * 16
TEST_MESSAGE = "This is a sweet test message :)"

def pack_data(*args): # copied from pride.utilities
    sizes = []
    for arg in args:
        sizes.append(str(len(arg)))
    return ' '.join(sizes + [args[0]]) + ''.join(str(arg) for arg in args[1:])
    
def unpack_data(packed_bytes, size_count): # copied from pride.utilities    
    sizes = packed_bytes.split(' ', size_count)
    packed_bytes = sizes.pop(-1)
    data = []
    for size in (int(size) for size in sizes):
        data.append(packed_bytes[:size])
        packed_bytes = packed_bytes[size:]
    return data
    
def _hmac_rng(key, seed, hash_function="sha512"):
    """ Generates psuedorandom bytes via HMAC. Implementation could be improved to
        a compliant scheme like HMAC-DRBG. """
    hasher = hmac.HMAC(key, seed, getattr(hashlib, hash_function))
    for counter in (str(number) for number in itertools.count()):
        yield hasher.digest()
        hasher.update(key + counter)
    
def psuedorandom_bytes(key, seed, count, hash_function="sha512"): 
    """ Generates count psuedorandom bytes, based on key and seed,
        generated using hash_function with HMAC. """
    generator = _hmac_rng(key, seed, hash_function)
    output = ''
    output_size = getattr(hashlib, hash_function)().digest_size    
    iterations, extra = divmod(count, output_size)
    for round in range(iterations + 1 if extra else iterations):
        output += next(generator)
    return output[:count]       
            
def hash_stream_cipher(data, key, nonce, hash_function="sha512"):    
    """ Generates key material and XORs with data. Provides confidentiality,
        but not authenticity or integrity. As such, this should seldom be used alone. """    
    output = bytearray(data)
    for index, key_byte in enumerate(bytearray(psuedorandom_bytes(key, nonce, len(data), hash_function))):
        output[index] ^= key_byte
    return bytes(output)    
        
def encrypt(data, key, extra_data='', nonce='', hash_function="sha512", nonce_size=32):
    """ Provides authenticated encryption of data, and authentication of 
        nonce and any extra data as well. Encryption is performed by hash_stream_cipher
        and integrity/authenticity via HMAC. """    
    nonce = nonce or os.urandom(nonce_size)
    encrypted_data = hash_stream_cipher(data, key, nonce, hash_function)
    mac_tag = hmac.HMAC(key, extra_data + nonce + encrypted_data, getattr(hashlib, hash_function)).digest()
    return pack_data(encrypted_data, nonce, mac_tag, extra_data)
        
def decrypt(data, key, hash_function="sha512"):
    """ Returns (extra_data, plaintext) when extra data is available, otherwise
        returns plaintext. Authenticity and integrity of the plaintext is
        (effectively) guaranteed. """
    hasher = getattr(hashlib, hash_function)
    encrypted_data, nonce, mac_tag, extra_data = unpack_data(data, 4)
    if hmac.HMAC(key, extra_data + nonce + encrypted_data, hasher).digest() == mac_tag:
        plaintext = hash_stream_cipher(encrypted_data, key, nonce, hash_function)
        if extra_data:
            return (extra_data, plaintext)
        else:
            return plaintext
    else:
        raise ValueError("Invalid tag")
        
def test_hmac_rng():
    output = ''
    one_megabyte = 1024 * 1024
    for random_data in _hmac_rng(TEST_KEY, TEST_MESSAGE):
        output += random_data
        if len(output) >= one_megabyte: 
            break
    
    outputs = dict((x, output.count(chr(x))) for x in xrange(256))
    import pprint
    #pprint.pprint(sorted(outputs.items()))
    
    output2 = psuedorandom_bytes(TEST_KEY, TEST_MESSAGE, one_megabyte)
    assert output == output2, (len(output), len(output2))
    
def test_encrypt_decrypt():        
    packet = encrypt(TEST_MESSAGE, TEST_KEY, "extra_data")
    #print "Encrypted packet: \n\n\n", packet
    assert decrypt(packet, TEST_KEY) == ("extra_data", TEST_MESSAGE)
    
if __name__ == "__main__":
    test_hmac_rng()
    test_encrypt_decrypt()