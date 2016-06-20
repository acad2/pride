import operator

functions = []
for function_name in (function_name for function_name in dir(operator) if function_name[0] != "_"):
    function = getattr(operator, function_name)
    try:
        function(1, 2)
    except:
        pass
    else:
        functions.append(function_name)        
        
functions.remove("attrgetter")
functions.remove("itemgetter")
functions.remove("methodcaller")

#import pprint
#pprint.pformat(functions)

def build_difference_distribution_table(sbox):
    for byte in range(1, 256):
        for difference in range(1, 256):
            