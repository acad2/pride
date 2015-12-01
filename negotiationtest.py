
#


# attacker receives hashes also
# attacker begins cracking hash:
#    number of unknown bytes: x + len(secret) per hash
#    theoretically cannot be cracked given the security of the underlying hash function    
#    UNLESS the attacker observed or obtained the initial secret value?

import random
import itertools
from hashlib import sha256

# generate and establish initial secret
initial_value = random._urandom(32)
# ... skipping how the exchange actually occurs, for brevity
# the initial_value must be transmitted securely (i.e. via tls) or out of band

# assume now both client and server have knowledge of the secret initial_value
def server_login(secret, key_size=32, bytes_per_hash=2):    
    # on login:
    #    generate x random bytes and append the secret
    #    hash the resultant string of length x + len(secret), buffer the bytes
    #    repeat the above, appending new hashes to the buffer while
    #    ensuring to hash the secret at each iteration
    #    send hashes to client
    key = ''
    challenge = ''
    while len(key) < key_size:
        random_bytes = random._urandom(2)
        key += random_bytes
        hash_input = random_bytes + secret
        challenge += sha256(hash_input).digest()
        secret = sha256(secret).digest()
    print "Generated key: ", key
    return key, challenge, secret
    
# client receives hashes
def client_login(secret, challenge, key_size=32, bytes_per_hash=2, hash_size=32):
    # client begins cracking hashes:
    #    number of unknown bytes: x; number of known bytes len(secret)
    #    x bytes are cracked in trivial amount of time and returned as part of the key
    #    repeat until all hashes are cracked, ensuring to hash the secret each round
    key = ''
    range_256 = [chr(x) for x in range(256)]
    while challenge:
        hash_output = challenge[:hash_size]
        for permutation in itertools.permutations(range_256, bytes_per_hash):
            #print permutation
            attempt = ''.join(permutation)
            if sha256(attempt + secret).digest() == hash_output:
                key += attempt
                break          
        print "Recovered part of key: ", key
        secret = sha256(secret).digest()
        challenge = challenge[hash_size:]
    return key, secret
    
if __name__ == "__main__":
    key, challenge, server_secret = server_login(initial_value)
    _key, client_secret = client_login(initial_value, challenge)
    assert key == _key
    assert server_secret == client_secret