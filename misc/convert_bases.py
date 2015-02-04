import string, sys, os
from random import randint

BASE_2 = ["0", "1"]
BASE_8 = string.octdigits
BASE_10 = string.digits
BASE_16 = string.hexdigits
BASE_256 = [chr(x) for x in xrange(256)]
ALPHABET = string.ascii_letters+" " # WARNING! combining lowercase+uppercase will break things
LOWERCASE_ALPHABET = string.ascii_lowercase+" "
UPPERCASE_ALPHABET = string.ascii_uppercase+" "
SYMBOLS = "!@#$%^&*()_+=-{}[]|\\:;\'\"<,>.?/`~ "
RALPHABET = ' ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba'
RSYMBOLS = " ~`/?.>,<\"\';:\\|][}[-=+_)(*&^%$#@!"
RBASE_10 = "9876543210"
RLOWERCASE_ALPHABET = "zyxwvutsrqponmlkjihgfedcba"
KEYBOARD = ALPHABET+SYMBOLS+BASE_10


class Number_Base(object):

    def __init__(self, base=('0', '1')):
        super(Number_Base, self).__init__()
        self.base = base
        self.base_size = len(base)

    def convert_from(self, old_value, old_base):
        """convert a value from one base another. base should be a list of length
        base containing the unique characters to be used to represent each value in
        the system. value should be a string representation of the value. new_base
        is the desired base you want the value in."""
        old_base_size = len(old_base)
        decimal_value = 0
        new_base = self.base
        new_base_size = self.base_size
        new_base_chunk_size = len(new_base[-1])
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

        while decimal_value > 0: # divmod = divide and modulo in one action
            old_value = decimal_value
            decimal_value, digit = divmod(decimal_value, new_base_size)
            digit = new_base[digit]
            new_value.append(digit)

        new_value = [str(item) for item in reversed(new_value)]

        return ''.join(new_value)

def convert(old_value, old_base, new_base):
    """convert a value from one base another. base should be a list of length
    base containing the unique characters to be used to represent each value in
    the system. value should be a string representation of the value. new_base
    is the desired base you want the value in."""

    old_base_size = len(old_base)
    decimal_value = 0
    new_base_size = len(new_base)
    new_base_chunk_size = len(new_base[-1])
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

    while decimal_value >0: # divmod = divide and modulo in one action
        old_value = decimal_value
        decimal_value, digit = divmod(decimal_value, new_base_size)
        digit = new_base[digit]
        new_value.append(digit)

    new_value = ''.join(str(item) for item in reversed(new_value))

    return new_value


def interpret_as(value, new_base):
    new_base_size = len(new_base)
    new_value = 0
    for power, number in enumerate(reversed(str(value))):
        new_value += int(number) * (new_base_size ** power)
    return new_value

def find_factors(value, old_base=BASE_16):
    series = []
    value_representation = str(value)
    for x in xrange(1, 256):
        new_base = ''.join(chr(y) for y in xrange(0, x+1))
        #print "converting to base {0}".format(new_base)
        new_number = convert(value_representation, old_base, new_base)
        binary_characters = zero, one = new_base[0], new_base[1]
        print "checking if {0} and {1} are in {2} (base {3})".format(zero, one, new_number, len(new_base))
        for character in new_number:
            if character not in binary_characters:
                break
            series.append(new_number)
    return '\n'.join(series)


if __name__ == "__main__":
    bits = "1111 1111".replace(' ', '') * 4
    bit_length = len(bits)
    decimal = interpret_as(bits, BASE_256)
    new_bits = format(decimal, 'b')
    new_bit_length = len(new_bits)
    difference = new_bit_length - bit_length

    format_args = (bit_length, bits, decimal, new_bits, new_bit_length, difference)
    #print "From the {0} bits {1}, the number {2} was generated, which itself in binary is {3}  and uses {4} bits. Size difference: {5}".format(*format_args)

    series = find_factors(decimal, BASE_10)
    print "found series", series
#    base_ten = Number_Base(BASE_10)
 #   original = ''.join(str(randint(0, 1)) for x in xrange(16))
  #  new = base_ten.convert_from(original, BASE_2)
   # print new

    """new = convert(original, BASE_2, BASE_256)
    count = 1
    while new[-1] != BASE_256[0]:
        count +=1
        print "({0} tries) looking for a factor...".format(count)
        original = ''.join(str(randint(0, 1)) for x in xrange(2048))
        new = convert(original, BASE_2, BASE_256)

    print "{0} is a factor of 256!".format(new)
    restored = convert(new, BASE_256, BASE_10)
    print restored, int(restored) % 256"""
