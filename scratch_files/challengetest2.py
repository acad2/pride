import hmac
import itertools
import random
import hashlib

RANGE_256 = tuple([chr(x) for x in range(256)])

class InvalidSignature(BaseException): pass

def pack_data(*args):
    """ Pack arguments into a stream, prefixed by size headers.
        Resulting bytestream takes the form:
            
            size1 size2 size3 ... sizeN data1data2data3...dataN
            
        The returned bytestream can be unpacked via unpack_data to
        return the original contents, in order. """
    sizes = []
    arg_strings = []
    for arg in args:
        arg_string = str(arg)
        arg_strings.append(arg_string)
        sizes.append(str(len(arg_string)))
        print "Packed data of size: ", sizes[-1]
    return ' '.join(sizes + [arg_strings[0]]) + ''.join(arg_strings[1:])
    
def unpack_data(packed_bytes, size_count):
    """ Unpack a stream according to its size header """
    sizes = packed_bytes.split(' ', size_count)
    packed_bytes = sizes.pop(-1)
    data = []
    for size in (int(size) for size in sizes):
        data.append(packed_bytes[:size])
        packed_bytes = packed_bytes[size:]
    return data
    
def generate_mac(key, data, algorithm="SHA256"):
    return hmac.new(key, data, getattr(hashlib, algorithm.lower())).digest()

def verify_mac(key, data, mac, algorithm="SHA256"):
    return hmac.compare_digest(hmac.new(key, data, 
                                        getattr(hashlib, algorithm.lower())).digest(),
                               mac)
                                   
def _xor(input_one, input_two):
    return ''.join(chr(ord(character) ^ ord(input_two[index])) for 
                   index, character in enumerate(input_one))            
            
def generate_challenge(key, mac_key, challenge_size=32, bytes_per_hash=1, 
                       hash_function="sha256", unencrypted_data='',
                       answer=bytes()):
    answer = answer or random._urandom(challenge_size)
    challenge = encrypt(answer, key, bytes_per_hash, hash_function)
    package = pack_data(challenge, unencrypted_data)
    print "Packed challenge and unencrypted data: ", len(package), package[:16]
  #  print
  #  print package
  #  print
    mac = generate_mac(mac_key, package, hash_function)
    print "Packing mac and data: ",
  #  print
  #  print pack_data((mac, package))
    return pack_data(mac, package), answer
    
def solve_challenge(packed_challenge, key, mac_key, key_size=32, bytes_per_hash=1, 
                    hash_function="sha256"):
    mac, package = unpack_data(packed_challenge, 2)
    if verify_mac(mac_key, package, hash_function):
        challenge, unencrypted_data = unpack_data(package, 2)
        return decrypt(challenge, key, bytes_per_hash, hash_function), unencrypted_data
    else:
        raise InvalidSignature("Message authentication code mismatch")
        
def encrypt(plaintext, key, bytes_per_hash=1, hash_function="sha256"):
    ciphertext = progress = ''
    hasher = getattr(hashlib, hash_function)
    hash_output = '\x00' * hasher().digestsize
    block_size = len(key)
    first_hash = True
    while plaintext:
        random_bytes = plaintext[:bytes_per_hash]
        progress += random_bytes
        hash_input = progress + key + hasher(hash_output + ':' + key).digest()
        hash_output = hasher(hash_input).digest()
        ciphertext += hash_output
        if first_hash:
            first_hash = False
            ciphertext = _xor(ciphertext, key)   
        key = hasher(key).digest()    
        plaintext = plaintext[bytes_per_hash:]      
    return ciphertext
    
def decrypt(ciphertext, key, bytes_per_hash=1, hash_function="sha256"):
    range_256 = RANGE_256
    hash_function = getattr(hashlib, hash_function)
    hash_size = hash_function().digestsize
    plaintext = ''
    
    previous_hash = hash_function(("\x00" * hash_function().digestsize) + ':' + key).digest()
    
    ciphertext = _xor(ciphertext[:hash_size], key)  + ciphertext[hash_size:]
    while ciphertext:
        current_hash = ciphertext[:hash_size]
        for permutation in itertools.permutations(range_256, bytes_per_hash):
            key_guess = ''.join(permutation)
            hash_output = hash_function(plaintext + key_guess + key + previous_hash).digest()
            if hash_output == current_hash:
                plaintext += key_guess
                new_key_length = len(plaintext)
                key = hash_function(key).digest()
                previous_hash = hash_function(hash_output + ':' + key).digest()                
                break          
        else:            
            raise ValueError("Unable to recover bytes from hash")        
        
        ciphertext = ciphertext[hash_size:]
    return plaintext
    
def test_encrypt_decrypt():
    key = random._urandom(32)
    message = random._urandom(32)
    ciphertext = encrypt(message, key)
    assert decrypt(ciphertext, key) == message, decrypt(ciphertext, key)
    
def test_challenge():
    key = random._urandom(32)
    mac_key = random._urandom(32)
    unencrypted_data = "This is some awesome unencrypted data"
    challenge, answer = generate_challenge(key, mac_key,
                                           unencrypted_data=unencrypted_data)
    _answer, _unencrypted_data = solve_challenge(challenge, key, mac_key)
    assert _answer == answer
    assert _unencrypted_data == unencrypted_data
    
if __name__ == "__main__":
    test_encrypt_decrypt()    
    test_challenge()