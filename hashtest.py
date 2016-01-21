import itertools   
import binascii

ASCII = ''.join(chr(x) for x in range(256))
# helper functions

def rotate(input_string, amount):
    """ Rotate input_string by amount. Amount may be positive or negative.
        Example:
            
            >>> data = "0001"
            >>> rotated = rotate(data, -1) # shift left one
            >>> print rotated
            >>> 0010
            >>> print rotate(rotated, 1) # shift right one, back to original
            >>> 0001 """
    if not amount or not input_string:            
        return input_string    
    else:
        amount = amount % len(input_string)
        return input_string[-amount:] + input_string[:-amount]
        
def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x]   
        
def binary_form(_string):
    """ Returns the a string representation of the binary bits that constitute _string. """
    try:
        return ''.join(format(ord(character), 'b').zfill(8) for character in _string)
    except TypeError:        
        bits = format(_string, 'b')
        bit_length = len(bits)
        if bit_length % 8:
            bits = bits.zfill(bit_length + (8 - (bit_length % 8)))        
        return bits
        
def byte_form(bitstring):
    """ Returns the ascii equivalent string of a string of bits. """
    _hex = hex(int(bitstring, 2))[2:]   
    try:
        return binascii.unhexlify(_hex[:-1 if _hex[-1] == 'L' else None])
    except TypeError:
        return binascii.unhexlify('0' + _hex[:-1 if _hex[-1] == 'L' else None])
        
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
PRIMES = [next(generator) for count in range(1000)]
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
        
def hash_function(hash_input, output_size=32, state_size=64):
    """ A tunable, variable output length hash function. Security is based on
        the hardness of the well known problem of integer factorization. """   
        
    # Compression first, if necessary. state_size can be set to 0 to never compress.
    # The size of the state determines how long unpack_factors takes to execute and
    # also influences collisions. Large inputs should be compressed or will take forever.
    # input size and a '1' bit are appended to help prevent collisions. 
    # example: unpack_factors would otherwise return 2 when supplied with 1, 10, 100, 1000, ...    
    input_size = len(hash_input)               
    if state_size and input_size > state_size:
        hash_input = one_way_compression(hash_input, state_size)
    state = binary_form(unpack_factors(binary_form(hash_input + str(input_size))))        
    
    if output_size is None:
        return byte_form(state)
    else:
        # make (at least) twice as many bits as needed and apply the compression function for output  
        required_bits = output_size * 2 * 8
        while len(state) < required_bits:
            state = binary_form(unpack_factors(state))                          
        return one_way_compression(byte_form(state), output_size)
                                    
def one_way_compression(data, state_size=256):    
    output = bytearray('\x00' * state_size)
    for _bytes in slide(data, state_size):
        for index, byte in enumerate(bytearray(_bytes)):
            output[index] ^= byte
    return bytes(output)                              
                
def cipher(data, key, iv):
    """ Cipher that is more or less equivalent to CTR mode with a hash function.
        Secure under the random oracle model. iv must never repeat.
        Encryption and decryption are the same operation. """
    assert isinstance(iv, bytes)
    data_size = len(data)
    key_material = hash_function(key + iv, output_size=data_size)
    return one_way_compression(data + key_material, data_size)        
        
class Hash_Object(object):
                        
    def __init__(self, hash_input='', output_size=32, state_size=64, state=None):                   
        self.output_size = output_size
        self.state_size = state_size
        self.state = ''
        if state is not None:
            self.state = state
        
        if hash_input:
            if self.state:
                self.update(hash_input)
            else:
                self.state = self.hash(hash_input)
        
    def hash(self, hash_input):
        return hash_function(hash_input, self.output_size, self.state_size)
       
    def update(self, hash_input):
        self.state = one_way_compression(self.state + self.hash(hash_input), self.state_size)
        
    def digest(self):
        return self.state

    def copy(self):
        return Hash_Object(output_size=self.output_size, state_size=self.state_size, state=self.state)

# test functions        
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
         
def print_hash_comparison(output1, output2):
    output1_binary = binary_form(output1)
    output2_binary = binary_form(output2)
    _distance = hamming_distance(binary_form(output1), binary_form(output2))
    bit_count = len(output1_binary)
    print "bit string length: ", bit_count
    print "Hamming weights: ", output1_binary.count('1'), output2_binary.count('1')
    print "Hamming distance and ratio: ", _distance, _distance / float(bit_count)
    print output1_binary
    print output2_binary    
    print output1
    print output2
    
def test_difference():
    from hashlib import sha256
    #output1 = sha256("The quick brown fox jumps over the lazy dog").digest()
    #output2 = sha256("The quick brown fox jumps over the lazy dog").digest()
    output1 = hash_function("The quick brown fox jumps over the lazy dog", output_size=32)
    output2 = hash_function("The quick brown fox jumps over the lazy cog", output_size=32)
   # for x in xrange(10):
   #     output1 = hash_function(output1, output_size=32)
   #     output2 = hash_function(output2, output_size=32)
    print_hash_comparison(output1, output2)
    
def test_time():
    from pride.decorators import Timed
    from hashlib import sha256
    print Timed(sha256, 100)("Timing test hash input" * 1000)
    print Timed(hash_function, 100)("Timing test hash input" * 1000)
    
def test_bias():
    biases = [[] for x in xrange(8)]    
    outputs2 = []
    from hashlib import sha256
    for x in xrange(256):
        output = hash_function(chr(x), output_size=32)
        for index, byte in enumerate(output[:8]):
            biases[index].append(ord(byte))
        outputs2.extend(output[:8])
        #outputs.append(ord(output[0]))    
    import pprint
    print "Byte bias: ", [len(set(_list)) for _list in biases]
  #  for _list in biases:
  #      print sorted(_list)    
    print "Symbols out of 256 that appeared anywhere: ", len(set(outputs2))
    
def test_hash_function():      
    outputs = {}    
    from hashlib import sha256
    for count, possibility in enumerate(itertools.product(ASCII, ASCII)):
        hash_input = ''.join(possibility)        
        hash_output = hash_function(hash_input, output_size=4)
        assert hash_output not in outputs, ("Collision", count, hash_output, binary_form(outputs[hash_output]), binary_form(hash_input))
        outputs[hash_output] = hash_input
    #    print hash_input, hash_output
        
def test_hash_object():
    hasher = Hash_Object("Test data")
    assert hasher.digest() == hash_function("Test data")
    
def test_performance():
    output = ''
    for x in xrange(10000):
        output = hash_function(output)
        
if __name__ == "__main__":
    test_hash_object()
    test_difference()
    test_bias()
    test_time()
    test_hash_function()
    #test_performance()