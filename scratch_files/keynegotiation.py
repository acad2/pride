""" Provides a simple protocol for establishing a new shared secret from an old one.
    This protocol is only valid for models that utilize initial registration through
    a secured channel (i.e. tls) or better, an out of band communication. """
import random
import itertools
import hashlib
import operator
try:
    import hmac  
except ImportError:
    try:
        from pride.security import apply_mac, verify_mac
    except ImportError:
        raise
else:
    def generate_mac(key, data, algorithm="SHA256"):
        return hmac.new(key, data, getattr(hashlib, algorithm.lower())).digest()
    
    def verify_mac(key, data, mac, algorithm="SHA256"):
        return hmac.compare_digest(hmac.new(key, data, 
                                            getattr(hashlib, algorithm.lower())).digest(),
                                   mac)

def _xor(input_one, input_two):
    return ''.join(chr(ord(character) ^ ord(input_two[index])) for 
                   index, character in enumerate(input_one))
    
def get_challenge(secret, mac_key, key_size=32, bytes_per_hash=1, 
                  hash_function="sha256", unencrypted_data=''):
    """ Usage: get_challenge(secret, key_size=32, 
                                   bytes_per_hash=1, 
                                   hash_function="sha256") => key, challenge, new_secret
        Create a challenge that only the holder of the shared secret (i.e. the client) can
        answer. Returns a randomly generated secret answer of key_size, and the challenge 
        with a message authentication code prefixed.
        
        Increasing the bytes_per_hash will increase the time required to
        crack a single hash exponentially. 
        
        Increasing key_size will increase the time required to complete the
        challenge by a multiple of how long it takes to crack a single hash"""          
    challenge = answer = ''
    hasher = getattr(hashlib, hash_function)
    hash_output = '\x00' * hasher().digestsize
    
    mac_key = secret 
    first_hash = True
    while len(answer) < key_size:
        random_bytes = random._urandom(bytes_per_hash)        
        answer += random_bytes
        hash_input = answer + secret + hasher(hash_output + ':' + secret).digest()
        hash_output = hasher(hash_input).digest()
        challenge += hash_output
        if first_hash:
            first_hash = False
            challenge = _xor(challenge, secret)   
        secret = hasher(secret).digest()    
    data_prefix_size = len(unencrypted_data)
    package = str(data_prefix_size) + ' ' + unencrypted_data + challenge
    mac = generate_mac(mac_key, package, hash_function)
    return answer, mac + package, secret
    
def solve_challenge(secret, challenge, mac_key, key_size=32, bytes_per_hash=1, 
                    hash_function="sha256"):
    hash_function = getattr(hashlib, hash_function)
    hash_size = hash_function().digestsize
    
    assert verify_mac(mac_key, challenge[hash_size:], 
                      generate_mac(mac_key, challenge[hash_size:])), "Message Authentication Code Invalid"
    challenge = challenge[32:] # remove the mac
    data_size, challenge = challenge.split(' ', 1)
    data_size = int(data_size)
    unencrypted_data = challenge[:data_size]
    challenge = challenge[data_size:]
    
    key = ''
    range_256 = [chr(x) for x in range(256)]
    previous_hash = hash_function(("\x00" * hash_function().digestsize) + ':' + secret).digest()
    
    challenge = _xor(challenge[:hash_size], secret)  + challenge[hash_size:]#first_hash = challenge[:hash_size]
    while challenge:
        current_hash = challenge[:hash_size]
        for permutation in itertools.permutations(range_256, bytes_per_hash):
            key_guess = ''.join(permutation)
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
    return key, unencrypted_data, secret
    
    
if __name__ == "__main__":
    _initial_value = random._urandom(32)
    mac_key = random._urandom(32)
    key, mac_challenge, server_secret = get_challenge(_initial_value, mac_key,
                                                      unencrypted_data="Authentication and Integrity guaranteed!")
    _key, extra_data, client_secret = solve_challenge(_initial_value, mac_challenge, mac_key)
    assert extra_data == "Authentication and Integrity guaranteed!", extra_data
    assert key == _key
    assert server_secret == client_secret    
    from pride.decorators import Timed
    print Timed(solve_challenge, 1)(_initial_value, mac_challenge, mac_key)
    