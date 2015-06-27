import math

PHI = (1 + 5 ** .5) / 2
def invert_fib(f):
    if f < 2:
        return f
    return int(round(math.log(f * 5 ** .5) / math.log(PHI)))
        
def phi(x):
    'Cumulative distribution function for the standard normal distribution'
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
def get_divisor(number):
    amount, remainder = divmod(number, 1.61)
    return int(amount)

def fibonnacci(x=1, y=1):
    while True:
        z = x + y
        yield x, y, z
        x, y = y, z
  
def test():  
    generator = fibonnacci(4, 7)    
    for iteration in xrange(100):
        x, y ,z = next(generator)
        print "Calculated z: ", z
        print "Inverted z  : ", invert_fib(z)
            
if __name__ == "__main__":
    test()