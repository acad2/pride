import itertools
import random

from pride.decorators import Timed
from pride.datastructures import Average
from pride.utilities import shell
from utilities import cast, binary_form

ASCII = ''.join(chr(x) for x in range(256))
    
def hamming_distance(input_one, input_two):
    size = len(input_one)
    if len(input_two) != size:
        raise ValueError("Inputs must be same length")
    count = 0
    for index, bit in enumerate(input_one):
        if input_two[index] == bit:
            count += 1
    return count
    #return format(int(input_one, 2) ^ int(input_two, 2), 'b').zfill(size).count('1')   
         
def print_hamming_info(output1, output2):    
    output1_binary = binary_form(output1)
    output2_binary = binary_form(output2)
    _distance = hamming_distance(binary_form(output1), binary_form(output2))
    bit_count = len(output1_binary)
    print "bit string length: ", bit_count
    print "Hamming weights: ", output1_binary.count('1'), output2_binary.count('1')
    print "Hamming distance and ratio (.5 is ideal): ", _distance, _distance / float(bit_count)
    
def test_avalanche(hash_function, blocksize=16):        
    print "Testing diffusion/avalanche... "
    output1 = hash_function(("\x00" * (blocksize - 1)) + "\x00")
    output2 = hash_function(("\x00" * (blocksize - 1)) + "\x01")    
    print_hamming_info(output1, output2)
    
def test_randomness(random_bytes):    
    size = len(random_bytes)
    print "Testing randomness of {} bytes... ".format(size)    
    with open("Test_Data_{}.bin".format(size), 'wb') as _file:
        _file.write(random_bytes)
        _file.flush()    
    print "Data generated; Running ent..."
    shell("./ent/ent.exe Test_Data_{}.bin".format(size))
    
    #outputs = dict((x, random_bytes.count(chr(x))) for x in xrange(256))
    #average = Average(values=tuple(random_bytes.count(chr(x))for x in xrange(256)))
    #print "Randomness distribution (min, average, max): (~4100 is good): ", average.range
    #import pprint
    #pprint.pprint(sorted(outputs.items()))
        
def test_hash_chain(hash_function, test_size=1):
    outputs = ['']
    output = ''   
    print "Testing hash chain period: "
    for cycle_length in itertools.count():        
        output = hash_function(output)[:test_size]
        if output in outputs:
            print "Hash chain cycled after {} with {} byte output: ".format(cycle_length, test_size)
            break
        outputs.append(output)
                
def test_bias(hash_function, byte_range=slice(8)):
    biases = [[] for x in xrange(8)]    
    outputs2 = []    
    for x in xrange(256):
        output = hash_function(chr(x))
        for index, byte in enumerate(output[:8]):
            biases[index].append(ord(byte))
        outputs2.extend(output[byte_range])        
    print "Byte bias: ", [len(set(_list)) for _list in biases]   
    print "Symbols out of 256 that appeared anywhere: ", len(set(outputs2))
    
def test_collisions(hash_function, output_size=3):      
    outputs = {}        
    print "Testing for collisions with output of {} bytes... ".format(output_size)
    for count, possibility in enumerate(itertools.product(ASCII, ASCII)):
        hash_input = ''.join(possibility)        
        hash_output = hash_function(hash_input)[:output_size]
        if hash_output in outputs:
            print "Collision after: ", count, "; Output size: ", output_size
            break
        else:
            outputs[hash_output] = hash_input
    else:
        print "No collisions after {} inputs with output size {}".format(count, output_size), len(set(outputs))
    
def test_compression_performance(hash_function):    
    print "Time testing compression function..."
    print Timed(hash_function, 10)("Timing test for input" * 1000)
    
def test_prng_performance(hash_function):    
    print "Testing time to generate 1024 * 1024 bytes... "
    print Timed(hash_function, 1)('', output_size=1024 * 1024)
    
def test_hash_function(hash_function):
    test_avalanche(hash_function)
    test_randomness(hash_function('', output_size=1024 * 1024))
    test_hash_chain(hash_function)    
    test_bias(hash_function)
    test_collisions(hash_function)
    test_compression_performance(hash_function)
    test_prng_performance(hash_function)
    
def test_block_cipher(cipher, blocksize=16):
    _cipher = cipher("\x00" * blocksize, "cbc")
    test_function = lambda data: _cipher.encrypt(data, "\x00" * blocksize)
    test_avalanche(test_function)
               
    random_bytes = _cipher.encrypt("\x00" * 1024 * 1024 * 1, "\x00" * blocksize)        
    test_randomness(random_bytes)
        
    #test_prng_performance(lambda data, output_size: _cipher.encrypt("\x00" * output_size, "\x00" * blocksize))
    
def test_random_metrics():
    from metrics import test_block_cipher
    from utilities import replacement_subroutine
    from os import urandom
    
    class Random_Cipher(pride.crypto.Cipher):
        
        def encrypt_block(self, plaintext, key):
            replacement_subroutine(plaintext, urandom(len(plaintext)))
            
    test_block_cipher(Random_Cipher)        

def test_aes_metrics():    
    from pride.security import encrypt as aes_encrypt
    from pride.utilities import load_data
    from utilities import replacement_subroutine
    from metrics import test_block_cipher
    from os import urandom
    class Aes_Cipher(pride.crypto.Cipher):
        
        def encrypt_block(self, plaintext, key):
            ciphertext = aes_encrypt(bytes(plaintext), urandom(16), urandom(16))
            header, ciphertext, iv, tag, extra_data = load_data(ciphertext)   
            replacement_subroutine(plaintext, bytearray(ciphertext))
    test_block_cipher(Aes_Cipher) 
    