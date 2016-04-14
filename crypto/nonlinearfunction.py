from ctypes import c_uint8 as eight_bit_integer, c_uint16 as word
from utilities import rotate as _rotate
from utilities import cast, hamming_weight

def rotate(word, amount):
    bits = cast(word, "binary")    
    bits = _rotate(bits, amount)
    return cast(bits, "integer")

def nonlinear_function(byte, constant):     
    byte ^= constant
    state = (byte + 1) % 256
    byte ^= eight_bit_integer(state << 5).value
    byte ^= eight_bit_integer(state >> 3).value             
    return byte
        
def nonlinear_function2(state, constant):     
    state ^= constant        
    state += 1    
    state ^= word(state >> 8).value        
    state ^= word(state << 8).value
    state = word(~state).value
  #  state ^= word(state << 5).value
  #  state ^= word(state >> 3).value
    
    
    return eight_bit_integer(state).value, state
        
def nonlinear_function3(data, mask=1 << 7):     
  #  data ^= 1 << (data % 8)
    for bit_number in range(8):    
        other_bits = (data ^ (data & (1 << bit_number))) % 2
        weight = hamming_weight(other_bits)
        data ^= other_bits << bit_number    
       # data = rotate(data, -1)
        data = (data + (other_bits + weight)) % 256
        data ^= 1 << (data % 8)
    
    return data
    
def __nonlinear_function2(data):
    for target_index, target_byte in enumerate(data):
        for source_index, source_byte in enumerate(data):
            if source_index == target_index:
                continue
            data[target_index] ^= nonlinear_function(source_byte)    
             
def find_cycle_length(function, _input, *args, **kwargs):
    outputs = []        
    while True:
        outputs.append(_input)
        _input = function(_input, *args, **kwargs)
        if _input in outputs:
            break
    return outputs
    
def test_nonlinear_function():
    cycle = find_cycle_length(nonlinear_function, 235, 131)
    print len(cycle), sorted(cycle)
    
    sbox = {}
    for byte in range(256):
        sbox[byte] = nonlinear_function(byte, 131)
    from differential import build_difference_distribution_table
    xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
    
    import pprint
    pprint.pprint(xor_ddt)
    pprint.pprint(rotational_ddt)
    
def test_nonlinear_function2():
    cycle = find_cycle_length(nonlinear_function2, 0, 131)
    print len(cycle), cycle
    
    sbox = dict((byte, nonlinear_function2(byte, 131)[0]) for byte in range(256))
    from differential import build_difference_distribution_table
    xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
    
    import pprint
    pprint.pprint(xor_ddt)
    pprint.pprint(rotational_ddt)
    
def test_nonlinear_function3():
    cycle = find_cycle_length(nonlinear_function3, 1)
    print len(cycle), cycle
    
    sbox = dict((byte, nonlinear_function3(byte)) for byte in range(256))
    from differential import build_difference_distribution_table
    xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
    
    import pprint
    for key in xor_ddt.keys():
        print max(xor_ddt[key].values())
    #pprint.pprint(xor_ddt)
    pprint.pprint(rotational_ddt)    
        
        
if __name__ == "__main__":
    #test_nonlinear_function()
    #test_nonlinear_function2()
    test_nonlinear_function3()