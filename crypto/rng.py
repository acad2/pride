import pride.crypto
from pride.crypto.utilities import xor_subroutine, xor_sum, shift_left, shift_right, rotate_left, rotate_right                   
    
def shuffle_extract(data, key):
    n = len(data)        
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)        
        data[i], data[j] = data[j], data[i]         
        
        key[i] ^= data[j] ^ data[i] ^ key[j]
    key[0] ^= data[j] ^ data[i] ^ key[j] ^ key[i]
    
def random_number_generator(key, seed, output_size=256):    
    shuffle_extract(seed, key)    
    state_size = len(seed)
    state = bytearray(state_size)
    output = bytearray(output_size)
    while True:      
        shuffle_extract(seed, key)  
                     
        for index in range(state_size):
            state[index] ^= seed[index]
        
        for index in range(output_size):            
            output[index] = state[seed[index]]        
        yield bytes(output)                                              
                        
class Disco(pride.crypto.Cipher):
            
    def __init__(self, key, mode, seed=None, output_size=256):
        super(Disco, self).__init__(key, mode)
        self.seed = seed or range(256)
        self.output_size = output_size
        self.keystream = random_number_generator(bytearray("\x00" * 256), bytearray(self.seed), output_size)
        self.blocksize = 256
        
    def encrypt_block(self, data, *args):
        xor_subroutine(data, self.random_bytes(len(data)))
        
    def random_bytes(self, quantity):
        count, remainder = divmod(quantity, self.output_size)
        if remainder:
            count += 1
        output = bytearray()
        keystream = self.keystream
        for counter in range(count):
            output.extend(next(keystream))
        return output
        
def test_extract_round_key():
    key = bytearray("\x00" * 256)
    for round in range(4):
        extract_round_key(key)
        print key
    
def test_random_number_generator():
    key = bytearray("\x00" * 256)
    generator = random_number_generator(key, range(256), 16)
    next(generator)
    print key
    for _bytes in range(16):
        print
        next(generator)
            
def test_Disco():
    #key = bytearray("\x00" * 256)
    Disco.test_metrics(avalanche_test=False, bias_test=True, randomness_test=False, period_test=False)
    #cipher = Disco(key, "ctr")
    
def test_extract_round_key_metrics():        
    class Test_Cipher(pride.crypto.Cipher):
        
        def __init__(self, *args):
            super(Test_Cipher, self).__init__(*args)
            self.blocksize = 16
            
        def encrypt_block(self, data, key):
            extract_round_key(data)            
            
    Test_Cipher.test_metrics(avalanche_test=False, randomness_test=False, period_test=False)    
  
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
        
def test_shuffle_extract():
    from metrics import test_randomness
    random_megabyte = bytearray()
    data = range(256)
    key = bytearray("\x00" * 256)
    for chunk in range((1024 * 1024) / 256):
        shuffle_extract(data, key)
        random_megabyte.extend(key[:])
    
    #generator = random_number_generator(bytearray("\x00" * 256), range(256))
    
     #   random_megabyte += next(generator)
    test_randomness(random_megabyte)
    
    outputs = [[] for count in range(256)]
    for chunk in slide(random_megabyte, 256):
        for index, byte in enumerate(chunk):
            outputs[index].append(byte)
    print [len(set(item)) for item in outputs]
    
if __name__ == "__main__":
    #test_extract_round_key()
    #test_extract_round_key_metrics()
    #test_random_number_generator()
    #test_shuffle_extract()
    test_Disco()
  #  test_nonlinear_function()
    