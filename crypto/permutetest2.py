from utilities import binary_form

def sixteen_bit_addition(left_byte, right_byte, amount):
    right_byte += amount
    right_bits = binary_form(right_byte)    
    overflow, right_bits = right_bits[:-8], right_bits[-8:]
    left_byte = (int(overflow or '0', 2) + left_byte) % 256    
    return left_byte, int(right_bits, 2)
    
def permute(data):    
    for index in reversed(range(1, len(data))):
        data[index - 1], data[index] = sixteen_bit_addition(data[index - 1], data[index], index + index + 1)        
    return data
        
def test_permute():
    from utilities import find_cycle_length
    data = bytearray("\x00" * 2)
    cycle = find_cycle_length(permute, data)
    print len(cycle)

if __name__ == "__main__":
    test_permute()
    