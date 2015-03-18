import mpre.base
import mpre.audio.audiolibrary as audiolibrary

Instruction = mpre.base.Instruction
      
def ensure_audio_enabled():
    if "Audio_Manager" not in mpre.environment.Component_Resolve:
        Instruction("Metapython", "create", 
                    "mpre.audio.audiolibrary.Audio_Manager").execute()
                    
ensure_audio_enabled()
      
def enable_audio(parent="Metapython"):
    """Executes the following instruction:
    
        Instruction("Metapython", "create", 
                    "mpre.audio.audiolibrary.Audio_Manager").execute()
    """                         
    Instruction(parent, "create", "mpre.audio.audiolibrary.Audio_Manager").execute()
    
def disable_audio(name="Audio_Manager"):
    Instruction(name, "delete").execute()
    
def wav_file_info(parse_args=True, **kwargs):
    wav_file = audiolibrary.Wav_File(parse_args=parse_args, **kwargs)
    
    print "{} information: ".format(wav_file.filename)
    for attribute in ("rate", "channels", "format", 
                      "sample_width", "number_of_frames"):
        print "{}: {}".format(attribute, getattr(wav_file, attribute))

def record_wav_file(parse_args=True, **kwargs):
    wav_file = audiolibrary.Wav_File(parse_args=parse_args, mode='wb', **kwargs)
    mpre.base.Instruction("Audio_Manager", "record", 
                          "Microphone", file=wav_file).execute()    