""" Tests remote procedure call mechanism. """
import unittest

import mpre
import mpre.rpc
import mpre.authentication

HOST_INFO = ("192.168.1.240", 40022)

class Test_Responder(mpre.base.Base):
    """ Runs on the remote machine """
    def test_method(self, arguments, test_flag=False):
        self.alert("Received: {}, test_flag={}".format(arguments, test_flag))
        return True
        
class RPC_Test(unittest.TestCase):
    """ Attempt to perform a remote procedure call on the remote machine
        specified by HOST_INFO. """
    def test_remote_procedure_call(self):
        def _response(result):
            self.failUnless(result)
            self.failIf(isinstance(result, 
                                   mpre.authentication.UnauthorizedError))
            
        mpre.Instruction("Test_Responder", "test_method", 
                         (1, 2, 3, 'string', [4, 5, 6], {'testagain' : None}),
                         test_flag=True).execute(callback=_response,
                                                 host_info=(HOST_INFO))
                                                 
if __name__ == "__main__":
    unittest.main()