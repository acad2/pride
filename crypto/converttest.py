import os    

def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)    
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
            
    for leading_zero_count, symbol in enumerate(old_value):
        if old_base_mapping[symbol]:
            break
    zero_padding = new_base[0] * leading_zero_count
    
    decimal_value = sum((old_base_mapping[value_representation] * (old_base_size ** power) for
                         power, value_representation in enumerate(reversed(old_value))))
    
    # this is the above in a potentially more readable format:
    # decimal_value = 0    
    # for power, value_representation in enumerate(reversed(old_value)):
    #     decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
                            
    if decimal_value:
        new_base_size = len(new_base)    
        new_value = ''
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return zero_padding + ''.join(reversed(new_value))  
    
def shuffle(data, key): 
    n = len(data)
    for i in reversed(range(1, n)):
        j = key[i] & (i - 1)
        data[i], data[j] = data[j], data[i]
    
def generate_key(size=256):
    key = bytearray(range(size))    
    _key = bytearray(os.urandom(size))
    shuffle(key, _key)    
    return key
    
def test_convert():
    
    key1, key2 = generate_key(), generate_key()

    assert len(set(key2)) == 256
    assert len(set(key1)) == len(set(key2))
    print key1
    print
    print
    print key2
    print
    print sorted([byte for byte in key1])
    message = "Test message!"
    key1, key2 = bytes(key1), bytes(key2)
    converted = convert(message, key1, key2)
    print
    print
    print converted
    print
    print
    _message = convert(converted, key2, key1)
    assert _message == message, _message
    
if __name__ == "__main__":
    test_convert()