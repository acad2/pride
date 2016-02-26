ASCII_CONSTANT = ''.join(chr(x) for x in xrange(256)) + "\x00"
                            
def xor_sum(data):
    output = 0
    for byte in data:
        output ^= byte
    return output
    
def one_way_function(old_value, tweak=ASCII_CONSTANT):
    new_base = tweak
    old_value = bytearray(old_value)
        
    old_base_mapping = bytearray(256)
    
    for index, symbol in enumerate(old_value):
        if not old_base_mapping[symbol]:
            old_base_mapping[symbol] = index
        
    key = xor_sum(old_value)
    old_base_size = len(old_value)    
    decimal_value = (sum(bytearray(old_value)) +
                     sum(((old_base_mapping[key ^ value_representation]) * (old_base_size ** power) for
                          power, value_representation in enumerate(reversed(old_value)))))
    #decimal_value = sum(old_value)
    #for power, value_representation in enumerate(reversed(old_value)):
    #    decimal_value += (key ^ old_base_mapping[key ^ value_representation]) * (old_base_size ** power)
    # #   key ^= (value_representation * (2 ** power) % 256)
        
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action 
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return ''.join(reversed(new_value))
    
if __name__ == "__main__":    
    from os import urandom
    print one_way_function("The quick brown fox jumps over the lazy dog" * 1)
    print
    print one_way_function("The quick brown fox jumps over the lazy cog" * 1)
    