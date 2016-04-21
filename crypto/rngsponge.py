import rng
from utilities import cast, slide, xor_subroutine, replacement_subroutine

def pad_input(hash_input, rate):
    size = len(hash_input)
    length = str(size)
    hash_input += "\x80" + ("\x00" * (size - len(length))) + length
    return hash_input    

def variable_length_hash(state, rate, output_size, mix_state_subroutine, absorb_mode, tweak, _state):    
    output = state[:rate]
    while len(output) < output_size:
        _state = mix_state_subroutine(tweak, state, _state)        
        output += state[:rate]      
    return bytes(output[:output_size])
    
def prng_generator(state, rate, output_size, mix_state_subroutine, absorb_mode, tweak, _state):    
    while True:
        yield state[:rate]
        _state = mix_state_subroutine(tweak, state, _state)    
    
def encryption_generator(state, rate, output_size, mix_state_subroutine, absorb_mode, tweak, _state):    
    input_block = yield None        
    while input_block is not None:
        xor_subroutine(state, bytearray(input_block))
        input_block = yield bytes(state[:len(input_block)])
        _state = mix_state_subroutine(tweak, state, _state)        
    yield bytes(state[:rate])
    
def decryption_generator(state, rate, output_size, mode_of_operation, absorb_mode, tweak, _state):    
    input_block = yield None       
    while input_block is not None:
        last_block = state[:len(input_block)]
        xor_subroutine(state, bytearray(input_block))
  
        input_block = yield bytes(state[:len(input_block)])
        xor_subroutine(state, last_block)       
        _state = mix_state_subroutine(tweak, state, _state)    
    authentication_code = yield bytes(state[:rate])
    if authentication_code != state[:rate]:
        raise ValueError("Invalid tag")
        
def rng_absorb(data, state, rate, mix_state_subroutine, absorb_subroutine, tweak, _state): 
    for block in slide(bytearray(data), rate):
        absorb_subroutine(state, block)
        _state = mix_state_subroutine(tweak, state, _state)
    return _state
        
def rng_sponge_function(hash_input, tweak=tuple(range(256)), key='', output_size=32, capacity=32, rate=224, 
                        mix_state_subroutine=rng.shuffle_extract,
                        mode_of_operation=variable_length_hash,
                        absorb_mode=xor_subroutine):  
    state_size = capacity + rate
    state = bytearray(state_size)
    tweak = bytearray(tweak)
    hash_input = bytearray(hash_input)
    _state = hash_input[0] if hash_input else 0
    if key:
        _state = rng_absorb(key, state, rate, mix_state_subroutine, absorb_mode, tweak, _state)      
    
    hash_input = pad_input(hash_input, rate)
        
    for _bytes in slide(hash_input, rate):
        _state = rng_absorb(_bytes, state, rate, mix_state_subroutine, absorb_mode, tweak, _state)
    
    _state = mix_state_subroutine(tweak, state, _state)
    return mode_of_operation(state, rate, output_size, mix_state_subroutine, absorb_mode, tweak, _state)
    
def test_rng_sponge_function():
    print rng_sponge_function('')
    for x in range(8):
        print rng_sponge_function(chr(x))
    from metrics import test_hash_function
    test_hash_function(rng_sponge_function)
        
if __name__ == "__main__":
    test_rng_sponge_function()
    