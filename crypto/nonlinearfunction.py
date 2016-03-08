from utilities import rotate as _rotate, cast

def rotation(byte, amount):
    return int(_rotate(cast(byte, "binary"), amount), 2)
    
def nonlinear_function(byte): 
    for count in range(8):
        byte += 13
        byte ^= rotation(byte, byte ^ count)
    #byte ^= 9
    #byte ^= rotation(byte, -4)
    #byte ^= 4
    #byte ^= rotation(byte, -3)  
   # byte ^= 32
   # byte ^= rotation(byte, 3)
    #byte 
    return byte
    
def cycle_test_8_bit(function):
    byte = 0
    outputs = [byte]
    for count in range(256):
        byte = function(byte)
        if byte in outputs:
            break
        else:
            outputs.append(byte)
    return outputs
    
def test_nonlinear_function():   
    result = cycle_test_8_bit(nonlinear_function)
    print len(result), ''.join(chr(int(format(byte, 'b').zfill(8)[-8:], 2)) for byte in result)
    
if __name__ == "__main__":
    test_nonlinear_function()