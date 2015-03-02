import mpre.base
Instruction = mpre.base.Instruction

def enable_audio(parent="Metapython"):
    """Executes the following instruction:
    
        Instruction("Metapython", "create", "mpre.audio.audiolibrary.Audio_Manager").execute()
    """                         
    Instruction(parent, "create", "mpre.audio.audiolibrary.Audio_Manager").execute()
    
def disable_audio(name="Audio_Manager"):
    Instruction(name, "delete").execute()