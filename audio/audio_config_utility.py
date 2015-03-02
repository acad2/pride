import mpre.base

launch_utility = mpre.base.Instruction("Metapython", "create",            
                             "mpre.audio.audiolibrary.Audio_Configuration_Utility", exit_when_finished=True)
if __name__ == "__main__":
    launch_utility.execute()