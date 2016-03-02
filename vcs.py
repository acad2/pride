import pride.authentication2
import pride.security

class Version_Control_System(pride.authentication2.Authenticated_Service):
    
    defaults = {"allow_registration" : True, "hash_type" : "sha512"}
    
    remotely_available_procedures = ("save_source", )
    
    def save_source(self, source, signature):
        source_hash = self.hash(source)
        session_id, host = self.current_session        
        self.database.insert_into("Sources", (self.session_id[session_id], # username
                                              self.hash(source), source, signature))
        return source_hash
        
    def hash(self, source):
        hasher = pride.security.hash_function(self.hash_type)
        hasher.update(source)
        return hasher.finalize()
        
    def load_source(self, source_hash):        
        result = self.database.query("Sources", where={"username" : self.current_user,
                                                       "source_hash" : source_hash},
                                     retrieve_fields=("source", "signature"))
        if not result:
            raise ValueError("Source hash not found in database")
        return result
        
        
class Version_Control_Client(pride.authentication2.Authenticated_Client):
            
    defaults = {"target_service" : "->Python->Version_Control_System"}

    @pride.authentication2.remote_procedure_call
    def save_source(self, source, signature)