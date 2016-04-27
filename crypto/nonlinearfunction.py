from ctypes import c_uint8 as eight_bit_integer, c_uint16 as word
from utilities import rotate as _rotate
from utilities import cast, hamming_weight, rotate_left, rotate_right, shift_left, shift_right

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
    
def nonlinear_function4(byte):        
    state = 0
    for bit in range(8):
        state ^= rotate_right(byte & rotate_left(1, bit), bit)                
             
    for bit in range(4):                        
        byte ^= rotate_left(state, bit)                  
        state ^= rotate_right(byte & rotate_left(1, bit), bit)
    
    byte = rotate_left(byte, 6)
    return byte
    
def nonlinear_function5(byte, key=6): 
    print "Function enter"
    for offset, bit in enumerate(reversed(range(1, 8))):
        random_bit = key & (bit - 1)
        shift_amount = bit - random_bit
        print format(byte, 'b').zfill(8), bit, random_bit
        byte ^= ((1 << offset) & byte) << shift_amount
        print format(byte, 'b').zfill(8), format(((1 << offset) & byte) << shift_amount, 'b').zfill(8)
        byte ^= ((1 << shift_amount) & byte) >> shift_amount
        print format(byte, 'b').zfill(8), format(((1 << shift_amount) & byte) >> shift_amount, 'b').zfill(8)
        byte ^= ((1 << offset) & byte) << shift_amount
        print format(byte, 'b').zfill(8)
                                  
    return byte
    
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
        
def test_nonlinear_function4():
    from differential import build_difference_distribution_table, find_best_output_differential
    #max_cycle = ([], 0)
    #for state in range(256):
    cycle = find_cycle_length(nonlinear_function4, 1)
 #       if len(cycle) > max_cycle[1]:
 #           max_cycle = (len(cycle), cycle, state)
    print len(cycle), set(range(256)).difference(cycle), cycle
  #  print max_cycle
    sbox = bytearray(nonlinear_function4(index) for index in range(256))
    xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
    best_differential = (None, None, 0)
    for difference in range(1, 256):
        info = find_best_output_differential(xor_ddt, difference)        
        if info[-1] > best_differential[-1]:
            best_differential = info
    print best_differential
            
def test_nonlinear_function5():
    from differential import build_difference_distribution_table, find_best_output_differential
    cycle = find_cycle_length(nonlinear_function5, 1)
    print len(cycle), set(range(256)).difference(cycle), cycle
    
   # sbox = bytearray(nonlinear_function4(index) for index in range(256))
   # xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
   # best_differential = (None, None, 0)
   # for difference in range(1, 256):
   #     info = find_best_output_differential(xor_ddt, difference)        
   #     if info[-1] > best_differential[-1]:
   #         best_differential = info
   # print best_differential    
    
if __name__ == "__main__":
    #test_nonlinear_function()
    #test_nonlinear_function2()
    #test_nonlinear_function3()
    test_nonlinear_function4()
    #test_nonlinear_function5()