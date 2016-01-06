import __builtin__

_max = __builtin__.max
def max(*args):
    print "Inside non standard max function"
    __builtin__.max = _max
    return min(args)
    
__builtin__.max = max    