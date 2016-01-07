import itertools

from random import _urandom as random_bytes
from pride.utilities import rotate

ascii = ''.join(chr(x) for x in range(256))

def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)    
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
            
    for leading_zero_count, symbol in enumerate(old_value):
        if old_base_mapping[symbol]:
            break
    zero_padding = new_base[0] * leading_zero_count
    
    decimal_value = sum((old_base_mapping[value_representation] * (old_base_size ** power) for
                         power, value_representation in enumerate(reversed(old_value))))                 
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return zero_padding + ''.join(reversed(new_value))  
    
def new_key(size=256):
    key = []
    while len(set(key)) < size:
        random_numbers = random_bytes(size)        
        key.extend(set(random_numbers).difference(key))
    return ''.join(key[:size])
        
def generate_primes(start=3, number=4, first_divisor=2, _lookahead_size=10):
    if not start % 2:
        if start == 2:
            yield 2
        start += 1# must be odd
    assert first_divisor < number, (first_divisor, number)
    assert start < number
    filter = set()
    for divisor in xrange(first_divisor, number):        
        for _number in xrange(start, number, 2):
            if _number not in filter:
                if _number == divisor:
                    yield _number                    
                    filter.update([_number * x for x in xrange(_lookahead_size)])
                elif not _number % divisor:         
                    filter.add(_number)
                  
def pack_factors(factors):
    output = ''
    prime_generator = generate_primes(2, 2 ** 16)
    prime = next(prime_generator)
    for factor, power in factors:
        while prime != factor:
            output += '0'
            prime = next(prime_generator)
        output += '1' * power
    return output
    
def one_way_function(bits):   
    """ Outputs a unique sequence of bits derived from bits"""
    prime_generator = generate_primes(2, 2 ** 16)
    prime = next(prime_generator)
    power = 0
    output = 1    
    last_bit = len(bits) - 1
    for index, bit in enumerate(bits):
        if bit == '1':
            power += 1
            if index == last_bit:
                output *= prime ** power
        else:
            output *= prime ** power
            power = 0
            prime = next(prime_generator)      
    return output
        
def test_hash(hash_input, constant=ascii, key=None):
    length = len(hash_input)
    key = key or ascii
    key2 = ''
    for character in hash_input + str(length):
        if character not in key2:
            key2 += character
    length2 = len(key2)
    print length, length2
    return convert(constant, key, key2)
    
def test_convert():
    data = chr(0) + chr(0) + "This is a test. This is a test. "
    _key = new_key()    
    #print data
    for key in (rotate(ascii, count) for count in range(3)): 
      #  key = new_key()
        converted = convert(data, _key, key)
        converted_back = convert(converted, key, _key)
    #    print converted
        assert data == converted_back, (len(data), len(converted_back), converted_back)
    
def test_test_hash():
    _input = "Test"
    output = test_hash(_input)
    _input2 = "Tdst"
    output2 = test_hash(_input2)
    assert output != output2
    print output
    print output2
    
def test_one_way_function():
    outputs = [one_way_function(format(x, 'b').zfill(16)) for x in xrange(512)]
    assert len(set(outputs)) == 512, len(set(outputs))
    for output in outputs:
        print output
        
def test_pack_factors():
    factors = ((11, 11), )
    number = 1
    for factor, power in factors:
        number *= factor ** power
    packed_factors = pack_factors(factors)
    packed_integer = format(number, 'b')
    print len(packed_factors), packed_factors
    print len(packed_integer), packed_integer
    
if __name__ == "__main__":
    #test_convert()
    test_one_way_function()
    #test_pack_factors()