import struct
from utilities import cast, slide

FORMAT_SYMBOL = {8 : 'B', 16 : 'H', 32 : 'L', 64 : 'Q'}

def divide_by_two(number, number_bit_size=64):
    ones = []    
    output_size = (2 ** number_bit_size) - 1
    while number > output_size:        
        if number % 2:
            ones.append('1')
            number -= 1
        else:
            ones.append('0')
        number /= 2       
    padding = 8 - len(ones) % 8    
    ones.extend('0' * padding)    

#    output = (run_length_encoding(struct.pack(FORMAT_SYMBOL[number_bit_size], number)), 
#              struct.pack('B', padding), 
#              run_length_encoding(cast(''.join(ones), "bytes")))
    output = (struct.pack(FORMAT_SYMBOL[number_bit_size], number),
              struct.pack('B', padding), 
              cast(''.join(ones), "bytes"))
    return output
    
def restore_from_divide_by_two(number_ones_counter_tuple, number_bit_size=64):
    number, padding, ones = number_ones_counter_tuple
    number = struct.unpack(FORMAT_SYMBOL[number_bit_size], number)[0]
    #number = struct.unpack(FORMAT_SYMBOL[number_bit_size], run_length_decoding(number))[0]    
    padding = struct.unpack('B', padding)[0]
    unpacked_flags = cast(ones, "binary")[:-padding]
    #unpacked_flags = cast(run_length_decoding(ones), "binary")[:-padding]    
    for add_one_flag in reversed(unpacked_flags):
        number *= 2
        if add_one_flag == '1':
            number += 1

    return number
    
def run_length_encoding(data):
    output = []
    while data:        
        current_byte = data[0]
        count = 0                  
        while data and data[0] == current_byte and count < 255:
            count += 1
            data = data[1:]                     
        output.append(struct.pack('B', count) + current_byte)
    return ''.join(output)
    
def run_length_decoding(encoded_data):
    output = []
    for count, symbol in slide(encoded_data, 2):
        count = struct.unpack('B', count)[0]
        output.append(symbol * count)
    return ''.join(output)
    
def test_run_length_encoding():
    data = ("1" * 8) + '0' + ('1' * 16)
    encoded = run_length_encoding(data)
    decoded = run_length_decoding(encoded)
    print len(data), len(encoded)
    assert decoded == data
    
def test_divide_by_two():
    number = 2 ** 4095 - 13
    #data = "This is a test message, maybe for a longer one it will work better?"
   # number = cast(cast(data, "binary"), "integer")
    divided = divide_by_two(number)
    restored = restore_from_divide_by_two(divided)
    assert restored == number
    print 1 + ((len(divided[2]) + len(divided[0])) * 8)#, len(data) * 8
    print divided
    
if __name__ == "__main__":
    test_run_length_encoding()
    test_divide_by_two()
    