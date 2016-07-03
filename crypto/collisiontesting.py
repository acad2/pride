#1 0 0000...
#0 1 0000...
#
#B A xxxx...
#D C xxxx...
#
#if a ^ b == d ^ c:
#    F E yyyy...
#    H G yyyy...
#    
#    if f ^ e == 

import os

def find_equivalent_xor_probability():    
    outputs = 0
    for counter in range(65536):
        a, b, c, d = bytearray(os.urandom(4))
        if a ^ b == c ^ d:
            outputs += 1
    print outputs, counter, (float(outputs) / counter)
    
def test_prp():
    from streamcipher2 import prp
    outputs = 0
    for input_one in range(256):
        for input_two in range(256):
            input_one, input_two = bytearray(os.urandom(2))
            data = bytearray(16)
            data[0] = input_one
            data[1] = input_two
            prp(data, input_one ^ input_two)
            
            data2 = bytearray(16)
            data2[0] = input_two
            data2[1] = input_one
            prp(data2, input_one ^ input_two)
            
            if data[0] ^ data[1] == data2[0] ^ data2[1]:
                outputs += 1
    print outputs
    
def test_prp_sponge():
    import sponge
    import streamcipher2
    from utilities import xor_sum
    
    prp_hash = sponge.sponge_factory(lambda data: streamcipher2.prp(data, xor_sum(data)), capacity=8, rate=8)
    print prp_hash("Testing")
    import metrics
    metrics.test_hash_function(prp_hash)
        
if __name__ == "__main__":
    #find_equivalent_xor_probability()
    test_prp()
    test_prp_sponge()
    