import os
import itertools

def permute(left, right, key, mask, bit_width):    
    for round in range(5):
        right = (right + key + key + 1 + round) & mask
        left = (left + (right >> 8)) & mask
        left ^= ((right >> 5) | (right << (bit_width - 5))) & mask        
    return left, right & 255
    
def permutation(data, key, mask, bit_width):
    for index in reversed(range(1, len(data))):
        next_index = index - 1
        data[next_index], data[index] = permute(data[next_index], data[index], key[index], mask, bit_width)        
        
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
    
def shuffle(data, key):
    for index in reversed(range(1, len(data))):
        other_index = next(key) & (index - 1)
        data[index], data[other_index] = data[other_index], data[index] 

def generate_key(size, key=None):
    if generate_key.primes is None:
        _primes = prime_generator()      
        generate_key.primes = [next(_primes) for count in range(2048)]    
    primes = generate_key.primes[:] 
    key = itertools.cycle(bytearray(key or os.urandom(size)))
    shuffle(primes, key)
    return primes[:size]
generate_key.primes = None
    
def find_permute_cycle_length(max_size, block_size, function, left, right, key, mask, bit_width):
    recycle_point =(left, right)
    count = 0
    blocks, extra = divmod(max_size, block_size)
    exit_flag = False
    for block in xrange(blocks if not extra else blocks + 1):        
        for counter in xrange(block_size):                           
            _input = left, right = function(left, right, key, mask, bit_width) 
          #  print _input
            if _input == recycle_point:  
                exit_flag = True                
                break
            else:
                count += 1
                
        if exit_flag:
            break                
        yield count

    yield count
        
def find_permutation_cycle_length(max_size, block_size, function, _input, key, mask, bit_width):
    recycle_point = set()     
    blocks, extra = divmod(max_size, block_size)
    exit_flag = False
    for block in xrange(blocks if not extra else blocks + 1):        
        for counter in xrange(block_size):                           
            function(_input, key, mask, bit_width) 
            __input = bytes(_input)
           # print __input
            if __input in recycle_point:  
                exit_flag = True                
                break
            else:                           
                recycle_point.add(__input)
                
        if exit_flag:
            break                
        yield len(recycle_point)
        
    yield len(recycle_point)
    yield recycle_point
    
def test_permute():    
    for progress in find_permute_cycle_length((2 ** 32), 1024, permute, 0, 0, 1, (2 ** 16) - 1, 16):
        print progress
        
def test_permutation():
    size = 3
    bits = size * 8
#    for test in range(16):
    for progress in find_permutation_cycle_length((2 ** bits), 1024, permutation, list(bytearray("\x00" * size)), generate_key(size), (2 ** bits) - 1, bits):
        if isinstance(progress, int):
            print progress
        
def bytes_to_words(seed, wordsize):
    state = []
    seed_size = len(seed)
    for offset in range(seed_size / wordsize):        
        byte = 0
        offset *= wordsize
        for index in range(wordsize):        
            byte |= seed[offset + index] << (8 * index)
        state.append(byte)
    return state
    
def words_to_bytes(state, wordsize):        
    output = bytearray()
    storage = state[:]
    while storage:
        byte = storage.pop(0)
        for amount in range(wordsize):
            output.append((byte >> (8 * amount)) & 255)
    return output
    
def iv_generator(key, seed, wordsize=8, mask=(2 ** 64) - 1):
    state = bytes_to_words(seed, wordsize)    
    bit_width = wordsize * 8
    while True:
        permutation(state, key, mask, bit_width)          
        yield words_to_bytes(state, wordsize)
        
def test_iv_generator():
    outputs = []
    size = 2
    seed = bytearray("\x00" * size)
    _seed = seed[:]
    key = generate_key(size)
    generator = iv_generator(key, seed)      
    next_iv = lambda *args: next(generator)
        
    for progress in find_permutation_cycle_length((2 ** 16), 1024, next_iv, _seed, None, None, None):
        print progress
        
    #for iv in iv_generator(key, seed):
    #    print iv
    #    if iv not in outputs:
    #        outputs.append(iv)
    #    else:
    #        break
            
if __name__ == "__main__":
    #test_permute()
    test_permutation()
    #test_iv_generator()
    