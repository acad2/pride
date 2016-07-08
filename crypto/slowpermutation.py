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

def test_encrypt_decrypt():
    message = "Testing!"
    key = "\x00" * 16
    iv = "\x00" * 16    
    work_factor = 1
    decryption_factor = 2
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

if __name__ == "__main__":
    test_encrypt_decrypt()
    