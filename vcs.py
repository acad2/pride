import pride.authentication2

class Version_Control(pride.authentication2.Authenticated_Service):
    
    database_structure = {"Repository" : ("module_id PRIMARY_KEY BLOB", "module_name TEXT",
                                          "module_source TEXT", "repo_id BLOB")}
                                 
    remotely_available_procedures = ("save_module", "load_module")
    
    def save_module(self, module_name, module_source, module_id, repo_id):
        self.database.insert_into("Repository", (module_id, module_name, module_source, repo_id))
        
    def load_module(self, module_name, module_id, repo_id):
        result = self.database.query("Repository", where={"module_id" : module_id, 
                                                           "module_name" : module_name, 
                                                           "repo_id" : repo_id}, retrieve_fields=("module_source", ))
        return result
        