def test_a():
    di = {1 : 2}
    test_b()
    return di[1]
    
def test_b():
    di = {}
    return di[1]
    
test_a()    