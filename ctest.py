ASCII = ''.join(chr(x) for x in xrange(256))

def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)
    new_base_size = len(new_base)
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
    decimal_value = 0    
    new_value = ''
    
    for power, value_representation in enumerate(reversed(old_value)):
        decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value == 0:
        new_value = new_base[0]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]

    return ''.join(reversed(new_value))
    
def compress_message(message):
    key = list(set(message))
    compressed = convert(message, key, ASCII)
    return key, compressed
    
if __name__ == "__main__":
    test_message = "This is a test message that will be compressed. Hopefully." * 100
    key, compressed_message = compress_message(test_message)
    print len(key), len(compressed_message), len(test_message)