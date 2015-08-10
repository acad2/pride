def xor(binary_string1, binary_string2):
    result = bytes()
    for power, bits in enumerate(zip(reversed(binary_string1), 
                                     reversed(binary_string2))):
        result += '1' if (bits[0] or bits[1]) and bits[0] != bits[1] else '0'
    return result
        
print xor('1011', '0100')
print xor('0011', '1100')
print xor('1001', '1001')

def xor2(any_base_string, same_base_string, base=2):
    result = bytes()
    for index, byte in enumerate(any_base_string):
        
    
    return format((int(any_base_string, base) + int(same_base_string, base)) % 10, 'b').zfill(4)
    
print xor2('1011', '0100')
print xor2('0011', '1100')
print xor2('1001', '1001')

