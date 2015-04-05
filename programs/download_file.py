import mpre
Instruction = mpre.Instruction
    
if __name__ == "__main__":    
    options = {"parse_args" : True,
               "exit_when_finished" : True}  
    Instruction("Metapython", "create", "mpre.network2.Download", **options).execute()