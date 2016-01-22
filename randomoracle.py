import collections
import time

import pride.authentication2
from pride.security import random_bytes

def random_oracle(input_bytes, output_size=16, 
                  memo=collections.defaultdict(lambda: random_bytes(output_size))):
    return memo[input_bytes]   
    
class Random_Oracle(pride.authentication2.Authenticated_Service):
    
    remotely_available_procedures = ("hash", )
    database_structure = {"Memo" : ("input_data BLOB PRIMARY_KEY", "output_data BLOB",
                                    "creator TEXT", "creation_date FLOAT")}
    
    def hash(self, input_data, output_size=16):
        try:
            return self.database.query("Memo", where={"input_data" : input_data}, 
                                       retrieve_fields=("output_data", ))[0]
        except IndexError:
            output_data = random_bytes(output_size)
            self.database.insert_into("Memo", (input_data, output_data, 
                                               self.session_id[self.current_session[0]],
                                               time.time()))
            return output_data
            

class Random_Oracle_Client(pride.authentication2.Authenticated_Client):
     
    defaults = {"target_service" : "->Random_Oracle"}
    verbosity = {"hash" : 0}
    
    @pride.authentication2.remote_procedure_call(callback_name="alert")
    def hash(self, input_data, output_size=16): pass
                               
                               
def test_random_oracle():
    oracle = Random_Oracle()
    client = Random_Oracle_Client(username="test", token_file_encrypted=False, token_file_indexable=True)
    client.hash("Testing!")
    client.hash("Testinf!")
    client.hash("Testing!")
    
if __name__ == "__main__":
    test_random_oracle()