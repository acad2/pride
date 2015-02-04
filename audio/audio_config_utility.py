#  Metapython.audio_config_utility - create config file for audiolibrary.audio_manager

import mpre.base as base
Instruction = base.Instruction

def metapython_main():
    Instruction("System", "create", "mpre.audio.audiolibrary.Audio_Configuration_Utility",            exit_when_finished=True).execute()   
if __name__ == "__main__":
    metapython_main()