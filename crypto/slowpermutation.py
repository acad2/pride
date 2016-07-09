import hashlib
from timeit import default_timer as timestamp
from utilities import slide, brute_force
        
def tunable_hash(data, key, work_factor, algorithm="sha224"):
    return hashlib.pbkdf2_hmac(algorithm, data, key, work_factor)
    
def encrypt(data, key, iv, work_factor=1000, decryption_factor=1, hash_function=tunable_hash):
    ciphertext = b''
    cumulative_input = b''
    
    for data_bytes in slide(data, decryption_factor):        
        output = hash_function(iv + cumulative_input + data_bytes, key, work_factor)
        ciphertext += output
        cumulative_input += data_bytes
    
    return ciphertext
    
def decrypt(ciphertext, key, iv, work_factor=1, decryption_factor=1, hash_function=tunable_hash):
    plaintext = b''    
    
    test_bytes = [bytes(bytearray(range(256))) for factor in range(decryption_factor)]
    _hash_function = lambda data: hash_function(data, key, work_factor)
    block_size = len(_hash_function(''))
    
    for ciphertext_bytes in slide(ciphertext, block_size):        
        data_bytes = brute_force(ciphertext_bytes, _hash_function, test_bytes, 
                                 prefix=iv + plaintext)
                                 
        plaintext += data_bytes        
    
    return plaintext
  
def slow_hash(data, iv, work_factor1=1, hash_function=tunable_hash):
    """ usage: slow_hash(data, iv, work_factor1=1, 
                         hash_function=tunable_hash) => digest
                         
        Produce a digest in a relatively slow and computationally expensive manner.
        Digests may be verified in very little time by calling verify_digest."""
    # current problems:
    # doesn't use enough RAM
    # low diffusion
    # search for the right hash is obviously not constant time
    digest = b''
    state = b''
    _looking_for = list(iv)
    looking_for = ''.join(_looking_for.pop(0) for factor in range(work_factor1))
    for data_bytes in slide(data, work_factor1):
        current_hash = hash_function(iv + state + data_bytes)
        state += current_hash
        while current_hash[:work_factor1] != looking_for:
            hash_input = current_hash
            current_hash = hash_function(hash_input)
            state += current_hash
        digest += hash_input
        looking_for = ''.join(_looking_for.pop(0) for factor in range(work_factor1))
    
    return digest
            
def verify_digest(digest, iv, work_factor1=1, hash_function=tunable_hash):
    digest_size = len(hash_function(''))    
    _looking_for = list(iv)
    looking_for = ''.join(_looking_for.pop(0) for count in range(work_factor1))
    failure = False    
    for current_hash in slide(digest, digest_size):        
        hash_input = current_hash
        if hash_function(hash_input)[:work_factor1] != looking_for:
            failure = True
        else:
            constant_time_operation = True
        looking_for = ''.join(_looking_for.pop(0) for count in range(work_factor1))
    return not failure                
                
def test_encrypt_decrypt():
    message = "Testing!"
    key = "\x00" * 16
    iv = "\x00" * 16    
    work_factor = 1
    decryption_factor = 1
    start = timestamp()
    ciphertext = encrypt(message, key, iv, work_factor, decryption_factor)
    encryption_time = timestamp() - start
    
    print "Plaintext size: ", len(message)
    print "Ciphertext size: ", len(ciphertext)
    
    start = timestamp()
    plaintext = decrypt(ciphertext, key, iv, work_factor, decryption_factor)
    decryption_time = timestamp() - start
    assert plaintext == message
    
    print "Encryption time: ", encryption_time
    print "Decryption time: ", decryption_time

def test_slow_hash():
    data = "Testing!"
    iv = "\x00" * 16
    work_factor1 = 1
    work_factor2 = 1
    hash_function = lambda data: tunable_hash(data, iv, work_factor2)
    start = timestamp()
    digest = slow_hash(data, iv, work_factor1, hash_function)
    time_required = timestamp() - start
    print("Digest size: {}".format(len(digest)))
    print("Digest:\n{}\n".format(digest))
    print("Time taken to generate digest: {}".format(time_required))
    
    start = timestamp()
    assert verify_digest(digest, iv, work_factor1, hash_function)
    print "Time taken to validate digest: {}".format(timestamp() - start)
        
if __name__ == "__main__":
    #test_encrypt_decrypt()
    test_slow_hash()
    