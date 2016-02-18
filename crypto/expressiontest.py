from pride.additional_builtins import slide

DEFAULT_FUNCTION_NAME = "S-BOX"

def get_xor_expression(*args, **kwargs):
    function_name = kwargs.get("function_name", DEFAULT_FUNCTION_NAME)
    arguments = []
    for arg in args:
        if isinstance(arg, tuple) or isinstance(arg, list):       
            line = "\n      {}[".format(function_name)
            line += get_xor_expression(*arg) + ']'   
            arguments.append(line)
        else:
            arguments.append(arg)
    return " xor ".join(arguments)
    
def test():
    cipher_bytes = []
    data = ["B{}".format(count) for count in range(8)]
    _key = key = ["K{}".format(count) for count in range(8)]
    expressions = []
    for index in range(8):
        expressions.append("(C{} = {}) # end C{}\n".format(index, get_xor_expression(data.pop(0), 
                                                                                   key.pop(0),
                                                                                   cipher_bytes + data + key),
                                                         index))
        cipher_bytes.append(expressions[-1])         
    return expressions
    
if __name__ == "__main__":  
    #print get_xor_expression("B0", "K0", ("B1", "K1", "B2", "K2", "B3", "K3"))
    print test()[7]