def round_subroutine(data_bytearray, key):
    modifier = ((21 + sum(data_bytearray) + sum(key)) * 2 * len(data_bytearray)) % 256
    for index, byte in enumerate(data_bytearray):
        data_bytearray[index] ^= (pow(251, modifier ^ key[index] ^
                                           sum(data_bytearray[:index]) + 
                                           sum(data_bytearray[index + 1:]),
                                      257) % 256)

# what would the graph of an ideal 8-bit S-Box look like?
# is there a way to visualize, graphically, what the ideal "non linearity" might look like?
# i.e., for each byte from 0 ... 255, substitute the byte and graph the input/output as x/y points       
# what would a good S-Box look like? A bad one?

                          
# the pow(251, x, 257) % 256 operation is equivalent to an S-Box and is invertible                                      
# each byte is equivalent to: data[index] XOR modifier XOR key[index] XOR sum(data[:index]) + sum(data[index + 1:]       
# the last byte is easiest, because the second term in sum(data[:index]) + sum(data[index + 1:]) is 0
# the last byte is equivalent to: data[index] XOR modifier XOR key[index] XOR sum(data[:index])
# XOR of the last byte with the second to last byte gives: data[-2] XOR data[-1] XOR key[-2] XOR key[-1] XOR sum(data[:-2]) + sum(data[-1:]) XOR sum(data[:-1])

# two separate inputs with the same key:
# modifier1 XOR key[index] XOR sum(data1[:index]) + sum(data2[index + 1:])
# modifier2 XOR key[index] XOR sum(data2[:index]) + sum(data2[index + 1:])
# A XOR K XOR B XOR C XOR K XOR D
# A XOR B XOR C XOR D
# K XOR K

             
def test_round_subroutine():        
    data = bytearray("\x00")
    key = bytearray("\x00")
    outputs = []    
    for cycle_length in xrange(256):
        round_subroutine(data, key)
        output = bytes(data)
        if output in outputs:
            break
        outputs.append(output)

    print len(outputs), cycle_length, outputs
    
if __name__ == "__main__":
    test_round_subroutine()