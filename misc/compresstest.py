def convert(old_value, old_base, new_base):
    """convert a value from one base another. base should be a list of length
    base containing the unique characters to be used to represent each value in
    the system. value should be a string representation of the value. new_base
    is the desired base you want the value in."""

    old_base_size = len(old_base)
    decimal_value = 0
    new_base_size = len(new_base)
    new_value = []

    for power, value_representation in enumerate(reversed(old_value)):
        # this is the decimal value of the _value character from the old system
        #print "looking for %s in %s" % (value_representation, old_base)
        _value = old_base.index(value_representation)
        #print "decimal value is: ", _value
        # the decimal value of the value at this place value in the old system
        result = _value*(old_base_size**power)
        # add the piece to the rest of the number
        #print "cumulative before: ", decimal_value
        decimal_value += result
        #print "cumulative after: ", decimal_value

    while decimal_value >= 1:
        decimal_value, digit = divmod(decimal_value, new_base_size)
        digit = new_base[digit]
        new_value.append(digit)

    new_value = ''.join(str(item) for item in reversed(new_value))

    return new_value
  
def interpret(bit_string):
    new = convert(bit_string, base_256, base_2)
    bits = len(new)
    print bits, divmod(bits, 8)
    return new

    
if __name__ == "__main__":
    base_256 = ''.join(str(x) for x in xrange(256))
    base_2 = ''.join(str(x) for x in xrange(2))
    base_1 = '0'
    test_bits = "00000001"
    b2to1 = convert(test_bits, base_2, base_1)
    print b2to1, len(b2to1)
  #  for x in xrange(4):
   #     test_bits = interpret(test_bits)
        
    #print "{} bits went in, {} bits came out".format(8, len(test_bits))