def factor(number):#long long number):
   # cdef long long x
   # cdef long long y
   # cdef long long r
   # cdef long long _r
    if number == 0:
        return [(0, 0, 0)]
    elif number == 1:
        return [(1, 1, 0)]
    #x, y, r = 1, number, 0        
    y, r = divmod(number, 2)
    x = 2
    factors = []
    if not r:
        factors.append((x, y))
        
    while y > 1:
     #   print "\nFactoring: ", x, y, r
        y -= 1
        r += x        
        while r > y:
            x += 1
            r -= y
      #  print "After adjustment: ", x, y, r  
        if r == y:
            x += 1
            r = 0
            
        if y == 1:
            x = x + r
            r = 0
        if not r:
            factors.append((x, y))
       # factors.append((x, y, r))
    
    return factors
    
if __name__ == "__main__":
    #for x in xrange(21):
    #    print "\nFactored {} into {}".format(x, factor(x))
    print factor(123)#535745324089)
   # print "Factored {} into {}".format(y, factor(y))