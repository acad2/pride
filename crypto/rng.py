import pride.crypto
from pride.crypto.utilities import xor_subroutine, xor_sum, shift_left, shift_right, rotate_left, rotate_right                   
    
def shuffle_extract(data, key, state):
    n = len(data)            
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)        
        data[i], data[j] = data[j], data[i]                 
        key[i] ^= data[j] ^ data[i] ^ key[j] ^ state[0]
        state[0] ^= key[i] ^ data[i]
        
    key[0] ^= data[j] ^ data[i] ^ key[j] ^ key[i] ^ state[0] 
    state[0] ^= key[0] ^ data[0]
    
def random_number_generator(key, seed, tweak, output_size=256):
    state = bytearray(1)    
    state[0] = xor_sum(seed)
    shuffle_extract(tweak, key, state)
    shuffle_extract(tweak, seed, state)

    output = bytearray(output_size)
    while True:              
        shuffle_extract(tweak, seed, state)        
        for index in range(output_size):            
            output[index] = seed[tweak[index]]   
        yield bytes(output)                                              
   
def random_number_generator_subroutine(key, seed, tweak, output, output_size=256):
    state = bytearray(1)    
    state[0] = xor_sum(seed)
    shuffle_extract(tweak, key, state)
    shuffle_extract(tweak, seed, state)
    
    while True:              
        shuffle_extract(tweak, seed, state)        
        for index in range(output_size):            
            output[index] = seed[tweak[index]]   
        yield        
        
def random_bytes(count, seed="\x00" * 256, key="\x00" * 256, tweak=tuple(range(256)), output_size=256):        
    output = bytearray(256)
    generator = random_number_generator_subroutine_inline(bytearray(key), bytearray(seed), bytearray(tweak), output, output_size)    
    amount, extra = divmod(count, output_size)
    amount = amount + 1 if extra else amount
    for chunk in range(amount):
        next(generator)
        output.extend(output[:output_size])    
    return output[output_size:count + output_size]
        
class Disco(pride.crypto.Cipher):
            
    def __init__(self, key, mode, seed=None, tweak=None, output_size=256):
        super(Disco, self).__init__(key, None)

        self.seed = bytearray(seed or "\x00" * 256)
        self.tweak = bytearray(tweak or range(256))
        self.output_size = output_size
        assert len(key) == 256, len(key)
        assert len(self.seed) == 256, (len(self.seed), [byte for byte in self.seed])
        assert len(self.tweak) == 256, len(self.tweak)        
        self.keystream = random_number_generator(bytearray(key), self.seed, self.tweak, output_size=output_size)        
        
    def encrypt(self, data, iv=None, tag=None):
        data = bytearray(data)
        xor_subroutine(data, self.random_bytes(len(data)))
        return bytes(data)
        
    def decrypt(self, data, iv=None, tag=None):
        data = bytearray(data)
        xor_subroutine(data, self.random_bytes(len(data)))
        return bytes(data)
        
    def random_bytes(self, quantity):
        count, remainder = divmod(quantity, self.output_size)
        if remainder:
            count += 1
        output = bytearray()
        keystream = self.keystream
        for counter in range(count):
            output.extend(next(keystream))
        return output        
    
def test_random_number_generator():
    key = bytearray("\x00" * 256)
    tweak = range(256)    
    import pride.datastructures
    from metrics import hamming_distance, cast, test_randomness, test_prng_performance
    #random_megabyte = random_bytes(1024 * 1024, "\x00" * 256)
    #test_randomness(random_megabyte)
    #random_megabyte2 = random_bytes(1024 * 1024, "\x00" * 255 + "\x01")
    #ratio = pride.datastructures.Average(size=65535)
    #for chunk in range((1024 * 1024) / 256):
    #    _slice = slice(chunk * 256, (chunk + 1) * 256)
    #    distance = hamming_distance(random_megabyte[_slice], random_megabyte2[_slice])
    #    ratio.add(distance) 
    #minimum, average, maximum = ratio.range
    #bit_count = float(len(cast(random_megabyte[_slice], "binary")))
    #print "Minimum Hamming distance and ratio: ", minimum / bit_count
    #print "Average Hamming distance and ratio: ", average / bit_count
    #print "Maximum Hamming distance and ratio: ", maximum / bit_count     
    #    
    #test_bias(random_megabyte)
    test_prng_performance(lambda data, output_size: random_bytes(output_size))
    
def test_Disco():
    #key = bytearray("\x00" * 256)
    Disco.test_metrics(avalanche_test=False, bias_test=True, randomness_test=True, period_test=True, keysize=256)
    #cipher = Disco(key, "ctr")
    
def test_nonlinear_function():
    import pprint
    from differential import build_difference_distribution_table, find_best_output_differential
    table1, table2 = build_difference_distribution_table(bytearray(nonlinear_function(count) for count in range(256)))
   # pprint.pprint(table1)
    #pprint.pprint(table2)
    max_probability = (0, 0, 0)
    for input_differential in xrange(1, 256):
        output = find_best_output_differential(table1, input_differential)
        if output[-1] > max_probability[-1]:
            max_probability = output
    print max_probability
    #for x in range(256):
    #    print nonlinear_function(x)
        
def test_bias(random_data):    
    outputs = [[] for count in range(256)]
    for chunk in slide(random_data, 256):
        for index, byte in enumerate(chunk):
            outputs[index].append(byte)
    print [len(set(item)) for item in outputs]
    
def test_shuffle_extract():
    from metrics import test_randomness, test_avalanche
    random_megabyte = bytearray()
    data = range(256)
    #key = bytearray("\x00" * 256)
    #for chunk in range((1024 * 1024) / 256):
    #    shuffle_extract(data, key)
    #    random_megabyte.extend(key[:])
    #
    #test_randomness(random_megabyte)
    #

    
    def _test_avalanche(_input):
        _input = bytearray(_input)
        key = bytearray("\x00" * len(_input))
        shuffle_extract(range(len(_input)), key, _input)
        return bytes(key)
        
    test_avalanche(_test_avalanche)
    
    #last_output = next(generator)
    #for x in range(65535):
    #    next_output = next(generator)
        
        
if __name__ == "__main__":
    test_random_number_generator()
    #test_shuffle_extract()
    #test_Disco()
  #  test_nonlinear_function()
    