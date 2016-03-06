import itertools

from utilities import slide, cast

DEFAULT_FUNCTION_NAME = "S-BOX"

def get_xor_expression(*args, **kwargs):
    function_name = kwargs.get("function_name", DEFAULT_FUNCTION_NAME)
    arguments = []
    for arg in args:
        if isinstance(arg, tuple) or isinstance(arg, list):       
            line = "\n      {}[".format(function_name)
            line += get_xor_expression(*arg) + ']'   
            arguments.append(line)
        else:
            arguments.append(arg)
    return " xor ".join(arguments)
    
def test_get_xor_expression():
    cipher_bytes = []
    data = ["B{}".format(count) for count in range(8)]
    _key = key = ["K{}".format(count) for count in range(8)]
    expressions = []
    for index in range(8):
        expressions.append("(C{} = {}) # end C{}\n".format(index, get_xor_expression(data.pop(0), 
                                                                                   key.pop(0),
                                                                                   cipher_bytes + data + key),
                                                         index))
        cipher_bytes.append(expressions[-1])         
    return expressions
    
def p_box(input_bytes):    
    """ Data concentrating permutation box. Evenly distributes input bits amongst output. """
    bits = cast(bytes(input_bytes), "binary")      
    # if a 64 bit block was acceptable, the operation would be this simple:
    #   for index, byte in enumerate(int(bits[index::8], 2) for index in range(8)):
    #       input_bytes[index] = byte  
    
    bit_count = len(bits)
    word_size = bit_count / 8
    word_size_in_bytes = word_size / 8
    for index in range(8):
        bits_at_index = bits[index::word_size]
        _index = index * word_size_in_bytes    
        
        for offset, _bits in enumerate(slide(bits_at_index, 8)):   
            input_bytes[_index + offset] = int(_bits, 2)
           
def bit_shuffle(data, key, indices):
    for index in indices:
        data = rotate(data[:index], key[index]) + data[index:]
    return data
    
SUBSTITUTION = dict((x, pow(251, x, 257) % 256) for x in xrange(1024 * 1024))
            
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
        _bytes[counter % byte_length] = counter ^ (pow(251, 
                                                       key ^ byte ^ (_bytes[(counter + 1) % byte_length] * counter), 
                                                       257) % 256)
    return _bytes
    