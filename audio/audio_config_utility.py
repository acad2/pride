import mpre.base

launch_utility = mpre.Instruction("Python", "create",            
                             "mpre.audio.audiolibrary.Config_Utility", exit_when_finished=True)
if __name__ == "__main__":
    launch_utility.execute()