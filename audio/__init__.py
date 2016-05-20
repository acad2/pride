import audioop
import platform
import os

import pride
import pride.datatransfer

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
else:
    def install_pyaudio():
        os.system("pip install pyaudio")
                
def enable():
    """ Creates an instance of pride.audio.audiolibrary.Audio_Manager if
        one does not already exist. """
    if "/Python/Audio_Manager" not in pride.objects:
        pride.objects["/Python"].create("pride.audio.audiolibrary.Audio_Manager")
                    
def mix_signals(audio_data, bit_width):
    _data = []
    size = max(len(data) for data in audio_data)
    for index in range(size):
        samples = ''
        for data in audio_data:
            try:
                samples += data[index]
            except IndexError:
                continue
        _data.append(audioop.avg(samples, bit_width))
    return _data
                                
class Audio_Transfer(pride.datatransfer.Data_Transfer_Client):
    """ A data transfer client that outputs data from the specified audio 
        input to any specified receivers (default: Microphone).
        
        Audio data received from clients is output through the specified
        audio output (default: Speakers). """
        
    defaults = {"audio_input" : "/Python/Audio_Manager/Audio_Input",
                "audio_output" : "/Python/Audio_Manager/Audio_Output",
                "receivers" : tuple()}
                
    required_attributes = ("receivers", )  
    
    def __init__(self, **kwargs):
        super(Audio_Transfer, self).__init__(**kwargs)
        objects[self.audio_input].add_listener(self.reference)
     
    def handle_audio_input(self, audio_data):
        for receiver in self.receivers:
            self.send_to(receiver, audio_data)
            
    def receive(self, messages):        
        audio_output = objects[self.audio_output]
        data = pride.audio.mix_signals([message for sender, message in messages], 
                                       audio_output.sample_size)
        audio_output.handle_audio_input(data)           
        