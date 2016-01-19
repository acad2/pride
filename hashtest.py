import itertools   

ASCII = ''.join(chr(x) for x in range(256))

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
    slice_count, remainder = divmod(len(bitstring), 8)                   
    output = ''
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * 8
        output += chr(int(bitstring[_position:_position + 8], 2))
    return output

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
    variables = prime_generator()
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
        
def hash_function(hash_input, key='', output_size=None, iterations=0, state_size=64):
    """ A tunable, variable output length hash function. Security is based on
        the hardness of the well known problem of integer factorization. """
    input_size = len(hash_input)
    _input_size = str(input_size)
    if input_size > state_size:
        hash_input = one_way_compression(hash_input, state_size)
    state = binary_form(unpack_factors(binary_form(hash_input + _input_size + '1')))

    random_index = input_size 
    for round in range(iterations):    
        psuedorandom_byte = int(state[random_index:random_index + 8], 2)
        state = rotate(state[:random_index] + state[random_index + 8:], psuedorandom_byte)
        random_index = pow(251, (psuedorandom_byte ** random_index), 257) % (len(state) - 8)
        state = binary_form(unpack_factors(state))     
    
    if not output_size:
        return byte_form(state)
    else:
        while len(state) / 8 < output_size:
            psuedorandom_byte = int(state[random_index:random_index + 8], 2)
            state = rotate(state[:random_index] + state[random_index + 8:], psuedorandom_byte)
            random_index = pow(251, (psuedorandom_byte ** random_index), 257) % (len(state) - 8)
            state = binary_form(unpack_factors(state))            
        return byte_form(state)[:output_size]
        
def one_way_compression(data, state_size=256):
    output = bytearray('\x00' * state_size)
    for _bytes in slide(data, state_size):
        for index, byte in enumerate(_bytes):
            output[index] ^= ord(byte)
    return bytes(output)
        
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
         
def test_difference():
    output1 = hash_function("The quick brown fox jumps over the lazy dog", output_size=32, iterations=2)
    output2 = hash_function("The quick brown fox jumps over the lazy cog", output_size=32, iterations=2)
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
    
def test_bias():
    outputs = []    
    outputs2 = []
    for x in xrange(256):
        output = hash_function(chr(x))
        #print output, type(output), len(output)
        outputs2.extend(output)
        outputs.append(ord(output[0]))    
    #import pprint
    print "Symbols out of 256 that appeared as first symbol: ", len(set(outputs))#sorted([item for item in outputs])
    print "Symbols out of 256 that appeared anywhere: ", len(set(outputs2))
    
def test_hash_function():      
    outputs = {}
    from hashlib import sha1
    for count, possibility in enumerate(itertools.product(ASCII, ASCII)):
        hash_input = ''.join(possibility)        
        hash_output = hash_function(hash_input, iterations=0)#, output_size=4, iterations=1)
        assert hash_output not in outputs, ("Collision", count, hash_output, binary_form(outputs[hash_output]), binary_form(hash_input))
        outputs[hash_output] = hash_input
    #    print hash_input, hash_output
        
if __name__ == "__main__":
    test_difference()
    #test_bias()
    #test_hash_function()
    