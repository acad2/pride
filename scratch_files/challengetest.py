import itertools
import random
import hashlib

RANGE_256 = tuple([chr(x) for x in range(256)])

def _xor(input_one, input_two):
    print len(input_one), len(input_two)

    return ''.join(chr(ord(character) ^ ord(input_two[index])) for 
                   index, character in enumerate(input_one))
                   
def encrypt(plaintext, key, bytes_per_hash=1, hash_function="sha256"):
    ciphertext = progress = ''
    hasher = getattr(hashlib, hash_function)
    hash_output = '\x00' * hasher().digestsize
    
    first_hash = True
    while plaintext:
        random_bytes = random._urandom(bytes_per_hash)        
        progress += plaintext[:bytes_per_hash]
        hash_input = progress + key + hasher(hash_output + ':' + key).digest()
        hash_output = hasher(hash_input).digest()
        print "Created hash: "
        print
        print hash_output
        ciphertext += hash_output
        if first_hash:
            first_hash = False
            ciphertext = _xor(ciphertext, key)   
        key = hasher(key).digest()   
        plaintext = plaintext[bytes_per_hash:]
        
    return ciphertext
    
def decrypt(ciphertext, key, bytes_per_hash=1, hash_function="sha256"):
    _range_256 = RANGE_256
    hash_function = getattr(hashlib, hash_function)
    hash_size = hash_function().digestsize
    previous_hash = hash_function(("\x00" * hash_function().digestsize) + ':' + key).digest()
    plaintext = ''
    while ciphertext:
        current_hash = ciphertext[:hash_size]
        print "Cracking: "
        print
        print current_hash
        for permutation in itertools.permutations(_range_256, bytes_per_hash):
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
    message = "This is such an awesome test message... "
    ciphertext = encrypt(message, key)
    assert decrypt(ciphertext, key) == message
    
if __name__ == "__main__":
    test_encrypt_decrypt()