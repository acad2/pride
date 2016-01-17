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
        
def hash_function(hash_input, key='', output_size=None, iterations=1):
    """ A tunable, variable output length hash function. Security is based on
        the hardness of the well known problem of integer factorization. """
    input_size = len(hash_input)
    _input_size = str(input_size)
    state = binary_form(hash_input)
   # random_index = input_size   
    for round in range(iterations):
        state = binary_form(unpack_factors(state))
        #random_index = pow(17, int(state[random_index:random_index + 16]), prime)
    state_size = len(state) / 8
    if output_size and state_size < output_size:
        return hash_function(byte_form(state), key=key, output_size=output_size, iterations=iterations)
    else:
        return byte_form(state)[:output_size]
        
    
    
        #random_index = pow(prime - g_offset, int(state, 2), prime)#pow(17, int(state, 2), len(state))
        #state = rotate(state[:random_index] + state[random_index+16:], 
        #               int(state[random_index:random_index+16], 2))        
        
    state_size = (len(state) / 8) - 1    
    if output_size and state_size < output_size:     
        return hash_function(state + str(state_size) + hash_input, 
                             output_size=output_size)
    else:
        return rotate(byte_form(state[:-8])[:output_size], int(state[-8:], 2))
        
def one_way_compression(data, prime=17, modulus=257):
    raise NotImplementedError
    bits = binary_form(data)
    half_size = len(data) / 2
    first_half, second_half = data[:half_size], data[half_size:]
    output = ''
    for index in range(half_size):
        output += chr(pow(prime, 
                          ord(first_half[index]) * ord(second_half[index]), 
                          modulus) % 256)
    return output
        
    output = ''
    for index in range(len(data)):
        last_symbol = data[index-1]
        symbol = data[index]
        print "value: ", ord(last_symbol), ord(symbol)
        output += chr(pow(17, (3 + ord(last_symbol)) * (7 + ord(symbol)), 257) % 256)
        #output += chr(\
        #              pow(int(binary_form(word), 2) * 
        #                  17, 257) % 256
    return output    
    #return ''.join(chr(pow(int(word, 2), 17, 257) % 256) for word in slide(bits, 16))
    
def hamming_distance(input_one, input_two):
    size = len(input_one)
    if len(input_two) != size:
        raise ValueError("Inputs must be same length")
    return format(int(input_one, 2) ^ int(input_two, 2), 'b').zfill(size).count('1')   
                
def test_bias():
    outputs = []
    for x in xrange(256):
        outputs.append(ord(hash_function(chr(x))[0]))    
    print sorted(outputs)
    
def test_hash_function():      
    outputs = {}
    from hashlib import sha1
    for count, possibility in enumerate(ASCII):#itertools.product(ASCII, ASCII)):
        hash_input = ''.join(possibility)        
        hash_output = hash_function(hash_input)#, output_size=4, iterations=1)
        assert hash_output not in outputs, ("Collision", hash_output, binary_form(outputs[hash_output]), binary_form(hash_input))
        outputs[hash_output] = hash_input
    #    print hash_input, hash_output
        
if __name__ == "__main__":
    test_hash_function()
    test_bias()