def max_period_psuedorandom_subroutine(seed, key):    
    key = (45 + sum(seed)) * len(seed) * 2    
    for index, byte in enumerate(seed):
        seed[index] = (pow(251, ((45 + byte) * 2) ^ byte, 257) % 256) #^ (index % 256)
        
def test_max_period_psuedorandom_subroutine(seed="\x00", key=''):
    seed = bytearray(seed)
    outputs = [bytes(seed)]
    for x in xrange(256):
        max_period_psuedorandom_subroutine(seed, key)
        output = bytes(seed)
        if output in outputs:
            break
        outputs.append(output)
    print "Cycle length: ", x, len(set(outputs))
    return x

def find_max_cycle():
    max_cycle = 0
    best = 0
    for x in xrange(256):
        cycle_length = test_max_period_psuedorandom_subroutine(key=x)
        if cycle_length > max_cycle:
            max_cycle = cycle_length
            best = x
    print max_cycle, best
    
if __name__ == "__main__":
    #find_max_cycle()
    for x in xrange(256):
        test_max_period_psuedorandom_subroutine(chr(x) * 2)