from math import ceil

def factor(number):
    factors = []
    exponent = 0
    while not number % 2:
        exponent += 1
        number /= 2
        print "Divided by 2 to: ", number
    if exponent:
        factors.append((2, exponent))
        
    quotients, remainders = [1], [0]
    divisor_offset = 1
    
    search_mode = "scalar"
    while number > 1:                
    #    print "Created divisor: ", number, divisor_offset, divisor_scalar
        divisor = number - divisor_offset
        quotient, remainder = divmod(number, divisor)
        print "{} / {} = {} {}".format(number, divisor, quotient, remainder)#, divisor_offset, divisor_scalar
        if not remainder:
            exponent = 0
            while not number % divisor:
                exponent += 1
                number /= divisor
                print "Divided by {} to".format(divisor), number
            factors.append((divisor, exponent))
            remainders, quotients = [remainder], [quotient]
       #     print "SET SEARCH MODE TO SCALAR!" * 5
            search_mode = "scalar"
            continue
            
        remainders.append(remainder)
        quotients.append(quotient)
        if remainders[-1] < remainders[-2] or quotients[-1] > quotients[-2]:
            if quotients[-1] > quotients[-2]:
                print "Looped around a quotient; lowering scalar", quotients[-1] , quotients[-2]
            else:
                print "Looped around remainders; lowering scalar", remainders[-1], remainders[-2]
            remainders.pop(-2)
            quotients.pop(-2)
            
            _quotient, _remainder = divmod(remainder, quotient)
                             
            _divisor = number - divisor_offset - _quotient
            if not number % _divisor:
                divisor_offset -= _quotient
            search_mode = "offset"            
        else:
            if search_mode == "scalar":
                print "Doubling divisor"
                divisor_offset *= 2
            else:
                print "Incrementing by 1"
                divisor_offset += 1
    return factors
    
if __name__ == "__main__":
    print factor(105)