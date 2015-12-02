""" Provides a simple protocol for establishing a new shared secret from an old one.
    This protocol is only valid for models that utilize initial registration through
    a secured channel (i.e. tls) or better, an out of band communication. """
import random
import itertools
import hashlib

# generate and establish an initial secret, for example via:
_initial_value = random._urandom(32)
# ... skipping how the exchange actually occurs, for brevity
# the initial_value MUST be transmitted securely (i.e. via tls or similar) or out of band!

# assuming both client and server have knowledge of the secret initial_value
def get_login_challenge(secret, key_size=32, bytes_per_hash=1, hash_function="sha256"):
    """ Usage: get_login_challenge(secret, key_size=32, 
                                   bytes_per_hash=1, 
                                   hash_function="sha256") => key, challenge, new_secret
        Create a challenge that only the holder of the shared secret (i.e. the client) can
        answer. Returns a randomly generated shared secret of key_size, the challenge with
        a message authentication code prefixed, and the new shared secret. """        
    # on login:
    #    generate x random bytes and append the secret + the previous hash (or len(digest) null bytes for the first hash)
    #    hash the resultant string of length x + len(secret), buffer the bytes
    #    repeat the above, appending new hashes to the buffer while
    #    ensuring to hash the secret at each iteration
    #    send hashes to client
    challenge = key = ''
    hash_function = getattr(hashlib, hash_function)
    hash_output = '\x00' * 32
    
    # below is just for simplicity sake; DO NOT use the secret as the mac key directly
    # use hkdf to derive a mac key from the secret
    mac_key = secret 
    while len(key) < key_size:
        random_bytes = random._urandom(bytes_per_hash)
        key += random_bytes
        
        hash_input = random_bytes + secret + hash_output
        hash_output = hash_function(hash_input).digest()
        challenge += hash_output
   #     print "Created challenge: ", hash_function(hash_input).digest()
        secret = hash_function(secret).digest()        
    mac = hash_function(challenge + mac_key).digest()
  #  print "Generated key: ", key
    return key, mac + challenge, secret
    
def client_attempt_login(secret, challenge, key_size=32, bytes_per_hash=1, hash_size=32, hash_function="sha256"):
    # client begins cracking hashes:
    #    number of unknown bytes: x; number of known bytes len(secret)
    #    x bytes are cracked in trivial amount of time and returned as part of the key
    #    repeat until all hashes are cracked, ensuring to hash the secret each round
    #    hashes must be cracked in order
    hash_function = getattr(hashlib, hash_function)
    assert hash_function(challenge[32:] + secret).digest() == challenge[:32], "Message Authentication Code Invalid"
    challenge = challenge[32:] # remove the mac
    key = ''
    range_256 = [chr(x) for x in range(256)]
    previous_hash = "\x00" * 32    
    
    while challenge:
        hash_output = challenge[:hash_size]
    #    print "Cracking challenge: ", hash_output
        for permutation in itertools.permutations(range_256, bytes_per_hash):
            key_guess = ''.join(permutation)
            #print "Guessing: ", key_guess
            if hash_function(key_guess + secret + previous_hash).digest() == hash_output:
                key += key_guess
                new_key_length = len(key)
                #print "Cracked and recoved key fragment"
                previous_hash = hash_output
                break          
        else:            
            raise ValueError("Unable to recover bytes from hash")        
        secret = hash_function(secret).digest()
        challenge = challenge[hash_size:]
    #print "Recovered key ", len(key)
    return key, secret
    
# assume attacker receives hashes also...
# attacker begins cracking hash:
#    number of unknown bytes: x + len(secret) per hash
#    theoretically cannot crack a single hash, assuming the security of the 
#    underlying hash function holds true
#    UNLESS the attacker observed or obtained the secret value!
#    the hashes must be cracked in order
    
if __name__ == "__main__":
    key, mac_challenge, server_secret = get_server_login_challenge(initial_value)
    _key, client_secret = client_login(initial_value, mac_challenge)
    assert key == _key
    assert server_secret == client_secret    
    from pride.decorators import Timed
    print Timed(client_login, 1)(initial_value, mac_challenge)
