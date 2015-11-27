def remote_procedure_call(callback):
    def decorate(function):
        call_name = function.__name__
        def _make_rpc(*args, **kwargs):
            self = args[0]
            print "Making request"
            self.session.execute(Instruction(self.target_service, call_name, 
                                             *args, **kwargs), callback)
        return _make_rpc
    return decorate
    
    
class Test(object):
    
    def callback(self, result):
        print self, result
        
    @remote_procedure_call(callback)
    def test_call(self, test_one): pass
        
if __name__ == "__main__":
    t = Test()
    t.test_call('woo!')