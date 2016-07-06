from blockcipher2 import prp as old_prp
from streamcipher2 import prp as new_prp

def test_for_collisions():
    data1 = bytearray(16)
    data2 = bytearray(16)
    data1[0] = 1
    data2[1] = 1
    
    old_prp(data1, 1)
    old_prp(data2, 1)
    
    data3 = bytearray(16)
    data4 = bytearray(16)
    data3[0] = 1
    data4[1] = 1
    
    new_prp(data3, 1, key_slice=None)
    new_prp(data4, 1, key_slice=None)
    
    print "Old prp: "
    print "data1:\n", data1
    print
    print "data2:\n", data2
    
    print "With new prp: "
    print "data3:\n", data3
    print    
    print "data4:\n", data4
    
if __name__ == "__main__":
    test_for_collisions()   
    
    