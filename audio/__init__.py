import platform
import os

import pride

def enable():
    """ Creates an instance of pride.audio.audiolibrary.Audio_Manager if
        one does not already exist. """
    if "Audio_Manager" not in pride.environment.objects:
        pride.Instruction("Python", "create", 
                         "pride.audio.audiolibrary.Audio_Manager").execute()
                    
if "Linux" == platform.system():
    def install_pyalsaaudio():
        source = '\n'.join(("sudo apt-get install python-dev",
                            "sudo apt-get install libasound2",
                            "sudo apt-get install libasound2-dev",
                            "sudo pip install pyalsaaudio"))
        if pride.shell.get_permission("{}\n\n".format(source) +
                                     "allow the above commands? "):
            [os.system(command) for command in source.split("\n")]
                
    def install_pyaudio():
        source = []
        for dependency in ("libportaudio0", "libportaudio2", "libportaudiocpp0",
                           "portaudio19-dev"):
            source.append("sudo apt-get install {}".format(dependency))
        if pride.shell.get_permission('\n'.join(source) + "\n\n" +
                                     "allow the above commands? "):        
            [os.system(command) for command in source]