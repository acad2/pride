def call_if(**conditions):
    def decorate(function):
        def new_call(*args, **kwargs):
            print args, kwargs
            self = args[0]
            for key, value in conditions.items():
                if not getattr(self, key) == value:
                    break
            else:
                return function(*args, **kwargs)
        return new_call
    return decorate
    
def remote_procedure_call(callback=None):
    def decorate(function):
        call_name = function.__name__
        def _make_rpc(*args, **kwargs):
            print function, args, kwargs
            return function(*args, **kwargs)
        return _make_rpc
    return decorate
    
def enter(entry_function):
    def decorate(function):
        def new_call(*args, **kwargs):
            print "Inside enter decorator", args, kwargs
            args, kwargs = entry_function(*args, **kwargs)
            return function(*args, **kwargs)
        return new_call
    return decorate    
    
import pride.authentication    
class Test(pride.authentication.Authenticated_Client):
    
    verbosity = {'_test' : 0}
    
    def _callback(*args, **kwargs):
        print "Inside _callback", args, kwargs
        return args, kwargs
    @pride.authentication.enter(_callback)
    @pride.authentication.remote_procedure_call(_callback)
    def _test(self, username, password):
        print "Inside _test", self, username, password
        
if __name__ == "__main__":
    t = Test(target_service='->Test')#, auto_login=False)
    t._test('a', 'b')