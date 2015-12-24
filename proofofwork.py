import operator
import getpass
import hmac
import itertools
import random
import hashlib

RANGE_256 = tuple([chr(x) for x in range(256)])
PRINTABLE_ASCII = tuple(chr(x) for x in xrange(32, 127))
SHA256 = lambda hash_input: hashlib.sha256(hash_input).digest()

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
    _hasher = getattr(hashlib, hash_function)
    function = lambda hash_input: _hasher(hash_input).digest()
    challenge = encrypt(answer, key, function, bytes_per_hash=bytes_per_hash)
    package = pack_data(challenge, unencrypted_data)
    return (pack_data(generate_mac(mac_key, package, hash_function), package), 
            answer)
    
def solve_challenge(packed_challenge, key, mac_key, key_size=32, bytes_per_hash=1, 
                    hash_function="sha256"):
    mac, package = unpack_data(packed_challenge, 2)
    if verify_mac(mac_key, package, mac, hash_function):
        challenge, unencrypted_data = unpack_data(package, 2)
        _hasher = getattr(hashlib, hash_function)
        function = lambda hash_input: _hasher(hash_input).digest()
        return decrypt(challenge, key, function, _hasher().digestsize, bytes_per_hash=bytes_per_hash), unencrypted_data
    else:
        raise InvalidSignature("Message authentication code mismatch")
        
def generate_padding(key, hash_size, function):
    key_padding = ''
    key_size = len(key)
    while key_size + len(key_padding) < hash_size:
        key_padding += function(key_padding + ':' + key)
    return key_padding
    
def brute_force(output, function, test_bytes, pre_key='', post_key=''):
    """ Attempt to find the input to function that produced output.
        
        test_bytes is an iterable of iterables; Each iterable contains the
        characters to be tested at the correlated index; characters may
        be byte strings of arbitrary length.
        
        pre_key and post_key are what information, if any, is already known 
        of the input that produced output. 
        
        Test guesses are formed by taking the next successive cartesian product
        from test_bytes. 
        
        Test function input is a concatenation of (pre_key | guess | post_key).
        
        Returns bytes of the permutation that produced output; Only the cracked
        bytes are returned, not the concatenation of the keys with the guess."""        
    for permutation in itertools.product(*test_bytes):
        #print "Guessing: ", ''.join(permutation)
        if function(pre_key + ''.join(permutation) + post_key) == output:
            return ''.join(permutation)
    else:           
        raise ValueError("Unable to recover bytes from hash")      

def identity_mode(plaintext_block, ciphertext_block, key, function):
    """ A do-nothing mode of operation/key rotation function.
        Returns inputs unmodified. 
        
        Net effect(s): None """
    return plaintext_block, ciphertext_block, key, function
    
def xor_with_key(plaintext_block, ciphertext_block, key, function):
    """ Xor the key with "ciphertext" (which in this case is hash output)
        If the key is not long enough to xor with the ciphertext,
        then it is padded with additional bytes generated from the key
        
        Net effect(s): 
        
            - The round key must known to begin to decrypt the block.
            - Ciphering is more effective in serial then in parallel. """
    ciphertext_size = len(ciphertext_block)
    if ciphertext_size > len(key):
        padded_key = key + generate_padding(key, ciphertext_size, function)
    else:
        padded_key = key
    ciphertext_block = _xor(ciphertext_block, padded_key[:ciphertext_size])
    return plaintext_block, ciphertext_block, key, function
    
def all_or_nothing(plaintext_block, ciphertext_block, key, function):
    """ Update the key with the previous plaintext. In order to derive the key
        for the next round, the previous plaintext must be obtained. 
        
        Net effect(s): 
            
            - In order to efficiently decrypt block N, block N-1 must first be decrypted.
            - Encryption cannot be done in serial
            - Decryption can be done more efficiently in serial then in parallel.
                     
        Note the effects presume that the decryptor wishes to use the informational
        advantage gained by decrypting cumulative plaintexts. A decryptor with the
        key can still attempt to decrypt block N1 without decrypting block N0 first
        by sheer brute force, without the trapdoor information. Doing so would
        require guessing the first plaintext bytes and the second at the same time,
        resulting in increased complexity and therefore time slowdown, potentially
        defeating any benefits of parallelism. """
    return plaintext_block, ciphertext_block, function(plaintext_block + ':' + key), function
    
def encrypt(plaintext, key, function, mode_of_operation=xor_with_key, 
            key_rotation=all_or_nothing, bytes_per_hash=1): 
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
    
    for plaintext_block in slide(plaintext, bytes_per_hash):
        ciphertext_block = function(plaintext_block + key) 
        (plaintext_block, ciphertext_block, 
         key, function) = mode_of_operation(plaintext_block, ciphertext_block, key, function)
        
        ciphertext += ciphertext_block
        
        (plaintext_block, ciphertext_block, 
         key, function) = key_rotation(plaintext_block, ciphertext_block, key, function)
    return ciphertext
    
def decrypt(ciphertext, key, function, block_size, mode_of_operation=xor_with_key, 
            key_rotation=all_or_nothing, bytes_per_hash=1):
    """ Decrypt the ciphertext hash chain as produced by encrypt. The amount
        of work and therefore time taken to recover the plaintext increases
        dramatically as bytes_per_hash is incremented. The bytes_per_hash
        argument must be set to the same value used by the server or the
        decryption will fail. """
    test_bytes = [RANGE_256 for count in range(bytes_per_hash)]
    plaintext = plaintext_block = ''

    for ciphertext_block in slide(ciphertext, block_size):
        (plaintext_block, ciphertext_block, 
         key, function) = mode_of_operation(plaintext_block, ciphertext_block, 
                                            key, function)
                                          
        plaintext_block = brute_force(ciphertext_block, function, test_bytes, post_key=key)
        plaintext += plaintext_block
        
        (plaintext_block, ciphertext_block,
         key, function) = key_rotation(plaintext_block, ciphertext_block, key, function)            
    return plaintext   
    
def split_secret(secret, piece_count, function):    
    piece_size, remainder = divmod(len(secret), piece_count - 1)    
    pieces = []
    for index in range(piece_count - 1):
        piece = secret[index * piece_size:(index + 1) * piece_size]
        challenge_iv = random._urandom(16)
        hash_output = function(piece + challenge_iv)
        pieces.append((index, hash_output, challenge_iv))
    last_iv = random._urandom(16)
    #print "Creating last block: ", -remainder
    pieces.append((index + 1, function(secret[-remainder:] + last_iv), last_iv))
    return pieces, function(secret), piece_size

def recover_secret_fragment(_hash, iv, piece_size, function=SHA256):
    return brute_force(_hash, function, [RANGE_256 for x in xrange(piece_size)], post_key=iv) 

def recover_secret_from_fragments(master_secret, available_pieces, shares, 
                                  last_share_size, function=SHA256):
    guesses = [RANGE_256 for count in range(shares - 1)]
    
    #_secret += recover_secret_fragment(last_hash, last_iv, len(secret) % (shares - 1))
    guesses.append
    for fragment_index, fragment in sorted(available_pieces, key=operator.itemgetter(0)):
        guesses[fragment_index] = [fragment]
    
    if fragment_index != shares:
        guesses.extend((RANGE_256 for count in range(last_share_size)))
  #  print "Recovering secret from fragments with guesses: ", guesses
    return brute_force(master_secret, function, guesses)
    
def create_password_recovery(function, trapdoor_information_size=16, password='',
                             password_prompt="Please enter the password to create a recovery hash: "):
    trapdoor_information = random._urandom(trapdoor_information_size)
    return (function((password or getpass.getpass(password_prompt)) + trapdoor_information), 
            trapdoor_information)
            
def recover_password(recovery_hash, trapdoor_information, function=SHA256,
                     character_set=PRINTABLE_ASCII):
    print "Welcome to the password recovery program"
    print "First, please enter your password, as best as you can remember."
    print "If you cannot remember a character, supply your best guess"
    guess = getpass.getpass("Please enter password: ")
    print "Next, enter your password again, and replace characters you are not certain of with a space"
    _guess = getpass.getpass("Please enter password: ")
    test_characters = []
    for index, character in enumerate(_guess):
        if character == ' ' and guess[index] != ' ':
            characters = [character.lower(), character.upper()]
            _characters = [ord(char) for char in characters]
            test_characters.append([char for char in character_set if ord(char) not in _characters])
        else:
            test_characters.append([character])
    
    return brute_force(recovery_hash, function, test_characters, post_key=trapdoor_information)
                      
def test_password_recovery():
    test_password = "This is a test"
    recovery_hash, iv = create_password_recovery(SHA256, password=test_password)
    recovered_password = recover_password(recovery_hash, iv)
    assert recovered_password == test_password
        
def test_split_secret():
    secret = "This is a test. " * 2    
    shares = 31
    pieces, master_secret, piece_size = split_secret(secret, shares, SHA256)
    
    recovered_pieces = []
    for index, _hash, iv in pieces[:shares - 1]:
        recovered_pieces.append((index, recover_secret_fragment(_hash, iv, piece_size)))
                           
    _secret = ''.join((item[1] for item in recovered_pieces))
    
    last_share_size = len(secret) % (shares - 1)
    last_index, last_hash, last_iv = pieces[shares - 1]
    _secret += recover_secret_fragment(last_hash, last_iv, len(secret) % (shares - 1))
    assert _secret == secret 
    
    # attempt to recover secret without last block
    recovered_secret = recover_secret_from_fragments(master_secret, recovered_pieces, 
                                                     shares, last_share_size)
    assert recovered_secret == secret
    
def test_encrypt_decrypt():
    key = random._urandom(32)
    message = random._urandom(32)    
    ciphertext = encrypt(message, key, SHA256)
    plaintext = decrypt(ciphertext, key, SHA256, 32)
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
    #test_password_recovery()
    test_split_secret()
    test_encrypt_decrypt()    
    test_challenge()
    #test_time()
   # test_validity()
    