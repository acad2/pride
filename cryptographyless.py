""" Provides authenticated encryption and decryption functions using only the python standard library.
    To be used in situations where the cryptography module cannot be installed, usually for permission reasons. """
    
import itertools
import hashlib
import hmac

TEST_KEY = "\x00" * 16
TEST_MESSAGE = "This is a sweet test message :)"
TEST_NONCE = "\x00"

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
    
def hmac_rng(key, seed, hash_function="sha512"):
    hasher = hmac.HMAC(key, seed, getattr(hashlib, hash_function))
    for counter in (str(number) for number in itertools.count()):
        yield hasher.digest()
        hasher.update(key + counter)
    
def psuedorandom_bytes(key, seed, count, hash_function="sha512"):    
    generator = hmac_rng(key, seed, hash_function)
    output = ''
    output_size = getattr(hashlib, hash_function)().digest_size    
    iterations, extra = divmod(count, output_size)
    for round in range(iterations + 1 if extra else iterations):
        output += next(generator)
    return output[:count]       
        
def xor(input1, input2):
    assert len(input1) == len(input2)
    output = bytearray(input1)
    for index, byte in enumerate(bytearray(input2)):
        output[index] ^= byte
    return bytes(output)
    
def hash_stream_cipher(data, key, nonce, hash_function="sha512"):    
    data_size = len(data)
    key_material = psuedorandom_bytes(key, nonce, data_size, hash_function)
    return xor(key_material, data)
        
def encrypt(data, key, nonce, extra_data='', hash_function="sha512",):
    encrypted_data = hash_stream_cipher(data, key, nonce, hash_function)
    mac_tag = hmac.HMAC(key, extra_data + nonce + encrypted_data, getattr(hashlib, hash_function)).digest()
    return pack_data(encrypted_data, nonce, mac_tag, extra_data)
        
def decrypt(data, key, hash_function="sha512"):
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
    for random_data in hmac_rng(TEST_KEY, TEST_NONCE):
        output += random_data
        if len(output) >= one_megabyte: 
            break
    
    outputs = dict((x, output.count(chr(x))) for x in xrange(256))
    import pprint
    pprint.pprint(sorted(outputs.items()))
        
    output2 = psuedorandom_bytes(TEST_KEY, TEST_NONCE, one_megabyte)
    assert output == output2, (len(output), len(output2))
    
def test_encrypt_decrypt():        
    packet = encrypt(TEST_MESSAGE, TEST_KEY, TEST_NONCE, "extra_data")
    assert decrypt(packet, TEST_KEY) == ("extra_data", TEST_MESSAGE)
    
if __name__ == "__main__":
   # test_hmac_rng()
    test_encrypt_decrypt()