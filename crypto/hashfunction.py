import itertools   
import binascii

from utilities import cast, slide, pack_data, unpack_data, byte_form, binary_form
# helper functions
            
SUBSTITUTION = dict((x, pow(251, x, 257) % 256) for x in xrange(1024 * 1024 * 2))
            
def prime_generator():
    """ Generates prime numbers in successive order. """
    primes = [2]
    yield 2
    for test_number in itertools.count(3, 2):
        for prime in primes:
            if not test_number % prime:
                break
        else:
            yield test_number
            primes.append(test_number)

generator = prime_generator()
PRIMES = [next(generator) for count in range(2048)]
del generator          
# end of helper functions
                                                
def unpack_factors(bits, initial_power=0, initial_output=1, power_increment=1):   
    """ Unpack encoded (prime, power) pairs and compose them into an integer.
        Each contiguous 1-bit increments the exponent of the current prime.
        Each zero advances to the next prime and composes the current prime and
        exponent into the output.
        
        For example:
            
            11001101
            
        Is interpreted to mean:
            
            (2 ** 2) * (3 ** 0) * (5 ** 2) * (7 ** 1)
            
        The bits that previously represented the number 205 are composed and 
        result in the integer 700. """    
    if '1' not in bits:
        return 0 
    variables = iter(PRIMES)#prime_generator()
    variable = next(variables)
    power = initial_power
    output = initial_output   
    last_bit = len(bits) - 1
    for bit in bits[:-1]:
        if bit == '1':
            power += power_increment
        else:                        
            output *= variable ** power
            power = initial_power        
            variable = next(variables)              
    if bits[-1] == '1':
        power += power_increment    
    output *= variable ** power       
    return output                       
                            
def mixing_subroutine(_bytes):    
    byte_length = len(_bytes)
    key = (45 + sum(_bytes)) * byte_length * 2    
    for counter, byte in enumerate(_bytes):
     #   psuedorandom_byte = SUBSTITUTION[key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter)]
#        psuedorandom_byte = pow(251, key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter), 257) % 256
  #      assert SUBSTITUTION[key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter)] == psuedorandom_byte
        _bytes[counter % byte_length] = SUBSTITUTION[key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter)] ^ (counter % 256)        
    return _bytes
        
def sponge_function(hash_input, key='', output_size=32, capacity=32, rate=32, 
                    mix_state_function=mixing_subroutine):  
    state_size = capacity + rate
    state = bytearray(state_size)
    if key:
        for index, value in enumerate(bytearray(key)):
            state[index % rate] ^= value
        mix_state_function(state)
    
    hash_input += '1'
    while len(hash_input) < rate: # expanding small inputs is good for diffusion/byte bias
        hash_input = byte_form(unpack_factors(binary_form(hash_input)))
        
    for _bytes in slide(hash_input, rate):
        for index, byte in enumerate(bytearray(_bytes)):
            state[index] ^= byte
        mix_state_function(state)
    
    mix_state_function(state)
    output = state[:rate]
    while len(output) < output_size:
        mix_state_function(state)
        output += state[:rate]
    return bytes(output[:output_size])
           
def sponge_encryptor(hash_input, key='', capacity=32, rate=32, 
                     mix_state_function=mixing_subroutine):  
    state_size = capacity + rate
    state = bytearray(state_size)
    if key:
        for index, value in enumerate(bytearray(key)):
            state[index % rate] ^= value
        mix_state_function(state)
    
    hash_input += '1'
    while len(hash_input) < rate: # expanding small inputs is good for diffusion/byte bias
        hash_input = byte_form(unpack_factors(binary_form(hash_input)))
        
    for _bytes in slide(hash_input, rate):
        for index, byte in enumerate(bytearray(_bytes)):
            state[index] ^= byte
        mix_state_function(state)
    
    mix_state_function(state)        
    input_block = yield None        
    while input_block is not None:
        for index, value in enumerate(bytearray(input_block)):
            state[index] ^= value     
        input_block = yield state[:len(input_block)]         
        mix_state_function(state)        
    yield state[:rate]
    
def sponge_decryptor(hash_input, key='', capacity=32, rate=32, 
                     mix_state_function=mixing_subroutine):      
    state_size = capacity + rate
    state = bytearray(state_size)
    if key:
        for index, value in enumerate(bytearray(key)):
            state[index % rate] ^= value
        mix_state_function(state)
    
    hash_input += '1'
    while len(hash_input) < rate: # expanding small inputs is good for diffusion/byte bias
        hash_input = byte_form(unpack_factors(binary_form(hash_input)))
        
    for _bytes in slide(hash_input, rate):
        for index, byte in enumerate(bytearray(_bytes)):
            state[index] ^= byte
        mix_state_function(state)
    
    mix_state_function(state)        
    input_block = yield None       
    while input_block is not None:
        last_block = state[:len(input_block)]
        for index, value in enumerate(bytearray(input_block)):
            state[index] ^= value     
        input_block = yield state[:len(input_block)]
        for index, value in enumerate(last_block):
            state[index] ^= value           
        mix_state_function(state)    

    yield state[:rate]
                        
def invert_mixing_function(_bytes):
    import itertools
    length = len(_bytes)
    recovered = bytearray()
    for counter, psuedorandom_byte in enumerate(_bytes):
        psuedorandom_byte ^= (counter % 256)
            
        reform_state = lambda byte: (45 + sum(recovered) + byte) * length * 2
        possible_inputs = []
        unknown_bytes = length - len(recovered)
        for byte in xrange(256):
            possible_state = reform_state(byte)
            for increment in xrange(unknown_bytes * 256):                
                if pow(251, (increment + possible_state) ^ byte, 257) % 256 == psuedorandom_byte:
                    possible_inputs.append(byte)
                    break                         
        
        if not possible_inputs:    
            print "Failed to find any possible inputs"
            raise Exception()
        elif len(possible_inputs) == 1:
            recovered.append(possible_inputs[0])
        else:
            print "ambiguous recovery: ", psuedorandom_byte, possible_inputs
    return recovered
    
def xor_compression(data, state_size=64):    
    output = bytearray('\x00' * state_size)
    for _bytes in slide(data, state_size):
        for index, byte in enumerate(bytearray(_bytes)):
            output[index] ^= byte
    return bytes(output)                              
             
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

# test functions        
            
def test_hash_object():
    hasher = Hash_Object("Test data")
    assert hasher.digest() == sponge_function("Test data")
    
def test_encrypt_decrypt():
    message = "I am an awesome test message, for sure :)"
    key = "Super secret key"
    ciphertext = encrypt(message, key, '0', "This is some extra awesome test extra data")
    assert decrypt(ciphertext, key) == (message, "This is some extra awesome test extra data")
        
def test_chain_cycle(state="\x00\x00", key=""):
    state = bytearray(key + state)
    size = len(state)
    outputs = [bytes(state)]
    import itertools
    import random
    max_length = 0
    for cycle_length in itertools.count():
        mixing_subroutine(state)   
        #  assert len(state) == 2, len(state)
        #state, key = state[:1], bytes(state[1:])                
        output = bytes(state)
        if not state[0]:
            state = bytearray(confusion_shuffle(state))
           #  print index, len(state), state[index], len(mixing_subroutine(bytearray(state[index])))
      #  print cycle_length
        if output in outputs:
            max_length = max(max_length, len(outputs))
            #break
            print "Cycle length: ", cycle_length, max_length, len(outputs)
            outputs = [output]
        else:
     #       print cycle_length, len(output)
            outputs.append(output)            
    #print "Cycle length: ", cycle_length, len(outputs)
    
def test_permutation():
    _input = "\x00"
    outputs = []
    max_cycle = 0
    best_initial_state = 0
    for initial_state in xrange(256):  
        outputs = []
        for y in xrange(256):
            _input = mixing_subroutine(_input)
            outputs.append(_input)  
                
        start = cycle = outputs.pop()
        for cycle_length, output in enumerate(reversed(outputs)):
            if output == start:                
                break
            cycle += output
        outputs.append(start)
        
        if cycle_length > max_cycle:
            best = (cycle_length, initial_state, len(set(outputs)))
            max_cycle = cycle_length
            _outputs = outputs
    print best# [char for char in reversed(cycle)]
    #print
    print [char for char in _outputs], "\n"
    print set(''.join(chr(x) for x in xrange(256))).difference(_outputs)
                
def encrypt(data, key, iv, extra_data='', block_size=32):
    """ Ella's Hash Cipher 0 - EHC0 (encrypt)
        
        Returns packet of encrypted data + meta data. 
        Encrypted data is authenticated and has assurance of integrity.
        extra_data is authenticated and integrity assured, but not encrypted. """
    sponge = sponge_encryptor(extra_data + iv, key, rate=block_size)
    next(sponge)
    ciphertext = ''
    for _bytes in slide(data, block_size):
        ciphertext += sponge.send(_bytes)
    mac_tag = sponge.send(None)
    return pack_data("EHC0_EHC0", ciphertext, iv, mac_tag, extra_data)
    
def decrypt(data, key, block_size=32):
    """ Ella's Hash Cipher 0 - EHC0 (decrypt)
    
        Returns (plaintext, extra data) when extra data is available
        Returns plaintext when extra data is not available
        Raises ValueError if an invalid mac tag is encountered. """
    header, ciphertext, iv, mac_tag, extra_data = unpack_data(data)
    sponge = sponge_decryptor(extra_data + iv, key, rate=block_size)
    next(sponge)
    plaintext = ''
    for _bytes in slide(ciphertext, block_size):
        plaintext += sponge.send(_bytes)
    _mac_tag = sponge.send(None)

    if _mac_tag != mac_tag:
        raise ValueError("Invalid mac tag")
    else:
        if extra_data:
            return plaintext, extra_data
        else:
            return plaintext
    
def test_duplex():
    sponge = sponge_encryptor("testing", "key")    
    next(sponge)
    message = "This is an excellent message!"
    output = ''
    for _bytes in slide(message, 32):
        output += sponge.send(_bytes)
    mac_tag = sponge.send(None)
    
    sponge = sponge_decryptor("testing", "key")
    next(sponge)
    _message = ''
    for _bytes in slide(output, 32):
        _message += sponge.send(_bytes)
    _mac_tag = sponge.send(None)
    assert _message == message
    assert mac_tag == _mac_tag    
    
if __name__ == "__main__":
    from hashtests import test_hash_function, test_performance
    #test_duplex()
    #test_encrypt_decrypt()
    #test_hash_function(sponge_function)
    #test_chain_cycle()
    test_performance(sponge_function)