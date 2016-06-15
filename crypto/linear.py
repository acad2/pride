from utilities import hamming_weight

def build_linear_approximation_table(sbox):
    approximations = {}
    for byte in range(256):        
        for mask1 in range(1, 256):
            for mask2 in range(256):            
                input = byte
                input_parity = hamming_weight(input & mask1) % 2
                output_parity = hamming_weight(sbox[input] & mask2) % 2
                                
                if input_parity == output_parity:
                    try:
                        approximations[(mask1, mask2)] += 1
                    except KeyError:
                        approximations[(mask1, mask2)] = 1
                    
    return approximations
    
def find_best_linear_approximation(sbox):
    table = build_linear_approximation_table(sbox)
    max_value = max_key = 0
    for key, value in table.iteritems():
        if value > max_value:
            max_value = value
            max_key = key
    return (max_key, max_value)
    
def calculate_linearity(sbox, bits=8, max_key_max_value=None):
    if not max_key_max_value:
        max_key_max_value = find_best_linear_approximation(sbox)
    return abs(max_key_max_value[1] - (2 ** 8) / 2)
    
def test_build_linear_approximation_table():
    from blockcipher import S_BOX as sbox
    approximations = build_linear_approximation_table(sbox)
    import pprint
    pprint.pprint(approximations)
    
def test_find_best_linear_approximation():
    from scratch import aes_s_box as sbox
    best_approximation = find_best_linear_approximation(sbox)
    print "Best approximation: ", best_approximation
    
if __name__ == "__main__":
    #test_build_linear_approximation_table()
    test_find_best_linear_approximation()
    