import differential
import linear

STANDARD_DIFFERENTIAL = ((differential.xor, differential.xor), )

def cryptanalyze_sbox(sbox, differential_types=STANDARD_DIFFERENTIAL):
    differentials = differential.find_best_differential(sbox, differential_types)
    linearity = linear.calculate_linearity(sbox)
    return differentials, linearity
    
def summarize_sbox(sbox, differential_types=STANDARD_DIFFERENTIAL):
    differentials, linearity = cryptanalyze_sbox(sbox, differential_types)
    print "The most probable differential characteristic(s):" 
    index = 0    
    for difference_input, difference_output, probability in differentials:
        input_difference_type, output_difference_type = differential_types[index]
        print "{} -> {} with probability {}/256 ({} -> {})".format(difference_input, difference_output, probability, 
                                                                   input_difference_type, output_difference_type)
        index += 1
    print "Linearity: {} ({})".format(linearity[1], linearity[0])
    
def test_cryptanalyze_sbox():
    from aes_procedures import S_BOX       
    summarize_sbox(S_BOX)
    
if __name__ == "__main__":
    test_cryptanalyze_sbox()
    