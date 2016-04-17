import pride.crypto
from pride.crypto.blockcipher import extract_round_key
from pride.crypto.utilities import xor_subroutine, xor_sum

def shuffle(data, key): 
    n = len(data)    
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)
        data[i], data[j] = data[j], data[i]
        
def extract_round_key(key): 
    """ Non invertible round key extraction function. """
    for round in range(2):
        xor_sum_of_key = xor_sum(key)    
        shuffle(key, key)
        for index, key_byte in enumerate(key):        
            key[index] = (xor_sum_of_key + key_byte + (~index + 256)) % 256    
        
def random_number_generator(key, first_set, output_size=256):
    extract_round_key(key)    
    key_two = key[:]
    extract_round_key(key_two)
    key_three = key_two[:]
    extract_round_key(key_three)
    
    print key
    print
    print key_two
    print
    print key_three
    shuffle(first_set, key)
    second_set = first_set[:]
    shuffle(second_set, key_two)
    third_set = second_set[:]
    shuffle(third_set, key_three)
    
    output_set = bytearray(256)
    while True:
        shuffle(first_set, key)
        shuffle(second_set, key_two)
        shuffle(third_set, key_three)
        
        for index in range(256):
            output_set[index] = first_set[index] ^ second_set[index] ^ third_set[index]
        shuffle(output_set, key)
        yield bytes(output_set[:output_size])                   
            
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
    key = bytearray("\x00" * 8)
    for round in range(4):
        extract_round_key(key)
        print key
    
def test_random_number_generator():
    key = bytearray("\x00" * 256)
    generator = random_number_generator(key, range(256), 16)
    next(generator)
    for _bytes in range(16):
        print next(generator)
            
def test_Disco():
    #key = bytearray("\x00" * 256)
    Disco.test_metrics(avalanche_test=False, bias_test=True)
    #cipher = Disco(key, "ctr")
    
    
if __name__ == "__main__":
    #test_extract_round_key()
    test_random_number_generator()
    #test_Disco()