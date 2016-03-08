from utilities import byte_rotation

def find_rotational_differentials(mapping):    
    differentials = []
    for rotation_amount in range(-7, 8):
        if not rotation_amount:
            continue
        for count in range(256):
            input_one = count
            input_two = byte_rotation(input_one, rotation_amount)
            
            output_one = mapping[input_one]
            output_two = mapping[input_two]
            if byte_rotation(output_one, rotation_amount) == output_two:
                differentials.append((input_one, input_two, rotation_amount, output_one, output_two))
    return differentials
    
def test_rotational_differentials(mapping, verbosity='v'):    
    differentials = find_rotational_differentials(mapping)
    if verbosity == 'v':
        for differential in differentials:
            print "\nFound rotational differential:\nInputs: {}, {}; Rotation: {}; Outputs: {}, {};".format(*differential)
    print "Found {} rotational differentials altogether".format(len(differentials))
    
def find_xor_differentials(mapping):
    differentials = []
    for count in range(256):
        input_one = count
        output_one = mapping[input_one]
        for input_two in range(256):
            if input_one == input_two:
                continue
                
            input_xor_difference = input_one ^ input_two              
            output_two = mapping[input_two]
            output_xor_difference = output_one ^ output_two
            if input_xor_difference == output_xor_difference:
                differentials.append((input_one, input_two, input_xor_difference, output_one, output_two))
    return differentials
    
def test_xor_differentials(mapping, verbosity='v'):
    differentials = find_xor_differentials(mapping)
    if verbosity == 'v':
        for differential in differentials:
            print "\nFound xor differential:\nInputs: {}, {}; Xor differential: {}; Outputs: {}, {};".format(*differential)
    print "Found {} xor differentials altogether".format(len(differentials))
    
if __name__ == "__main__":
    from blockcipher import S_BOX
    from scratch import aes_s_box    
    test_s_box = S_BOX
    test_rotational_differentials(test_s_box, 0)
    test_xor_differentials(test_s_box, 0)