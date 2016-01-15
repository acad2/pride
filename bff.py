""" binary factor format - stores an integer representation of a number with
    potentially less bits. Encodes prime numbers and exponents based on bit indices.
    
    Each bit of regular binary is potentially an addition to the exponent of 
    the base number 2. For example:
        
        0001 # 2 ** 0
        0010 # 2 ** 1
        0100 # 2 ** 2
        1000 # 2 ** 3
        ...
        
    With the binary factor format, the base value is incremented to the 
    next prime every time a 0 bit is encountered in the bit string. Thus:
        
        0001 # 7 ** 1
        0010 # 5 ** 1
        0100 # 3 ** 1
        1000 # 2 ** 1
        
    The exponent for each prime is determined by the number of contiguous 1 bits.
    For example:
        
        1000 # 2 ** 1
        1100 # 2 ** 2
        1101 # (2 ** 2) * (5 ** 1)
        
    Because each '1' bit is usually an exponent of a power significantly larger
    then two, this encoding can potentially represent larger numbers with the
    same quantity of bits. """                          
from itertools import cycle, product, chain
from mathutilities import prime_generator
from mathutilities import _factor as factor

BINARY_SETS = (set("01"), set('0'), set('1'))

def slide(iterable, x=16):
    """ Yields x bytes at a time from iterable """
    slice_count, remainder = divmod(len(iterable), x)
    for position in range((slice_count + 1 if remainder else slice_count)):
        _position = position * x
        yield iterable[_position:_position + x] 
        
def pack_factors(factors, variables=None):
    """ Pack a series of (prime, power) tuples into a bitstring.
        Depending on the composition of the factors, the returned
        bitstring may represent the integer form of the factored number
        with less bits then the integer form requires. """
    output = ''     
    if not variables:
        variables = prime_generator()
    else:
        variables = chain(iter(variables), prime_generator())
    variable = next(variables)
    for factor, power in factors:
        while variable != factor:
            output += '0'
            variable = next(variables)
        output += '1' * power
    return output    
    
def unpack_factors(bits, variables=None):   
    """ Unpack encoded (prime, power) pairs and compose them into an integer """    
    if set(bits) not in BINARY_SETS:        
        raise ValueError("bits must contain only '0' and/or '1', not {}".format(set(bits)))
    if '1' not in bits:
        return 0 
        
    if not variables:
        variables = prime_generator()
    else:        
        variables = chain(iter(variables), prime_generator())        
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
    print "Performing final operation: ", variable, power
    output *= variable ** power       
    return output
   
def compress(data):    
    raise NotImplementedError
    bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)    
    return pack_factors(factor(int(bits, 2)))

def decompress(compressed_bits):    
    integer_form = unpack_factors(compressed_bits)
    bits = format(integer_form, 'b')
    padding = 8 - (len(bits) % 8)
    bits = ('0' * padding) + bits    
    return ''.join(chr(int(byte, 2)) for byte in slide(bits, 8))
    
def compress_runs(bitstring, bit_width=4):
    first_symbol = last_symbol = bitstring[0]
    output = ''
    count = 0
    _bit_width = (2 ** bit_width) - 1
  #  print "Set symbol to: ", last_symbol
    for bit in bitstring:
        if bit == last_symbol and count < _bit_width:
            count += 1
        else:
            assert count <= _bit_width, (count, _bit_width)
            print count, _bit_width
            output += format(count, 'b').zfill(bit_width) 
            count = 1
            last_symbol = bit
    return first_symbol + output
        
def decompress_runs(bitstring, bit_width=2):
    output = ''
    current_symbol = bitstring[0]
    opposite_symbol = '1' if current_symbol == '0' else '0'
    for bits in slide(bitstring[1:], bit_width):       
        output += int(bits, 2) * current_symbol
        current_symbol, opposite_symbol = opposite_symbol, current_symbol
    return output
        
def expand_seed(seed="00000001", iterations=0, variables=None):     
    iterations = cycle((1, )) if not iterations else xrange(iterations)
    seed_width = len(seed)
    for iteration in iterations:        
        seed = ''.join(format(unpack_factors(seed, variables), 'b'))#.zfill(seed_width))    
    return seed.zfill(seed_width)
    
def test_pack_factors():
    factors = ((11, 11), (101, 8))
    packed_factors = pack_factors(factors, prime_generator())
    
    #number = 1
    #for factor, power in factors:
    #    number *= factor ** power    
    #packed_integer = format(number, 'b')
    #print len(packed_factors), packed_factors
    #print len(packed_integer), packed_integer   
    
def test_unpack_factors():
    outputs = []
    primes = []
    prime_gen = prime_generator()
    for x in xrange(4096):
        primes.append(next(prime_gen))        
        
    for x in xrange(256):#2 ** 16):
        output = unpack_factors(format(x, 'b').zfill(8), primes)
        assert output not in outputs
        print format(x, 'b').zfill(16), format(output, 'b').zfill(16)
        outputs.append(output)
    #outputs = [unpack_factors(format(x, 'b').zfill(16), prime_generator()) for x in xrange(512)]
    #assert len(set(outputs)) == 512, len(set(outputs)) 
   
def test_expand_seed():
    outputs = {}
    inputs = [('0', '1') for x in xrange(8)]
    for _input in product(*inputs * 2):                
        _input = ''.join(_input)
        output = expand_seed(_input, iterations=1)
        assert output not in outputs, ("Collision found: ", output, outputs[output], _input)
        outputs[output] = _input
    
def test_compress():
    data = "Test" 
    byte = "000000011"
    key = None#(int(byte * 8, 2), int(byte * 4, 2), int(byte * 2, 2), int(byte * 1, 2))
    compressed = compress(data)
    data_bits = ''.join(format(ord(character), 'b').zfill(8) for character in data)
    print "Data bits: ", len(data_bits), data_bits
    print "Comp bits: ", len(compressed), compressed
    runs_compressed = compress_runs(compressed)
    print "Runs bits: ", len(runs_compressed), runs_compressed
    hrmm = compress_runs(data_bits)
    print "Well hrmm: ", len(hrmm), hrmm
    decompressed = decompress(compressed)
    assert decompressed == data, decompressed
    print decompress(compressed)
    
def test_compress_runs():
    bits = "110011100011110000101010"
    compressed = compress_runs(bits)
    print "Bits: ", bits
    print "Comp: ", compressed
    decompressed = decompress_runs(compressed)
    assert decompressed == bits, (decompressed, bits)
    
if __name__ == "__main__":
    #test_pack_factors()
    test_unpack_factors()
    #test_expand_seed()
    #test_compress_runs()
    #test_compress()