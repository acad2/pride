STR_XOR = {('0', '0') : '0', ('1', '0') : '1', ('0', '1') : '1',
           ('1', '1') : '0'}

class Sponge_Function(object):
    
    def _get_state_byte_size(self):
        return self.state_bit_size / 8
    def _set_state_byte_size(self, value):
        if value % 8:
            raise ValueError("State size must be divisible by 8 ({} supplied)".format(value))
        self.state_bit_size = value * 8
    state_byte_size = property(_get_state_byte_size, _set_state_byte_size)
    
    def __init__(self, state_bit_size):
        self.state_bit_size = state_bit_size
        
    def permutation_function(self, state):
        """ Permutes the state """
        
    def padding_function(self, input_string):
        """ Appends enough bits to the input string so that the
            length of the padded input is a multiple of the bitrate. """
            string_length = len(input_string)
            size = self.size
            if string_length < size:
                bits_remaining = size - string_length
            else:
                bits_remaining = size - (string_length % size)
            return input_string + ('1' * bits_remaining)
            
    def operate(self, input_string):
        input_string = self.padding_function(input_string)
        bitrate_size = bytearray(self.state_byte_size)     
        size = self.size
        str_xor = STR_XOR
        while input_string:
            for index, bit in enumerate(input_string[:size]):
                state[index] = str_xor[(bit, state[index])]
            state = self.permutation_function(state)