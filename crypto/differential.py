from utilities import rotate, cast

def rotational_difference(input_one, input_two):
    if input_one == input_two:
        return 0
        
    input_one_bits = cast(input_one, "binary")
    input_two_bits = cast(input_two, "binary")
    if input_one_bits.count('1') == input_two_bits.count('1'):
        for rotation_amount in range(1, 8):
            if rotate(input_one_bits, rotation_amount) == input_two_bits:
                return rotation_amount 
                
def build_difference_distribution_table(sbox):
    xor_difference_distribution_table = {}
    rotational_ddt = {}
    
    for input_one in range(256):
        for input_two in range(input_one + 1, 256):
            input_differential = input_one ^ input_two
            output_differential = sbox[input_one] ^ sbox[input_two]
            try:
                xor_difference_distribution_table[input_differential][output_differential] += 1
            except KeyError:
                if input_differential in xor_difference_distribution_table:
                    xor_difference_distribution_table[input_differential][output_differential] = 1
                else:
                     xor_difference_distribution_table[input_differential] = {output_differential : 1}
                     
            input_differential = rotational_difference(input_one, input_two)
            output_differential = rotational_difference(sbox[input_one], sbox[input_two])            
            try:
                rotational_ddt[input_differential][output_differential] += 1
            except KeyError:
                if input_differential in rotational_ddt:
                    rotational_ddt[input_differential][output_differential] = 1
                else:
                    rotational_ddt[input_differential] = {output_differential : 1}                  
                
    return xor_difference_distribution_table, rotational_ddt
    
def find_best_output_differential(xor_ddt, input_differential):    
    best_find = 0
    input_correlations = xor_ddt[input_differential]
    for output_differential in input_correlations.keys():
        count = input_correlations[output_differential]
        if count > best_find:
            best_find = count
            best_differential = (input_differential, output_differential, count)
    return best_differential
        
def calculate_differential_chain(xor_ddt, input_differential):    
    input_differential, output_differential, probability = find_best_output_differential(xor_ddt, input_differential)
    chain = [(input_differential, output_differential, probability)]
    
    input_differential = output_differential
    while True:
        most_likely_next_differential = find_best_output_differential(xor_ddt, input_differential)
        if most_likely_next_differential not in chain:            
            chain.append(most_likely_next_differential)
            input_differential = most_likely_next_differential[1]
        else:    
            chain.append(most_likely_next_differential)
            break
    return chain
    
def differential_attack(encryption_function, cipher_s_box, blocksize, 
                        first_differential=1, trail_length_range=(1, 1)):    
    from os import urandom
    xor_ddt, rotational_ddt = build_difference_distribution_table(cipher_s_box)
    input_differential, output_differential, probablility = find_best_output_differential(xor_ddt, first_differential)  
    differential_chain = calculate_differential_chain(xor_ddt, input_differential)
    _outputs = dict((item[1], index) for index, item in enumerate(differential_chain))        
    minimum_length, maximum_length = trail_length_range
    
    while True:
        data = bytearray(urandom(blocksize))
        data2 = bytearray(byte ^ input_differential for byte in data)    
        encryption_function(data)
        encryption_function(data2)
        
        s_box_applications = {}
        for index, byte in enumerate(data):
            output_differential = byte ^ data2[index]
            if output_differential in _outputs:
                trail_length = _outputs[output_differential]
                if trail_length >= minimum_length and trail_length <= maximum_length:
                    s_box_applications[index] = trail_length
                    
        if s_box_applications:
            print s_box_applications
            
    
def test_build_difference_distribution_table():
    import pprint
    from blockcipher import S_BOX  
    #from scratch import aes_s_box as S_BOX       
    table1, table2 = build_difference_distribution_table(S_BOX)
   # print max(table1[1].values())
    print find_best_output_differential(table1, 128)
    #print
    pprint.pprint(table2)

def test_calculate_differential_chain():
    from blockcipher import S_BOX    
    chain = calculate_differential_chain(build_difference_distribution_table(S_BOX)[0], 128)
    print len(chain), chain
    
def test_differential_attack():
    from blockcipher import S_BOX, encrypt_block
    key = bytearray("\x00\x00")
    def encryption_function(data):
        encrypt_block(data, key)
    differential_attack(encryption_function, S_BOX, 2, 128, (2, 4))
    
if __name__ == "__main__":
    #test_build_difference_distribution_table()
    #test_calculate_differential_chain()
    test_differential_attack()