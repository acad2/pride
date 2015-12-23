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
    
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        yield iterable[position * x:x * (position + 1)]  
        
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
    challenge = encrypt(answer, key, getattr(hashlib, hash_function), bytes_per_hash=bytes_per_hash)
    package = pack_data(challenge, unencrypted_data)
    return (pack_data(generate_mac(mac_key, package, hash_function), package), 
            answer)
    
def solve_challenge(packed_challenge, key, mac_key, key_size=32, bytes_per_hash=1, 
                    hash_function="sha256"):
    mac, package = unpack_data(packed_challenge, 2)
    if verify_mac(mac_key, package, mac, hash_function):
        challenge, unencrypted_data = unpack_data(package, 2)
        hasher = getattr(hashlib, hash_function)
        return decrypt(challenge, key, hasher, hasher().digestsize, bytes_per_hash=bytes_per_hash), unencrypted_data
    else:
        raise InvalidSignature("Message authentication code mismatch")
        
def generate_padding(key, hash_size, hasher):
    key_padding = ''
    key_size = len(key)
    while key_size + len(key_padding) < hash_size:
        key_padding += hasher(key_padding + ':' + key).digest()
    return key_padding
    
def crack_round(key, current_hash, hasher, test_bytes):       
    for permutation in itertools.product(*test_bytes):
        plaintext_guess = ''.join(permutation)
        hash_output = hasher(plaintext_guess + key).digest()            
        if hash_output == current_hash:
            return plaintext_guess
            #plaintext += key_guess
            #previous_hash = hasher(hash_output + ':' + key).digest()                
            #break
    else:           
        raise ValueError("Unable to recover bytes from hash")      

def all_or_nothing(plaintext_block, ciphertext_block, key, hasher):    
    # make it to where the previous plaintext block is required to recover the next block. 
    # aims to resist parallel decryption
    return plaintext_block, ciphertext_block, hasher(plaintext_block + ':' + key).digest(), hasher

def idek_yet():    
    # xor key with "ciphertext", which in this case is hash output
    # If the key is not long enough to xor with the ciphertext,
    # then it is padded with additional bytes generated from the key
    padded_key = key + generate_padding(key, hash_size, hasher)        
    progress, plaintext, ciphertext = _next_round()
    ciphertext = _xor(ciphertext, padded_key[:hash_size]) 
    
def encrypt(plaintext, key, hasher, mode_of_operation=all_or_nothing, bytes_per_hash=1): 
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
    if len(plaintext) % bytes_per_hash:
        raise ValueError("Plaintext length not a multiple of bytes_per_hash")
    ciphertext = ''
             
    if mode_of_operation:
        for plaintext_block in slide(plaintext, bytes_per_hash):
            ciphertext_block = hasher(plaintext_block + key).digest()   
            plaintext_block, ciphertext_block, key, hasher = mode_of_operation(plaintext_block, ciphertext_block, key, hasher)
            ciphertext += ciphertext_block
        return ciphertext
    else:
        return ''.join(hasher(plaintext_block + key).digest() for 
                       plaintext_block in slide(plaintext, bytes_per_hash))
    
def decrypt(ciphertext, key, hasher, block_size, 
            mode_of_operation=all_or_nothing, bytes_per_hash=1):
    """ Decrypt the ciphertext hash chain as produced by encrypt. The amount
        of work and therefore time taken to recover the plaintext increases
        dramatically as bytes_per_hash is incremented. The bytes_per_hash
        argument must be set to the same value used by the server or the
        decryption will fail. """
    test_bytes = [RANGE_256 for count in range(bytes_per_hash)]
    plaintext = ''

    if mode_of_operation:
        for ciphertext_block in slide(ciphertext, block_size):
            plaintext_block = crack_round(key, ciphertext_block, hasher, test_bytes)
            plaintext_block, ciphertext, key, hasher = mode_of_operation(plaintext_block, ciphertext_block, key, hasher)             
            plaintext += plaintext_block
        return plaintext
    else:
        return ''.join(crack_round(key, ciphertext_block, hasher, test_bytes) for 
                       ciphertext_block in slide(ciphertext, block_size))    
    
def split_secret(secret, piece_count, hasher):
    piece_size, remainder = divmod(len(secret), piece_count)
    if remainder:
        piece_size += 1
    pieces = []
    for index, piece in enumerate(slide(secret, piece_size)):
        challenge_iv = random._urandom(16)
        hash_output = hasher(piece + challenge_iv).digest()
        pieces.append((index, hash_output, challenge_iv))
    return pieces, piece_size

def test_split_secret():
    secret = random._urandom(32)
    pieces, piece_size = split_secret(secret, 16, hashlib.sha256)
    _secret = ''
    for index, _hash, iv in pieces:
        _secret += crack_round(iv, _hash, hashlib.sha256, [RANGE_256 for x in xrange(piece_size)])    
    assert _secret == secret
    
def test_encrypt_decrypt():
    key = random._urandom(32)
    message = random._urandom(32)    
    ciphertext = encrypt(message, key, hashlib.sha256)
    plaintext = decrypt(ciphertext, key, hashlib.sha256, 32)
    assert plaintext == message, plaintext
    
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
    key = random._urandom(15)
    mac_key = random._urandom(32)
    unencrypted_data = "This is some awesome unencrypted data"
    from pride.decorators import Timed
    for bytes_per_hash in (1, 2, 3):
        if bytes_per_hash == 3:
            challenge_size = 33
        else:
            challenge_size = 32
            
        print ("Time to generate challenge with {} bytes per hash: ".format(bytes_per_hash), 
               Timed(generate_challenge, 1)(key, mac_key, unencrypted_data=unencrypted_data,
                                             bytes_per_hash=bytes_per_hash, 
                                             challenge_size=challenge_size))
                                             
        challenge, answer = generate_challenge(key, mac_key, bytes_per_hash=bytes_per_hash,
                                               unencrypted_data=unencrypted_data,
                                               challenge_size=challenge_size)
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
    test_split_secret()
    test_encrypt_decrypt()    
    test_challenge()
    test_time()
   # test_validity()
    