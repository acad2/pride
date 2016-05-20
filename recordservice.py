import pride.authentication2
import pride.security

class Record_Service(pride.authentication2.Authenticated_Service):
    
    defaults = {"hash_type" : "SHA512"}
    
    remotely_available_procedures = ("save_record", "load_record")
    
    database_structure = {"Public_Record" : ("filename BLOB PRIMARY_KEY", "file_data BLOB", 
                                             "file_hash BLOB", "file_description BLOB", "submitter BLOB"),
                          "Private_Record" : ("filename BLOB PRIMARY KEY", "file_data BLOB",
                                              "file_hash BLOB", "file_description BLOB", "submitter BLOB")}                                                 
    
    def save_record(self, access, file_data, filename, file_description=''):
        table = "Public_Record" if access.lower() == "public" else "Private_Record"   
        file_hash = self.hash(file_data)
        try:
            self.database.insert_into(table, (filename, file_data, file_hash, file_description, self.current_user))        
        except self.database.IntegrityError:
            self.database.update_table(table, {"filename" : filename}, 
                                       {"file_data" : file_data, "file_hash" : file_hash, 
                                        "file_description" : file_description, "submitter" : self.current_user})        
        
    def load_record(self, access, filename, file_description=''):
        where = {"filename " : filename}
        if file_description:
            where["file_description"] = file_description
        if access.lower() == "public":
            record = "Public_Record"
        else:
            record = "Private_Record"
            where["submitter"] = self.current_user        
        return self.database.query(record, where=where, retrieve_fields=("file_data", "file_hash", "submitter"))
         
    def hash(self, file_data):    
        hasher = pride.security.hash_function(self.hash_type)
        hasher.update(file_data)
        return hasher.finalize()        
        
        
class Record_Service_Client(pride.authentication2.Authenticated_Client):
            
    defaults = {"target_service" : "/Python/Record_Service",
                "token_file_encrypted" : False, "token_file_indexable" : True}
    
    verbosity = {"save_record" : 0, "load_record" : 0, "auto_login" : 0}
    
    @pride.authentication2.remote_procedure_call(callback_name="display_record")
    def save_record(self, access, file_data, filename, file_description=''): pass
    
    @pride.authentication2.remote_procedure_call(callback_name="display_record")
    def load_record(self, access, filename, file_description=''): pass
    
    def display_record(self, records):
        if records is not None:
            self.alert("Received records:\n{}", (records, ), level=0)
        
        
def test_Record_Service():
    service = objects["/Python"].create(Record_Service)    
    client = Record_Service_Client(username="Ella")
    record = ("public", "Wonderful test data :)", "test filename!", "cool description")
    record2 = ("private", "Nobody but you ;)", "secret filename!", "nondescript")
    client.save_record(*record)
    client.save_record(*record2)    
    client.load_record("public", "test filename!")
    client.load_record("private", "secret filename!")
        
if __name__ == "__main__":
    test_Record_Service()
    