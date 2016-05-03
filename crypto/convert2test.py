import os
from converttest import generate_key

ASCII = ''.join(chr(x) for x in xrange(256))

def convert(old_value, old_base, new_base):
    old_base_size = len(old_base)    
    old_base_mapping = dict((symbol, index) for index, symbol in enumerate(old_base))
            
    for leading_zero_count, symbol in enumerate(old_value):
        if old_base_mapping[symbol]:
            break
    #zero_padding = new_base[0] * leading_zero_count
    
    decimal_value = sum((old_base_mapping[value_representation] * (old_base_size ** power) for
                         power, value_representation in enumerate(reversed(old_value))))
    
    # this is the above in a potentially more readable format:
    # decimal_value = 0    
    # for power, value_representation in enumerate(reversed(old_value)):
    #     decimal_value += old_base_mapping[value_representation]*(old_base_size**power)
    new_value = ''                        
    if decimal_value:
        new_base_size = len(new_base)           
        while decimal_value > 0: # divmod = divide and modulo in one action
            decimal_value, digit = divmod(decimal_value, new_base_size)
            new_value += new_base[digit]
    return ''.join(reversed(new_value)).rjust(max(leading_zero_count, len(old_value)), new_base[0])
    
def arbitrary_base_addition(value1, value2, base):
    assert len(value1) == len(value2)
    size = len(value1) - 1
    base_size = len(base)     
    for offset in xrange(size + 1):                    
        current_index = size - offset              
        other_value = base.index(value2[current_index])
        while other_value:               
            first_value = base.index(value1[current_index])
            new_value = first_value + other_value            
            other_value, right_value = divmod(new_value, base_size)
            value1[current_index] = base[right_value]
            
            # increment the byte to the left with any overflow
            current_index -= 1            
                
def arbitrary_base_subtraction(value1, value2, base):
    assert len(value1) == len(value2), (len(value1), len(value2))
    size = len(value1) - 1
    base_size = len(base)
    for offset in xrange(size + 1):
        current_index = size - offset
        first_value = base.index(value1[current_index])
        second_value = base.index(value2[current_index])
        
        new_value = first_value - second_value
        if second_value > first_value:
            carry_index = current_index - 1
            while carry_index:
                if value1[carry_index] != base[0]:                    
                    value1[carry_index] = base[base.index(value1[carry_index]) - 1]
                    break
                else:
                    carry_index -= 1            
            value1[current_index] = base[base_size + new_value]
        else:            
            value1[current_index] = base[new_value]
        
def test_key_exchange_idea():
    public_key1 = bytes(generate_key(256))    
    
    private_key1 = bytes(generate_key(256))
    private_key2 = bytes(generate_key(256))
    
    message = os.urandom(32)#("\x00" * 31) + "\x01"    
    message = convert(message, ASCII, private_key1)
    message = convert(message, private_key1, public_key1)
    
    message2 = os.urandom(32)#("\x00" * 31) + "\x02"#os.urandom(32)    
    message2 = convert(message2, ASCII, private_key2)
    message2 = convert(message2, private_key2, public_key1)
    
    message3 = list(message)
    arbitrary_base_addition(message3, message2, public_key1)
        
    print "Message: "
    print
    print message
    print
    print "Message2: "
    print
    print message2
    print
    print "Message3: "
    print 
    print ''.join(message3)
    print
    print "In ascii: ", 
    print convert(convert(message3, public_key1, private_key1), private_key1, ASCII)
    
    arbitrary_base_subtraction(message3, message, public_key1)
    print
    print "Message3 - Message: "
    print
    print [ord(char) for char in message3]
    print
    print [ord(char) for char in message2]
    assert message3 == list(message2)
    
def test_arbitrary_base_addition():
    value1 = list("0123456789")
    value2 = list("9876543210")
    base = bytes(generate_key(seed=range(10)))# list("3017845962")    
    
    value1_in_base = convert(value1, "0123456789", base)
    value2_in_base = convert(value2, "0123456789", base)
        
    value1_in_public_base = list(convert(value1_in_base, base, ASCII))
    value2_in_public_base = list(convert(value2_in_base, base, ASCII))
    print "Adding encoded numbers: "
    print ''.join(value1_in_public_base)
    print ''.join(value2_in_public_base) + " +"
    print "_" * len(value1)
    arbitrary_base_addition(value1_in_public_base, value2_in_public_base, ASCII) 
    print ''.join(value1_in_public_base), '        ({})'.format(value1_in_public_base)
    print convert(convert(value1_in_public_base, ASCII, base), base, "0123456789")        
                     
def test_arbitrary_base_subtraction():
    value1 = list("9876543210")
    value2 = list("0123456789")
    
    base = bytes(generate_key(seed=range(10)))# list("3017845962")    
    
    value1_in_base = convert(value1, "0123456789", base)
    value2_in_base = convert(value2, "0123456789", base)
        
    value1_in_public_base = list(convert(value1_in_base, base, ASCII))
    value2_in_public_base = list(convert(value2_in_base, base, ASCII))
    print "Subtracting encoded numbers: "
    print ''.join(value1_in_public_base)
    print ''.join(value2_in_public_base) + " -"
    print "_" * len(value1)
    arbitrary_base_subtraction(value1_in_public_base, value2_in_public_base, ASCII) 
    print ''.join(value1_in_public_base), '        ({})'.format(value1_in_public_base)
    print convert(convert(value1_in_public_base, ASCII, base), base, "0123456789")
    print 9876543210 - 123456789
    
if __name__ == "__main__":
    #test_arbitrary_base_addition()
    #test_arbitrary_base_subtraction()
    test_key_exchange_idea()    
    