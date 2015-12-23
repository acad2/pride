def test(arg, arg1, arg2):
    _test = lambda: arg + arg1 + arg2
    print _test()
    arg += 10
    arg1 *= 10
    print _test()
    
test(10, 11, 12)    