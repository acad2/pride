""" Provides a simple protocol for establishing a new shared secret from an old one.
    This protocol is only valid for models that utilize initial registration through
    a secured channel (i.e. tls) or better, an out of band communication. """
import random
import itertools
import hashlib
import operator

def _xor(input_one, input_two):
    return ''.join(chr(ord(character) ^ ord(input_two[index])) for 
                   index, character in enumerate(input_one))
    
# generate and establish an initial secret, for example via:
_initial_value = random._urandom(32)
# ... skipping how the exchange actually occurs, for brevity
# the initial_value MUST be transmitted securely (i.e. via tls or similar) or out of band!

# assuming both client and server have knowledge of the secret initial_value
def get_challenge(secret, key_size=32, bytes_per_hash=1, hash_function="sha256",
                  unencrypted_authenticated_associated_data=''):
    """ Usage: get_challenge(secret, key_size=32, 
                                   bytes_per_hash=1, 
                                   hash_function="sha256") => key, challenge, new_secret
        Create a challenge that only the holder of the shared secret (i.e. the client) can
        answer. Returns a randomly generated shared secret of key_size, and the challenge 
        with a message authentication code prefixed.
        
        Increasing the bytes_per_hash will increase the time required to
        crack a single hash exponentially. 
        
        Increasing key_size will increase the time required to complete the
        challenge by a multiple of how long it takes to crack a single hash"""          
    # on login:
    #    generate x random bytes and append the secret + the previous hash (or len(digest) null bytes for the first hash)
    #    hash the resultant string of length x + len(secret), buffer the bytes
    #    repeat the above, appending new hashes to the buffer while
    #    ensuring to hash the secret at each iteration
    #    send hashes to client
    challenge = key = ''
    hash_function = getattr(hashlib, hash_function)
    hash_output = '\x00' * hash_function().digestsize
    
    # below is just for simplicity sake; DO NOT use the secret as the mac key directly
    # use hkdf to derive a mac key from the secret
    mac_key = secret 
    first_hash = True
    while len(key) < key_size:
        random_bytes = random._urandom(bytes_per_hash)        
        key += random_bytes
        hash_input = key + secret + hash_function(hash_output + ':' + secret).digest()
        hash_output = hash_function(hash_input).digest()
        challenge += hash_output
        if first_hash:
            first_hash = False
            challenge = _xor(challenge, secret)
   #     print "Created challenge: ", hash_function(hash_input).digest()
        secret = hash_function(secret).digest()    
    data_prefix_size = len(unencrypted_authenticated_associated_data)
    package = str(data_prefix_size) + ' ' + unencrypted_authenticated_associated_data + challenge
    mac = hash_function(package + mac_key).digest()
    return key, mac + package, secret
    
def solve_challenge(secret, challenge, key_size=32, bytes_per_hash=1, hash_function="sha256"):
    # client begins cracking hashes:
    #    number of unknown bytes: x; number of known bytes len(secret)
    #    x bytes are cracked in trivial amount of time and returned as part of the key
    #    repeat until all hashes are cracked, ensuring to hash the secret each round
    #    hashes must be cracked in order
    hash_function = getattr(hashlib, hash_function)
    hash_size = hash_function().digestsize
    assert hash_function(challenge[hash_size:] + secret).digest() == challenge[:hash_size], "Message Authentication Code Invalid"
    challenge = challenge[32:] # remove the mac
    data_size, challenge = challenge.split(' ', 1)
    data_size = int(data_size)
    unencrypted_authenticated_associated_data = challenge[:data_size]
    challenge = challenge[data_size:]
    
    key = ''
    range_256 = [chr(x) for x in range(256)]
    previous_hash = hash_function(("\x00" * hash_function().digestsize) + ':' + secret).digest()
    
    challenge = _xor(challenge[:hash_size], secret)  + challenge[hash_size:]#first_hash = challenge[:hash_size]
    while challenge:
        current_hash = challenge[:hash_size]
    #    print "Cracking challenge: ", current_hash
        for permutation in itertools.permutations(range_256, bytes_per_hash):
            key_guess = ''.join(permutation)
            #print "Guessing: ", key_guess
            hash_output = hash_function(key + key_guess + secret + previous_hash).digest()
            if hash_output == current_hash:
                key += key_guess
                new_key_length = len(key)
                secret = hash_function(secret).digest()
                previous_hash = hash_function(hash_output + ':' + secret).digest()                
                break          
        else:            
            raise ValueError("Unable to recover bytes from hash")        
        
        challenge = challenge[hash_size:]
    #print "Recovered key ", len(key)
    return key, unencrypted_authenticated_associated_data, secret
    
# assume attacker receives hashes also...
# attacker begins cracking hash:
#    number of unknown bytes: x + len(secret) per hash
#    theoretically cannot crack a single hash, assuming the security of the 
#    underlying hash function holds true
#    UNLESS the attacker observed or obtained the secret value!
#    the hashes must be cracked in order
    
if __name__ == "__main__":
    key, mac_challenge, server_secret = get_challenge(_initial_value, 
                                                      unencrypted_authenticated_associated_data="Authentication and Integrity guaranteed!")
    _key, extra_data, client_secret = solve_challenge(_initial_value, mac_challenge)
    assert extra_data == "Authentication and Integrity guaranteed!", extra_data
    assert key == _key
    assert server_secret == client_secret    
    from pride.decorators import Timed
    print Timed(solve_challenge, 1)(_initial_value, mac_challenge)
    