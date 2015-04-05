import mpre.base
Instruction = mpre.Instruction

def test_authentication():
    verbosity = 'vv'
    options = {"verbosity" : verbosity,
            "port" : 41337}
    
    options2 = {"verbosity" : verbosity,
                "target" : ("localhost", 41337)}
                
    Instruction("Metapython", "create", 
                "network2.Authenticated_Service", **options).execute()
                
    Instruction("Metapython", "create", 
                "network2.Authenticated_Client", **options2).execute()
    
    
def test_file_service():
    verbosity = 'vv'
    service_options = {"port" : 40021,
                    "verbosity" : verbosity}    
    
    download_options = {"target" : ("localhost", 40021),
                        "filename" : "demofile.exe",
                        "verbosity" : verbosity}
                        
    Instruction("Metapython", "create", "network2.File_Service", **service_options).execute()
    Instruction("Metapython", "create", "network2.Download", **download_options).execute()    