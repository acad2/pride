import itertools   
from utilities import rotate
from additional_builtins import slide

ASCII = ''.join(chr(x) for x in range(256))

def binary_form(_string):
    try:
        return ''.join(format(ord(character), 'b').zfill(8) for character in _string)
    except TypeError:        
        return format(_string, 'b')
        
def byte_form(bitstring):
    slice_count, remainder = divmod(len(bitstring), 8)                   
    output = ''
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * 8
        output += chr(int(bitstring[_position:_position + 8], 2))
    return output

def prime_generator():
    primes = [2]
    yield 2
    for test_number in itertools.count(3, 2):
        for prime in primes:
            if not test_number % prime:
                break
        else:
            yield test_number
            primes.append(test_number)
            
def unpack_factors(bits):   
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
    power = 0
    output = 1    
    last_bit = len(bits) - 1
    for bit in bits[:-1]:
        if bit == '1':
            power += 1
        else:                        
            output *= variable ** power
            power = 0          
            variable = next(variables)              
    if bits[-1] == '1':
        power += 1
    output *= variable ** power       
    return output
    
def one_way_compression(data, prime=17, modulus=257):
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
    
def hash_function(hash_input, key='', output_size=None, iterations=1):
    """ A tunable, variable output length hash function. Security is based on
        the hardness of the well known problem of integer factorization. """
    input_size = str(len(hash_input))
    state = binary_form(hash_input + input_size)
    state += binary_form(input_size + str(len(state)))
  #  print state
    
    for round in range(iterations):
        state = binary_form(unpack_factors(state))# + binary_form(str(len(state)))
        random_index = pow(17, int(state, 2), len(state))
        state = rotate(state[:random_index] + state[random_index+16:], 
                       int(state[random_index:random_index+16], 2))        
        
    state_size = (len(state) / 8) - 1    
    if output_size and state_size < output_size:     
        return hash_function(state + str(state_size) + hash_input, 
                             output_size=output_size)
    else:
        return rotate(byte_form(state[:-8])[:output_size], int(state[-8:], 2))
        
def test_hash_function():      
    outputs = []    
    from hashlib import sha1
    for count, possibility in enumerate(itertools.product(ASCII, ASCII)):
        hash_input = ''.join(possibility)        
        hash_output = hash_function(hash_input, output_size=4, iterations=1)
        assert hash_output not in outputs, ("Collision", count, hash_output)
        outputs.append(hash_output)       
        
if __name__ == "__main__":
    test_hash_function()