from utilities import byte_rotation, rotate

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
    
def test_rotational_differentials(mapping, verbosity=0):    
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
    
def test_xor_differentials(mapping, verbosity=0):
    differentials = find_xor_differentials(mapping)
    if verbosity == 'v':
        for differential in differentials:
            print "\nFound xor differential:\nInputs: {}, {}; Xor differential: {}; Outputs: {}, {};".format(*differential)
    print "Found {} xor differentials altogether".format(len(differentials))
    import pprint    
    #pprint.pprint(mapping)
    
  
def _sanity_check(s_box):            
    assert len(set(s_box.keys())) == 256, len(set(s_box.keys()))
    assert len(set(s_box.values())) == 256, len(set(s_box.values()))
    
def find_good_sbox(s_box=None, s_boxes=None, exit_flag=0):    
    s_box = s_box or dict((count, count + 1) for count in range(256))
    s_boxes = s_boxes or []    
    xor_differentials = find_xor_differentials(s_box)
    s_boxes.append((len(xor_differentials), s_box.copy()))
    
    inputs = set()    
    for input_one, input_two, difference, output_one, output_two in xor_differentials:
        inputs.add(input_one)        
    
    if exit_flag == 256:        
        return s_boxes
    else: 
        outputs = []
        for input in inputs:
            outputs.append(s_box[input])        
        outputs = rotate(outputs, 1)              
        for index, input in enumerate(inputs):
            s_box[input] = outputs[index]         
        
        return find_good_sbox(s_box, s_boxes, exit_flag + 1)
    
if __name__ == "__main__":
    from blockcipher import S_BOX
    from scratch import aes_s_box   
    import operator   
    #test_s_box = S_BOX
    #test_rotational_differentials(test_s_box, 0)
    #test_xor_differentials(test_s_box, 0)
    from os import urandom        
    values = []    
    while len(values) < 256:
        for byte in slide(urandom(1024), 1):
            byte = ord(byte)
            if byte not in values:
                values.append(byte)
            if len(values) == 256:
                break
                
    test_sbox = dict((index, aes_s_box[index]) for index in range(256))      
    test_rotational_differentials(test_sbox)    
    sboxes = find_good_sbox(test_sbox)#dict((index, random_sbox[index]) for index in range(256)))
    from pride.datastructures import Average
    average = Average(values=[amount for amount, sbox in sboxes])
    print average.average
    test_xor_differentials(sorted(sboxes, key=operator.itemgetter(0))[0][1])
    