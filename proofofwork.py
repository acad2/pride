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
    return (pack_data(generate_mac(mac_key, package, hash_function), package), 
            answer)
    
def solve_challenge(packed_challenge, key, mac_key, key_size=32, bytes_per_hash=1, 
                    hash_function="sha256", answer=''):
    mac, package = unpack_data(packed_challenge, 2)
    if verify_mac(mac_key, package, mac, hash_function):
        challenge, unencrypted_data = unpack_data(package, 2)
        return decrypt(challenge, key, bytes_per_hash, hash_function, answer=answer), unencrypted_data
    else:
        raise InvalidSignature("Message authentication code mismatch")
        
def encrypt(plaintext, key, bytes_per_hash=1, hash_function="sha256"): 
    """ An encryption function with an associated work factor. Returns a
        ciphertext encrypted under key. 
        
        The bytes_per_hash function adjusts two factors: First, by a smaller
        amount, as bytes_per_hash increases, generating the challenge tends
        to take less time. Second, as bytes_per_hash increases, solving the
        challenge tends to take significantly more time.
        
        As an example, consider a server that requires proof of work with
        each request submitted by a client. An overloaded server could 
        increment the bytes per hash to crack. As a result, it would spend 
        less time generating each challenge, while clients would take 
        significantly longer to solve each challenge. The net effect is
        an actual reduction in traffic, as clients cannot effectively make
        additional requests until the current challenge is solved.

        Note that the ciphertext is necessarily significantly larger then the 
        plaintext. This limits practicality of this form of encryption mostly
        to proof of work/time released schemes."""
    ciphertext = progress = ''
    hasher = getattr(hashlib, hash_function)
    hash_output = '\x00' * hasher().digestsize
    block_size = len(key)
    first_hash = True
    counter = 1
    
    # pad plaintext to multiple of bytes_per_hash
    plaintext += "\x00" * (bytes_per_hash - (len(plaintext) % bytes_per_hash))
    
    while plaintext:
        progress += plaintext[:bytes_per_hash]
        # making the hash input include the cumulative progress aims to ensure that
        # hashes must be cracked in order. 
        hash_input = progress + key + hasher(hash_output + ':' + key).digest()
        hash_output = hasher(hash_input).digest()
        ciphertext += hash_output
        
        if first_hash:
            first_hash = False
            # the goal here is to make it to where you cannot begin to crack
            # the first hash unless you have the key
            ciphertext = _xor(ciphertext, key)
        counter += 1
        key = hasher(key).digest()    
        plaintext = plaintext[bytes_per_hash:]
    return ciphertext
    
def decrypt(ciphertext, key, bytes_per_hash=1, hash_function="sha256", answer=''):
    """ Decrypt the ciphertext hash chain as produced by encrypt. The amount
        of work and therefore time taken to recover the plaintext increases
        dramatically as bytes_per_hash is incremented. The bytes_per_hash
        argument must be set to the same value used by the server or the
        decryption will fail. """
    test_bytes = [RANGE_256 for count in range(bytes_per_hash)]
    hash_function = getattr(hashlib, hash_function)
    hash_size = hash_function().digestsize
    plaintext = ''
    
    previous_hash = hash_function(("\x00" * hash_function().digestsize) + ':' + key).digest()
    
    # remove the key to reveal the first hash
    ciphertext = _xor(ciphertext[:hash_size], key)  + ciphertext[hash_size:]  
    while ciphertext:
        current_hash = ciphertext[:hash_size]
        for permutation in itertools.product(*test_bytes):
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
    assert decrypt(ciphertext, key)[:32] == message, decrypt(ciphertext, key)
    
def test_challenge():
    key = random._urandom(32)
    mac_key = random._urandom(32)
    unencrypted_data = "This is some awesome unencrypted data"
    challenge, answer = generate_challenge(key, mac_key,
                                           unencrypted_data=unencrypted_data)
    _answer, _unencrypted_data = solve_challenge(challenge, key, mac_key)
    assert _answer == answer
    assert _unencrypted_data == unencrypted_data
    
def test_time():
    key = random._urandom(32)
    mac_key = random._urandom(32)
    unencrypted_data = "This is some awesome unencrypted data"
    from pride.decorators import Timed
    for bytes_per_hash in (1, 2, 3):
        print ("Time to generate challenge with {} bytes per hash: ".format(bytes_per_hash), 
               Timed(generate_challenge, 1)(key, mac_key, unencrypted_data=unencrypted_data,
                                             bytes_per_hash=bytes_per_hash))
        challenge, answer = generate_challenge(key, mac_key, bytes_per_hash=bytes_per_hash,
                                               unencrypted_data=unencrypted_data)
        print ("Time to solve challenge with {} bytes per hash: ".format(bytes_per_hash),
               Timed(solve_challenge, 1)(challenge, key, mac_key, bytes_per_hash=bytes_per_hash))
        
def test_validity():
    key = random._urandom(32)
    mac_key = random._urandom(32)
    unencrypted_data = "This is some awesome unencrypted data"
    for x in xrange(100):
        challenge, answer = generate_challenge(key, mac_key, unencrypted_data=unencrypted_data,
                                               bytes_per_hash=3)
        _answer, data = solve_challenge(challenge, key, mac_key, bytes_per_hash=3, answer=answer)
        assert _answer == answer
        
if __name__ == "__main__":
    test_encrypt_decrypt()    
   # test_challenge()
   # test_time()
   # test_validity()
    