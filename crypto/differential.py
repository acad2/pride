import pprint

from utilities import rotate, cast, rotate_left 

def rotational_difference(input_one, input_two):
    if input_one == input_two:
        return 0
        
    input_one_bits = cast(input_one, "binary")
    input_two_bits = cast(input_two, "binary")
    if input_one_bits.count('1') == input_two_bits.count('1'):
        for rotation_amount in range(1, 8):
            if rotate(input_one_bits, rotation_amount) == input_two_bits:
                return rotation_amount 
            
def _difference(input_one, input_difference, sbox, distribution_table, difference_function1, difference_function2=None):
    input_two = difference_function1(input_one, input_difference)            
    output_differential = (difference_function2 or difference_function1)(sbox[input_one], sbox[input_two])
    try:
        distribution_table[input_difference][output_differential] += 1
    except KeyError:
        if input_difference in distribution_table:
            try:
                distribution_table[input_difference][output_differential] += 1
            except KeyError:
                distribution_table[input_difference][output_differential] = 1
        else:
            distribution_table[input_difference] = {output_differential : 1}
    
def _xor_difference(input_one, input_difference, sbox, distribution_table):            
    _difference(input_one, input_difference, sbox, distribution_table, operator.xor)

def _rotational_difference(input_one, input_difference, sbox, distribution_table):        
    _difference(input_one, input_difference, sbox, distribution_table, rotate_left, rotational_difference)
                    
def build_difference_distribution_table(sbox):
    xor_difference_distribution_table = {}
    rotational_ddt = {}
    size = len(sbox)
    
    for input_one in range(size):
        for input_difference in range(size):                                   
            _xor_difference(input_one, input_difference, sbox, xor_difference_distribution_table)                     
            if input_difference < 8:
                _rotational_difference(input_one, input_difference, sbox, rotational_ddt)                           
                
    return xor_difference_distribution_table, rotational_ddt
    
def find_best_output_differential(xor_ddt, input_difference):    
    best_find = 0
    input_correlations = xor_ddt[input_difference]
    for output_differential in input_correlations.keys():
        count = input_correlations[output_differential]
        if count > best_find:
            best_find = count
            best_differential = (input_difference, output_differential, count)
    return best_differential
        
def calculate_differential_chain(xor_ddt, input_difference):    
    input_difference, output_differential, probability = find_best_output_differential(xor_ddt, input_difference)
    chain = [(input_difference, output_differential, probability)]
    
    input_difference = output_differential
    while True:
        most_likely_next_differential = find_best_output_differential(xor_ddt, input_difference)
        if most_likely_next_differential not in chain:            
            chain.append(most_likely_next_differential)
            input_difference = most_likely_next_differential[1]
        else:    
            chain.append(most_likely_next_differential)
            break
    return chain
    
def differential_attack(encryption_function, cipher_s_box, blocksize, 
                        first_differential=1, trail_length_range=(1, 1)):    
    from os import urandom
    xor_ddt, rotational_ddt = build_difference_distribution_table(cipher_s_box)
    input_difference, output_differential, probablility = find_best_output_differential(xor_ddt, first_differential)  
    minimum_length, maximum_length = trail_length_range
    differential_chain = calculate_differential_chain(xor_ddt, input_difference)[:maximum_length]
    _outputs = dict((item[1], index) for index, item in enumerate(differential_chain))          
    
    while True:
        data = bytearray(urandom(blocksize))
        data2 = bytearray(byte ^ input_difference for byte in data)    
        encryption_function(data)
        encryption_function(data2)
        
        s_box_applications = {}
        for index, byte in enumerate(data):
            output_differential = byte ^ data2[index]
            if output_differential in _outputs:
                trail_length = _outputs[output_differential]
                if trail_length >= minimum_length:
                    s_box_applications[index] = trail_length
                    
        if s_box_applications:
            print '*' * 80 #s_box_applications
            if 0 in s_box_applications:
                print differential_chain[:s_box_applications[0]]
            if 1 in s_box_applications:
                print differential_chain[:s_box_applications[1]]
            
def find_best_differential(sbox):    
    """ Returns the single best xor differential for the supplied sbox.
        Output consists of the input difference, output difference, and
        probability that the difference will hold. """
    xor_ddt, rotational_ddt = build_difference_distribution_table(sbox)
    best_differential = (None, None, 0)
    for difference in range(1, 256):
        info = find_best_output_differential(xor_ddt, difference)        
        if info[-1] > best_differential[-1]:
            best_differential = info
    return best_differential 
    
def find_impossible_differentials(xor_ddt):
    impossible_differentials = {}
    for difference in range(1, 256):
        differentials = xor_ddt[difference]
        impossible_differentials[difference] = [differential for differential, probability in differentials.items() if not probability]
    return impossible_differentials
    
def test_find_impossible_differentials():
    #from blockcipher import S_BOX as s_box
    from scratch import aes_s_box as s_box
    xor_ddt, table2 = build_difference_distribution_table(s_box)
    impossible_differentials = find_impossible_differentials(xor_ddt)
    pprint.pprint(impossible_differentials)
    
def test_build_difference_distribution_table():
    import pprint
    #from blockcipher import S_BOX  
    from scratch import aes_s_box as S_BOX       
    table1, table2 = build_difference_distribution_table(S_BOX)
   # print max(table1[1].values())
    print find_best_output_differential(table1, 128)
    #print
    pprint.pprint(table2)

    #pprint.pprint(table1)
    
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
    test_build_difference_distribution_table()
    #test_calculate_differential_chain()
    #test_differential_attack()
    #test_find_impossible_differentials()
    