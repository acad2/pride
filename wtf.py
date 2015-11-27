import dis

source = \
"""def test(first_argument, default_argument=True, *args, **kwargs):
    print "what the fuck?"
    x = 10
    x += 15
    internal_local = "test_string"
    return 1"""
code = compile(source, 'test', 'exec')
print dis.dis(code)    
exec code