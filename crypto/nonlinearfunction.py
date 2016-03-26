from utilities import rotate as _rotate
from utilities import cast

def rotate(word, amount):
    bits = cast(word, "binary")
    size = len(bits)
    bits = _rotate(bits, amount)
    return cast(bits, "integer")

def nonlinear_function(byte):
    byte ^= rotate(byte, 4)
    
    
    
def nonlinear_function2(data):
    for target_index, target_byte in enumerate(data):
        for source_index, source_byte in enumerate(data):
            if source_index == target_index:
                continue
            data[target_index] ^= nonlinear_function(source_byte)
        
def test_nonlinear_function():
    left, right = 0, 1
    outputs = [(left, right)]    
    while True:
        word = left, right = nonlinear_function(left, right, 2, 7)
        if word in outputs:
            break
        else:
            outputs.append(word)    
            left ^= 13
            right ^= 123
    print len(set(outputs)), outputs
    
if __name__ == "__main__":
    test_nonlinear_function()