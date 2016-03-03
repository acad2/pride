import functools

from utilities import cast, slide
from hashfunction import unpack_factors, mixing_subroutine

def pad_input(hash_input, rate):    
    hash_input += '1'
    while len(hash_input) < rate: # expanding small inputs is good for diffusion/byte bias
        hash_input = cast(unpack_factors(cast(hash_input, "binary")), "bytes")
    return hash_input
    
def variable_length_hash(state, rate, output_size, mix_state_subroutine):    
    output = state[:rate]
    while len(output) < output_size:
        mix_state_subroutine(state)        
        output += state[:rate]
    return bytes(output[:output_size])
    
def encryption_generator(state, rate, output_size, mix_state_subroutine):    
    input_block = yield None        
    while input_block is not None:
        for index, value in enumerate(bytearray(input_block)):
            state[index] ^= value     
        input_block = yield bytes(state[:len(input_block)])
        mix_state_subroutine(state)        
    yield bytes(state[:rate])
    
def decryption_generator(state, rate, output_size, mode_of_operation):    
    input_block = yield None       
    while input_block is not None:
        last_block = state[:len(input_block)]
        for index, value in enumerate(bytearray(input_block)):
            state[index] ^= value     
        input_block = yield bytes(state[:len(input_block)])
        for index, value in enumerate(last_block):
            state[index] ^= value           
        mix_state_subroutine(state)    
    authentication_code = yield bytes(state[:rate])
    if authentication_code != state[:rate]:
        raise ValueError("Invalid tag")
    #yield state[:rate]
    
def xor_absorb(data, state, rate, mix_state_subroutine):        
    for index, value in enumerate(bytearray(data)):
        state[index % rate] ^= value
    mix_state_subroutine(state)
        
def sponge_function(hash_input, key='', output_size=32, capacity=32, rate=32, 
                    mix_state_subroutine=mixing_subroutine,
                    mode_of_operation=variable_length_hash,
                    absorb=xor_absorb):  
    state_size = capacity + rate
    state = bytearray(state_size)
    if key:
        absorb(key, state, rate, mix_state_subroutine)      
    
    hash_input = pad_input(hash_input, rate)
        
    for _bytes in slide(hash_input, rate):
        absorb(_bytes, state, rate, mix_state_subroutine)
    
    mix_state_subroutine(state)
    return mode_of_operation(state, rate, output_size, mix_state_subroutine)               

def encrypt(data, key, iv, rate=32):
    encryptor = sponge_function(iv, key, mode_of_operation=encryption_generator)
    next(encryptor)
    return ''.join(encryptor.send(block) for block in slide(data, rate))

def decrypt(data, key, iv, rate=32):
    decryptor = sponge_function(iv, key, mode_of_operation=decryption_generator)
    next(decryptor)    
    return ''.join(decryptor.send(block) for block in slide(data, rate))                    
               
def sponge_factory(key='', output_size=32, capacity=32, rate=32, 
                   mix_state_subroutine=mixing_subroutine,
                   mode_of_operation=variable_length_hash,
                   absorb=xor_absorb):
    return functools.partial(sponge_function, key=key, output_size=output_size, 
                                              capacity=capacity, rate=rate,
                                              mix_state_subroutine=mix_state_subroutine,
                                              mode_of_operation=mode_of_operation, 
                                              absorb=absorb)                       
                    
def test_cipher_metrics():
    from metrics import test_hash_function, test_performance
    from os import urandom
    from ciphertest import encrypt_block, substitution
    from modes import encrypt    
    from pride.security import encrypt as aes_encrypt
    from pride.utilities import load_data
    from utilities import replacement_subroutine
        
    def test_aes(input_bytes):
        ciphertext = aes_encrypt(bytes(input_bytes), "\x00" * 16, bytes(input_bytes[:16]))
        header, ciphertext, iv, tag, extra_data = load_data(ciphertext)   
        replacement_subroutine(input_bytes, bytearray(ciphertext))   
        
    def test_ciphertest(input_bytes):        
        size = len(input_bytes)                   
        encrypt(input_bytes, bytearray("\x00" * size), bytearray("\x00" * size), encrypt_block, "cbc")
        
    def test_random_data(input_bytes):    
        replacement_subroutine(input_bytes, bytearray(urandom(len(input_bytes))))
    #test_performance(sponge_factory(mix_state_subroutine=test_mixer))
    test_hash_function(sponge_factory(mix_state_subroutine=test_ciphertest))    
    
def test_hash():
    print sponge_function('')
    for x in xrange(5):
        print sponge_function(chr(x))
    
def test_encrypt_decrypt():
    plaintext = "Awesome test message"
    iv = key = "\x00" * 16
    ciphertext = encrypt(plaintext, key, iv)
    _plaintext = decrypt(ciphertext, key, iv)
    print len(ciphertext), ciphertext
    print len(plaintext), plaintext
    assert plaintext == _plaintext, (plaintext, _plaintext)
    
if __name__ == "__main__":
    #test_hash()
    #test_encrypt_decrypt()
    test_cipher_metrics()