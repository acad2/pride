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
 
# input = pa | ss | wo | rd
# input = hash(iv + pa) | (hash(iv + hash0 + output0 + ss) | hash(iv + hash0 + hash1 + wo) ...
# output = brute_force(hash0[work_factor_slice]) | brute_force(hash1[work_factor_slice]) | brute_force(hash2[work_factor_slice]) ...

# verification:
# assert hash(output0) == hash(iv + pa)
# assert hash(output1) == hash(iv + hash0 + output0 + ss)
# assert hash(output2) == hash(iv + hash0 + hash1 + output0 + output1 + wa)
# ...
 
def slow_hash(data, iv, work_factor1=1, hash_function=tunable_hash):
    digest = b''
    state = b''
    _looking_for = list(iv)
    looking_for = ''.join(_looking_for.pop(0) for factor in range(work_factor1)) # iv[:work_factor1]
    for data_bytes in slide(data, work_factor1):
        current_hash = hash_function(iv + state + data_bytes)
        state += current_hash
        while current_hash[:work_factor1] != looking_for:
            hash_input = current_hash + data_bytes
            current_hash = hash_function(hash_input)
            state += current_hash
        digest += hash_input[:-work_factor1]
        looking_for = ''.join(_looking_for.pop(0) for factor in range(work_factor1))
    
    return digest
            
def verify_digest(digest, data, iv, work_factor1=1, hash_function=tunable_hash):
    digest_size = len(hash_function(''))
    _data = list(data)
    _looking_for = list(iv)
    looking_for = ''.join(_looking_for.pop(0) for count in range(work_factor1))
    failure = False    
    for current_hash in slide(digest, digest_size):
        data_bytes = ''.join(_data.pop(0) for count in range(work_factor1))
        hash_input = current_hash + data_bytes
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
    digest = slow_hash(data, iv, work_factor1, hash_function)
    print len(digest)#, digest#, [byte for byte in bytearray(digest)]
    
    assert verify_digest(digest, data, iv, work_factor1, hash_function)
    
if __name__ == "__main__":
    #test_encrypt_decrypt()
    test_slow_hash()
    