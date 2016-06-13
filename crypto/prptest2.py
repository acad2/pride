from utilities import rotate_left

def xor_sum(data):
    output = 0
    for byte in data:
        output ^= byte
    return output
    
def interleaved_sum(data):
    output = 0
    for index, byte in enumerate(data):        
        output = byte ^ (((output ^ byte) + byte + index) & 255)
    return output
    
def prp(data, key, mask=255, rotation_amount=5, bit_width=8):    
    for index in range(len(data)):
        byte = data[index]
        key ^= byte                        
        data[index] = rotate_left((byte + key + index) & mask, rotation_amount, bit_width)
        key ^= data[index]            
    return key    
    
def test_prp():    
    for function in (xor_sum, interleaved_sum):
        data = bytearray(8)
        data[-1] = 1
        
        data2 = bytearray(8)
        data2[-2] = 1    
        
        data3 = bytearray(8)
        data3[-2] = 2
        prp(data, function(data))
        prp(data2, function(data2))
        prp(data3, function(data3))
        print "Using function: ", function
        print "Data: ", data
        print
        print "Data2: ", data2
        print
        print "Data3: ", data3
        
    
    
    
if __name__ == "__main__":
    test_prp()
    