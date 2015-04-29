def convert(old_value, old_base, new_base):
    """ usage: convert(value, values_base, new_base) => new_value
        
        Converts old_value represented in old_base to the equivalent value represented
        in new_base. old_value and new_value are strings, and old_base and new_base are
        iterables (keys) containing string character symbols in order of magnitude, i.e. 
        base ten is represnted by the key "0123456789".
        The symbols used may be arbitrary but may produce non intuitive results if the
        symbols ordinal is greater then 256 as such a symbol cannot be represented by
        a single byte. Currently only supports ascii"""

    old_base_size = len(old_base)
    decimal_value = 0
    new_base_size = len(new_base)
    new_value = []

    for power, value_representation in enumerate(reversed(old_value)):
        _value = old_base.index(value_representation)
        result = _value*(old_base_size**power)
        decimal_value += result
            
    if decimal_value == 0:
        new_value = [new_base[0]]
    else:
        while decimal_value > 0: # divmod = divide and modulo in one action
            old_value = decimal_value
            decimal_value, digit = divmod(decimal_value, new_base_size)
            digit = new_base[digit]
            new_value.append(digit)

    new_value = ''.join(str(item) for item in reversed(new_value))
    return new_value
