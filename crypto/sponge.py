import functools

from utilities import cast, slide, xor_subroutine, replacement_subroutine
    
def pad_input(hash_input, size):
    hash_input += chr(128)
    padding = size - (len(hash_input) % size)
    hash_input += ("\x00" * padding)
    return hash_input
        
def example_mixing_subroutine(_bytes):    
    byte_length = len(_bytes)
    key = (45 + sum(_bytes)) * byte_length * 2    
    for counter, byte in enumerate(_bytes):
        _bytes[counter % byte_length] = counter ^ (pow(251, 
                                                       key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter), 
                                                       257) % 256)
    return _bytes
    
def variable_length_hash(state, rate, output_size, mix_state_subroutine, absorb_mode):    
    output = state[:rate]
    while len(output) < output_size:
        mix_state_subroutine(state)        
        output += state[:rate]      
    return bytes(output[:output_size])
    
def prng_generator(state, rate, output_size, mix_state_subroutine, absorb_mode):    
    while True:
        yield state[:rate]
        mix_state_subroutine(state)    
    
def encryption_generator(state, rate, output_size, mix_state_subroutine, absorb_mode):    
    input_block = yield None        
    while input_block is not None:
        xor_subroutine(state, bytearray(input_block))
        input_block = yield bytes(state[:len(input_block)])
        mix_state_subroutine(state)        
    yield bytes(state[:rate])
    
def decryption_generator(state, rate, output_size, mode_of_operation, absorb_mode):    
    input_block = yield None       
    while input_block is not None:
        last_block = state[:len(input_block)]
        xor_subroutine(state, bytearray(input_block))
  
        input_block = yield bytes(state[:len(input_block)])
        xor_subroutine(state, last_block)       
        mix_state_subroutine(state)    
    authentication_code = yield bytes(state[:rate])
    if authentication_code != state[:rate]:
        raise ValueError("Invalid tag")
        
def absorb(data, state, rate, mix_state_subroutine, replacement_subroutine): 
    for block in slide(bytearray(data), rate):
        replacement_subroutine(state, block)
        mix_state_subroutine(state)
       
def sponge_function(hash_input, key='', output_size=32, capacity=32, rate=32, 
                    mix_state_subroutine=example_mixing_subroutine,
                    mode_of_operation=variable_length_hash,
                    absorb_mode=xor_subroutine):  
    state_size = capacity + rate
    state = bytearray(state_size)
    if key:
        absorb(key, state, rate, mix_state_subroutine, absorb_mode)      
    
    hash_input = pad_input(hash_input, rate)
        
    for _bytes in slide(hash_input, rate):
        absorb(_bytes, state, rate, mix_state_subroutine, absorb_mode)
    
    mix_state_subroutine(state)
    return mode_of_operation(state, rate, output_size, mix_state_subroutine, absorb_mode)                
    
def encrypt(data, key, iv, mix_state_subroutine=example_mixing_subroutine, rate=32):
    encryptor = sponge_function(iv, key, mix_state_subroutine=mix_state_subroutine,
                                mode_of_operation=encryption_generator)
    next(encryptor)
    return ''.join(encryptor.send(block) for block in slide(data, rate))

def decrypt(data, key, iv, mix_state_subroutine=example_mixing_subroutine, rate=32):
    decryptor = sponge_function(iv, key, mix_state_subroutine=mix_state_subroutine,
                                mode_of_operation=decryption_generator)
    next(decryptor)    
    return ''.join(decryptor.send(block) for block in slide(data, rate))                    
               
def psuedorandom_data(quantity, seed, key, mix_state_subroutine=example_mixing_subroutine, rate=32):
    return sponge_function(seed, key, mix_state_subroutine=mix_state_subroutine, 
                           output_size=quantity, rate=rate)
    
def sponge_factory(key='', output_size=32, capacity=32, rate=32, 
                   mix_state_subroutine=example_mixing_subroutine,
                   mode_of_operation=variable_length_hash,
                   absorb_mode=xor_subroutine):
    return functools.partial(sponge_function, key=key, output_size=output_size, 
                                              capacity=capacity, rate=rate,
                                              mix_state_subroutine=mix_state_subroutine,
                                              mode_of_operation=mode_of_operation, 
                                              absorb_mode=absorb_mode)                       
            
class Hash_Object(object):
                        
    def __init__(self, hash_input='', output_size=32, capacity=32, rate=32, state=None):  
        self.rate = rate
        self.capacity = capacity
        self.output_size = output_size        
        self.state = ''
        if state is not None:
            self.state = state
        
        if hash_input:
            if self.state:
                self.update(hash_input)
            else:
                self.state = self.hash(hash_input)
        
    def hash(self, hash_input, key=''):
        return sponge_function(hash_input, key, self.output_size, self.capacity, self.rate)
       
    def update(self, hash_input):
        self.state = xor_compression(self.state + self.hash(hash_input), self.state_size)
        
    def digest(self):
        return self.state

    def copy(self):
        return Hash_Object(output_size=self.output_size, capacity=self.state_size, 
                           rate=self.rate, state=self.state)
             
def test_hash_object():
    hasher = Hash_Object("Test data")
    assert hasher.digest() == sponge_function("Test data")
    
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
    
def test_psuedorandom_data():
    data = psuedorandom_data(257, "\x00" * 16, "\x00" * 16)    
    assert len(data) == 257
    print data
    
if __name__ == "__main__":
    test_hash()
    test_hash_object()
    test_encrypt_decrypt()
    test_psuedorandom_data()