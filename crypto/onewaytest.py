from utilities import slide

ASCII_CONSTANT = ''.join(chr(x) for x in xrange(256)) + "\x00"
                            
def xor_sum(data):
    output = 0
    for byte in data:
        output ^= byte
    return output
    
def one_way_function(old_value, tweak=ASCII_CONSTANT, output_size=16):
    generator = one_way_function_gen(old_value, tweak)
    return ''.join(next(generator) for count in range(output_size))
    
def one_way_function_gen(old_value, tweak=ASCII_CONSTANT):
    new_base = tweak           
    old_base_mapping = {}
    old_value = ''.join(reversed(old_value))
    for index, symbol in enumerate(slide(old_value, 2)):
        old_base_mapping[symbol] = index
   # print old_base_mapping
    _old_value = bytearray(old_value)    
    
    xor_key = xor_sum(_old_value)
    sum_key = sum(_old_value)
    old_base_size = len(old_base_mapping)    
#    decimal_value = ((sum(bytearray(_old_value)) ^ key) +
#                      sum(((key ^ old_base_mapping[value_representation]) * (old_base_size ** power) for
#                            power, value_representation in enumerate(slide(old_value, 2)))))
    decimal_value = sum_key ^ xor_key
    for power, value_representation in enumerate(slide(old_value, 2)):
        decimal_value += (xor_key ^ old_base_mapping[value_representation]) * (old_base_size ** power)
        xor_key ^= (2 ** power) % 256
        #sum_key += power 
                
    new_value = ''
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action 
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
            yield new_base[digit]
            decimal_value += (sum_key ^ xor_key)
            decimal_value ^= xor_key << 1
    #return ''.join(reversed(new_value))#[:-1])) if len(new_value) > 1 else new_value
        
if __name__ == "__main__":    
    from os import urandom
    print one_way_function("The quick brown fox jumps over the lazy dog" * 1)
    print
    print one_way_function("The quick brown fox jumps over the lazy dog" * 1)
    outputs = []
    import itertools
    for _bytes in (chr(byte1) + chr(byte2) for byte1, byte2 in itertools.product(range(256), range(256))):        
        output = one_way_function(_bytes)
        outputs.append(output)
     #   print output
    print len(set(outputs)), len(outputs)