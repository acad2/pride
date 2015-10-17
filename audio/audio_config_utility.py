import pride.base

launch_utility = pride.Instruction("Python", "create",            
                             "pride.audio.audiolibrary.Config_Utility", exit_when_finished=True)
if __name__ == "__main__":
    launch_utility.execute()