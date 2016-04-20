def shuffle_extract(data, key, state):
    """ State update and round key extraction function. """
    n = len(data)            
    for i in reversed(range(1, n)):
        # Fisher-Yates shuffle
        j = state[0] & (i - 1)        
        data[i], data[j] = data[j], data[i]  
                
        key[i] ^= data[j] ^ data[i] # randomize key value
        state[0] ^= key[i] ^ i ^ key[j] # update state with output feedback + nonce
        
    key[0] ^= data[j] ^ data[i] 
    state[0] ^= key[0] ^ key[j]
    
def random_number_generator(key, seed, tweak, output_size=256):
    """ Psuedorandom number generator. Operates by randomly shuffling the
        set of 256 elements according to an internal state array.
        
        One round consists of a permutation of the set array along with a
        randomizing of the internal state array. 
        
        Each output byte is obtained by selecting a byte from the state in
        a random location determined by the set.
        
        Output size is configurable to allow for a tunable security capacity,
        similar to a cryptographic sponge function. 
        
        Internally, two states are used: The main state array, and an 8-bit
        byte. The 8-bit byte contributes to diffusion and avalanche"""    
    state = bytearray(1)            
    for byte in seed:
        state[0] ^= byte    
    shuffle_extract(tweak, key, state)
    shuffle_extract(tweak, seed, state)
    
    output = bytearray(output_size)
    while True:                  
        shuffle_extract(tweak, seed, state)        
        for index in range(output_size):            
            output[index] = seed[tweak[index]]   
        yield bytes(output)                                              
      
def _random_number_generator_subroutine(key, seed, tweak, output, output_size=256):
    """ Identical to random_number_generator; This uses less allocations and is more performant. """
    state = bytearray(1)        
    for byte in seed:
        state[0] ^= byte
    shuffle_extract(tweak, key, state)
    shuffle_extract(tweak, seed, state)
    
    while True:         
        shuffle_extract(tweak, seed, state)        
        for index in range(output_size):            
            output[index] = seed[tweak[index]]   
        yield        
        
def random_bytes(count, seed="\x00" * 256, key="\x00" * 256, tweak=tuple(range(256)), output_size=256):   
    """ Generates count random bytes using random_number_generator using the 
        supplied/default seed, key, tweak, and output_size. """
    output = bytearray(256)
    generator = _random_number_generator_subroutine(bytearray(key), bytearray(seed), bytearray(tweak), output, output_size)    
    amount, extra = divmod(count, output_size)
    amount = amount + 1 if extra else amount
    for chunk in range(amount):
        next(generator)
        output.extend(output[:output_size])    
    return bytes(output[output_size:count + output_size])
    