def perm_given_index(alist, apermindex):
    alist = alist[:]
    length = len(alist)
    for i in range(length-1):
        apermindex, j = divmod(apermindex, length-i)
        alist[i], alist[i+j] = alist[i+j], alist[i]
    return alist
    
if __name__ == "__main__":
    from decorators import Timed
    
    print Timed(perm_given_index, 1000)([str(x) for x in xrange(10)], 1)
  #  print Timed(perm_given_index, 1000)(bytearray("0123456789"), 1)